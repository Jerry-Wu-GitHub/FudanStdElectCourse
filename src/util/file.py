r"""
`file` library provides some general operations related to file.
"""

import os


def write_to_file(path, content:str, mode:str = "w", encoding:str = "utf-8") -> None:
    r"""
    将`content`内容写入`path`文件中。
    """

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, mode = mode, encoding = encoding) as file:
        file.write(content)


def get_size(path):
    r"""
    返回文件`path`的大小，单位为 Bytes 。
    """

    return os.stat(path).st_size
