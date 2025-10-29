"""
MPC Controller Package
MPC控制器包

包含完整的模型预测控制器实现和实验代码。
Model Predictive Control - Advanced control method with optimization
"""

from .mpc_controller import MPCController, LinearMPCController, AdaptiveMPCController, cartpole_dynamics

__version__ = "1.0.0"
__author__ = "Control Engineering Lab"

__all__ = [
    'MPCController',
    'LinearMPCController',
    'AdaptiveMPCController',
    'cartpole_dynamics',
]

