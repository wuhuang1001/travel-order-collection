"""
网络层包
负责处理所有网络请求相关的功能
"""

# 导入主要的类，方便外部使用
from .login import LoginRequest
from .history import GetHistoryList, GetHistoryDetail

__all__ = [
    'LoginRequest',
    'GetHistoryList', 
    'GetHistoryDetail',
]

__version__ = '1.0.0'