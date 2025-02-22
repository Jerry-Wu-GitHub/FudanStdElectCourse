r"""
class: Campus
"""

from config.constants import CAMPUS_CODES
from config.constants import CAMPUS_NAMES, CAMPUS_COMMUTE_TIMES


class Campus():
    r"""
    复旦大学的校区。

    ## 实例属性

    - `code: str`：校区代码，如`"H"`。
    - `name: str`：校区名，如`"邯郸校区"`。

    ## 类属性

    - `campuses: dict[str, Campus]`：存储了复旦大学的四个校区，以`code:Campus实例`对的形式存储。
    """

    def __init__(self, code:str):
        r"""
        根据校区代码初始化校区实例。

        ## 参数

        - `code: str`：校区代码，必须是预定义代码 `"H"`、`"J"`、`"F"`、`"Z"` 之一。
        
        ## 异常

        - `ValueError`: 当提供的代码未被识别时抛出。
        """

        if code not in CAMPUS_CODES:
            raise ValueError(f"unknown campus code: {code}")

        self.code = code
        self.name = CAMPUS_NAMES[code]


    def __hash__(self) -> int:
        return hash(self.code)


    def __eq__(self, other: "Campus") -> bool:
        return self.code == other.code


    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.code)})"


    def __str__(self) -> str:
        return f"{self.code}{self.name}"


    def commuteTime(self, other: "Campus") -> int:
        r"""
        从`self`校区到`other`校区乘校车的通勤时间，单位：分钟。

        ## 注意

        - 这只是预测时间，可能不准确。
        """

        if self == other:
            return 0
        return CAMPUS_COMMUTE_TIMES[(self.code, other.code)]



# 复旦大学所有的校区
Campus.campuses = {code: Campus(code) for code in CAMPUS_CODES}
