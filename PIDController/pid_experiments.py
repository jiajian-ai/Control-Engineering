"""
PID控制器实验
详细展示Kp, Ki, Kd三个参数对系统控制效果的影响
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

# 导入本地模块
try:
    from .pid_controller import PIDController
    from .simulated_system import FirstOrderSystem, SecondOrderSystem, SystemWithNoise
except ImportError:
    from pid_controller import PIDController
    from simulated_system import FirstOrderSystem, SecondOrderSystem, SystemWithNoise

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PIDExperiments:
    """PID控制实验类"""
    
    def __init__(self):
        self.simulation_time = 20.0  # 仿真时间(秒)
        self.dt = 0.01  # 时间步长
        self.time_steps = int(self.simulation_time / self.dt)
        self.time = np.linspace(0, self.simulation_time, self.time_steps)
    
    def run_single_experiment(self, pid_controller, system, setpoint=1.0, 
                             disturbance_time=None, disturbance_value=0.0):
        """
        运行单个实验
        
        参数:
            pid_controller: PID控制器对象
            system: 被控系统对象
            setpoint: 目标值
            disturbance_time: 扰动发生时间
            disturbance_value: 扰动大小
        
        返回:
            time, output, control_signal
        """
        # 重置控制器和系统
        pid_controller.reset()
        pid_controller.set_setpoint(setpoint)
        system.reset()
        
        outputs = []
        control_signals = []
        
        for i, t in enumerate(self.time):
            # 获取当前系统输出(从系统对象获取)
            if hasattr(system, 'state'):
                current_output = system.state
            elif hasattr(system, 'position'):
                current_output = system.position
            elif hasattr(system, 'base_system'):
                # 处理SystemWithNoise包装器
                if hasattr(system.base_system, 'state'):
                    current_output = system.base_system.state
                elif hasattr(system.base_system, 'position'):
                    current_output = system.base_system.position
            else:
                current_output = 0.0 if i == 0 else outputs[-1]
            
            # 计算控制信号
            control_signal = pid_controller.update(current_output, self.dt)
            
            # 添加扰动
            if disturbance_time is not None and t >= disturbance_time:
                control_signal += disturbance_value
            
            # 更新系统
            new_output = system.update(control_signal, self.dt)
            
            outputs.append(new_output)
            control_signals.append(control_signal)
        
        return self.time, np.array(outputs), np.array(control_signals), pid_controller
    
    def experiment_kp_effect(self):
        """
        实验1: Kp参数影响
        比例增益Kp的作用：
        - 增大Kp可以加快系统响应速度
        - 减小稳态误差
        - 但过大会导致超调和振荡
        """
        print("=" * 60)
        print("实验1: 比例增益 Kp 的影响")
        print("=" * 60)
        
        kp_values = [0.5, 1.0, 2.0, 5.0, 10.0]
        
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        # 主响应曲线
        ax1 = fig.add_subplot(gs[0:2, 0])
        ax2 = fig.add_subplot(gs[0:2, 1])
        
        # 性能指标
        ax3 = fig.add_subplot(gs[2, 0])
        ax4 = fig.add_subplot(gs[2, 1])
        
        rise_times = []
        settling_times = []
        overshoots = []
        steady_state_errors = []
        
        for kp in kp_values:
            # 使用一阶系统
            system = FirstOrderSystem(tau=1.0)
            pid = PIDController(Kp=kp, Ki=0.0, Kd=0.0, setpoint=1.0)
            
            time, output, control, _ = self.run_single_experiment(pid, system, setpoint=1.0)
            
            # 绘制输出响应
            ax1.plot(time, output, label=f'Kp={kp}', linewidth=2)
            
            # 绘制控制信号
            ax2.plot(time, control, label=f'Kp={kp}', linewidth=2)
            
            # 计算性能指标
            rise_time = self._calculate_rise_time(time, output, 1.0)
            settling_time = self._calculate_settling_time(time, output, 1.0)
            overshoot = self._calculate_overshoot(output, 1.0)
            sse = abs(1.0 - output[-1])
            
            rise_times.append(rise_time)
            settling_times.append(settling_time)
            overshoots.append(overshoot)
            steady_state_errors.append(sse)
            
            print(f"\nKp = {kp}:")
            print(f"  上升时间: {rise_time:.3f} s")
            print(f"  调节时间: {settling_time:.3f} s")
            print(f"  超调量: {overshoot:.2f} %")
            print(f"  稳态误差: {sse:.4f}")
        
        # 设置图表
        ax1.axhline(y=1.0, color='r', linestyle='--', linewidth=2, label='目标值')
        ax1.set_xlabel('时间 (s)', fontsize=12)
        ax1.set_ylabel('系统输出', fontsize=12)
        ax1.set_title('Kp对系统响应的影响', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        ax2.set_xlabel('时间 (s)', fontsize=12)
        ax2.set_ylabel('控制信号', fontsize=12)
        ax2.set_title('控制信号变化', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # 性能指标对比
        x_pos = np.arange(len(kp_values))
        ax3.bar(x_pos, rise_times, alpha=0.7, color='blue', edgecolor='black')
        ax3.set_xlabel('Kp值', fontsize=12)
        ax3.set_ylabel('上升时间 (s)', fontsize=12)
        ax3.set_title('上升时间对比', fontsize=12, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels([f'{kp}' for kp in kp_values])
        ax3.grid(True, alpha=0.3, axis='y')
        
        ax4.bar(x_pos, steady_state_errors, alpha=0.7, color='red', edgecolor='black')
        ax4.set_xlabel('Kp值', fontsize=12)
        ax4.set_ylabel('稳态误差', fontsize=12)
        ax4.set_title('稳态误差对比', fontsize=12, fontweight='bold')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels([f'{kp}' for kp in kp_values])
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('实验1: 比例增益Kp的影响\n增大Kp加快响应但可能引起振荡', 
                     fontsize=16, fontweight='bold', y=0.995)
        
        output_path = os.path.join('..', 'output', 'experiment_1_kp_effect.png')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n图表已保存: {output_path}")
        plt.close()
        
        return fig
    
    def experiment_ki_effect(self):
        """
        实验2: Ki参数影响
        积分增益Ki的作用：
        - 消除稳态误差
        - 但过大会导致积分饱和和系统不稳定
        """
        print("\n" + "=" * 60)
        print("实验2: 积分增益 Ki 的影响")
        print("=" * 60)
        
        # 固定Kp，变化Ki
        kp = 2.0
        ki_values = [0.0, 0.5, 1.0, 2.0, 5.0]
        
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)
        
        # 主响应曲线
        ax1 = fig.add_subplot(gs[0, :])
        ax2 = fig.add_subplot(gs[1, 0])
        ax3 = fig.add_subplot(gs[1, 1])
        
        # 误差和积分项
        ax4 = fig.add_subplot(gs[2, 0])
        ax5 = fig.add_subplot(gs[2, 1])
        
        for ki in ki_values:
            # 使用带有小扰动的系统来体现积分作用
            base_system = FirstOrderSystem(tau=1.0)
            system = SystemWithNoise(base_system, noise_std=0.01)
            
            pid = PIDController(Kp=kp, Ki=ki, Kd=0.0, setpoint=1.0)
            
            time, output, control, pid_obj = self.run_single_experiment(
                pid, system, setpoint=1.0
            )
            
            # 绘制输出响应
            ax1.plot(time, output, label=f'Ki={ki}', linewidth=2)
            
            # 绘制控制信号
            ax2.plot(time, control, label=f'Ki={ki}', linewidth=2)
            
            # 绘制误差
            errors = np.array(pid_obj.error_history)
            ax4.plot(time, errors, label=f'Ki={ki}', linewidth=2)
            
            # 绘制积分项
            i_terms = np.array(pid_obj.i_term_history)
            ax5.plot(time, i_terms, label=f'Ki={ki}', linewidth=2)
            
            # 计算稳态误差
            sse = abs(1.0 - np.mean(output[-100:]))
            print(f"\nKi = {ki} (Kp = {kp}):")
            print(f"  稳态误差: {sse:.4f}")
            print(f"  最终积分项: {i_terms[-1]:.4f}")
        
        # 设置图表
        ax1.axhline(y=1.0, color='r', linestyle='--', linewidth=2, label='目标值')
        ax1.set_xlabel('时间 (s)', fontsize=12)
        ax1.set_ylabel('系统输出', fontsize=12)
        ax1.set_title('Ki对系统响应的影响', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10, ncol=3)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([-0.1, 1.5])
        
        ax2.set_xlabel('时间 (s)', fontsize=12)
        ax2.set_ylabel('控制信号', fontsize=12)
        ax2.set_title('控制信号变化', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # 绘制放大的稳态区域
        zoom_time = time > 10
        for ki in ki_values:
            base_system = FirstOrderSystem(tau=1.0)
            system = SystemWithNoise(base_system, noise_std=0.01)
            pid = PIDController(Kp=kp, Ki=ki, Kd=0.0, setpoint=1.0)
            time_z, output_z, _, _ = self.run_single_experiment(pid, system, setpoint=1.0)
            ax3.plot(time_z[zoom_time], output_z[zoom_time], label=f'Ki={ki}', linewidth=2)
        
        ax3.axhline(y=1.0, color='r', linestyle='--', linewidth=2, label='目标值')
        ax3.set_xlabel('时间 (s)', fontsize=12)
        ax3.set_ylabel('系统输出', fontsize=12)
        ax3.set_title('稳态响应放大图 (消除稳态误差)', fontsize=14, fontweight='bold')
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim([0.9, 1.1])
        
        ax4.axhline(y=0, color='k', linestyle='-', linewidth=1)
        ax4.set_xlabel('时间 (s)', fontsize=12)
        ax4.set_ylabel('误差', fontsize=12)
        ax4.set_title('跟踪误差', fontsize=14, fontweight='bold')
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3)
        
        ax5.set_xlabel('时间 (s)', fontsize=12)
        ax5.set_ylabel('积分项贡献', fontsize=12)
        ax5.set_title('积分项累积 (消除稳态误差的关键)', fontsize=14, fontweight='bold')
        ax5.legend(fontsize=10)
        ax5.grid(True, alpha=0.3)
        
        plt.suptitle('实验2: 积分增益Ki的影响\nKi消除稳态误差，但过大会导致超调和振荡', 
                     fontsize=16, fontweight='bold', y=0.998)
        
        output_path = os.path.join('..', 'output', 'experiment_2_ki_effect.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n图表已保存: {output_path}")
        plt.close()
        
        return fig
    
    def experiment_kd_effect(self):
        """
        实验3: Kd参数影响
        微分增益Kd的作用：
        - 减小超调
        - 提高系统稳定性
        - 但对噪声敏感
        """
        print("\n" + "=" * 60)
        print("实验3: 微分增益 Kd 的影响")
        print("=" * 60)
        
        # 固定Kp和Ki，变化Kd
        kp = 5.0
        ki = 1.0
        kd_values = [0.0, 0.5, 1.0, 2.0, 5.0]
        
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)
        
        # 主响应曲线
        ax1 = fig.add_subplot(gs[0, :])
        ax2 = fig.add_subplot(gs[1, 0])
        ax3 = fig.add_subplot(gs[1, 1])
        
        # PID各项贡献
        ax4 = fig.add_subplot(gs[2, 0])
        ax5 = fig.add_subplot(gs[2, 1])
        
        overshoots = []
        
        for kd in kd_values:
            # 使用二阶系统，更容易看出阻尼效果
            system = SecondOrderSystem(mass=1.0, damping=0.3, stiffness=1.0)
            
            pid = PIDController(Kp=kp, Ki=ki, Kd=kd, setpoint=1.0)
            
            time, output, control, pid_obj = self.run_single_experiment(
                pid, system, setpoint=1.0
            )
            
            # 绘制输出响应
            ax1.plot(time, output, label=f'Kd={kd}', linewidth=2)
            
            # 绘制控制信号
            ax2.plot(time, control, label=f'Kd={kd}', linewidth=2)
            
            # 计算超调量
            overshoot = self._calculate_overshoot(output, 1.0)
            overshoots.append(overshoot)
            
            # 绘制微分项
            d_terms = np.array(pid_obj.d_term_history)
            ax4.plot(time, d_terms, label=f'Kd={kd}', linewidth=2)
            
            print(f"\nKd = {kd} (Kp = {kp}, Ki = {ki}):")
            print(f"  超调量: {overshoot:.2f} %")
            print(f"  最大微分项: {np.max(np.abs(d_terms)):.4f}")
        
        # 绘制超调量对比
        x_pos = np.arange(len(kd_values))
        ax3.bar(x_pos, overshoots, alpha=0.7, color='green', edgecolor='black')
        ax3.set_xlabel('Kd值', fontsize=12)
        ax3.set_ylabel('超调量 (%)', fontsize=12)
        ax3.set_title('Kd对超调量的影响', fontsize=14, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels([f'{kd}' for kd in kd_values])
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 测试Kd对噪声的敏感性
        print("\n测试Kd对噪声的敏感性...")
        for kd in [0.0, 2.0]:
            base_system = SecondOrderSystem(mass=1.0, damping=0.3, stiffness=1.0)
            system = SystemWithNoise(base_system, noise_std=0.05)
            
            pid = PIDController(Kp=kp, Ki=ki, Kd=kd, setpoint=1.0)
            time, output, _, _ = self.run_single_experiment(pid, system, setpoint=1.0)
            
            ax5.plot(time, output, label=f'Kd={kd} (有噪声)', linewidth=2, alpha=0.7)
        
        # 设置图表
        ax1.axhline(y=1.0, color='r', linestyle='--', linewidth=2, label='目标值')
        ax1.set_xlabel('时间 (s)', fontsize=12)
        ax1.set_ylabel('系统输出', fontsize=12)
        ax1.set_title('Kd对系统响应的影响 (减小超调)', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10, ncol=3)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([-0.1, 2.0])
        
        ax2.set_xlabel('时间 (s)', fontsize=12)
        ax2.set_ylabel('控制信号', fontsize=12)
        ax2.set_title('控制信号变化', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        ax4.set_xlabel('时间 (s)', fontsize=12)
        ax4.set_ylabel('微分项贡献', fontsize=12)
        ax4.set_title('微分项 (阻尼效果)', fontsize=14, fontweight='bold')
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3)
        
        ax5.axhline(y=1.0, color='r', linestyle='--', linewidth=2, label='目标值')
        ax5.set_xlabel('时间 (s)', fontsize=12)
        ax5.set_ylabel('系统输出', fontsize=12)
        ax5.set_title('Kd对噪声的敏感性', fontsize=14, fontweight='bold')
        ax5.legend(fontsize=10)
        ax5.grid(True, alpha=0.3)
        
        plt.suptitle('实验3: 微分增益Kd的影响\nKd减小超调和振荡，但对噪声敏感', 
                     fontsize=16, fontweight='bold', y=0.998)
        
        output_path = os.path.join('..', 'output', 'experiment_3_kd_effect.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n图表已保存: {output_path}")
        plt.close()
        
        return fig
    
    def experiment_combined_tuning(self):
        """
        实验4: PID参数综合调节
        展示如何协调三个参数以获得最佳性能
        """
        print("\n" + "=" * 60)
        print("实验4: PID参数综合调节")
        print("=" * 60)
        
        # 不同的参数组合
        configs = [
            {'name': '仅P控制', 'Kp': 3.0, 'Ki': 0.0, 'Kd': 0.0},
            {'name': 'PI控制', 'Kp': 3.0, 'Ki': 1.5, 'Kd': 0.0},
            {'name': 'PD控制', 'Kp': 3.0, 'Ki': 0.0, 'Kd': 1.0},
            {'name': '未调优PID', 'Kp': 5.0, 'Ki': 5.0, 'Kd': 0.1},
            {'name': '优化PID', 'Kp': 3.5, 'Ki': 1.8, 'Kd': 1.2},
        ]
        
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)
        
        ax1 = fig.add_subplot(gs[0, :])
        ax2 = fig.add_subplot(gs[1, 0])
        ax3 = fig.add_subplot(gs[1, 1])
        ax4 = fig.add_subplot(gs[2, :])
        
        performance_metrics = []
        
        for config in configs:
            system = SecondOrderSystem(mass=1.0, damping=0.5, stiffness=1.0)
            pid = PIDController(
                Kp=config['Kp'], 
                Ki=config['Ki'], 
                Kd=config['Kd'], 
                setpoint=1.0
            )
            
            # 添加阶跃扰动
            time, output, control, pid_obj = self.run_single_experiment(
                pid, system, setpoint=1.0, 
                disturbance_time=10.0, disturbance_value=-0.5
            )
            
            # 绘制响应
            ax1.plot(time, output, label=config['name'], linewidth=2.5)
            
            # 绘制控制信号
            ax2.plot(time, control, label=config['name'], linewidth=2)
            
            # 绘制P, I, D各项贡献
            if config['name'] == '优化PID':
                p_terms = np.array(pid_obj.p_term_history)
                i_terms = np.array(pid_obj.i_term_history)
                d_terms = np.array(pid_obj.d_term_history)
                
                ax4.plot(time, p_terms, label='P项', linewidth=2, linestyle='-')
                ax4.plot(time, i_terms, label='I项', linewidth=2, linestyle='--')
                ax4.plot(time, d_terms, label='D项', linewidth=2, linestyle='-.')
                ax4.plot(time, control, label='总控制信号', linewidth=2.5, 
                        linestyle='-', color='black', alpha=0.7)
            
            # 计算性能指标
            rise_time = self._calculate_rise_time(time, output, 1.0)
            settling_time = self._calculate_settling_time(time, output, 1.0)
            overshoot = self._calculate_overshoot(output[:1000], 1.0)  # 前10秒
            sse = abs(1.0 - np.mean(output[500:1000]))  # 5-10秒的平均误差
            
            performance_metrics.append({
                'name': config['name'],
                'rise_time': rise_time,
                'settling_time': settling_time,
                'overshoot': overshoot,
                'sse': sse
            })
            
            print(f"\n{config['name']} (Kp={config['Kp']}, Ki={config['Ki']}, Kd={config['Kd']}):")
            print(f"  上升时间: {rise_time:.3f} s")
            print(f"  调节时间: {settling_time:.3f} s")
            print(f"  超调量: {overshoot:.2f} %")
            print(f"  稳态误差: {sse:.4f}")
        
        # 性能指标对比表
        metrics_names = [m['name'] for m in performance_metrics]
        rise_times = [m['rise_time'] for m in performance_metrics]
        overshoots = [m['overshoot'] for m in performance_metrics]
        
        x_pos = np.arange(len(metrics_names))
        width = 0.35
        
        ax3_twin = ax3.twinx()
        bars1 = ax3.bar(x_pos - width/2, rise_times, width, 
                       alpha=0.7, color='blue', edgecolor='black', label='上升时间')
        bars2 = ax3_twin.bar(x_pos + width/2, overshoots, width, 
                            alpha=0.7, color='orange', edgecolor='black', label='超调量')
        
        ax3.set_xlabel('控制策略', fontsize=12)
        ax3.set_ylabel('上升时间 (s)', fontsize=12, color='blue')
        ax3_twin.set_ylabel('超调量 (%)', fontsize=12, color='orange')
        ax3.set_title('性能指标对比', fontsize=14, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(metrics_names, rotation=15, ha='right')
        ax3.tick_params(axis='y', labelcolor='blue')
        ax3_twin.tick_params(axis='y', labelcolor='orange')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 组合图例
        lines1, labels1 = ax3.get_legend_handles_labels()
        lines2, labels2 = ax3_twin.get_legend_handles_labels()
        ax3.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)
        
        # 设置主图
        ax1.axhline(y=1.0, color='r', linestyle='--', linewidth=2, label='目标值')
        ax1.axvline(x=10.0, color='gray', linestyle=':', linewidth=2, alpha=0.5, label='扰动时刻')
        ax1.set_xlabel('时间 (s)', fontsize=12)
        ax1.set_ylabel('系统输出', fontsize=12)
        ax1.set_title('不同PID配置的控制效果对比', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=11, ncol=3, loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([-0.2, 1.8])
        
        ax2.set_xlabel('时间 (s)', fontsize=12)
        ax2.set_ylabel('控制信号', fontsize=12)
        ax2.set_title('控制信号对比', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        ax4.axvline(x=10.0, color='gray', linestyle=':', linewidth=2, alpha=0.5)
        ax4.set_xlabel('时间 (s)', fontsize=12)
        ax4.set_ylabel('控制贡献', fontsize=12)
        ax4.set_title('优化PID的各项贡献分解', fontsize=14, fontweight='bold')
        ax4.legend(fontsize=11, ncol=4)
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle('实验4: PID参数综合调节\n协调Kp, Ki, Kd以达到最佳控制性能', 
                     fontsize=16, fontweight='bold', y=0.998)
        
        output_path = os.path.join('..', 'output', 'experiment_4_combined_tuning.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n图表已保存: {output_path}")
        plt.close()
        
        return fig
    
    def run_all_experiments(self):
        """运行所有实验"""
        print("\n" + "=" * 60)
        print("PID控制器完整实验")
        print("=" * 60)
        print("\n本实验将展示:")
        print("1. 比例增益 Kp 的影响")
        print("2. 积分增益 Ki 的影响")
        print("3. 微分增益 Kd 的影响")
        print("4. PID参数综合调节\n")
        
        self.experiment_kp_effect()
        self.experiment_ki_effect()
        self.experiment_kd_effect()
        self.experiment_combined_tuning()
        
        print("\n" + "=" * 60)
        print("所有实验完成!")
        print("=" * 60)
    
    # 辅助函数
    def _calculate_rise_time(self, time, output, setpoint, threshold=0.9):
        """计算上升时间 (达到目标值90%的时间)"""
        try:
            idx = np.where(output >= setpoint * threshold)[0][0]
            return time[idx]
        except:
            return time[-1]
    
    def _calculate_settling_time(self, time, output, setpoint, tolerance=0.02):
        """计算调节时间 (进入±2%误差带的时间)"""
        upper = setpoint * (1 + tolerance)
        lower = setpoint * (1 - tolerance)
        
        for i in range(len(output)-100, -1, -1):
            if output[i] > upper or output[i] < lower:
                if i + 100 < len(time):
                    return time[i + 100]
                else:
                    return time[-1]
        return time[0]
    
    def _calculate_overshoot(self, output, setpoint):
        """计算超调量 (%)"""
        max_output = np.max(output)
        if max_output > setpoint:
            return ((max_output - setpoint) / setpoint) * 100
        return 0.0


if __name__ == "__main__":
    # 运行所有实验
    experiments = PIDExperiments()
    experiments.run_all_experiments()

