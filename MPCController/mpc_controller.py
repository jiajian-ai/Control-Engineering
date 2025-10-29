"""
MPC (Model Predictive Control) 控制器实现
模型预测控制 - 基于优化的先进控制方法

MPC特点:
- 基于系统模型预测未来状态
- 滚动优化求解最优控制序列
- 可以处理约束
- 适合多变量系统
"""

import numpy as np
from scipy.optimize import minimize
import sys

# 设置UTF-8编码输出
if sys.platform == 'win32' and not hasattr(sys.stdout, '_wrapped'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdout._wrapped = True


class MPCController:
    """
    模型预测控制器
    
    参数:
        prediction_horizon: 预测时域 (N步)
        control_horizon: 控制时域 (M步, M <= N)
        dt: 采样时间
        Q: 状态权重矩阵
        R: 控制权重矩阵
        u_min, u_max: 控制输入约束
    """
    
    def __init__(self, prediction_horizon=10, control_horizon=5, dt=0.01,
                 Q=None, R=None, u_min=-100, u_max=100):
        self.N = prediction_horizon  # 预测时域
        self.M = min(control_horizon, prediction_horizon)  # 控制时域
        self.dt = dt
        
        # 默认权重矩阵
        self.Q = Q if Q is not None else np.eye(4)  # 状态权重
        self.R = R if R is not None else np.eye(1) * 0.1  # 控制权重
        
        # 控制约束
        self.u_min = u_min
        self.u_max = u_max
        
        # 目标状态 [x, x_dot, theta, theta_dot]
        self.target_state = np.array([0.0, 0.0, 0.0, 0.0])
        
        # 历史记录
        self.control_history = []
        self.cost_history = []
    
    def set_target(self, target_state):
        """设置目标状态"""
        self.target_state = np.array(target_state)
    
    def predict_state(self, current_state, control_sequence, system_model):
        """
        预测未来状态轨迹
        
        参数:
            current_state: 当前状态 [x, x_dot, theta, theta_dot]
            control_sequence: 控制序列 [u0, u1, ..., u_{M-1}]
            system_model: 系统动力学模型函数
        
        返回:
            predicted_states: (N+1) x 4 矩阵，包含当前和未来N步的状态
        """
        predicted_states = np.zeros((self.N + 1, 4))
        predicted_states[0] = current_state
        
        for i in range(self.N):
            # 如果超过控制时域，使用最后一个控制输入
            u = control_sequence[min(i, self.M - 1)]
            
            # 预测下一状态
            predicted_states[i + 1] = system_model(predicted_states[i], u, self.dt)
        
        return predicted_states
    
    def cost_function(self, control_sequence, current_state, system_model):
        """
        MPC代价函数
        
        J = Σ[(x_k - x_ref)^T Q (x_k - x_ref) + u_k^T R u_k]
        
        参数:
            control_sequence: 待优化的控制序列
            current_state: 当前状态
            system_model: 系统模型
        
        返回:
            总代价
        """
        # 预测状态轨迹
        predicted_states = self.predict_state(current_state, control_sequence, system_model)
        
        cost = 0.0
        
        # 状态误差代价
        for i in range(1, self.N + 1):
            state_error = predicted_states[i] - self.target_state
            cost += state_error.T @ self.Q @ state_error
        
        # 控制代价
        for i in range(self.M):
            cost += control_sequence[i]**2 * self.R[0, 0]
        
        # 控制变化率代价（平滑性）
        for i in range(self.M - 1):
            delta_u = control_sequence[i + 1] - control_sequence[i]
            cost += 0.01 * delta_u**2  # 平滑性惩罚
        
        return cost
    
    def update(self, current_state, system_model, initial_guess=None):
        """
        MPC更新 - 求解优化问题
        
        参数:
            current_state: 当前状态 [x, x_dot, theta, theta_dot]
            system_model: 系统动力学模型
            initial_guess: 控制序列初始猜测
        
        返回:
            optimal_control: 最优控制输入（当前时刻）
        """
        # 初始猜测
        if initial_guess is None:
            u0 = np.zeros(self.M)
        else:
            u0 = initial_guess
        
        # 定义约束
        bounds = [(self.u_min, self.u_max) for _ in range(self.M)]
        
        # 优化求解
        result = minimize(
            fun=lambda u: self.cost_function(u, current_state, system_model),
            x0=u0,
            method='SLSQP',
            bounds=bounds,
            options={'maxiter': 100, 'ftol': 1e-6}
        )
        
        optimal_control_sequence = result.x
        optimal_cost = result.fun
        
        # 记录历史
        self.control_history.append(optimal_control_sequence[0])
        self.cost_history.append(optimal_cost)
        
        # 返回第一个控制输入（滚动优化）
        return optimal_control_sequence[0]
    
    def reset(self):
        """重置历史记录"""
        self.control_history = []
        self.cost_history = []


class LinearMPCController:
    """
    线性MPC控制器（更快速的实现）
    
    假设系统可以线性化：x_{k+1} = A*x_k + B*u_k
    使用二次规划求解
    """
    
    def __init__(self, prediction_horizon=10, control_horizon=5, dt=0.01,
                 Q=None, R=None, u_min=-100, u_max=100):
        self.N = prediction_horizon
        self.M = min(control_horizon, prediction_horizon)
        self.dt = dt
        
        self.Q = Q if Q is not None else np.diag([10, 1, 100, 10])  # 状态权重
        self.R = R if R is not None else np.array([[0.1]])  # 控制权重
        
        self.u_min = u_min
        self.u_max = u_max
        
        self.target_state = np.array([0.0, 0.0, 0.0, 0.0])
        
        # 历史记录
        self.control_history = []
        self.state_predictions = []
    
    def linearize_system(self, x_op, u_op, system_params):
        """
        在工作点附近线性化系统
        
        对于CartPole: x = [x, x_dot, theta, theta_dot]
        """
        M, m, l, g = system_params
        
        # 在竖直平衡点 theta=0 附近线性化
        # x_dot = A*x + B*u
        A = np.array([
            [0, 1, 0, 0],
            [0, 0, -m*g/M, 0],
            [0, 0, 0, 1],
            [0, 0, (M+m)*g/(M*l), 0]
        ])
        
        B = np.array([
            [0],
            [1/M],
            [0],
            [-1/(M*l)]
        ])
        
        # 离散化 (欧拉法)
        Ad = np.eye(4) + self.dt * A
        Bd = self.dt * B
        
        return Ad, Bd
    
    def update(self, current_state, system_params):
        """
        线性MPC更新
        
        参数:
            current_state: [x, x_dot, theta, theta_dot]
            system_params: [M, m, l, g]
        """
        # 线性化
        Ad, Bd = self.linearize_system(current_state, 0, system_params)
        
        # 构建预测矩阵
        # X = Phi*x0 + Gamma*U
        Phi = np.zeros((4 * self.N, 4))
        Gamma = np.zeros((4 * self.N, self.M))
        
        A_power = Ad
        for i in range(self.N):
            Phi[4*i:4*(i+1), :] = A_power
            for j in range(min(i + 1, self.M)):
                if i - j >= 0:
                    Gamma[4*i:4*(i+1), j:j+1] = np.linalg.matrix_power(Ad, i - j) @ Bd
            A_power = A_power @ Ad
        
        # 构建代价函数矩阵
        Q_bar = np.kron(np.eye(self.N), self.Q)
        R_bar = np.kron(np.eye(self.M), self.R)
        
        # QP问题: min 0.5*U^T*H*U + f^T*U
        H = 2 * (Gamma.T @ Q_bar @ Gamma + R_bar)
        x_ref = np.tile(self.target_state, self.N)
        f = 2 * Gamma.T @ Q_bar @ (Phi @ current_state - x_ref)
        
        # 简单的约束处理：投影到可行域
        try:
            U_opt = -np.linalg.solve(H, f)
        except:
            U_opt = np.zeros(self.M)
        
        # 约束投影
        U_opt = np.clip(U_opt, self.u_min, self.u_max)
        
        # 记录
        self.control_history.append(U_opt[0])
        
        return U_opt[0]
    
    def reset(self):
        """重置"""
        self.control_history = []
        self.state_predictions = []


def cartpole_dynamics(state, u, dt):
    """
    CartPole系统动力学模型（用于MPC预测）
    
    参数:
        state: [x, x_dot, theta, theta_dot]
        u: 控制力
        dt: 时间步长
    
    返回:
        next_state: 下一时刻状态
    """
    # 系统参数
    M = 1.0  # 小车质量
    m = 0.1  # 杆子质量
    l = 0.5  # 杆子长度
    g = 9.8  # 重力加速度
    
    x, x_dot, theta, theta_dot = state
    
    # 动力学方程
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    
    temp = (u + m * l * theta_dot**2 * sin_theta) / (M + m)
    theta_acc = (g * sin_theta - cos_theta * temp) / \
               (l * (4.0/3.0 - m * cos_theta**2 / (M + m)))
    x_acc = temp - m * l * theta_acc * cos_theta / (M + m)
    
    # 欧拉积分
    x_new = x + x_dot * dt
    x_dot_new = x_dot + x_acc * dt
    theta_new = theta + theta_dot * dt
    theta_dot_new = theta_dot + theta_acc * dt
    
    return np.array([x_new, x_dot_new, theta_new, theta_dot_new])


class AdaptiveMPCController:
    """
    自适应MPC控制器
    
    特点:
    - 根据系统状态自动调整权重
    - 根据误差大小调整预测时域
    - 更智能的控制策略
    """
    
    def __init__(self, base_N=10, base_M=5, dt=0.01):
        self.base_N = base_N
        self.base_M = base_M
        self.dt = dt
        
        # 自适应参数
        self.Q_base = np.diag([10, 1, 100, 10])
        self.R_base = np.array([[0.1]])
        
        self.u_min = -100
        self.u_max = 100
        
        self.target_state = np.array([0.0, 0.0, 0.0, 0.0])
        self.control_history = []
    
    def adapt_parameters(self, current_state):
        """
        根据当前状态自适应调整参数
        """
        theta = current_state[2]
        theta_dot = current_state[3]
        
        # 角度越大，增加角度权重
        angle_weight = 100 * (1 + 10 * abs(theta))
        velocity_weight = 10 * (1 + 5 * abs(theta_dot))
        
        Q = np.diag([10, 1, angle_weight, velocity_weight])
        
        # 调整预测时域
        if abs(theta) > 0.15:  # 大角度，缩短时域快速响应
            N = max(5, self.base_N // 2)
            M = max(3, self.base_M // 2)
        else:  # 小角度，延长时域精细控制
            N = self.base_N
            M = self.base_M
        
        return Q, N, M
    
    def update(self, current_state, system_model):
        """自适应MPC更新"""
        # 自适应调整参数
        Q, N, M = self.adapt_parameters(current_state)
        
        # 创建临时MPC控制器
        mpc = MPCController(
            prediction_horizon=N,
            control_horizon=M,
            dt=self.dt,
            Q=Q,
            R=self.R_base,
            u_min=self.u_min,
            u_max=self.u_max
        )
        mpc.set_target(self.target_state)
        
        # 求解
        u_opt = mpc.update(current_state, system_model)
        
        self.control_history.append(u_opt)
        return u_opt
    
    def reset(self):
        self.control_history = []


if __name__ == "__main__":
    # 测试MPC控制器
    print("=" * 60)
    print("MPC控制器测试")
    print("=" * 60)
    
    # 创建MPC控制器
    mpc = MPCController(
        prediction_horizon=10,
        control_horizon=5,
        dt=0.02,
        Q=np.diag([10, 1, 100, 10]),
        R=np.array([[0.1]]),
        u_min=-50,
        u_max=50
    )
    
    # 初始状态（小角度偏离）
    current_state = np.array([0.0, 0.0, 0.1, 0.0])
    
    print(f"\n初始状态: {current_state}")
    print(f"目标状态: {mpc.target_state}")
    
    # 测试一步优化
    print("\n执行MPC优化...")
    u_opt = mpc.update(current_state, cartpole_dynamics)
    
    print(f"最优控制: {u_opt:.4f} N")
    print(f"优化代价: {mpc.cost_history[-1]:.4f}")
    
    # 预测未来状态
    control_seq = [u_opt] * mpc.M
    predicted = mpc.predict_state(current_state, control_seq, cartpole_dynamics)
    
    print(f"\n预测状态轨迹（前5步）:")
    for i in range(min(5, len(predicted))):
        print(f"  Step {i}: {predicted[i]}")
    
    print("\n✓ MPC控制器测试完成!")

