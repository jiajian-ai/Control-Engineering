"""
模拟被控系统
实现一个一阶和二阶系统用于PID控制实验
"""
import numpy as np


class FirstOrderSystem:
    """
    一阶系统: τ * dy/dt + y = u
    
    参数:
        tau: 时间常数
        initial_value: 初始状态
    """
    
    def __init__(self, tau=1.0, initial_value=0.0):
        self.tau = tau
        self.state = initial_value
        self.history = [initial_value]
    
    def update(self, control_input, dt):
        """
        更新系统状态
        
        参数:
            control_input: 控制输入
            dt: 时间步长
        
        返回:
            当前系统输出
        """
        # 使用欧拉法求解微分方程
        dydt = (control_input - self.state) / self.tau
        self.state += dydt * dt
        self.history.append(self.state)
        return self.state
    
    def reset(self, initial_value=0.0):
        """重置系统状态"""
        self.state = initial_value
        self.history = [initial_value]


class SecondOrderSystem:
    """
    二阶系统: m * d²y/dt² + c * dy/dt + k * y = u
    
    参数:
        mass: 质量 (m)
        damping: 阻尼系数 (c)
        stiffness: 刚度系数 (k)
        initial_position: 初始位置
        initial_velocity: 初始速度
    """
    
    def __init__(self, mass=1.0, damping=0.5, stiffness=1.0, 
                 initial_position=0.0, initial_velocity=0.0):
        self.mass = mass
        self.damping = damping
        self.stiffness = stiffness
        
        self.position = initial_position
        self.velocity = initial_velocity
        self.history = [initial_position]
    
    def update(self, control_input, dt):
        """
        更新系统状态
        
        参数:
            control_input: 控制输入
            dt: 时间步长
        
        返回:
            当前系统输出 (位置)
        """
        # 计算加速度: a = (u - c*v - k*x) / m
        acceleration = (control_input - self.damping * self.velocity - 
                       self.stiffness * self.position) / self.mass
        
        # 更新速度和位置 (欧拉法)
        self.velocity += acceleration * dt
        self.position += self.velocity * dt
        
        self.history.append(self.position)
        return self.position
    
    def reset(self, initial_position=0.0, initial_velocity=0.0):
        """重置系统状态"""
        self.position = initial_position
        self.velocity = initial_velocity
        self.history = [initial_position]


class SystemWithNoise:
    """
    带噪声的系统包装器
    
    参数:
        base_system: 基础系统对象
        noise_std: 噪声标准差
    """
    
    def __init__(self, base_system, noise_std=0.0):
        self.base_system = base_system
        self.noise_std = noise_std
        self.history = []
    
    def update(self, control_input, dt):
        """更新系统并添加噪声"""
        clean_output = self.base_system.update(control_input, dt)
        noise = np.random.normal(0, self.noise_std)
        noisy_output = clean_output + noise
        self.history.append(noisy_output)
        return noisy_output
    
    def reset(self, *args, **kwargs):
        """重置系统"""
        self.base_system.reset(*args, **kwargs)
        self.history = []

