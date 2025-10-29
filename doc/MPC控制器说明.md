# MPC模型预测控制器说明

## 📚 简介

MPC（Model Predictive Control，模型预测控制）是一种基于优化的先进控制方法，介于经典PID控制和现代强化学习之间。

## 🎯 MPC原理

### 核心思想

1. **预测**: 基于系统模型预测未来N步状态
2. **优化**: 在预测时域内求解最优控制序列
3. **执行**: 仅执行第一个控制输入
4. **滚动**: 下一时刻重复上述过程（滚动优化）

### 数学表达

**优化问题**：
```
min  Σ[(x_k - x_ref)^T Q (x_k - x_ref) + u_k^T R u_k]
u    k=1 to N

subject to:
  x_{k+1} = f(x_k, u_k)  # 系统动力学
  u_min ≤ u_k ≤ u_max   # 控制约束
```

其中：
- N: 预测时域（Prediction Horizon）
- Q: 状态权重矩阵
- R: 控制权重矩阵
- f: 系统模型

## 📦 实现类型

### 1. MPCController (非线性MPC)

**特点**：
- 使用完整的非线性模型
- scipy优化求解
- 适合复杂非线性系统

**使用示例**：
```python
from MPCController import MPCController, cartpole_dynamics

mpc = MPCController(
    prediction_horizon=10,
    control_horizon=5,
    dt=0.02,
    Q=np.diag([10, 1, 200, 20]),
    R=np.array([[0.01]]),
    u_min=-50,
    u_max=50
)

# 控制循环
current_state = np.array([x, x_dot, theta, theta_dot])
u_opt = mpc.update(current_state, cartpole_dynamics)
```

### 2. LinearMPCController (线性MPC)

**特点**：
- 在工作点线性化
- 二次规划求解，更快
- 适合小范围控制

**使用示例**：
```python
from MPCController import LinearMPCController

mpc = LinearMPCController(
    prediction_horizon=15,
    control_horizon=8,
    dt=0.02
)

# 系统参数 [M, m, l, g]
system_params = [1.0, 0.1, 0.5, 9.8]
u_opt = mpc.update(current_state, system_params)
```

### 3. AdaptiveMPCController (自适应MPC)

**特点**：
- 根据系统状态自动调整权重
- 动态改变预测时域
- 更智能的控制策略

**使用示例**：
```python
from MPCController import AdaptiveMPCController

mpc = AdaptiveMPCController(
    base_N=10,
    base_M=5,
    dt=0.02
)

u_opt = mpc.update(current_state, cartpole_dynamics)
```

## 🔧 参数调节指南

### 预测时域 N

| N值 | 效果 | 计算量 | 适用场景 |
|-----|------|--------|---------|
| 5-10 | 短期预测，快速响应 | 低 | 快速系统 |
| 10-20 | 中期预测，平衡性能 | 中 | 一般系统 |
| 20+ | 长期预测，全局优化 | 高 | 慢速系统 |

### 控制时域 M

- 通常设为 M ≤ N
- M 越小，计算量越小
- 推荐: M = N/2 到 N

### 权重矩阵 Q

```python
Q = np.diag([q_x, q_x_dot, q_theta, q_theta_dot])
```

**调节原则**：
- 重要状态 → 大权重
- 次要状态 → 小权重

**CartPole示例**：
```python
Q = np.diag([10, 1, 200, 20])
#            ↑  ↑   ↑   ↑
#            |  |   |   角速度权重
#            |  |   角度权重(最重要!)
#            |  速度权重
#            位置权重
```

### 权重矩阵 R

```python
R = np.array([[r]])
```

- R越大 → 控制越平滑，响应越慢
- R越小 → 控制越激进，可能振荡
- 推荐范围: 0.001 ~ 1.0

## 📊 CartPole实验结果

### 性能对比

| 控制器 | 存活时间 | 优势 | 劣势 |
|--------|----------|------|------|
| PID | 0.10s | 简单 | 无法处理非线性 |
| MPC (Nonlinear) | 3.15s | 预测能力强 | 计算量大 |
| MPC (Linear) | 4.09s | 快速，效果好 | 仅适合小角度 |
| Adaptive MPC | 2.38s | 自适应 | 调节复杂 |

### 关键发现

1. ✅ **MPC远优于PID**: 30-40倍存活时间
2. ✅ **线性MPC效果最好**: 在小角度下有效
3. ✅ **预测很重要**: N=15 优于 N=10
4. ⚠️ **仍未完全成功**: CartPole太难，需要RL

## 💡 MPC vs PID vs RL

### 决策树

```
需要控制系统？
  ├─ 系统简单、线性？
  │   └─ 使用 PID ✓
  │
  ├─ 有准确模型 + 约束？
  │   └─ 使用 MPC ✓
  │
  └─ 模型未知 + 超高性能？
      └─ 使用 RL ✓
```

### 适用场景

#### MPC擅长：
- ✅ 化工过程控制
- ✅ 汽车自适应巡航
- ✅ 机器人路径规划
- ✅ 多变量约束系统
- ✅ 电力系统控制

#### MPC不适合：
- ❌ 超快速系统 (< 1ms)
- ❌ 模型完全未知
- ❌ 计算资源有限
- ❌ 简单SISO系统

## 🔬 实验运行

### 实验1: MPC温度控制（推荐入门）

**更直观的MPC学习示例！**

```bash
python start.py mpc-temp
```

**为什么这个例子更适合学习？**
- ✅ **简单系统**: 只有一个状态（温度），容易理解
- ✅ **物理直观**: 房间加热，人人都能理解
- ✅ **约束明显**: 加热器功率限制（0-2000W）
- ✅ **预测清晰**: 温度变化慢，容易看到预测效果
- ✅ **两种方法都有效**: 展示MPC优势而非必要性

