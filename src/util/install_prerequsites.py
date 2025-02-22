r"""
自动安装所依赖的拓展库。
"""

from importlib import import_module
from os import system

from config.constants import REQUIRED_MODULES


def install_prerequsites(modules:dict[str, str] = REQUIRED_MODULES):
    r"""
    检查并安装指定的Python模块作为运行某些程序的先决条件。

    ## 参数

    - `modules`（`dict[str, str]`）：一个字典，包含需要检查或安装的模块信息。键是模块导入时使用的名称值是用于通过 pip 安装该模块时所用的名称。默认值是从 'config.constants' 模块中导入的 `REQUIRED_MODULES` 常量。

    ## 操作

    1. 遍历传入的 modules 字典。
    2. 尝试使用 Python 的 import_module 函数来导入（检查）每个模块。
    3. 如果模块未找到（引发 ModuleNotFoundError），则调用系统命令通过 pip 自动安装该模块。
        
    ## 输出

    对于每个需要安装的模块，函数将打印一条消息告知用户正在安装该模块，请稍候。
        
    ## 注意

    该函数使用`os.system`调用来执行`pip`安装命令，这意味着它依赖于系统的`pip`工具链和网络环境。在某些环境中，可能需要管理员权限才能成功安装软件包。
        
    ## 示例

    >>> install_prerequsites({'numpy': 'numpy', 'pandas': 'pandas>=1.0.0'})
    如果 numpy 已经安装，则不会有任何输出；如果 pandas 未安装，则会尝试通过 pip 安装之。
    """

    for (imported_name, installed_name) in modules.items():
        try:
            import_module(imported_name)
        except ModuleNotFoundError:
            print(f"Installing {imported_name}, please wait...\n")
            print("------------------------------------\n")
            system(f"pip3 install {installed_name}")
