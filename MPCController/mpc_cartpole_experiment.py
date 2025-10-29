"""
MPC控制CartPole实验
对比PID、MPC和强化学习三种方法
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

import sys
sys.path.insert(0, '..')

try:
    from .mpc_controller import MPCController, LinearMPCController, AdaptiveMPCController, cartpole_dynamics
except ImportError:
    from mpc_controller import MPCController, LinearMPCController, AdaptiveMPCController, cartpole_dynamics

# Import from PIDController package
try:
    from PIDController.pid_controller import PIDController
    from PIDController.cartpole_pid import CartPole, CartPolePIDController
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'PIDController'))
    from pid_controller import PIDController
    from cartpole_pid import CartPole, CartPolePIDController


def run_mpc_cartpole_experiment():
    """运行MPC CartPole控制实验"""
    print("=" * 70)
    print("CartPole Control Comparison: PID vs MPC vs RL")
    print("=" * 70)
    
    # 仿真参数
    dt = 0.02  # 20ms
    sim_time = 10.0
    time_steps = int(sim_time / dt)
    time = np.linspace(0, sim_time, time_steps)
    
    # 创建图表
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(4, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    # 测试场景
    scenarios = [
        {
            'name': 'MPC (Nonlinear, N=10)',
            'controller_type': 'mpc',
            'initial_theta': 0.1,
            'color': 'blue',
            'N': 10
        },
        {
            'name': 'MPC (Linear, N=15)',
            'controller_type': 'linear_mpc',
            'initial_theta': 0.1,
            'color': 'green',
            'N': 15
        },
        {
            'name': 'Adaptive MPC',
            'controller_type': 'adaptive_mpc',
            'initial_theta': 0.15,
            'color': 'purple',
            'N': 10
        },
        {
            'name': 'PID (Cascade)',
            'controller_type': 'pid',
            'initial_theta': 0.1,
            'color': 'red',
            'N': 0
        }
    ]
    
    # 子图
    ax1 = fig.add_subplot(gs[0, :])   # 角度
    ax2 = fig.add_subplot(gs[1, :])   # 位置
    ax3 = fig.add_subplot(gs[2, 0])   # 控制力
    ax4 = fig.add_subplot(gs[2, 1])   # 代价
    ax5 = fig.add_subplot(gs[2, 2])   # 相图
    ax6 = fig.add_subplot(gs[3, :])   # 性能对比
    
    results = []
    
    for scenario in scenarios:
        print(f"\nRunning: {scenario['name']}")
        print(f"  Initial angle: {scenario['initial_theta']:.3f} rad ({np.degrees(scenario['initial_theta']):.1f}°)")
        
        # 创建系统
        cartpole = CartPole()
        cartpole.reset(theta=scenario['initial_theta'])
        
        # 创建控制器
        if scenario['controller_type'] == 'mpc':
            controller = MPCController(
                prediction_horizon=scenario['N'],
                control_horizon=5,
                dt=dt,
                Q=np.diag([10, 1, 200, 20]),
                R=np.array([[0.01]]),
                u_min=-50,
                u_max=50
            )
            use_mpc = True
        elif scenario['controller_type'] == 'linear_mpc':
            controller = LinearMPCController(
                prediction_horizon=scenario['N'],
                control_horizon=8,
                dt=dt,
                Q=np.diag([10, 1, 200, 20]),
                R=np.array([[0.01]]),
                u_min=-50,
                u_max=50
            )
            use_mpc = True
        elif scenario['controller_type'] == 'adaptive_mpc':
            controller = AdaptiveMPCController(
                base_N=scenario['N'],
                base_M=5,
                dt=dt
            )
            use_mpc = True
        else:  # PID
            controller = CartPolePIDController()
            use_mpc = False
        
        # 运行仿真
        angles = []
        positions = []
        forces = []
        costs = []
        failed = False
        fail_time = None
        
        for i, t in enumerate(time):
            # 当前状态
            current_state = np.array([
                cartpole.x,
                cartpole.x_dot,
                cartpole.theta,
                cartpole.theta_dot
            ])
            
            # 计算控制
            if use_mpc:
                if scenario['controller_type'] == 'linear_mpc':
                    force = controller.update(current_state, [1.0, 0.1, 0.5, 9.8])
                else:
                    force = controller.update(current_state, cartpole_dynamics)
                
                if hasattr(controller, 'cost_history') and len(controller.cost_history) > 0:
                    costs.append(controller.cost_history[-1])
                else:
                    costs.append(0)
            else:  # PID
                force = controller.control_cascade(cartpole.x, cartpole.theta, dt)
                costs.append((cartpole.theta**2 + cartpole.x**2))  # 简单代价
            
            # 检查失败
            if cartpole.is_failed():
                failed = True
                fail_time = t
                print(f"  ❌ Failed at {t:.2f}s")
                break
            
            # 更新系统
            cartpole.step(force, dt)
            
            # 记录
            angles.append(np.degrees(cartpole.theta))
            positions.append(cartpole.x)
            forces.append(force)
        
        if not failed:
            print(f"  ✓ Success! Maintained balance for {sim_time}s")
            final_angle_error = np.mean(np.abs(angles[-50:]))
            final_pos_error = np.mean(np.abs(positions[-50:]))
            print(f"  Final angle error: {final_angle_error:.3f}°")
            print(f"  Final position error: {final_pos_error:.3f}m")
        
        # 保存结果
        result_time = time[:len(angles)]
        results.append({
            'name': scenario['name'],
            'angles': angles,
            'positions': positions,
            'forces': forces,
            'costs': costs,
            'time': result_time,
            'failed': failed,
            'fail_time': fail_time,
            'color': scenario['color']
        })
        
        # 绘图
        ax1.plot(result_time, angles, label=scenario['name'], 
                linewidth=2, color=scenario['color'], alpha=0.8)
        ax2.plot(result_time, positions, linewidth=2, 
                color=scenario['color'], alpha=0.8)
        ax3.plot(result_time, forces, linewidth=1.5, 
                color=scenario['color'], alpha=0.8)
        
        if len(costs) > 0:
            cost_time = result_time[:len(costs)]
            ax4.plot(cost_time, costs[:len(cost_time)], linewidth=1.5, 
                    color=scenario['color'], alpha=0.8)
        
        # 相图
        ax5.plot(angles, [cartpole.history['theta_dot'][i] * 180/np.pi 
                         for i in range(len(angles))],
                linewidth=1.5, color=scenario['color'], alpha=0.6)
    
    # 设置图表
    ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax1.axhline(y=12, color='r', linestyle=':', alpha=0.3, linewidth=1)
    ax1.axhline(y=-12, color='r', linestyle=':', alpha=0.3, linewidth=1)
    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Pole Angle (degrees)', fontsize=12)
    ax1.set_title('Pole Angle Response (Target: 0°, Limit: ±12°)', 
                 fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10, loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([-15, 15])
    
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax2.axhline(y=2.4, color='r', linestyle=':', alpha=0.3, label='Boundary')
    ax2.axhline(y=-2.4, color='r', linestyle=':', alpha=0.3)
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Cart Position (m)', fontsize=12)
    ax2.set_title('Cart Position Response', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([-3, 3])
    
    ax3.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax3.set_xlabel('Time (s)', fontsize=12)
    ax3.set_ylabel('Control Force (N)', fontsize=12)
    ax3.set_title('Control Signal', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    ax4.set_xlabel('Time (s)', fontsize=12)
    ax4.set_ylabel('Cost Function Value', fontsize=12)
    ax4.set_title('Optimization Cost Over Time', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.set_yscale('log')
    
    ax5.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax5.axvline(x=0, color='k', linestyle='--', alpha=0.3)
    ax5.set_xlabel('Angle (degrees)', fontsize=12)
    ax5.set_ylabel('Angular Velocity (deg/s)', fontsize=12)
    ax5.set_title('Phase Portrait', fontsize=13, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 性能对比
    categories = [r['name'].split('(')[0].strip() for r in results]
    success = [not r['failed'] for r in results]
    colors_bar = [r['color'] for r in results]
    
    bars = ax6.bar(categories, [1 if s else 0 for s in success],
                   color=colors_bar, alpha=0.7, edgecolor='black', width=0.6)
    ax6.set_ylabel('Success/Failure', fontsize=12)
    ax6.set_title('Control Strategy Performance Comparison', 
                 fontsize=13, fontweight='bold')
    ax6.set_ylim([0, 1.2])
    ax6.set_yticks([0, 1])
    ax6.set_yticklabels(['Failed', 'Success'])
    ax6.grid(True, alpha=0.3, axis='y')
    
    # 标注
    for i, (bar, result) in enumerate(zip(bars, results)):
        if result['failed']:
            label = f"Failed\n{result['fail_time']:.2f}s"
            ax6.text(i, 0.05, label, ha='center', va='bottom', 
                    fontsize=9, fontweight='bold')
        else:
            label = "✓ Success"
            ax6.text(i, 1.05, label, ha='center', va='bottom', 
                    fontsize=11, fontweight='bold', color='green')
    
    plt.suptitle('CartPole Control: PID vs MPC Comparison\nModel Predictive Control with Optimization',
                 fontsize=15, fontweight='bold', y=0.995)
    
    output_path = os.path.join('..', 'output', 'mpc_cartpole_comparison.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nFigure saved: {output_path}")
    plt.close()
    
    print("\n" + "=" * 70)
    print("Experiment Complete!")
    print("=" * 70)


def print_mpc_comparison():
    """打印MPC vs PID vs RL对比"""
    print("\n" + "=" * 70)
    print("Control Methods Comparison: PID vs MPC vs RL")
    print("=" * 70)
    
    comparison = """
    
    📊 Three Control Approaches for CartPole
    
    ┌──────────────┬────────────────┬────────────────┬────────────────┐
    │   Feature    │      PID       │      MPC       │       RL       │
    ├──────────────┼────────────────┼────────────────┼────────────────┤
    │ Model Need   │ Not required   │ Required       │ Not required   │
    │              │ (Simple rules) │ (Dynamics)     │ (Learn it)     │
    ├──────────────┼────────────────┼────────────────┼────────────────┤
    │ Computation  │ Very Low       │ Medium-High    │ Low (inference)│
    │              │ O(1)           │ O(N²)          │ O(1)           │
    ├──────────────┼────────────────┼────────────────┼────────────────┤
    │ Constraints  │ Hard to handle │ Native support │ Requires design│
    ├──────────────┼────────────────┼────────────────┼────────────────┤
    │ Optimality   │ No guarantee   │ Locally optimal│ Can be optimal │
    ├──────────────┼────────────────┼────────────────┼────────────────┤
    │ Tuning       │ 3 parameters   │ Q, R matrices  │ Hyperparameters│
    │              │ (Kp, Ki, Kd)   │ + horizons     │ + architecture │
    ├──────────────┼────────────────┼────────────────┼────────────────┤
    │ Horizon      │ Instantaneous  │ N-step ahead   │ Episode-long   │
    ├──────────────┼────────────────┼────────────────┼────────────────┤
    │ Nonlinearity │ Limited        │ Good           │ Excellent      │
    ├──────────────┼────────────────┼────────────────┼────────────────┤
    │ Training     │ None           │ None           │ Extensive      │
    ├──────────────┼────────────────┼────────────────┼────────────────┤
    │ Online Adapt │ Difficult      │ Possible       │ Can retrain    │
    ├──────────────┼────────────────┼────────────────┼────────────────┤
    │ CartPole     │ ⭐⭐          │ ⭐⭐⭐⭐       │ ⭐⭐⭐⭐⭐     │
    │ Performance  │ Poor           │ Good           │ Excellent      │
    └──────────────┴────────────────┴────────────────┴────────────────┘
    
    🎯 MPC Advantages:
      1. ✅ Predictive - looks ahead N steps
      2. ✅ Handles constraints naturally (u_min, u_max)
      3. ✅ Optimal within prediction horizon
      4. ✅ Can handle MIMO (Multi-Input Multi-Output)
      5. ✅ Systematic tuning (Q, R weights)
      6. ✅ Better than PID for complex systems
    
    ⚠️ MPC Limitations:
      1. ❌ Requires accurate model
      2. ❌ Computationally expensive
      3. ❌ Real-time constraints (optimization time)
      4. ❌ Model mismatch can degrade performance
      5. ❌ Tuning Q, R, N can be complex
    
    💡 When to Use Each Method:
    
    Use PID when:
      • Simple, well-understood system
      • Fast response needed (< 1ms)
      • No model available
      • Industrial standard acceptable
      
    Use MPC when:
      • Model available
      • Constraints are critical
      • Multi-variable system
      • Can afford 10-100ms computation
      • Want optimal performance
      
    Use RL when:
      • Model unknown or complex
      • Can collect lots of data
      • Extreme performance needed
      • System changes over time
      • Non-standard cost function
    
    🔬 CartPole Results (Expected):
      • PID: Fails in < 0.2s (unstable equilibrium)
      • MPC: Success! (with good model & tuning)
      • RL: Success! (after training)
    
    📈 Key Insight:
      MPC bridges classical control (PID) and modern AI (RL)
      - More sophisticated than PID
      - More interpretable than RL
      - Best for known models with constraints
    
    """
    print(comparison)


if __name__ == "__main__":
    run_mpc_cartpole_experiment()
    print_mpc_comparison()