**场景**: 冬天室外5°C，需要将房间从5°C加热到22°C并保持

**系统模型**:
```
dT/dt = -a*(T - T_ambient) + b*u

其中:
  T: 房间温度 (°C)
  T_ambient: 环境温度 (5°C)
  u: 加热器功率 (0-2000W)
  a = 0.05: 热损失系数
  b = 0.002: 加热效率
```

**MPC设置**:
```python
prediction_horizon = 20  # 预测200秒（3.3分钟）
control_horizon = 10     # 控制100秒
Q_weight = 10.0         # 温度误差权重
R_weight = 0.001        # 控制输入权重
```

**对比内容**:
1. **MPC控制器**
   - 预测未来温度变化
   - 优化加热功率
   - 平滑控制，无超调

2. **PID控制器**
   - 传统反馈控制
   - 可能有超调
   - 反应而非预测

3. **无控制基线**
   - 展示系统自然响应

**结果图表**: `output/mpc_temperature_control.png`

包含：
- 温度响应曲线
- 加热功率变化
- 跟踪误差分析
- 性能指标对比

**学习要点**:
1. 观察MPC如何预测温度变化
2. 对比MPC与PID的控制策略
3. 理解预测时域N的作用
4. 体会约束处理的自然性

---

### 实验2: MPC CartPole控制（高级）

**展示MPC在复杂系统上的能力**

```bash
python start.py mpc
```

**实验内容**:

1. **非线性MPC** (N=10)
   - 使用完整CartPole动力学
   - scipy优化求解

2. **线性MPC** (N=15)
   - 在平衡点线性化
   - 二次规划求解

3. **自适应MPC**
   - 动态调整权重和时域
   - 智能控制策略

4. **PID对比**
   - 展示MPC的优势

**结果图表**: `output/mpc_cartpole_comparison.png`

包含：
- 杆子角度响应
- 小车位置响应
- 控制信号
- 优化代价
- 相图
- 性能对比

## 💡 两个实验的对比

### 为什么有两个例子？

| 特性 | 温度控制 | CartPole |
|------|----------|----------|
| **状态维度** | 1D (温度) | 4D (位置、速度、角度、角速度) |
| **系统复杂度** | 简单（一阶） | 复杂（非线性耦合） |
| **物理意义** | 非常直观 | 需要理解 |
| **控制难度** | 低 | 极高 |
| **PID效果** | 有效 | 失败 |
| **MPC优势** | 明显但非必需 | 显著优于PID |
| **学习目的** | 理解MPC原理 | 展示MPC能力 |
| **推荐顺序** | **首先学习** ✨ | 之后挑战 |

### 学习路径建议

```
1. 温度控制 (mpc-temp) 👈 从这里开始！
   ↓
   理解MPC基本概念：
   - 预测时域
   - 滚动优化
   - 约束处理
   - 权重调节
   
2. CartPole (mpc)
   ↓
   体验MPC在复杂系统上的威力：
   - 多变量耦合
   - 强非线性
   - 不稳定平衡点
   - 与RL的对比
```

### 关键洞察

**温度控制告诉你**:
- MPC **如何工作**（原理清晰）
- 参数**如何调节**（效果直观）
- 与PID**区别在哪**（预测vs反应）

**CartPole告诉你**:
- MPC **能做什么**（处理复杂系统）
- MPC **局限在哪**（需要准确模型）
- **何时选择RL**（模型未知或极端性能需求）

## 📖 高级主题

### 1. 状态估计

MPC需要完整状态信息，实际应用中可能需要：
- 卡尔曼滤波器
- 扩展卡尔曼滤波
- 粒子滤波

### 2. 鲁棒MPC

处理模型不确定性：
- Tube MPC
- Min-Max MPC
- Stochastic MPC

### 3. 非线性MPC加速

提高求解速度：
- Real-Time Iteration
- Multiple Shooting
- 预计算数据表

### 4. 学习型MPC

结合机器学习：
- 数据驱动模型
- 神经网络MPC
- MPC + RL混合

## 📚 参考文献

1. **经典教材**:
   - "Model Predictive Control" - Camacho & Bordons
   - "Predictive Control" - Maciejowski

2. **在线资源**:
   - ACADO Toolkit
   - CasADi (Python)
   - do-mpc

3. **论文**:
   - Mayne et al. "Constrained Model Predictive Control: Stability and Optimality"

## 🎓 学习路径

1. **基础**: 理解状态空间、优化
2. **实践**: 运行本项目MPC实验
3. **深入**: 学习约束处理、稳定性
4. **应用**: 在实际系统上测试

## 🛠️ 故障排查

### 问题1: 优化不收敛
**解决**: 
- 减小预测时域N
- 调整Q, R权重
- 改善初始猜测

### 问题2: 控制振荡
**解决**:
- 增大R权重
- 添加控制变化率惩罚
- 缩短控制时域M

### 问题3: 计算太慢
**解决**:
- 使用线性MPC
- 减小N, M
- 使用更快的求解器

## 📝 总结

MPC是强大的控制方法：
- ✅ 基于模型，可预测
- ✅ 天然处理约束
- ✅ 多变量系统优化
- ⚠️ 需要准确模型
- ⚠️ 计算量较大

在CartPole上，MPC显著优于PID，但仍不如RL。这正说明了：
- 简单问题 → PID
- 中等问题 → MPC
- 复杂问题 → RL

---

**作者**: Control Engineering Lab
**日期**: 2025年10月29日
**版本**: 1.0.0

