"""
PID Controller Package
PID控制器包

包含完整的PID控制器实现和实验代码。
"""

from .pid_controller import PIDController
from .simulated_system import FirstOrderSystem, SecondOrderSystem, SystemWithNoise

__version__ = "1.1.0"
__author__ = "Control Engineering Lab"

__all__ = [
    'PIDController',
    'FirstOrderSystem',
    'SecondOrderSystem',
    'SystemWithNoise',
]

