"""
精简的美化输出模块 - 参考 sqlmap 风格
用于结构化的、简洁的命令行输出：
- 重要信息用颜色区分（仅蓝色和绿色）
- 过程信息保持简洁
- 异常捕获和简化输出
- 类似 sqlmap 的输出风格
"""

from rich.console import Console
from rich.style import Style
from typing import Optional, Any
import sys

# 创建 Console 实例（无花哨效果）
console = Console(highlight=False, soft_wrap=True)

# 定义简洁的样式
STYLE_SUCCESS = Style(color="green")      # 成功 - 绿色
STYLE_INFO = Style(color="blue")           # 信息 - 蓝色
STYLE_NORMAL = Style()                     # 正常 - 无色
STYLE_DIM = Style(dim=True)                # 暗化 - 用于过程信息


class SimpleOutput:
    """简洁的输出工具类（参考 sqlmap 风格）"""

    @staticmethod
    def success(message: str):
        """
        输出成功消息（绿色）
        
        Args:
            message: 要输出的消息
        """
        console.print(f"[+] {message}", style=STYLE_SUCCESS)

    @staticmethod
    def info(message: str):
        """
        输出信息消息（蓝色）
        
        Args:
            message: 要输出的消息
        """
        console.print(f"[*] {message}", style=STYLE_INFO)

    @staticmethod
    def verbose(message: str):
        """
        输出详细信息（暗化，用于过程信息）
        
        Args:
            message: 要输出的消息
        """
        console.print(f"[~] {message}", style=STYLE_DIM)

    @staticmethod
    def error(message: str):
        """
        输出错误消息（默认颜色，重要信息保留给用户）
        
        Args:
            message: 要输出的消息
        """
        console.print(f"[-] {message}")

    @staticmethod
    def normal(message: str):
        """
        输出普通消息（无特殊样式）
        
        Args:
            message: 要输出的消息
        """
        console.print(f"    {message}")

    @staticmethod
    def separator(char: str = "-", length: int = 50):
        """
        打印分隔符
        
        Args:
            char: 分隔符字符
            length: 长度
        """
        console.print(char * length)

    @staticmethod
    def print_dict(data: dict, title: Optional[str] = None):
        """
        简洁地打印字典信息
        
        Args:
            data: 要打印的字典
            title: 可选的标题
        """
        if title:
            SimpleOutput.info(title)
        
        for key, value in data.items():
            value_str = str(value)
            if len(value_str) > 60:
                value_str = value_str[:57] + "..."
            console.print(f"    {key}: {value_str}")

    @staticmethod
    def print_list(items: list, title: Optional[str] = None):
        """
        简洁地打印列表信息
        
        Args:
            items: 要打印的列表
            title: 可选的标题
        """
        if title:
            SimpleOutput.info(title)
        
        for idx, item in enumerate(items, 1):
            console.print(f"    {idx}. {item}")

    @staticmethod
    def section(title: str):
        """
        打印一个分隔符和标题
        
        Args:
            title: 部分标题
        """
        console.print("")
        console.print(f">> {title.upper()}")
        SimpleOutput.separator()

    @staticmethod
    def exception_brief(e: Exception):
        """
        打印简化的异常信息（仅显示异常类型和消息）
        
        Args:
            e: 异常对象
        """
        error_type = type(e).__name__
        error_msg = str(e) if str(e) else "(无错误信息)"
        
        if len(error_msg) > 100:
            error_msg = error_msg[:97] + "..."
        
        SimpleOutput.error(f"{error_type}: {error_msg}")


# 便捷函数别名
success = SimpleOutput.success
info = SimpleOutput.info
verbose = SimpleOutput.verbose
error = SimpleOutput.error
normal = SimpleOutput.normal
separator = SimpleOutput.separator
print_dict = SimpleOutput.print_dict
print_list = SimpleOutput.print_list
section = SimpleOutput.section
exception_brief = SimpleOutput.exception_brief
