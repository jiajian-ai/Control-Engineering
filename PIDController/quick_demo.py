"""
快速演示脚本 - 简单的PID控制示例
"""
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import numpy as np
import os

# 导入本地模块
try:
    from .pid_controller import PIDController
    from .simulated_system import FirstOrderSystem
except ImportError:
    from pid_controller import PIDController
    from simulated_system import FirstOrderSystem

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def quick_demo():
    """快速演示PID控制效果"""
    print("=" * 60)
    print("PID控制器快速演示")
    print("=" * 60)
    
    # 仿真参数
    simulation_time = 15.0
    dt = 0.01
    time_steps = int(simulation_time / dt)
    time = np.linspace(0, simulation_time, time_steps)
    
    # 创建系统
    system = FirstOrderSystem(tau=1.0, initial_value=0.0)
    
    # 创建PID控制器 (使用合理的参数避免剧烈振荡)
    pid = PIDController(Kp=2.0, Ki=0.5, Kd=0.1, setpoint=1.0)
    
    # 存储数据
    outputs = []
    controls = []
    setpoints = []
    
    print("\n运行仿真...")
    for i, t in enumerate(time):
        # 在t=5s时改变目标值
        if t >= 5.0 and t < 5.01:
            pid.set_setpoint(1.5)
            print(f"  时间 {t:.1f}s: 目标值变更为 1.5")
        
        # 在t=10s时改变目标值
        if t >= 10.0 and t < 10.01:
            pid.set_setpoint(0.5)
            print(f"  时间 {t:.1f}s: 目标值变更为 0.5")
        
        # 获取当前系统输出
        current_output = system.state
        
        # PID控制
        control = pid.update(current_output, dt)
        
        # 更新系统
        new_output = system.update(control, dt)
        
        outputs.append(new_output)
        controls.append(control)
        setpoints.append(pid.setpoint)
    
    # 可视化结果
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # 系统响应
    ax1.plot(time, outputs, 'b-', linewidth=2, label='系统输出')
    ax1.plot(time, setpoints, 'r--', linewidth=2, label='目标值')
    ax1.fill_between(time, outputs, setpoints, alpha=0.2)
    ax1.set_xlabel('时间 (s)', fontsize=12)
    ax1.set_ylabel('输出值', fontsize=12)
    ax1.set_title('PID控制系统响应', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.axvline(x=5.0, color='gray', linestyle=':', alpha=0.5)
    ax1.axvline(x=10.0, color='gray', linestyle=':', alpha=0.5)
    
    # 控制信号
    ax2.plot(time, controls, 'g-', linewidth=2)
    ax2.set_xlabel('时间 (s)', fontsize=12)
    ax2.set_ylabel('控制信号', fontsize=12)
    ax2.set_title('PID控制信号', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axvline(x=5.0, color='gray', linestyle=':', alpha=0.5)
    ax2.axvline(x=10.0, color='gray', linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    output_path = os.path.join('..', 'output', 'quick_demo.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: {output_path}")
    plt.close()
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)
    print(f"\nPID参数: Kp={pid.Kp}, Ki={pid.Ki}, Kd={pid.Kd}")
    print(f"最终输出: {outputs[-1]:.4f}")
    print(f"最终目标: {setpoints[-1]:.4f}")
    print(f"最终误差: {abs(outputs[-1] - setpoints[-1]):.4f}")


if __name__ == "__main__":
    quick_demo()

