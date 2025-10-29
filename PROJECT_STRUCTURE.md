# 项目结构说明

## 📁 完整目录结构

```
Control-Engineering/
│
├── 📄 README.md                    # 项目导航和快速开始指南
├── 📄 requirements.txt             # Python依赖包列表
├── 📄 PROJECT_STRUCTURE.md         # 项目结构详细说明(本文件)
│
├── 📁 PIDController/               # 【核心代码】PID控制器源代码
│   ├── __init__.py                # Python包初始化文件
│   ├── pid_controller.py          # PID控制器核心实现
│   ├── simulated_system.py        # 模拟被控系统
│   ├── pid_experiments.py         # 完整实验代码
│   ├── quick_demo.py              # 快速演示脚本
│   └── run_all_demos.py           # 一键运行所有实验
│
├── 📁 output/                      # 【输出目录】实验结果图片
│   ├── quick_demo.png             # 快速演示结果
│   ├── experiment_1_kp_effect.png # 实验1: Kp参数影响
│   ├── experiment_2_ki_effect.png # 实验2: Ki参数影响
│   ├── experiment_3_kd_effect.png # 实验3: Kd参数影响
│   └── experiment_4_combined_tuning.png # 实验4: PID综合调节
│
└── 📁 doc/                         # 【文档目录】项目文档
    ├── 实验报告.md                 # 详细实验报告和数据分析
    └── 使用说明.md                 # 完整使用指南和API文档
```

## 📂 目录分类说明

### 1️⃣ 根目录文件

| 文件 | 用途 | 说明 |
|------|------|------|
| `README.md` | 项目导航 | 项目概览、快速开始、文档索引 |
| `requirements.txt` | 依赖管理 | Python包依赖列表 |
| `PROJECT_STRUCTURE.md` | 结构说明 | 本文件，详细的项目结构说明 |

### 2️⃣ PIDController/ - 源代码目录

**核心模块:**

#### `pid_controller.py`
- **功能**: PID控制器核心实现
- **主要类**: `PIDController`
- **特性**:
  - 完整的PID算法
  - P、I、D各项独立可调
  - 输出限幅功能
  - 历史数据记录

**使用示例:**
```python
from PIDController import PIDController

pid = PIDController(Kp=2.0, Ki=0.5, Kd=0.1, setpoint=1.0)
control_signal = pid.update(current_output, dt=0.01)
```

#### `simulated_system.py`
- **功能**: 模拟被控系统
- **主要类**:
  - `FirstOrderSystem`: 一阶系统
  - `SecondOrderSystem`: 二阶系统
  - `SystemWithNoise`: 带噪声系统
  
**使用示例:**
```python
from PIDController import FirstOrderSystem

system = FirstOrderSystem(tau=1.0)
output = system.update(control_input, dt=0.01)
```

#### `pid_experiments.py`
- **功能**: 完整实验代码
- **主要类**: `PIDExperiments`
- **实验内容**:
  - 实验1: Kp参数影响
  - 实验2: Ki参数影响
  - 实验3: Kd参数影响
  - 实验4: PID综合调节

**使用示例:**
```python
from PIDController.pid_experiments import PIDExperiments

experiments = PIDExperiments()
experiments.run_all_experiments()
```

#### `quick_demo.py`
- **功能**: 快速演示脚本
- **特点**: 简单的PID控制示例，展示目标值跟踪

**运行方式:**
```bash
cd PIDController
python quick_demo.py
```

#### `run_all_demos.py`
- **功能**: 一键运行所有实验
- **特点**: 自动运行快速演示和完整实验

**运行方式:**
```bash
cd PIDController
python run_all_demos.py
```

#### `__init__.py`
- **功能**: Python包初始化
- **作用**: 使PIDController成为可导入的Python包

### 3️⃣ output/ - 输出目录

存放所有实验生成的可视化图片。

| 文件 | 内容 | 对应实验 |
|------|------|---------|
| `quick_demo.png` | PID跟踪变化目标值 | 快速演示 |
| `experiment_1_kp_effect.png` | Kp对响应速度和稳态误差的影响 | 实验1 |
| `experiment_2_ki_effect.png` | Ki消除稳态误差的作用 | 实验2 |
| `experiment_3_kd_effect.png` | Kd减小超调的效果 | 实验3 |
| `experiment_4_combined_tuning.png` | 不同控制策略对比 | 实验4 |

**图片特点:**
- 高分辨率 (300 DPI)
- 中文标注清晰
- 包含多个子图
- 性能指标可视化

### 4️⃣ doc/ - 文档目录

