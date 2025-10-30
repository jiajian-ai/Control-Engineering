"""
生成控制工程文档中的示意图
Generate figures for control engineering documentation
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，减少警告
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
import os
import sys
import warnings
import logging

# 设置UTF-8编码输出
if sys.platform == 'win32' and not hasattr(sys.stdout, '_wrapped'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdout._wrapped = True

# 抑制所有matplotlib警告
warnings.filterwarnings('ignore')
logging.getLogger('matplotlib').setLevel(logging.ERROR)
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

# 设置中文字体 - 多种备选方案
import matplotlib.font_manager as fm

# 尝试查找可用的中文字体
def find_chinese_font():
    """查找系统中可用的中文字体"""
    chinese_fonts = [
        'SimHei',           # 黑体
        'Microsoft YaHei',  # 微软雅黑
        'SimSun',           # 宋体
        'KaiTi',            # 楷体
        'FangSong',         # 仿宋
        'STSong',           # 华文宋体
        'STHeiti',          # 华文黑体
        'Arial Unicode MS', # Arial Unicode (Mac)
        'PingFang SC',      # 苹方-简 (Mac)
        'Heiti SC',         # 黑体-简 (Mac)
    ]
    
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    for font in chinese_fonts:
        if font in available_fonts:
            print(f"使用中文字体: {font}")
            return font
    
    print("警告: 未找到中文字体，将使用默认字体（可能无法正常显示中文）")
    return None

# 配置字体
chinese_font = find_chinese_font()
if chinese_font:
    plt.rcParams['font.sans-serif'] = [chinese_font, 'DejaVu Sans']
else:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
plt.rcParams['font.size'] = 10

# 禁用matplotlib的详细日志输出
import matplotlib
matplotlib.set_loglevel("ERROR")

# 确保输出目录存在
output_dir = os.path.join(os.path.dirname(__file__), 'figures')
os.makedirs(output_dir, exist_ok=True)


def generate_time_domain_response():
    """
    生成时域响应性能指标示意图
    包含：上升时间、超调量、调节时间、稳态误差等
    """
    # 创建典型二阶欠阻尼系统的阶跃响应
    t = np.linspace(0, 10, 1000)
    
    # 系统参数
    wn = 2.0  # 自然频率
    zeta = 0.3  # 阻尼比 (欠阻尼)
    
    # 二阶系统阶跃响应解析解
    wd = wn * np.sqrt(1 - zeta**2)  # 阻尼自然频率
    y = 1 - np.exp(-zeta * wn * t) * (np.cos(wd * t) + (zeta / np.sqrt(1 - zeta**2)) * np.sin(wd * t))
    
    # 平滑处理，避免震荡
    y = np.clip(y, 0, None)
    
    # 找到关键点
    y_final = 1.0  # 稳态值
    
    # 上升时间 (10% 到 90%)
    idx_10 = np.where(y >= 0.1)[0][0]
    idx_90 = np.where(y >= 0.9)[0][0]
    t_rise = t[idx_90] - t[idx_10]
    t_10 = t[idx_10]
    t_90 = t[idx_90]
    
    # 峰值时间和超调量
    idx_peak = np.argmax(y)
    t_peak = t[idx_peak]
    y_peak = y[idx_peak]
    overshoot = (y_peak - y_final) / y_final * 100
    
    # 调节时间 (2% 误差带)
    tolerance = 0.02
    settled = False
    for i in range(len(y) - 1, 0, -1):
        if abs(y[i] - y_final) > tolerance * y_final:
            t_settle = t[i + 1]
            settled = True
            break
    if not settled:
        t_settle = t[-1]
    
    # 延迟时间 (50%)
    idx_50 = np.where(y >= 0.5)[0][0]
    t_delay = t[idx_50]
    
    # 创建图形 - 调整大小和边距
    fig, ax = plt.subplots(figsize=(16, 9))
    
    # 绘制响应曲线
    ax.plot(t, y, 'b-', linewidth=3, label='系统响应 y(t)', zorder=10)
    
    # 绘制稳态值参考线
    ax.axhline(y=y_final, color='k', linestyle='--', linewidth=1.5, 
               label=f'稳态值 = {y_final:.2f}', alpha=0.7, zorder=5)
    
    # 绘制阶跃输入 (参考)
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
    
    # ==================== 1. 延迟时间 ====================
    ax.plot([0, t_delay], [0.5, 0.5], 'r--', linewidth=1.5, alpha=0.6)
    ax.plot([t_delay, t_delay], [0, 0.5], 'r--', linewidth=1.5, alpha=0.6)
    ax.plot(t_delay, 0.5, 'ro', markersize=9, zorder=15)
    ax.annotate('延迟时间 td\n(到达50%稳态值)', 
                xy=(t_delay, 0.5), xytext=(t_delay - 0.8, 0.25),
                fontsize=11, color='red', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8),
                arrowprops=dict(arrowstyle='->', color='red', lw=2.5))
    
    # ==================== 2. 上升时间 ====================
    ax.plot([t_10, t_90], [0.1, 0.1], 'g--', linewidth=1.5, alpha=0.6)
    ax.plot([t_10, t_10], [0, 0.1], 'g--', linewidth=1.5, alpha=0.6)
    ax.plot([t_90, t_90], [0, 0.9], 'g--', linewidth=1.5, alpha=0.6)
    ax.plot(t_10, 0.1, 'go', markersize=8, zorder=15)
    ax.plot(t_90, 0.9, 'go', markersize=8, zorder=15)
    
    # 上升时间标注 - 调整位置避免遮挡
    ax.annotate('', xy=(t_90, 0.05), xytext=(t_10, 0.05),
                arrowprops=dict(arrowstyle='<->', color='green', lw=2.5))
    ax.text((t_10 + t_90) / 2, -0.08, f'上升时间 tr = {t_rise:.2f}s\n(10% -> 90%)', 
            fontsize=11, ha='center', color='green', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.8))
    
    # 10% 和 90% 标注
    ax.text(t_10 - 0.3, 0.1, '10%', fontsize=9, ha='right', color='green')
    ax.text(t_90 - 0.3, 0.9, '90%', fontsize=9, ha='right', color='green')
    
    # ==================== 3. 峰值时间和超调量 ====================
    ax.plot([0, t_peak], [y_peak, y_peak], 'm--', linewidth=1.5, alpha=0.6)
    ax.plot([t_peak, t_peak], [0, y_peak], 'm--', linewidth=1.5, alpha=0.6)
    ax.plot(t_peak, y_peak, 'mo', markersize=10, zorder=15)
    
    # 超调量标注 - 右侧标注
    ax.annotate('', xy=(t_peak + 0.3, y_final), xytext=(t_peak + 0.3, y_peak),
                arrowprops=dict(arrowstyle='<->', color='magenta', lw=2.5))
    ax.text(t_peak + 1.0, (y_final + y_peak) / 2, 
            f'超调量 Mp\n= {overshoot:.1f}%', 
            fontsize=11, color='magenta', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='pink', alpha=0.8))
    
    # 峰值点标注 - 移到上方避免遮挡
    ax.annotate(f'峰值点\ntp = {t_peak:.2f}s\nymax = {y_peak:.3f}', 
                xy=(t_peak, y_peak), xytext=(t_peak + 1.2, y_peak + 0.18),
                fontsize=10, color='magenta', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='pink', alpha=0.8),
                arrowprops=dict(arrowstyle='->', color='magenta', lw=2.5))
    
    # ==================== 4. 调节时间 ====================
    # 2% 误差带
    ax.axhspan(y_final * (1 - tolerance), y_final * (1 + tolerance), 
               alpha=0.15, color='cyan', zorder=1)
    ax.axhline(y=y_final * (1 + tolerance), color='cyan', linestyle=':', 
               linewidth=1.5, alpha=0.7, label='±2% 误差带')
    ax.axhline(y=y_final * (1 - tolerance), color='cyan', linestyle=':', 
               linewidth=1.5, alpha=0.7)
    
    ax.plot([t_settle, t_settle], [0, y_final], 'c--', linewidth=2, alpha=0.8)
    ax.plot(t_settle, y_final, 'co', markersize=10, zorder=15)
    
    ax.annotate(f'调节时间 ts = {t_settle:.2f}s\n(进入±2%误差带)', 
                xy=(t_settle, y_final), xytext=(t_settle - 2.0, y_final + 0.25),
                fontsize=11, color='cyan', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcyan', alpha=0.8),
                arrowprops=dict(arrowstyle='->', color='cyan', lw=2.5))
    
    # 误差带标注
    ax.text(t[-1] - 0.5, y_final * (1 + tolerance) + 0.02, '+2%', 
            fontsize=9, ha='right', color='cyan')
    ax.text(t[-1] - 0.5, y_final * (1 - tolerance) - 0.02, '-2%', 
            fontsize=9, ha='right', color='cyan')
    
    # ==================== 5. 稳态误差 ====================
    y_actual_final = y[-1]
    if abs(y_actual_final - y_final) > 0.001:
        ax.annotate('', xy=(t[-1] - 0.5, y_final), xytext=(t[-1] - 0.5, y_actual_final),
                    arrowprops=dict(arrowstyle='<->', color='orange', lw=2))
        ax.text(t[-1] - 1.0, (y_final + y_actual_final) / 2, 
                f'$e_{{ss}}$\n稳态误差', 
                fontsize=10, color='orange', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='wheat', alpha=0.7))
    
    # 设置图形属性
    ax.set_xlabel('时间 t (秒)', fontsize=13, fontweight='bold')
    ax.set_ylabel('系统输出 y(t)', fontsize=13, fontweight='bold')
    ax.set_title('二阶系统阶跃响应 - 时域性能指标详解\n' + 
                 f'(自然频率 wn = {wn}, 阻尼比 zeta = {zeta})',
                 fontsize=16, fontweight='bold', pad=20)
    
    ax.set_xlim(-0.5, t[-1])
    ax.set_ylim(-0.15, y_peak + 0.35)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
    
    # 添加性能指标总结文本框 - 使用无衬线字体避免符号问题
    summary_text = (
        f'性能指标总结\n'
        f'----------------\n'
        f'延迟时间 td = {t_delay:.2f} s\n'
        f'上升时间 tr = {t_rise:.2f} s\n'
        f'峰值时间 tp = {t_peak:.2f} s\n'
        f'超调量 Mp = {overshoot:.1f} %\n'
        f'调节时间 ts = {t_settle:.2f} s\n'
        f'稳态值 yss = {y_final:.3f}'
    )
    
    ax.text(0.02, 0.97, summary_text, transform=ax.transAxes,
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='wheat', 
                     edgecolor='black', alpha=0.9, linewidth=2))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, '时域响应性能指标.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[OK] 已生成: {output_path}")
    plt.close()


def generate_control_system_block_diagram():
    """
    生成控制系统框图
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # 定义位置
    x_positions = {
        'setpoint': 1,
        'comparator': 2,
        'controller': 3.5,
        'actuator': 5,
        'plant': 6.5,
        'output': 8,
        'sensor': 6.5,
        'feedback': 2
    }
    
    y_main = 4
    y_feedback = 2
    
    # 绘制方框
    box_style = dict(boxstyle='round,pad=0.3', facecolor='lightblue', 
                     edgecolor='black', linewidth=2)
    
    # 设定值
    ax.text(x_positions['setpoint'], y_main, '设定值\nSetpoint\n$r(t)$', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', 
                     edgecolor='black', linewidth=2))
    
    # 比较器
    circle = plt.Circle((x_positions['comparator'], y_main), 0.25, 
                        facecolor='white', edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    ax.text(x_positions['comparator'], y_main, '±', ha='center', va='center', 
            fontsize=16, fontweight='bold')
    ax.text(x_positions['comparator'] - 0.15, y_main + 0.15, '+', 
            fontsize=12, color='blue', fontweight='bold')
    ax.text(x_positions['comparator'] - 0.15, y_main - 0.35, '−', 
            fontsize=12, color='red', fontweight='bold')
    ax.text(x_positions['comparator'], y_main - 0.6, '比较器', 
            ha='center', fontsize=9, style='italic')
    
    # 控制器
    ax.text(x_positions['controller'], y_main, '控制器\nController\nPID/MPC', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=box_style)
    
    # 执行器
    ax.text(x_positions['actuator'], y_main, '执行器\nActuator', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=box_style)
    
    # 被控对象
    ax.text(x_positions['plant'], y_main, '被控对象\nPlant/Process', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', 
                     edgecolor='black', linewidth=2))
    
    # 输出
    ax.text(x_positions['output'], y_main, '输出\nOutput\n$y(t)$', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', 
                     edgecolor='black', linewidth=2))
    
    # 传感器
    ax.text(x_positions['sensor'], y_feedback, '传感器\nSensor', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcyan', 
                     edgecolor='black', linewidth=2))
    
    # 绘制箭头
    arrow_style = dict(arrowstyle='->', lw=2.5, color='black')
    
    # 前向路径
    ax.annotate('', xy=(x_positions['comparator'] - 0.3, y_main), 
                xytext=(x_positions['setpoint'] + 0.4, y_main),
                arrowprops=arrow_style)
    
    ax.annotate('', xy=(x_positions['controller'] - 0.5, y_main), 
                xytext=(x_positions['comparator'] + 0.3, y_main),
                arrowprops=arrow_style)
    ax.text((x_positions['comparator'] + x_positions['controller']) / 2, 
            y_main + 0.3, '误差 $e(t)$', ha='center', fontsize=10, 
            color='blue', fontweight='bold')
    
    ax.annotate('', xy=(x_positions['actuator'] - 0.5, y_main), 
                xytext=(x_positions['controller'] + 0.5, y_main),
                arrowprops=arrow_style)
    ax.text((x_positions['controller'] + x_positions['actuator']) / 2, 
            y_main + 0.3, '控制信号 $u(t)$', ha='center', fontsize=10, 
            color='blue', fontweight='bold')
    
    ax.annotate('', xy=(x_positions['plant'] - 0.5, y_main), 
                xytext=(x_positions['actuator'] + 0.5, y_main),
                arrowprops=arrow_style)
    
    ax.annotate('', xy=(x_positions['output'] - 0.4, y_main), 
                xytext=(x_positions['plant'] + 0.5, y_main),
                arrowprops=arrow_style)
    
    # 反馈路径
    ax.annotate('', xy=(x_positions['sensor'], y_main - 0.5), 
                xytext=(x_positions['output'] - 0.2, y_main - 0.3),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='red'))
    
    ax.annotate('', xy=(x_positions['sensor'], y_feedback + 0.5), 
                xytext=(x_positions['sensor'], y_main - 0.5),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='red'))
    
    ax.annotate('', xy=(x_positions['comparator'], y_feedback), 
                xytext=(x_positions['sensor'] - 0.5, y_feedback),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='red'))
    
    ax.annotate('', xy=(x_positions['comparator'], y_main - 0.3), 
                xytext=(x_positions['comparator'], y_feedback + 0.3),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='red'))
    ax.text(x_positions['comparator'] - 0.6, (y_main + y_feedback) / 2, 
            '反馈信号\n$y_m(t)$', ha='center', fontsize=10, 
            color='red', fontweight='bold')
    
    # 标题
    ax.text(5, 5.5, '闭环反馈控制系统框图', ha='center', fontsize=16, 
            fontweight='bold')
    
    # 添加说明文本
    explanation = (
        '工作原理：\n'
        '1. 比较器计算误差: e(t) = r(t) - y_m(t)\n'
        '2. 控制器根据误差生成控制信号: u(t)\n'
        '3. 执行器执行控制动作\n'
        '4. 被控对象产生输出: y(t)\n'
        '5. 传感器测量输出，形成反馈闭环'
    )
    
    ax.text(1, 0.8, explanation, fontsize=9,
            bbox=dict(boxstyle='round,pad=0.8', facecolor='lightyellow', 
                     edgecolor='black', alpha=0.9, linewidth=1.5),
            verticalalignment='top')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, '控制系统框图.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[OK] 已生成: {output_path}")
    plt.close()


