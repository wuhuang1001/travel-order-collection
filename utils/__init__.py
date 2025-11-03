"""
工具包
提供各种通用工具函数
"""

# 导入工具函数
from .omgid import get_omgid
from .wsgsig import generate_wsgsig, get_wsgsig
from .tools import *

__all__ = [
    'get_omgid',
    'generate_wsgsig',
    'get_wsgsig'
]

__version__ = '1.0.0'