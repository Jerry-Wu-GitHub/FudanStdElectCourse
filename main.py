r"""
主程序
"""

from src.util.install_prerequsites import install_prerequsites

try:
    install_prerequsites()
except BaseException as error:
    print(f"安装依赖的拓展库失败，可能需要管理员权限，错误信息：{type(error).__name__}: {str(error)}")


from src.core.arrange_schedule import arrange_schedule


try:
    install_prerequsites()
    arrange_schedule()
except BaseException as error:
    print(f"出错了，错误信息：{type(error).__name__}: {str(error)}")

input()
