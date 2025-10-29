"""
CartPole倒立摆 - PID控制实现
使用PID控制器解决经典的倒立摆平衡问题

CartPole问题描述:
- 小车可以左右移动
- 杆子连接在小车上，需要保持平衡
- 目标: 通过控制小车的左右移动，保持杆子竖直
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import sys

# 设置UTF-8编码输出
if sys.platform == 'win32' and not hasattr(sys.stdout, '_wrapped'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdout._wrapped = True

# 设置字体为Times New Roman
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 10

try:
    from .pid_controller import PIDController
except ImportError:
    from pid_controller import PIDController


class CartPole:
    """
    CartPole倒立摆系统
    
    状态变量:
        x: 小车位置
        x_dot: 小车速度
        theta: 杆子角度 (0 = 竖直向上)
        theta_dot: 杆子角速度
    
    参数:
        M: 小车质量
        m: 杆子质量
        l: 杆子长度
        g: 重力加速度
    """
    
    def __init__(self, M=1.0, m=0.1, l=0.5, g=9.8):
        self.M = M  # 小车质量
        self.m = m  # 杆子质量
        self.l = l  # 杆子长度 (到质心)
        self.g = g  # 重力加速度
        
        # 状态变量
        self.x = 0.0           # 小车位置
        self.x_dot = 0.0       # 小车速度
        self.theta = 0.0       # 杆子角度 (弧度)
        self.theta_dot = 0.0   # 杆子角速度
        
        # 历史记录
        self.history = {
            'x': [self.x],
            'x_dot': [self.x_dot],
            'theta': [self.theta],
            'theta_dot': [self.theta_dot]
        }
    
    def reset(self, x=0.0, x_dot=0.0, theta=0.1, theta_dot=0.0):
        """重置系统状态"""
        self.x = x
        self.x_dot = x_dot
        self.theta = theta  # 初始偏离一点
        self.theta_dot = theta_dot
        
        self.history = {
            'x': [self.x],
            'x_dot': [self.x_dot],
            'theta': [self.theta],
            'theta_dot': [self.theta_dot]
        }
    
    def step(self, force, dt):
        """
        更新系统状态
        
        参数:
            force: 施加在小车上的力
            dt: 时间步长
        
        返回:
            (x, x_dot, theta, theta_dot)
        """
        # 使用Runge-Kutta 4阶方法求解
        def derivatives(state, u):
            """计算状态导数"""
            x, x_dot, theta, theta_dot = state
            
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)
            
            # 系统动力学方程
            temp = (u + self.m * self.l * theta_dot**2 * sin_theta) / (self.M + self.m)
            theta_acc = (self.g * sin_theta - cos_theta * temp) / \
                       (self.l * (4.0/3.0 - self.m * cos_theta**2 / (self.M + self.m)))
            x_acc = temp - self.m * self.l * theta_acc * cos_theta / (self.M + self.m)
            
            return np.array([x_dot, x_acc, theta_dot, theta_acc])
        
        # RK4积分
        state = np.array([self.x, self.x_dot, self.theta, self.theta_dot])
        k1 = derivatives(state, force)
        k2 = derivatives(state + dt/2 * k1, force)
        k3 = derivatives(state + dt/2 * k2, force)
        k4 = derivatives(state + dt * k3, force)
        
        state_new = state + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
        
        # 更新状态
        self.x, self.x_dot, self.theta, self.theta_dot = state_new
        
        # 记录历史
        self.history['x'].append(self.x)
        self.history['x_dot'].append(self.x_dot)
        self.history['theta'].append(self.theta)
        self.history['theta_dot'].append(self.theta_dot)
        
        return self.x, self.x_dot, self.theta, self.theta_dot
    
    def is_failed(self, x_threshold=2.4, theta_threshold=0.21):
        """
        检查是否失败
        
        失败条件:
        - 小车超出范围 (|x| > x_threshold)
        - 杆子倾斜过大 (|theta| > theta_threshold ≈ 12度)
        """
        return abs(self.x) > x_threshold or abs(self.theta) > theta_threshold


class CartPolePIDController:
    """CartPole的PID控制器"""
    
    def __init__(self):
        """
        初始化多个PID控制器
        
        策略1: 仅控制角度 (单PID)
        策略2: 角度+位置级联控制 (双PID)
        """
        # 策略1: 单PID - 仅控制角度
        self.angle_pid = PIDController(
            Kp=150.0,   # 比例增益 - 快速响应角度偏差
            Ki=0.5,     # 积分增益 - 消除稳态误差
            Kd=40.0,    # 微分增益 - 阻尼振荡
            setpoint=0.0  # 目标角度为0 (竖直)
        )
        
        # 策略2: 双PID - 位置控制器
        self.position_pid = PIDController(
            Kp=1.0,
            Ki=0.01,
            Kd=8.0,
            setpoint=0.0  # 目标位置为0 (中心)
        )
        
        self.angle_pid.set_output_limits(-100, 100)
        self.position_pid.set_output_limits(-0.3, 0.3)
    
    def control_angle_only(self, theta, theta_dot, dt):
        """
        策略1: 仅控制角度
        
        这是最简单的策略，只关注保持杆子竖直
        缺点: 小车可能会漂移
        """
        force = self.angle_pid.update(theta, dt)
        return force
    
    def control_cascade(self, x, theta, dt):
        """
        策略2: 级联控制
        
        外环: 控制小车位置
        内环: 控制杆子角度
        
        这种策略既保持平衡，又防止小车漂移
        """
        # 外环: 位置控制器输出期望角度
        desired_angle = self.position_pid.update(x, dt)
        
        # 内环: 角度控制器，跟踪期望角度
        self.angle_pid.set_setpoint(desired_angle)
        force = self.angle_pid.update(theta, dt)
        
        return force
    
    def reset(self):
        """重置所有PID控制器"""
        self.angle_pid.reset()
        self.position_pid.reset()


def run_cartpole_experiment():
    """运行CartPole PID控制实验"""
    print("=" * 70)
    print("CartPole倒立摆 - PID控制实验")
    print("=" * 70)
    
    # 仿真参数
    dt = 0.02  # 20ms控制周期 (50Hz)
    sim_time = 10.0  # 10秒仿真
    time_steps = int(sim_time / dt)
    time = np.linspace(0, sim_time, time_steps)
    
    # 创建图表
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(4, 2, figure=fig, hspace=0.35, wspace=0.3)
    
    # 测试不同的策略和初始条件
    experiments = [
        {
            'name': 'Strategy 1: Angle Only (Small Disturbance)',
            'strategy': 'angle_only',
            'initial_theta': 0.1,  # ~5.7 degrees
            'color': 'blue'
        },
        {
            'name': 'Strategy 1: Angle Only (Large Disturbance)',
            'strategy': 'angle_only',
            'initial_theta': 0.2,  # ~11.5 degrees
            'color': 'red'
        },
        {
            'name': 'Strategy 2: Cascade Control (Small Disturbance)',
            'strategy': 'cascade',
            'initial_theta': 0.1,
            'color': 'green'
        },
        {
            'name': 'Strategy 2: Cascade Control (Large Disturbance)',
            'strategy': 'cascade',
            'initial_theta': 0.2,
            'color': 'purple'
        }
    ]
    
    # 创建子图
    ax1 = fig.add_subplot(gs[0, :])  # 角度
    ax2 = fig.add_subplot(gs[1, :])  # 位置
    ax3 = fig.add_subplot(gs[2, 0])  # 控制力
    ax4 = fig.add_subplot(gs[2, 1])  # 相图
    ax5 = fig.add_subplot(gs[3, :])  # 性能对比
    
    results = []
    
    for exp in experiments:
        print(f"\n运行实验: {exp['name']}")
        print(f"  初始角度: {exp['initial_theta']:.3f} rad ({np.degrees(exp['initial_theta']):.1f}°)")
        
        # 创建系统和控制器
        cartpole = CartPole()
        controller = CartPolePIDController()
        
        # 重置状态
        cartpole.reset(theta=exp['initial_theta'])
        controller.reset()
        
        # 运行仿真
        forces = []
        failed = False
        fail_time = None
        
        for i, t in enumerate(time):
            # 获取当前状态
            x, x_dot, theta, theta_dot = cartpole.x, cartpole.x_dot, cartpole.theta, cartpole.theta_dot
            
            # 计算控制力
            if exp['strategy'] == 'angle_only':
                force = controller.control_angle_only(theta, theta_dot, dt)
            else:  # cascade
                force = controller.control_cascade(x, theta, dt)
            
            forces.append(force)
            
            # 检查是否失败
            if not failed and cartpole.is_failed():
                failed = True
                fail_time = t
                print(f"  ❌ 失败时间: {t:.2f}s")
                break
            
            # 更新系统
            cartpole.step(force, dt)
        
        if not failed:
            print(f"  ✅ 成功保持平衡 {sim_time}秒")
            final_angle_error = np.mean(np.abs(cartpole.history['theta'][-50:]))
            final_position_error = np.mean(np.abs(cartpole.history['x'][-50:]))
            print(f"  最终角度误差: {np.degrees(final_angle_error):.3f}°")
            print(f"  最终位置误差: {final_position_error:.3f}m")
        
        # 记录结果
        results.append({
            'name': exp['name'],
            'history': cartpole.history,
            'forces': forces,
            'time': time[:len(forces)],
            'failed': failed,
            'fail_time': fail_time,
            'color': exp['color']
        })
        
        # 绘制结果
        result_time = time[:len(forces)]
        ax1.plot(result_time, np.degrees(cartpole.history['theta'][:len(forces)]), 
                label=exp['name'], linewidth=2, color=exp['color'], alpha=0.8)
        ax2.plot(result_time, cartpole.history['x'][:len(forces)], 
                linewidth=2, color=exp['color'], alpha=0.8)
        ax3.plot(result_time, forces, linewidth=1.5, color=exp['color'], alpha=0.8)
        
        # 相图 (角度 vs 角速度)
        ax4.plot(np.degrees(cartpole.history['theta'][:len(forces)]), 
                np.degrees(cartpole.history['theta_dot'][:len(forces)]),
                linewidth=1.5, color=exp['color'], alpha=0.6)
    
    # 设置图表
    ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Pole Angle (degrees)', fontsize=12)
    ax1.set_title('Pole Angle Response (Target: 0 degrees)', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=9, loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([-15, 15])
    
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax2.axhline(y=2.4, color='r', linestyle=':', alpha=0.5, label='Boundary')
    ax2.axhline(y=-2.4, color='r', linestyle=':', alpha=0.5)
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Cart Position (m)', fontsize=12)
    ax2.set_title('Cart Position Response', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([-3, 3])
    
    ax3.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax3.set_xlabel('Time (s)', fontsize=12)
    ax3.set_ylabel('Control Force (N)', fontsize=12)
    ax3.set_title('Control Signal', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    ax4.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax4.axvline(x=0, color='k', linestyle='--', alpha=0.3)
    ax4.set_xlabel('Angle (degrees)', fontsize=12)
    ax4.set_ylabel('Angular Velocity (deg/s)', fontsize=12)
    ax4.set_title('Phase Portrait: Angle vs Angular Velocity', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 性能对比
    categories = ['Strategy 1\nSmall Dist.', 'Strategy 1\nLarge Dist.', 
                  'Strategy 2\nSmall Dist.', 'Strategy 2\nLarge Dist.']
    success = [not r['failed'] for r in results]
    colors_bar = [r['color'] for r in results]
    
    bars = ax5.bar(categories, [1 if s else 0 for s in success], 
                   color=colors_bar, alpha=0.7, edgecolor='black')
    ax5.set_ylabel('Success/Failure', fontsize=12)
    ax5.set_title('Control Strategy Performance Comparison', fontsize=14, fontweight='bold')
    ax5.set_ylim([0, 1.2])
    ax5.set_yticks([0, 1])
    ax5.set_yticklabels(['Failed', 'Success'])
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 在柱状图上添加文字
    for i, (bar, result) in enumerate(zip(bars, results)):
        if result['failed']:
            label = f"Failed\n{result['fail_time']:.2f}s"
            ax5.text(i, 0.05, label, ha='center', va='bottom', fontsize=10, fontweight='bold')
        else:
            label = "Success"
            ax5.text(i, 1.05, label, ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.suptitle('CartPole Inverted Pendulum - PID Control Experiment\nPID vs Reinforcement Learning', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    output_path = os.path.join('..', 'output', 'cartpole_pid_control.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: {output_path}")
    plt.close()
    
    print("\n" + "=" * 70)
    print("实验完成!")
    print("=" * 70)


def compare_pid_vs_rl():
    """
    PID vs 强化学习对比分析
    """
    print("\n" + "=" * 70)
    print("PID控制 vs 强化学习 - 对比分析")
    print("=" * 70)
    
    comparison = """
    
    📊 CartPole问题中的PID vs 强化学习
    
    ┌────────────────────┬─────────────────────┬─────────────────────┐
    │      对比项        │      PID控制        │     强化学习(RL)    │
    ├────────────────────┼─────────────────────┼─────────────────────┤
    │  设计难度          │  ⭐⭐⭐            │  ⭐⭐              │
    │                    │  需要理解系统动力学 │  自动学习策略       │
    ├────────────────────┼─────────────────────┼─────────────────────┤
    │  训练时间          │  ⭐⭐⭐⭐⭐        │  ⭐⭐              │
    │                    │  无需训练，直接使用 │  需要大量试错       │
    ├────────────────────┼─────────────────────┼─────────────────────┤
    │  性能              │  ⭐⭐⭐⭐          │  ⭐⭐⭐⭐⭐        │
    │                    │  在已知模型下很好   │  可能找到更优策略   │
    ├────────────────────┼─────────────────────┼─────────────────────┤
    │  鲁棒性            │  ⭐⭐⭐            │  ⭐⭐⭐⭐          │
    │                    │  对参数变化敏感     │  对变化适应性强     │
    ├────────────────────┼─────────────────────┼─────────────────────┤
    │  可解释性          │  ⭐⭐⭐⭐⭐        │  ⭐⭐              │
    │                    │  每个参数有明确意义 │  策略是黑盒         │
    ├────────────────────┼─────────────────────┼─────────────────────┤
    │  计算资源          │  ⭐⭐⭐⭐⭐        │  ⭐⭐              │
    │                    │  计算量极小         │  训练需要大量计算   │
    ├────────────────────┼─────────────────────┼─────────────────────┤
    │  泛化能力          │  ⭐⭐              │  ⭐⭐⭐⭐          │
    │                    │  限于相似系统       │  可迁移到变体       │
    └────────────────────┴─────────────────────┴─────────────────────┘
    
    ✅ PID的优势:
      1. 不需要训练，直接部署
      2. 参数物理意义明确，易于调试
      3. 计算量小，实时性好
      4. 对于线性或近线性系统效果很好
      5. 几十年的工程实践经验
    
    ❌ PID的局限:
      1. 需要手动调参（虽然有经验法则）
      2. 对非线性系统效果有限
      3. 难以处理约束和多目标优化
      4. 在复杂环境中可能不够鲁棒
    
    ✅ 强化学习的优势:
      1. 自动学习最优策略
      2. 可以处理复杂非线性系统
      3. 可以优化长期回报
      4. 能够处理部分可观测问题
    
    ❌ 强化学习的局限:
      1. 需要大量数据和训练时间
      2. 可能不稳定，需要精心设计奖励函数
      3. 黑盒特性，难以调试和解释
      4. 可能学到非预期的策略
    
    💡 实践建议:
      • 简单控制问题: 优先考虑PID
      • 有明确数学模型: PID通常足够
      • 超高维状态空间: 考虑深度RL
      • 需要快速部署: 使用PID
      • 追求极致性能: 可尝试RL
      • 混合方法: PID+RL（用PID初始化RL策略）
    
    """
    print(comparison)


if __name__ == "__main__":
    run_cartpole_experiment()
    compare_pid_vs_rl()

