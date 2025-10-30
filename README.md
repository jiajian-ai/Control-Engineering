# Control Engineering - PID控制器项目

<div align="center">

**一个完整的PID控制器实现与实验项目**

[English](#english) | [中文](#chinese)

</div>

---

## <a id="chinese"></a>🇨🇳 中文说明

### 📋 项目简介

本项目实现了完整的PID(比例-积分-微分)控制器，并通过4个详细实验展示了Kp、Ki、Kd三个参数对系统控制性能的影响。所有实验结果都进行了专业的可视化。

### 📁 项目结构

```
Control-Engineering/
│
├── 📄 README.md                    # 项目导航(本文件)
├── 📄 requirements.txt             # Python依赖包
├── 📄 CONTROL_ENGINEERING_OUTLINE.md # 控制工程课程大纲
├── 📄 start.py                     # 项目启动脚本
│
├── 📁 PIDController/               # PID控制器源代码
│   ├── pid_controller.py          # PID控制器核心实现
│   ├── simulated_system.py        # 模拟被控系统(一阶/二阶)
│   ├── pid_experiments.py         # 完整实验代码
│   ├── quick_demo.py              # 快速演示脚本
│   ├── cartpole_pid.py            # CartPole倒立摆PID控制
│   └── run_all_demos.py           # 一键运行所有实验
│
├── 📁 MPCController/               # MPC控制器源代码
│   ├── mpc_controller.py          # MPC控制器核心实现
│   ├── mpc_cartpole_experiment.py # CartPole MPC实验
│   └── mpc_temperature_control.py # 温度控制MPC实验
│
├── 📁 output/                      # 实验输出图片
│   ├── quick_demo.png             # 快速演示结果
│   ├── experiment_1_kp_effect.png # 实验1: Kp参数影响
│   ├── experiment_2_ki_effect.png # 实验2: Ki参数影响
│   ├── experiment_3_kd_effect.png # 实验3: Kd参数影响
│   ├── experiment_4_combined_tuning.png # 实验4: PID综合调节
│   ├── cartpole_pid_control.png   # CartPole PID控制结果
│   ├── mpc_cartpole_comparison.png # MPC CartPole对比实验
│   └── mpc_temperature_control.png # MPC温度控制结果
│
└── 📁 doc/                         # 文档目录
    ├── 实验报告.md                 # 详细实验报告
    ├── 使用说明.md                 # 完整使用指南
    ├── MPC控制器说明.md            # MPC控制器详细说明
    ├── PID_vs_RL_对比.md          # PID与强化学习对比
    ├── 第1章_控制工程基础.md       # 第1章：控制工程基础
    ├── 第2章_系统动力学与响应.md   # 第2章：系统动力学与响应
    ├── 第3章_PID控制与工程调节.md  # 第3章：PID控制与工程调节
    ├── 第4章_现代控制理论基础.md   # 第4章：现代控制理论基础
    ├── 第5章_先进控制方法入门.md   # 第5章：先进控制方法入门
    ├── 第6章_典型工程案例分析.md   # 第6章：典型工程案例分析
    ├── 第7章_仿真工具与实验平台.md # 第7章：仿真工具与实验平台
    ├── 第8章_控制系统设计综合.md   # 第8章：控制系统设计综合
    └── figures/                    # 图片资源目录
        ├── 开环vs闭环控制.png
        ├── 控制系统框图.png
        └── 时域响应性能指标.png
```

### 🚀 快速开始

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 运行实验

**方式一: 使用快速启动脚本 (推荐)**
```bash
python start.py          # 显示菜单
python start.py demo     # 运行快速演示
python start.py all      # 运行所有实验
python start.py exp1     # 运行单个实验
```

**方式二: 直接运行**
```bash
# 运行所有实验
python PIDController/run_all_demos.py

# 或单独运行
python PIDController/quick_demo.py          # 快速演示
python PIDController/pid_experiments.py     # 完整实验
```

#### 3. 查看结果
- 📊 实验图片: 查看 `output/` 目录
- 📖 实验报告: 查看 `doc/实验报告.md`
- 📘 使用指南: 查看 `doc/使用说明.md`

### 🔬 实验内容

| 实验 | 内容 | 结果文件 |
|------|------|---------|
| **实验0** | 快速演示 | `output/quick_demo.png` |
| **实验1** | Kp(比例增益)的影响 | `output/experiment_1_kp_effect.png` |
| **实验2** | Ki(积分增益)的影响 | `output/experiment_2_ki_effect.png` |
| **实验3** | Kd(微分增益)的影响 | `output/experiment_3_kd_effect.png` |
| **实验4** | PID参数综合调节 | `output/experiment_4_combined_tuning.png` |
| **实验5** | CartPole倒立摆(PID vs RL) | `output/cartpole_pid_control.png` |
| **实验6** | MPC模型预测控制(CartPole) | `output/mpc_cartpole_comparison.png` |
| **实验7** | MPC温度控制 ⭐ 推荐入门 | `output/mpc_temperature_control.png` |

### 📚 核心功能

#### PID控制器 (`PIDController/`)
- ✅ 完整的PID算法实现
- ✅ 支持P、I、D各项独立调节
- ✅ 输出限幅功能
- ✅ 历史数据记录
- ✅ CartPole倒立摆控制实验

#### MPC控制器 (`MPCController/`)
- ✅ 非线性MPC（基于优化）
- ✅ 线性MPC（更快速）
- ✅ 自适应MPC（智能调节）
- ✅ 预测时域和控制时域可配置
- ✅ 温度控制示例（推荐入门）⭐
- ✅ CartPole对比实验（高级）

#### 模拟系统 (`PIDController/simulated_system.py`)
- ✅ 一阶系统 (温度、液位等)
- ✅ 二阶系统 (机械系统、电机等)
- ✅ 噪声模拟

#### 实验模块
- ✅ PID: 4个详细实验
- ✅ MPC: 温度控制示例（适合学习MPC原理）
- ✅ MPC: CartPole对比实验（展示MPC能力）
- ✅ 性能指标计算
- ✅ 专业可视化

### 📖 文档导航

| 文档 | 说明 | 路径 |
|------|------|------|
| 📘 **使用说明** | 详细的使用指南和API文档 | `doc/使用说明.md` |
| 📊 **实验报告** | 完整的实验数据和分析 | `doc/实验报告.md` |
| 🎯 **MPC控制器说明** | MPC原理与实验指南 ⭐ | `doc/MPC控制器说明.md` |
| 🆚 **PID vs RL对比** | CartPole控制方法对比 | `doc/PID_vs_RL_对比.md` |
| 📚 **课程大纲** | 控制工程完整课程大纲 | `CONTROL_ENGINEERING_OUTLINE.md` |
| 📖 **第1章** | 控制工程基础 | `doc/第1章_控制工程基础.md` |
| 📖 **第2章** | 系统动力学与响应 | `doc/第2章_系统动力学与响应.md` |
| 📖 **第3章** | PID控制与工程调节 | `doc/第3章_PID控制与工程调节.md` |
| 📖 **第4章** | 现代控制理论基础 | `doc/第4章_现代控制理论基础.md` |
| 📖 **第5章** | 先进控制方法入门 | `doc/第5章_先进控制方法入门.md` |
| 📖 **第6章** | 典型工程案例分析 | `doc/第6章_典型工程案例分析.md` |
| 📖 **第7章** | 仿真工具与实验平台 | `doc/第7章_仿真工具与实验平台.md` |
| 📖 **第8章** | 控制系统设计综合 | `doc/第8章_控制系统设计综合.md` |
| 📄 **项目导航** | 项目结构和快速开始(本文件) | `README.md` |

### 🎯 学习路径

#### 初学者
1. 阅读 `doc/使用说明.md` 了解基本概念
2. 运行 `python PIDController/quick_demo.py`
3. 查看 `output/quick_demo.png` 理解效果
4. 尝试修改PID参数观察变化

#### 进阶使用
1. 运行完整实验 `python PIDController/run_all_demos.py`
2. 阅读 `doc/实验报告.md` 理解参数影响
3. 修改实验代码测试不同场景
4. 尝试控制不同的系统

#### 高级应用
1. 学习MPC模型预测控制
   - 先运行 `python start.py mpc-temp`（温度控制，推荐入门）
   - 再运行 `python start.py mpc`（CartPole，挑战高级）
   - 查看 `doc/MPC控制器说明.md` 理解MPC原理
2. 实现自适应PID
3. 添加前馈控制
4. 实现抗积分饱和
5. 连接实际硬件测试

### 💡 PID参数速查

| 参数 | 作用 | 增大效果 | 适用场景 |
|------|------|---------|---------|
| **Kp** | 比例控制 | 响应更快，但可能振荡 | 需要快速响应 |
| **Ki** | 积分控制 | 消除稳态误差 | 需要高精度 |
| **Kd** | 微分控制 | 减小超调和振荡 | 需要平稳控制 |

### 🛠️ 技术栈

- **语言**: Python 3.7+
- **核心库**: NumPy, Matplotlib
- **控制理论**: PID控制、一阶/二阶系统

### 📝 许可证

本项目仅供学习和研究使用。

---

## <a id="english"></a>🇬🇧 English Documentation

### 📋 Project Overview

A comprehensive PID (Proportional-Integral-Derivative) controller implementation with detailed experiments demonstrating the effects of Kp, Ki, and Kd parameters on control system performance.

### 📁 Project Structure

```
Control-Engineering/
│
├── 📄 README.md                    # Project Navigation (this file)
├── 📄 requirements.txt             # Python Dependencies
│
├── 📁 PIDController/               # Source Code
│   ├── pid_controller.py          # PID Controller Core
│   ├── simulated_system.py        # Simulated Systems
│   ├── pid_experiments.py         # Experiments
│   ├── quick_demo.py              # Quick Demo
│   └── run_all_demos.py           # Run All Experiments
│
├── 📁 output/                      # Experiment Output
│   ├── quick_demo.png
│   ├── experiment_1_kp_effect.png
│   ├── experiment_2_ki_effect.png
│   ├── experiment_3_kd_effect.png
│   └── experiment_4_combined_tuning.png
│
└── 📁 doc/                         # Documentation
    ├── 实验报告.md                 # Experiment Report (Chinese)
    └── 使用说明.md                 # User Guide (Chinese)
```

### 🚀 Quick Start

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Run Experiments
```bash
# Run all experiments
python PIDController/run_all_demos.py

# Or run individually
python PIDController/quick_demo.py          # Quick demo
python PIDController/pid_experiments.py     # Full experiments
```

#### 3. View Results
- 📊 Charts: Check `output/` directory
- 📖 Reports: Check `doc/` directory

### 🔬 Experiments

| Experiment | Description | Output |
|------------|-------------|--------|
| **Demo** | Quick demonstration | `output/quick_demo.png` |
| **Exp 1** | Kp (Proportional Gain) Effect | `output/experiment_1_kp_effect.png` |
| **Exp 2** | Ki (Integral Gain) Effect | `output/experiment_2_ki_effect.png` |
| **Exp 3** | Kd (Derivative Gain) Effect | `output/experiment_3_kd_effect.png` |
| **Exp 4** | Combined PID Tuning | `output/experiment_4_combined_tuning.png` |

### 📚 Core Features

#### PID Controller
- ✅ Complete PID algorithm
- ✅ Independent P, I, D tuning
- ✅ Output limiting
- ✅ History tracking

#### Simulated Systems
- ✅ First-order systems
- ✅ Second-order systems
- ✅ Noise simulation

#### Experiments
- ✅ 4 detailed experiments
- ✅ Performance metrics
- ✅ Professional visualization

### 💡 PID Parameters Quick Reference

| Parameter | Function | Effect of Increase | Use Case |
|-----------|----------|-------------------|----------|
| **Kp** | Proportional | Faster response, possible oscillation | Fast response needed |
| **Ki** | Integral | Eliminates steady-state error | High precision needed |
| **Kd** | Derivative | Reduces overshoot | Smooth control needed |

### 🛠️ Technology Stack

- **Language**: Python 3.7+
- **Libraries**: NumPy, Matplotlib
- **Theory**: PID Control, First/Second-order Systems

### 📝 License

For learning and research purposes only.

---

<div align="center">

**Made with ❤️ for Control Engineering Education**

⭐ Star this project if you find it helpful!

</div>
