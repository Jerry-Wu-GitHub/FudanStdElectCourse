r"""
该模块提供了对日志的操作。
"""

import os
import time

from config.constants import LOG_PATH, STR_TIME_FORMAT


def get_str_time() -> str:
    r"""
    获取当前时间并格式化为特定字符串格式。

    此函数调用`time.localtime()`获取当前的本地时间，并使用预定义的时间格式`STR_TIME_FORMAT`，通过`time.strftime()`将其格式化为一个字符串形式的时间表达式返回。

    ## 参数
    
    无。
    
    ## 返回

    - `str`：格式化后的当前时间字符串，格式为`config.constants.STR_TIME_FORMAT`。

    ## 示例
    
    >>> print(get_str_time())
    2025-02-14 21:40:39
    """

    now = time.localtime()
    return time.strftime(STR_TIME_FORMAT, now)


def log(message:str) -> None:
    r"""
    记录消息到指定的日志文件中，并在消息前添加当前时间戳。

    此函数将传入的消息追加到由`LOG_PATH`指定的日志文件中，并在每条消息前添加一个时间。
    时间通过`get_str_time()`函数获取。

    ## 参数

    - `message`（`str`）：要记录的消息内容。

    ## 返回

    - `None`。
        
    ## 注意
    
    - 确保`LOG_PATH`指向有效的文件路径，并且程序有权限在此路径下创建或写入文件。

    ## 示例

    >>> log("这是一个测试消息。")
    # 这将在LOG_PATH指向的日志文件中添加一行如下：
    # [2025-02-14 21:44:02]这是一个测试消息。
    """

    # 保证文件的目录存在
    if os.path.isfile(LOG_PATH):
        mode = "a"
    else:
        mode = "w"
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    # 写入文件
    with open(LOG_PATH, mode = mode, encoding = "utf-8") as file:
        file.write(f"[{get_str_time()}]{message}\n")

    # 输出到标准输出
    print(message)


def clear() -> None:
    r"""
    清除指定的日志文件内容。

    如果由`LOG_PATH`指定的日志文件存在，则通过以写模式（'w'）打开该文件来清空其内容。
    若该文件不存在，则抛出`FileNotFoundError`异常。

    ## 参数

    无。

    ## 返回

    - `None`：此函数没有返回值。

    ## 异常
    
    - `FileNotFoundError`：如果`LOG_PATH`指向的文件不存在，则会抛出此异常，提示用户日志文件无法找到。

    ## 注意
        
    - 请确保程序有权限对指定路径下的文件执行写入操作。

    ## 示例

    >>> clear()
    # 如果"logfile.log"存在，它的内容将被清空。
    # 如果"logfile.log"不存在，则会抛出类似以下的异常：
    # FileNotFoundError: path/to/your/logfile.log
    """

    if os.path.isfile(LOG_PATH):
        with open(LOG_PATH, mode = "w", encoding = "utf-8"):
            pass
    else:
        raise FileNotFoundError(LOG_PATH)
