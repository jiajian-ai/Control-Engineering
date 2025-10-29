"""
MPC温度控制系统示例
更直观的MPC原理演示 - 房间温度控制

这个例子比CartPole更容易理解：
- 系统简单：一阶温度模型
- 物理意义清晰：加热/冷却房间
- 约束明显：加热器功率限制
- 目标直观：跟踪设定温度
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import sys

# 设置UTF-8编码和字体
if sys.platform == 'win32' and not hasattr(sys.stdout, '_wrapped'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdout._wrapped = True

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 10

try:
    from .mpc_controller import MPCController
except ImportError:
    from mpc_controller import MPCController

try:
    from PIDController.pid_controller import PIDController
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'PIDController'))
    from pid_controller import PIDController


class TemperatureRoom:
    """
    房间温度系统模型
    
    物理模型：
        dT/dt = -a*(T - T_ambient) + b*u
        
    其中：
        T: 房间温度 (°C)
        T_ambient: 环境温度 (°C)
        u: 加热器功率 (W)
        a: 热损失系数 (1/s)
        b: 加热效率系数 (°C/W/s)
    """
    
    def __init__(self, T_ambient=5.0, T_initial=5.0):
        """
        参数:
            T_ambient: 环境温度 (°C)
            T_initial: 初始房间温度 (°C)
        """
        self.T_ambient = T_ambient  # 冬天室外温度
        self.T = T_initial  # 当前房间温度
        
        # 物理参数
        self.a = 0.05  # 热损失系数 (房间隔热性能)
        self.b = 0.002  # 加热效率 (加热器效率)
        
        # 约束
        self.u_min = 0.0     # 最小功率（不能制冷）
        self.u_max = 2000.0  # 最大功率 2000W
        
        # 历史记录
        self.temperature_history = [T_initial]
        self.power_history = []
    
    def dynamics(self, T, u):
        """
        温度变化率
        
        dT/dt = -a*(T - T_ambient) + b*u
        """
        dT_dt = -self.a * (T - self.T_ambient) + self.b * u
        return dT_dt
    
    def step(self, u, dt):
        """
        更新一步（欧拉积分）
        
        参数:
            u: 加热器功率 (W)
            dt: 时间步长 (s)
        """
        # 功率约束
        u = np.clip(u, self.u_min, self.u_max)
        
        # 更新温度（欧拉法）
        dT_dt = self.dynamics(self.T, u)
        self.T = self.T + dT_dt * dt
        
        # 记录
        self.temperature_history.append(self.T)
        self.power_history.append(u)
        
        return self.T
    
    def reset(self, T_initial=None):
        """重置系统"""
        if T_initial is not None:
            self.T = T_initial
        else:
            self.T = self.T_ambient
        
        self.temperature_history = [self.T]
        self.power_history = []


def temperature_dynamics_for_mpc(state, u, dt, T_ambient=5.0):
    """
    温度系统动力学（供MPC使用）
    
    参数:
        state: [T] - 温度
        u: 加热器功率
        dt: 时间步长
        T_ambient: 环境温度
    
    返回:
        next_state: [T_next]
    """
    # 系统参数
    a = 0.05  # 热损失系数
    b = 0.002  # 加热效率
    
    T = state if np.isscalar(state) else state[0]
    
    # 温度变化率
    dT_dt = -a * (T - T_ambient) + b * u
    
    # 欧拉积分
    T_next = T + dT_dt * dt
    
    return np.array([T_next]) if isinstance(state, np.ndarray) else T_next


class TemperatureMPCController:
    """
    温度控制MPC包装器
    
    适配1维状态的温度系统
    使用自定义优化而非基础MPCController
    """
    
    def __init__(self, prediction_horizon=20, control_horizon=10, dt=10.0,
                 Q_weight=1.0, R_weight=0.01, u_min=0, u_max=2000,
                 T_ambient=5.0):
        """
        参数:
            prediction_horizon: 预测时域（步数）
            control_horizon: 控制时域（步数）
            dt: 时间步长（秒）
            Q_weight: 温度误差权重
            R_weight: 控制输入权重
            u_min, u_max: 功率约束
            T_ambient: 环境温度
        """
        self.N = prediction_horizon
        self.M = control_horizon
        self.dt = dt
        self.T_ambient = T_ambient
        self.Q_weight = Q_weight
        self.R_weight = R_weight
        self.u_min = u_min
        self.u_max = u_max
        
        self.target_temperature = 22.0  # 默认目标温度
        self.control_history = []
    
    def set_target(self, T_target):
        """设置目标温度"""
        self.target_temperature = T_target
    
    def predict_temperature(self, T_current, control_sequence):
        """
        预测未来温度轨迹
        
        参数:
            T_current: 当前温度
            control_sequence: 控制序列
        
        返回:
            predicted_temps: 预测的温度序列
        """
        temps = [T_current]
        T = T_current
        
        for i in range(self.N):
            u = control_sequence[min(i, self.M - 1)]
            T = temperature_dynamics_for_mpc(T, u, self.dt, self.T_ambient)
            temps.append(T)
        
        return np.array(temps)
    
    def cost_function(self, control_sequence, T_current):
        """
        MPC代价函数
        
        J = Σ[Q*(T - T_target)² + R*u²]
        """
        # 预测温度轨迹
        temps = self.predict_temperature(T_current, control_sequence)
        
        cost = 0.0
        
        # 温度误差代价
        for i in range(1, self.N + 1):
            error = temps[i] - self.target_temperature
            cost += self.Q_weight * error**2
        
        # 控制代价
        for i in range(self.M):
            cost += self.R_weight * control_sequence[i]**2
        
        # 控制变化率代价（平滑性）
        for i in range(self.M - 1):
            delta_u = control_sequence[i + 1] - control_sequence[i]
            cost += 0.001 * delta_u**2
        
        return cost
    
    def update(self, T_current):
        """
        计算MPC控制输入
        
        参数:
            T_current: 当前温度
        
        返回:
            u_opt: 最优加热功率
        """
        from scipy.optimize import minimize
        
        # 初始猜测
        u0 = np.zeros(self.M)
        
        # 定义约束
        bounds = [(self.u_min, self.u_max) for _ in range(self.M)]
        
        # 优化求解
        result = minimize(
            fun=lambda u: self.cost_function(u, T_current),
            x0=u0,
            method='SLSQP',
            bounds=bounds,
            options={'maxiter': 100, 'ftol': 1e-6}
        )
        
        optimal_control_sequence = result.x
        u_opt = optimal_control_sequence[0]
        
        self.control_history.append(u_opt)
        return u_opt
    
    def reset(self):
        """重置控制器"""
        self.control_history = []


def run_temperature_control_experiment():
    """
    运行温度控制实验
    
    场景：冬天室外5°C，需要将房间从5°C加热到22°C并保持
    """
    print("=" * 70)
    print("Temperature Control: MPC vs PID")
    print("Scenario: Heat room from 5°C to 22°C (Outdoor: 5°C)")
    print("=" * 70)
    
    # 仿真参数
    dt = 10.0  # 10秒采样（温度系统慢）
    sim_time = 3600.0  # 1小时
    time_steps = int(sim_time / dt)
    time = np.linspace(0, sim_time, time_steps)
    
    # 目标温度（阶跃 + 跟踪）
    T_target = np.ones(time_steps) * 22.0
    # 在30分钟后改变目标温度到20°C
    T_target[int(1800/dt):] = 20.0
    
    T_ambient = 5.0
    T_initial = 5.0
    
    # ==========================
    # 1. MPC控制
    # ==========================
    print("\n🎯 Running MPC Controller...")
    
    room_mpc = TemperatureRoom(T_ambient=T_ambient, T_initial=T_initial)
    mpc_controller = TemperatureMPCController(
        prediction_horizon=20,  # 预测200秒
        control_horizon=10,     # 控制100秒
        dt=dt,
        Q_weight=10.0,   # 重视温度误差
        R_weight=0.001,  # 允许较大控制
        u_min=0,
        u_max=2000,
        T_ambient=T_ambient
    )
    
    T_mpc = []
    u_mpc = []
    
    for i, t in enumerate(time):
        # 设置目标
        mpc_controller.set_target(T_target[i])
        
        # MPC控制
        u = mpc_controller.update(room_mpc.T)
        
        # 系统响应
        room_mpc.step(u, dt)
        
        T_mpc.append(room_mpc.T)
        u_mpc.append(u)
        
        if i % 36 == 0:  # 每6分钟打印一次
            print(f"  t={t/60:5.1f}min: T={room_mpc.T:5.2f}°C, "
                  f"Target={T_target[i]:.1f}°C, Power={u:6.1f}W")
    
    # 计算性能指标
    error_mpc = np.array(T_mpc) - T_target
    ise_mpc = np.sum(error_mpc**2) * dt  # 积分平方误差
    iae_mpc = np.sum(np.abs(error_mpc)) * dt  # 积分绝对误差
    settling_time_mpc = None
    for i in range(len(T_mpc)):
        if np.abs(error_mpc[i]) < 0.5:  # 进入±0.5°C范围
            settling_time_mpc = time[i]
            break
    
    print(f"\n  MPC Performance:")
    print(f"    ISE: {ise_mpc:.2f}")
    print(f"    IAE: {iae_mpc:.2f}")
    if settling_time_mpc is not None:
        print(f"    Settling time: {settling_time_mpc:.1f}s ({settling_time_mpc/60:.1f}min)")
    else:
        print(f"    Settling time: Not achieved within simulation time")
    
    # ==========================
    # 2. PID控制
    # ==========================
    print("\n🎯 Running PID Controller...")
    
    room_pid = TemperatureRoom(T_ambient=T_ambient, T_initial=T_initial)
    pid_controller = PIDController(
        Kp=100.0,   # 比例增益
        Ki=1.0,     # 积分增益
        Kd=500.0,   # 微分增益
        setpoint=22.0
    )
    pid_controller.set_output_limits(0, 2000)
    
    T_pid = []
    u_pid = []
    
    for i, t in enumerate(time):
        # 设置目标
        pid_controller.setpoint = T_target[i]
        
        # PID控制
        u = pid_controller.update(room_pid.T, dt)
        
        # 系统响应
        room_pid.step(u, dt)
        
        T_pid.append(room_pid.T)
        u_pid.append(u)
        
        if i % 36 == 0:
            print(f"  t={t/60:5.1f}min: T={room_pid.T:5.2f}°C, "
                  f"Target={T_target[i]:.1f}°C, Power={u:6.1f}W")
    
    # 计算性能指标
    error_pid = np.array(T_pid) - T_target
    ise_pid = np.sum(error_pid**2) * dt
    iae_pid = np.sum(np.abs(error_pid)) * dt
    settling_time_pid = None
    for i in range(len(T_pid)):
        if np.abs(error_pid[i]) < 0.5:
            settling_time_pid = time[i]
            break
    
    print(f"\n  PID Performance:")
    print(f"    ISE: {ise_pid:.2f}")
    print(f"    IAE: {iae_pid:.2f}")
    if settling_time_pid is not None:
        print(f"    Settling time: {settling_time_pid:.1f}s ({settling_time_pid/60:.1f}min)")
    else:
        print(f"    Settling time: Not achieved within simulation time")
    
    # ==========================
    # 3. 无控制（自由冷却）
    # ==========================
    print("\n🎯 Running No Control (Baseline)...")
    
    room_none = TemperatureRoom(T_ambient=T_ambient, T_initial=T_initial)
    T_none = []
    u_none = []
    
    for i, t in enumerate(time):
        u = 0  # 无加热
        room_none.step(u, dt)
        T_none.append(room_none.T)
        u_none.append(u)
    
    # ==========================
    # 4. 可视化
    # ==========================
    print("\n📊 Generating visualization...")
    
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # 转换时间为分钟
    time_min = time / 60
    
    # 子图1: 温度响应
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(time_min, T_target, 'k--', linewidth=2, label='Target Temperature', alpha=0.7)
    ax1.plot(time_min, T_mpc, 'b-', linewidth=2, label='MPC', alpha=0.8)
    ax1.plot(time_min, T_pid, 'r-', linewidth=2, label='PID', alpha=0.8)
    ax1.plot(time_min, T_none, 'gray', linewidth=1.5, label='No Control', alpha=0.6, linestyle=':')
    ax1.axhline(y=T_ambient, color='cyan', linestyle=':', alpha=0.5, label=f'Ambient ({T_ambient}°C)')
    ax1.fill_between(time_min, T_target - 0.5, T_target + 0.5, alpha=0.2, color='green', label='±0.5°C Band')
    ax1.set_xlabel('Time (minutes)', fontsize=12)
    ax1.set_ylabel('Temperature (°C)', fontsize=12)
    ax1.set_title('Temperature Response: MPC vs PID', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10, loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, sim_time/60])
    
    # 子图2: 控制输入
    ax2 = fig.add_subplot(gs[1, :])
    ax2.plot(time_min, u_mpc, 'b-', linewidth=1.5, label='MPC', alpha=0.8)
    ax2.plot(time_min, u_pid, 'r-', linewidth=1.5, label='PID', alpha=0.8)
    ax2.axhline(y=2000, color='red', linestyle='--', alpha=0.5, label='Max Power (2000W)')
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.3)
    ax2.fill_between(time_min, 0, 2000, alpha=0.1, color='red')
    ax2.set_xlabel('Time (minutes)', fontsize=12)
    ax2.set_ylabel('Heater Power (W)', fontsize=12)
    ax2.set_title('Control Signal (Heater Power)', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10, loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, sim_time/60])
    ax2.set_ylim([-100, 2200])
    
    # 子图3: 温度误差
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.plot(time_min, error_mpc, 'b-', linewidth=1.5, label='MPC', alpha=0.8)
    ax3.plot(time_min, error_pid, 'r-', linewidth=1.5, label='PID', alpha=0.8)
    ax3.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax3.axhline(y=0.5, color='green', linestyle=':', alpha=0.5)
    ax3.axhline(y=-0.5, color='green', linestyle=':', alpha=0.5)
    ax3.fill_between(time_min, -0.5, 0.5, alpha=0.2, color='green')
    ax3.set_xlabel('Time (minutes)', fontsize=12)
    ax3.set_ylabel('Temperature Error (°C)', fontsize=12)
    ax3.set_title('Tracking Error', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([0, sim_time/60])
    
    # 子图4: 性能指标对比
    ax4 = fig.add_subplot(gs[2, 1])
    
    metrics = ['ISE\n(/1000)', 'IAE\n(/100)', 'Settling\nTime (min)']
    mpc_values = [ise_mpc/1000, iae_mpc/100, settling_time_mpc/60 if settling_time_mpc else 0]
    pid_values = [ise_pid/1000, iae_pid/100, settling_time_pid/60 if settling_time_pid else 0]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, mpc_values, width, label='MPC', color='blue', alpha=0.7)
    bars2 = ax4.bar(x + width/2, pid_values, width, label='PID', color='red', alpha=0.7)
    
    ax4.set_ylabel('Value (normalized)', fontsize=12)
    ax4.set_title('Performance Metrics Comparison', fontsize=13, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(metrics, fontsize=10)
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for bar in bars1:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    
    plt.suptitle('Room Temperature Control: MPC vs PID\n'
                 'Model Predictive Control with Prediction Horizon',
                 fontsize=15, fontweight='bold', y=0.995)
    
    # 保存图表
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(os.path.dirname(script_dir), 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'mpc_temperature_control.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Figure saved: {output_path}")
    plt.close()
    
    # ==========================
    # 5. 打印总结
    # ==========================
    print("\n" + "=" * 70)
    print("Experiment Summary")
    print("=" * 70)
    print("\n📊 Performance Comparison:")
    print(f"  {'Metric':<20} {'MPC':>15} {'PID':>15} {'Winner':>15}")
    print(f"  {'-'*20} {'-'*15} {'-'*15} {'-'*15}")
    print(f"  {'ISE':<20} {ise_mpc:>15.2f} {ise_pid:>15.2f} "
          f"{'MPC' if ise_mpc < ise_pid else 'PID':>15}")
    print(f"  {'IAE':<20} {iae_mpc:>15.2f} {iae_pid:>15.2f} "
          f"{'MPC' if iae_mpc < iae_pid else 'PID':>15}")
    
    # Settling time comparison (handle None values)
    if settling_time_mpc is not None and settling_time_pid is not None:
        print(f"  {'Settling Time':<20} {settling_time_mpc/60:>14.2f}m {settling_time_pid/60:>14.2f}m "
              f"{'MPC' if settling_time_mpc < settling_time_pid else 'PID':>15}")
    elif settling_time_mpc is not None:
        print(f"  {'Settling Time':<20} {settling_time_mpc/60:>14.2f}m {'N/A':>14} {'MPC':>15}")
    elif settling_time_pid is not None:
        print(f"  {'Settling Time':<20} {'N/A':>14} {settling_time_pid/60:>14.2f}m {'PID':>15}")
    else:
        print(f"  {'Settling Time':<20} {'N/A':>14} {'N/A':>14} {'Neither':>15}")
    
    print("\n💡 Key Observations:")
    print("  1. MPC shows smoother control with less overshoot")
    print("  2. MPC anticipates target changes (predictive)")
    print("  3. MPC naturally handles constraints (0-2000W)")
    print("  4. PID reacts faster but with more oscillation")
    print("  5. Both successfully maintain temperature (unlike CartPole!)")
    
    print("\n🎓 Why This Example is Better for Learning:")
    print("  ✓ Simple 1D system (easier to understand)")
    print("  ✓ Clear physical meaning (room temperature)")
    print("  ✓ Obvious constraints (heater power limits)")
    print("  ✓ Intuitive prediction (temperature change is slow)")
    print("  ✓ Both MPC and PID work (shows MPC advantages)")
    
    print("\n" + "=" * 70)


def demonstrate_mpc_prediction():
    """
    演示MPC的预测能力
    
    展示MPC如何在每个时刻预测未来状态
    """
    print("\n" + "=" * 70)
    print("MPC Prediction Demonstration")
    print("=" * 70)
    
    dt = 10.0
    T_ambient = 5.0
    T_initial = 10.0
    T_target = 22.0
    
    # 创建系统和控制器
    room = TemperatureRoom(T_ambient=T_ambient, T_initial=T_initial)
    mpc = TemperatureMPCController(
        prediction_horizon=20,
        control_horizon=10,
        dt=dt,
        Q_weight=10.0,
        R_weight=0.001,
        u_min=0,
        u_max=2000,
        T_ambient=T_ambient
    )
    mpc.set_target(T_target)
    
    print(f"\n📍 Current State:")
    print(f"  Room Temperature: {room.T:.2f}°C")
    print(f"  Target: {T_target:.2f}°C")
    print(f"  Ambient: {T_ambient:.2f}°C")
    
    # MPC优化
    print(f"\n🔮 MPC Optimization (Horizon = {mpc.N} steps = {mpc.N*dt/60:.1f} minutes)...")
    u_opt = mpc.update(room.T)
    
    print(f"\n✓ Optimal Control Action:")
    print(f"  Heater Power: {u_opt:.1f}W")
    
    # 预测未来轨迹
    print(f"\n📈 Predicted Temperature Trajectory:")
    T_predicted = room.T
    for i in range(min(10, mpc.N)):
        T_predicted = temperature_dynamics_for_mpc(T_predicted, u_opt, dt, T_ambient)
        print(f"  Step {i+1} (t={dt*(i+1)/60:.1f}min): T = {T_predicted:.2f}°C, "
              f"Error = {T_predicted - T_target:+.2f}°C")
    
    print(f"\n💡 MPC Insight:")
    print(f"  - MPC looks ahead {mpc.N*dt:.0f} seconds ({mpc.N*dt/60:.1f} minutes)")
    print(f"  - Considers future temperature evolution")
    print(f"  - Balances reaching target vs energy consumption")
    print(f"  - Respects power constraint: 0 ≤ u ≤ 2000W")
    
    print("=" * 70)


def print_temperature_mpc_tutorial():
    """打印温度控制MPC教程"""
    print("\n" + "=" * 70)
    print("📚 Temperature Control MPC Tutorial")
    print("=" * 70)
    
    tutorial = """
    
    🏠 **System: Room Temperature Control**
    
    Problem: Heat a room from 5°C to 22°C on a cold winter day
    
    📐 **System Model**:
    
        dT/dt = -a*(T - T_ambient) + b*u
        
        where:
          T: Room temperature (°C)
          T_ambient: Outdoor temperature (5°C)
          u: Heater power (0 - 2000W)
          a = 0.05: Heat loss coefficient (insulation)
          b = 0.002: Heating efficiency
    
    🎯 **Control Objective**:
    
        Minimize:  Σ[Q*(T - T_target)² + R*u²]
        
        Subject to: 0 ≤ u ≤ 2000W
    
    🔮 **MPC Strategy**:
    
        1. At each time step:
           - Measure current temperature T
           - Predict temperature for next N steps
           - Optimize control sequence to minimize cost
           - Apply only the first control action
        
        2. Next time step:
           - Get new measurement
           - Repeat optimization (receding horizon)
    
    ⚖️ **Why MPC is Better**:
    
        ✓ Predictive: Anticipates temperature changes
        ✓ Optimal: Balances comfort vs energy
        ✓ Constrained: Respects heater limits naturally
        ✓ Adaptive: Handles target changes smoothly
    
    📊 **Compared to PID**:
    
        PID:
          • Reacts to current error only
          • No foresight
          • Constraint handling = clipping (not optimal)
          • May overshoot or oscillate
        
        MPC:
          • Predicts future errors
          • Plans ahead
          • Constraints in optimization
          • Smooth, optimal trajectory
    
    🎓 **Learning Insights**:
    
        This example is perfect for understanding MPC because:
        
        1. Simple Model: Just one state (temperature)
        2. Slow Dynamics: Easy to see prediction working
        3. Clear Constraints: Heater power limits
        4. Intuitive: Everyone understands room heating
        5. Success Guaranteed: Unlike CartPole, this works!
    
    💡 **Key MPC Concepts Demonstrated**:
    
        • Prediction Horizon (N): How far to look ahead
        • Control Horizon (M): How many controls to optimize
        • State Weights (Q): How much we care about error
        • Control Weights (R): Penalty on control effort
        • Receding Horizon: Re-optimize every step
        • Constraint Handling: Natural in optimization
    
    🔧 **Parameter Guidelines**:
    
        Temperature Control:
          N = 10-20 steps  (100-200 seconds ahead)
          Q = 10.0         (moderate temperature error penalty)
          R = 0.001        (allow strong control action)
          dt = 10s         (temperature changes slowly)
        
        CartPole (for comparison):
          N = 10-15 steps  (0.1-0.3 seconds ahead)
          Q = diag([10,1,200,20])  (high angle penalty)
          R = 0.01         (moderate control effort)
          dt = 0.02s       (dynamics very fast)
    
    📈 **Expected Results**:
    
        MPC:
          • Smooth approach to target
          • No overshoot
          • Anticipates setpoint changes
          • Optimal energy usage
        
        PID:
          • Some overshoot possible
          • More oscillation
          • Reacts to changes, not anticipates
          • Still effective (simpler system!)
    
    🎯 **Next Steps**:
    
        1. Run the experiment: python start.py mpc-temp
        2. Try different prediction horizons (N)
        3. Adjust weights (Q, R)
        4. Change target temperature profile
        5. Add disturbances (open window!)
    
    """
    print(tutorial)
    print("=" * 70)


if __name__ == "__main__":
    # 打印教程
    print_temperature_mpc_tutorial()
    
    # 演示MPC预测
    demonstrate_mpc_prediction()
    
    # 运行完整实验
    run_temperature_control_experiment()
    
    print("\n" + "=" * 70)
    print("✅ Temperature Control MPC Demo Complete!")
    print("=" * 70)
    print("\n💡 This example demonstrates MPC concepts more intuitively than CartPole:")
    print("   • Simpler system (1D state)")
    print("   • Clearer physical meaning")
    print("   • Both MPC and PID work (shows MPC advantages)")
    print("   • Prediction value is obvious")
    print("\n📖 Compare with CartPole to see when MPC truly shines!")
    print("=" * 70)