| 文档 | 内容 | 适合人群 |
|------|------|---------|
| `使用说明.md` | 详细使用指南、API文档、调参指南 | 初学者和开发者 |
| `实验报告.md` | 完整实验报告、数据分析、结论 | 学习者和研究者 |

**文档特色:**
- ✅ 详细的理论说明
- ✅ 完整的代码示例
- ✅ 实验数据表格
- ✅ 性能指标分析
- ✅ 调参策略指导

## 🔄 工作流程

### 新用户学习路径

1. **第一步**: 阅读 `README.md`
   - 了解项目概览
   - 安装依赖包

2. **第二步**: 运行快速演示
   ```bash
   cd PIDController
   python quick_demo.py
   ```
   - 查看 `output/quick_demo.png`
   - 理解基本控制效果

3. **第三步**: 阅读使用说明
   - 打开 `doc/使用说明.md`
   - 学习PID基本概念
   - 了解参数作用

4. **第四步**: 运行完整实验
   ```bash
   cd PIDController
   python run_all_demos.py
   ```
   - 查看所有实验图片
   - 对比不同参数效果

5. **第五步**: 阅读实验报告
   - 打开 `doc/实验报告.md`
   - 深入理解实验结果
   - 学习调参技巧

### 开发者使用路径

1. **导入模块**
   ```python
   from PIDController import PIDController, FirstOrderSystem
   ```

2. **创建控制系统**
   ```python
   pid = PIDController(Kp=2.0, Ki=0.5, Kd=0.1, setpoint=1.0)
   system = FirstOrderSystem(tau=1.0)
   ```

3. **运行仿真**
   ```python
   for t in time_steps:
       output = system.state
       control = pid.update(output, dt)
       system.update(control, dt)
   ```

4. **自定义实验**
   - 修改 `pid_experiments.py`
   - 添加新的实验场景
   - 测试不同参数组合

## 📦 模块依赖关系

```
run_all_demos.py
    ├── quick_demo.py
    │   ├── pid_controller.py
    │   └── simulated_system.py
    └── pid_experiments.py
        ├── pid_controller.py
        └── simulated_system.py
```

**说明:**
- `pid_controller.py` 和 `simulated_system.py` 是独立模块
- `quick_demo.py` 和 `pid_experiments.py` 使用核心模块
- `run_all_demos.py` 调用演示和实验模块

## 🚀 快速命令参考

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行实验
```bash
# 方式1: 运行所有实验
cd PIDController
python run_all_demos.py

# 方式2: 单独运行
cd PIDController
python quick_demo.py              # 快速演示
python pid_experiments.py         # 完整实验
```

### 导入使用
```python
# 方式1: 从包导入
from PIDController import PIDController, FirstOrderSystem

# 方式2: 直接导入模块
import sys
sys.path.append('./PIDController')
from pid_controller import PIDController
```

## 📝 文件命名规范

### 代码文件
- 使用小写字母和下划线: `pid_controller.py`
- 模块名要有描述性: `simulated_system.py`

### 输出文件
- 使用小写字母和下划线: `quick_demo.png`
- 包含实验编号: `experiment_1_kp_effect.png`

### 文档文件
- 中文文档使用中文名: `实验报告.md`
- 英文文档使用英文名: `README.md`
- 全大写用于重要文档: `PROJECT_STRUCTURE.md`

## 🔧 扩展建议

### 添加新实验
1. 在 `PIDController/pid_experiments.py` 中添加新方法
2. 在 `run_all_experiments()` 中调用
3. 更新文档说明

### 添加新系统
1. 在 `PIDController/simulated_system.py` 中添加新类
2. 继承基础系统类或独立实现
3. 在 `__init__.py` 中导出

### 自定义可视化
1. 修改实验类中的绘图代码
2. 调整图表布局和样式
3. 保存到 `output/` 目录

## 📊 项目统计

- **代码文件**: 6个Python文件
- **文档文件**: 4个Markdown文件  
- **输出图片**: 5张高质量可视化图
- **实验数量**: 4个详细实验
- **代码行数**: ~1000+ 行
- **文档字数**: ~10000+ 字

## 🎯 项目特色

1. ✅ **结构清晰**: 代码、文档、输出分类明确
2. ✅ **易于使用**: 一键运行所有实验
3. ✅ **文档完善**: 详细的使用说明和实验报告
4. ✅ **可视化专业**: 高质量的图表展示
5. ✅ **可扩展性强**: 模块化设计，易于扩展
6. ✅ **教学友好**: 适合学习PID控制原理

---

**更新日期**: 2025年10月29日  
**项目版本**: 1.0.0

