"""
一键运行所有演示
Run all PID demonstrations
"""
import os
import sys

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("=" * 70)
    print("PID控制器完整演示")
    print("PID Controller Complete Demonstration")
    print("=" * 70)
    
    # 运行快速演示
    print("\n[1/2] 运行快速演示...")
    print("[1/2] Running quick demo...")
    try:
        try:
            from .quick_demo import quick_demo
        except ImportError:
            from quick_demo import quick_demo
        quick_demo()
        print("✓ 快速演示完成")
        print("✓ Quick demo completed")
    except Exception as e:
        print(f"✗ 快速演示失败: {e}")
        print(f"✗ Quick demo failed: {e}")
    
    # 运行完整实验
    print("\n[2/2] 运行完整实验 (这可能需要几分钟)...")
    print("[2/2] Running full experiments (this may take a few minutes)...")
    try:
        try:
            from .pid_experiments import PIDExperiments
        except ImportError:
            from pid_experiments import PIDExperiments
        experiments = PIDExperiments()
        experiments.run_all_experiments()
        print("✓ 完整实验完成")
        print("✓ Full experiments completed")
    except Exception as e:
        print(f"✗ 实验失败: {e}")
        print(f"✗ Experiments failed: {e}")
    
    # 总结
    print("\n" + "=" * 70)
    print("所有实验已完成! All experiments completed!")
    print("=" * 70)
    print("\n生成的文件 Generated files (in ../output/):")
    print("  📊 quick_demo.png - 快速演示结果")
    print("  📊 experiment_1_kp_effect.png - Kp参数影响")
    print("  📊 experiment_2_ki_effect.png - Ki参数影响")
    print("  📊 experiment_3_kd_effect.png - Kd参数影响")
    print("  📊 experiment_4_combined_tuning.png - PID综合调节")
    print("\n请查看output文件夹中的图片文件以了解详细结果。")
    print("Please check the image files in output/ folder for detailed results.")
    print("\n详细分析请参阅: doc/实验报告.md")
    print("For detailed analysis, see: doc/实验报告.md")
    

if __name__ == "__main__":
    main()

