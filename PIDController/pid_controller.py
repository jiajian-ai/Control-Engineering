"""
PID控制器实现
包含完整的比例-积分-微分控制算法
"""
import numpy as np


class PIDController:
    """
    PID控制器类
    
    参数:
        Kp: 比例增益 (Proportional gain)
        Ki: 积分增益 (Integral gain)
        Kd: 微分增益 (Derivative gain)
        setpoint: 目标值
    """
    
    def __init__(self, Kp=1.0, Ki=0.0, Kd=0.0, setpoint=0.0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        
        # 内部状态变量
        self.integral = 0.0
        self.previous_error = 0.0
        self.output_limits = (-np.inf, np.inf)
        
        # 记录历史数据用于分析
        self.error_history = []
        self.output_history = []
        self.p_term_history = []
        self.i_term_history = []
        self.d_term_history = []
    
    def set_output_limits(self, min_output, max_output):
        """设置输出限制"""
        self.output_limits = (min_output, max_output)
    
    def reset(self):
        """重置控制器内部状态"""
        self.integral = 0.0
        self.previous_error = 0.0
        self.error_history = []
        self.output_history = []
        self.p_term_history = []
        self.i_term_history = []
        self.d_term_history = []
    
    def update(self, measured_value, dt):
        """
        更新PID控制器
        
        参数:
            measured_value: 当前测量值
            dt: 时间步长
        
        返回:
            控制输出值
        """
        # 计算误差
        error = self.setpoint - measured_value
        
        # 比例项 (P)
        p_term = self.Kp * error
        
        # 积分项 (I)
        self.integral += error * dt
        i_term = self.Ki * self.integral
        
        # 微分项 (D)
        if dt > 0:
            derivative = (error - self.previous_error) / dt
        else:
            derivative = 0.0
        d_term = self.Kd * derivative
        
        # 计算总输出
        output = p_term + i_term + d_term
        
        # 应用输出限制
        output = np.clip(output, self.output_limits[0], self.output_limits[1])
        
        # 更新历史记录
        self.error_history.append(error)
        self.output_history.append(output)
        self.p_term_history.append(p_term)
        self.i_term_history.append(i_term)
        self.d_term_history.append(d_term)
        
        # 更新状态
        self.previous_error = error
        
        return output
    
    def set_setpoint(self, setpoint):
        """设置新的目标值"""
        self.setpoint = setpoint
    
    def get_tuning_info(self):
        """返回当前调参信息"""
        return {
            'Kp': self.Kp,
            'Ki': self.Ki,
            'Kd': self.Kd,
            'setpoint': self.setpoint
        }