def generate_open_vs_closed_loop():
    """
    生成开环vs闭环对比示意图
    """
    # 调整图形大小，让两个子图更紧凑
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 9))
    
    # ========== 开环控制 ==========
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0.5, 3.2)  # 缩小Y轴范围，避免太空
    ax1.axis('off')
    
    box_style = dict(boxstyle='round,pad=0.3', facecolor='lightblue', 
                     edgecolor='black', linewidth=2)
    
    # 开环系统方框
    ax1.text(1.5, 1.5, '输入\nInput', ha='center', va='center', 
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', 
                     edgecolor='black', linewidth=2))
    
    ax1.text(3.5, 1.5, '控制器\nController', ha='center', va='center', 
            fontsize=11, fontweight='bold', bbox=box_style)
    
    ax1.text(5.5, 1.5, '执行器\nActuator', ha='center', va='center', 
            fontsize=11, fontweight='bold', bbox=box_style)
    
    ax1.text(7.5, 1.5, '被控对象\nPlant', ha='center', va='center', 
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', 
                     edgecolor='black', linewidth=2))
    
    ax1.text(9, 1.5, '输出\nOutput', ha='center', va='center', 
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightcoral', 
                     edgecolor='black', linewidth=2))
    
    # 开环箭头
    arrow_style = dict(arrowstyle='->', lw=2.5, color='black')
    for x_from, x_to in [(2, 3), (4, 5), (6, 7), (8, 8.7)]:
        ax1.annotate('', xy=(x_to, 1.5), xytext=(x_from, 1.5),
                    arrowprops=arrow_style)
    
    # 干扰 - 调整位置
    ax1.annotate('干扰\nDisturbance', xy=(7.5, 2.0), xytext=(7.5, 2.5),
                fontsize=11, color='red', fontweight='bold', ha='center',
                arrowprops=dict(arrowstyle='->', lw=2.5, color='red'))
    ax1.text(8.8, 2.5, '无法\n自动补偿', fontsize=10, color='red', 
            ha='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='pink', 
                     edgecolor='red', alpha=0.8, linewidth=1.5))
    
    ax1.text(5, 3.0, '开环控制系统 (Open-Loop Control)', 
            ha='center', fontsize=15, fontweight='bold')
    
    # 开环特点 - 移除特殊符号，使用简单文字
    open_features = (
        '特点：\n'
        '结构简单，成本低\n'
        '维护方便\n'
        '无法纠正干扰\n'
        '精度依赖模型准确性\n'
        '\n'
        '应用：定时器，步进电机等'
    )
    ax1.text(0.3, 0.8, open_features, fontsize=10,
            bbox=dict(boxstyle='round,pad=0.7', facecolor='lightyellow', 
                     edgecolor='red', alpha=0.9, linewidth=2),
            verticalalignment='top')
    
    # ========== 闭环控制 ==========
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0.2, 4.2)  # 缩小Y轴范围，布局更紧凑
    ax2.axis('off')
    
    y_main = 2.8
    y_feedback = 1.2
    
    # 闭环系统方框
    ax2.text(1.5, y_main, '设定值\nSetpoint', ha='center', va='center', 
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', 
                     edgecolor='black', linewidth=2))
    
    # 比较器
    circle = plt.Circle((2.5, y_main), 0.2, facecolor='white', 
                        edgecolor='black', linewidth=2)
    ax2.add_patch(circle)
    ax2.text(2.5, y_main, '±', ha='center', va='center', 
            fontsize=14, fontweight='bold')
    ax2.text(2.5, y_main - 0.45, '比较器', ha='center', fontsize=8)
    
    ax2.text(4, y_main, '控制器\nController', ha='center', va='center', 
            fontsize=11, fontweight='bold', bbox=box_style)
    
    ax2.text(5.5, y_main, '执行器\nActuator', ha='center', va='center', 
            fontsize=11, fontweight='bold', bbox=box_style)
    
    ax2.text(7, y_main, '被控对象\nPlant', ha='center', va='center', 
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', 
                     edgecolor='black', linewidth=2))
    
    ax2.text(8.5, y_main, '输出\nOutput', ha='center', va='center', 
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightcoral', 
                     edgecolor='black', linewidth=2))
    
    ax2.text(7, y_feedback, '传感器\nSensor', ha='center', va='center', 
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcyan', 
                     edgecolor='black', linewidth=2))
    
    # 前向箭头
    for x_from, x_to in [(1.8, 2.3), (2.7, 3.5), (4.5, 5), (6, 6.5), (7.5, 8.2)]:
        ax2.annotate('', xy=(x_to, y_main), xytext=(x_from, y_main),
                    arrowprops=arrow_style)
    
    # 反馈箭头
    ax2.annotate('', xy=(7, y_main - 0.4), xytext=(8.3, y_main - 0.3),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='red'))
    ax2.annotate('', xy=(7, y_feedback + 0.4), xytext=(7, y_main - 0.4),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='red'))
    ax2.annotate('', xy=(2.5, y_feedback), xytext=(6.5, y_feedback),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='red'))
    ax2.annotate('', xy=(2.5, y_main - 0.25), xytext=(2.5, y_feedback + 0.25),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='red'))
    
    ax2.text(5, y_feedback - 0.3, '反馈路径 (Feedback Path)', 
            ha='center', fontsize=10, color='red', fontweight='bold',
            style='italic')
    
    # 干扰 - 调整位置和样式
    ax2.annotate('干扰\nDisturbance', xy=(7, y_main + 0.5), 
                xytext=(7, y_main + 1.0),
                fontsize=11, color='orange', fontweight='bold', ha='center',
                arrowprops=dict(arrowstyle='->', lw=2.5, color='orange'))
    ax2.text(8.5, y_main + 1.0, '自动\n补偿', fontsize=10, color='green', 
            ha='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', 
                     edgecolor='green', alpha=0.8, linewidth=1.5))
    
    ax2.text(5, 4.0, '闭环控制系统 (Closed-Loop Control)', 
            ha='center', fontsize=15, fontweight='bold')
    
    # 闭环特点 - 移除特殊符号，使用简单文字
    closed_features = (
        '特点：\n'
        '自动纠正干扰\n'
        '精度高，鲁棒性好\n'
        '对参数变化不敏感\n'
        '结构复杂，成本高\n'
        '可能不稳定\n'
        '\n'
        '应用：温控，伺服系统等'
    )
    ax2.text(0.3, 0.5, closed_features, fontsize=10,
            bbox=dict(boxstyle='round,pad=0.7', facecolor='lightcyan', 
                     edgecolor='green', alpha=0.9, linewidth=2),
            verticalalignment='top')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, '开环vs闭环控制.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[OK] 已生成: {output_path}")
    plt.close()


if __name__ == "__main__":
    print("=" * 60)
    print("生成控制工程文档示意图")
    print("=" * 60)
    
    print("\n正在生成图表...")
    generate_time_domain_response()
    generate_control_system_block_diagram()
    generate_open_vs_closed_loop()
    
    print("\n" + "=" * 60)
    print("所有图表已生成完成！")
    print(f"保存位置: {output_dir}")
    print("=" * 60)

