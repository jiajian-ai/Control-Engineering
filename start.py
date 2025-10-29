#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速启动脚本
Quick Start Script

用法:
  python start.py              # 显示菜单
  python start.py demo         # 运行快速演示
  python start.py all          # 运行所有实验
  python start.py exp1         # 运行实验1
  python start.py exp2         # 运行实验2
  python start.py exp3         # 运行实验3
  python start.py exp4         # 运行实验4
"""

import sys
import os

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加PIDController到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PIDController'))


def show_menu():
    """显示菜单"""
    print("=" * 70)
    print("🎯 PID控制器实验 - 快速启动")
    print("🎯 PID Controller Experiments - Quick Start")
    print("=" * 70)
    print("\n可用命令 Available Commands:")
    print("  python start.py demo     # 运行快速演示 (Quick Demo)")
    print("  python start.py all      # 运行所有实验 (All Experiments)")
    print("  python start.py exp1     # 实验1: Kp参数影响")
    print("  python start.py exp2     # 实验2: Ki参数影响")
    print("  python start.py exp3     # 实验3: Kd参数影响")
    print("  python start.py exp4     # 实验4: PID综合调节")
    print("\n快捷方式 Shortcuts:")
    print("  python start.py          # 显示此菜单")
    print("  python start.py help     # 显示帮助信息")
    print("\n" + "=" * 70)
    print("\n💡 提示: 实验结果将保存在 output/ 目录")
    print("💡 Tip: Results will be saved in output/ folder")
    print("\n📖 更多信息请查看 README.md 和 doc/ 目录")
    print("📖 For more info, check README.md and doc/ folder\n")


def run_demo():
    """运行快速演示"""
    print("\n🚀 运行快速演示...")
    print("🚀 Running quick demo...\n")
    try:
        from quick_demo import quick_demo
        quick_demo()
        print("\n✅ 快速演示完成！查看 output/quick_demo.png")
        print("✅ Quick demo completed! Check output/quick_demo.png\n")
    except Exception as e:
        print(f"\n❌ 错误: {e}\n")
        import traceback
        traceback.print_exc()


def run_all():
    """运行所有实验"""
    print("\n🚀 运行所有实验...")
    print("🚀 Running all experiments...\n")
    try:
        from run_all_demos import main
        main()
        print("\n✅ 所有实验完成！查看 output/ 目录")
        print("✅ All experiments completed! Check output/ folder\n")
    except Exception as e:
        print(f"\n❌ 错误: {e}\n")
        import traceback
        traceback.print_exc()


def run_single_experiment(exp_num):
    """运行单个实验"""
    exp_names = {
        1: "Kp参数影响 (Kp Parameter Effect)",
        2: "Ki参数影响 (Ki Parameter Effect)",
        3: "Kd参数影响 (Kd Parameter Effect)",
        4: "PID综合调节 (Combined PID Tuning)"
    }
    
    print(f"\n🚀 运行实验{exp_num}: {exp_names.get(exp_num, '未知实验')}")
    print(f"🚀 Running Experiment {exp_num}...\n")
    
    try:
        from pid_experiments import PIDExperiments
        experiments = PIDExperiments()
        
        if exp_num == 1:
            experiments.experiment_kp_effect()
        elif exp_num == 2:
            experiments.experiment_ki_effect()
        elif exp_num == 3:
            experiments.experiment_kd_effect()
        elif exp_num == 4:
            experiments.experiment_combined_tuning()
        else:
            print(f"❌ 无效的实验编号: {exp_num}")
            return
        
        print(f"\n✅ 实验{exp_num}完成！查看 output/experiment_{exp_num}_*.png")
        print(f"✅ Experiment {exp_num} completed! Check output/experiment_{exp_num}_*.png\n")
    except Exception as e:
        print(f"\n❌ 错误: {e}\n")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_menu()
        return
    
    command = sys.argv[1].lower()
    
    if command in ['help', '-h', '--help']:
        show_menu()
    elif command == 'demo':
        run_demo()
    elif command == 'all':
        run_all()
    elif command == 'exp1':
        run_single_experiment(1)
    elif command == 'exp2':
        run_single_experiment(2)
    elif command == 'exp3':
        run_single_experiment(3)
    elif command == 'exp4':
        run_single_experiment(4)
    else:
        print(f"\n❌ 未知命令: {command}")
        print("💡 使用 'python start.py' 查看可用命令\n")


if __name__ == "__main__":
    main()

