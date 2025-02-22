r"""
class: Arrangement
"""

from config.constants import WEEKDAY_MAPPING, MAX_CLASSES_PER_DAY
from src.util.verify_parameters import type_verifier
from src.model.building import Building
from src.model.room import Room


class Arrangement():
    r"""
    课程安排类。

    ## 属性

    - `course: Course`：与此安排关联的`Course`实例。
    - `endUnit: int`：课程结束的节次，如`13`。
    - `isOnline: bool`：是否是在线教学，如`True`。
    - `nearestCanteen: Building|None`：距离这个安排的地点最近的食堂，如`Building('H本部食堂')`、`None`（对于在线教学）。
    - `rooms: list[Room]`：上课的教室，如`[Room('HGX507')]`、`[]`（对于在线教学）。
    - `roomsString: str`：教室的字符串表示，如`"HGX507"`、`"在线教学"`。
    - `startUnit: int`：课程开始的节次，如`11`。
    - `weekDay: int`：上课在星期几，`0`表示星期一，如`6`（表示星期日）。
    - `weekState: str`：若`weekState[n]`为`'1'`，表示在第`n`周有课，若`weekState[n]`为`'0'`，表示在第`n`周没课。如：`"01111111111111111000000000000000000000000000000000000"`。
    - `weekStateDigest: str`：以摘要的形式表示`weekState`，如`"1-16"`。
    - `weekStateDigit: int`：以二进制整型的形式表示`weekState`，如`4503530907893760`（即`0b01111111111111111000000000000000000000000000000000000`）。

    """

    # 可以从`arrangeJSON`原封不动赋过来的键值对的键
    unchangedJSONKeys = {
        "endUnit",
        "startUnit",
        "weekState",
        "weekStateDigest",
    }


    # `__init__`方法需要传入的参数名，就比`unchangedJSONKeys`多了一个`"roomsString"`
    initializationParameterNames = unchangedJSONKeys | {"roomsString"}


    @type_verifier
    def __init__(self, weekState:str, weekStateDigest:str, weekDay:int, startUnit:int, endUnit:int, roomsString:str):
        r"""
        将提供的参数作为属性来初始化。

        ## 参数

        - `endUnit: int`
        - `roomsString: str`
        - `startUnit: int`
        - `weekDay: int`
        - `weekState: str`
        - `weekStateDigest: str`
        """

        # 检查参数
        if startUnit < 1:
            raise ValueError(f"the first class is `1`, so you can't pass a `startUnit` (`{startUnit}`) less than `1`")
        if startUnit > endUnit:
            raise ValueError(f"the `endUnit` (`{endUnit}`) must't be earlier than the `startUnit` (`{startUnit}`)")
        if endUnit > MAX_CLASSES_PER_DAY:
            raise ValueError(f"the `endUnit` (`{endUnit}`) can't be greater than the maximum number of classes per day (`{MAX_CLASSES_PER_DAY}`)")

        # 获取教室信息、是否在线教学信息，如果是在线教学，则`rooms`为空列表`[]`
        if roomsString == "在线教学":
            self.rooms = [] # 没有上课教室
            self.isOnline = True # 是在线教学
            self.nearestCanteen = None
        else:
            # 解析`roomsString`信息为`Room`对象
            self.rooms = list(map(Room.fromString, roomsString.split(",")))
            self.isOnline = False # 不是在线教学
            self.nearestCanteen = self.rooms[0].nearestCanteen

        self.course = None

        # 将`weekState`以二进制形式转换为整数，方便在后续判断安排是否冲突时进行“按位与”运算
        self.weekStateDigit = int(weekState, 2)

        # 赋值
        self.endUnit = endUnit
        self.roomsString = roomsString
        self.startUnit = startUnit
        self.weekDay = weekDay
        self.weekState = weekState
        self.weekStateDigest = weekStateDigest


    def __hash__(self) -> int:
        return hash((self.weekState, self.weekDay, self.startUnit, self.endUnit, self.roomsString))


    def __getitem__(self, name: str) -> object:
        r"""
        索引取值。返回`self`的名为`name`的成员。

        ## 返回

        - 要取的值。

        ## 异常
        
        1. `TypeError`：如果`name`的类型不是字符串。
        2. `AttributeError`：如果`self`没有名为`name`的成员。
        """

        return getattr(self, name)


    def __setitem__(self, name: str, value: object):
        r"""
        索引设值。将`self`的`name`属性设为`value`。

        ## 返回

        - `None`。

        ## 异常

        - `TypeError`：如果`name`的类型不是字符串。
        """

        setattr(self, name, value)


    def __repr__(self) -> str:
        r"""
        返回对象的正式字符串表示，可用于重新创建该对象。

        ## 返回

        - `str`: 包含类名及初始化所需参数名称和值的字符串。

        ## 示例

        ```python
        "Arrangement(weekDay=5, startUnit=6, weekStateDigest='1-16', endUnit=10, roomsString='HGX507', weekState='01111111111111111000000000000000000000000000000000000')"
        ```
        """

        # 初始化对象所需要的参数名和值
        parameters = ", ".join(f"{para_name}={repr(self[para_name])}" for para_name in self.initializationParameterNames)

        return f"{type(self).__name__}({parameters})"


    def __str__(self) -> str:
        r"""
        返回对象的非正式字符串表示，提供简明信息。

        ## 返回
        - `str`: 格式化的字符串，包含周状态摘要、星期几、节次和房间信息或在线教学标识。

        ## 示例

        ```python
        "1-16周\n星期日 11-13节 在线教学"
        ```

        ```python
        "1-16周\n星期五 6-10节 HGX507"
        ```
        """

        # 星期几，汉字
        weekday = WEEKDAY_MAPPING[self.weekDay]

        return f"{self.weekStateDigest}周\n星期{weekday} {self.startUnit}-{self.endUnit}节 {self.roomsString}"


    def getTimeTuple(self) -> (int, int, int):
        r"""
        返回`(self.weekDay, self.startUnit, self.endUnit)`，作为该对象的时间元组，用于比较两个安排的时间先后。
        """

        return (self.weekDay, self.startUnit, self.endUnit)


    def getCourseString(self) -> str:
        r"""
        以字符串`"[课程序号]课程名[教室代码]"`的形式返回。
        """

        return f"{str(self.course)}[{self.roomsString}]"


    @classmethod
    def fromJSON(cls, arrangeJSON: dict[str, int|str]) -> "Arrangement":
        """
        根据给定的 JSON 数据（字典格式）创建并返回一个新的 `Arrangement` 实例。

        ## 参数

        - `arrangeJSON`（`dict[str, int|str]`）：包含课程安排信息的字典。

        ## 返回

        - `Arrangement`: 根据提供的数据创建的新 `Arrangement` 实例。

        ## 异常

        - `KeyError`: 如果输入字典缺少必要的键。
        - `TypeError`: 如果尝试将不正确的类型用于特定字段。
        
        ## 示例

        ```python
        arrange = Arrangement.fromJSON({
            "startUnit":6,
            "rooms":"HGX507,HGX508",
            "weekDay":5,
            "weekState":"01111111111111111000000000000000000000000000000000000",
            "weekStateDigest":"1-16",
            "endUnit":10
        })
        ```
        """
        attributes = {}

        attributes["roomsString"] = arrangeJSON["rooms"]
        attributes["weekDay"] = arrangeJSON["weekDay"] - 1

        # 直接赋值那些不用变的项目
        for name in cls.unchangedJSONKeys:
            attributes[name] = arrangeJSON[name]

        # 创建并返回实例
        return cls(**attributes)


    def toJSON(self) -> dict[str, int|str]:
        r"""
        将当前 `Arrangement` 实例的状态序列化为字典（可直接转换为 JSON 格式）。

        ## 返回

        - `dict[str, int|str]`：包含课程安排信息的字典。

        ## 示例

        ```python
        {
            "startUnit":6,
            "rooms":"HGX507,HGX508",
            "weekDay":5,
            "weekState":"01111111111111111000000000000000000000000000000000000",
            "weekStateDigest":"1-16",
            "endUnit":10
        }
        ```
        """

        arrangeJSON = {}

        arrangeJSON["rooms"] = self["roomsString"]
        arrangeJSON["weekDay"] = self["weekDay"] + 1

        # 直接赋值那些不用变的项目
        for name in self.unchangedJSONKeys:
            arrangeJSON[name] = self[name]

        return arrangeJSON


    def is_conflict_with(self, other:"Arrangement") -> bool:
        r"""
        检查当前课程安排是否与另一个课程安排存在时间冲突。
        
        时间冲突条件：
        - 两个课程安排在一周的同一天。
        - 两个课程的节次有交集（即开始和结束节次之间有重叠）。
        - 两个课程的上课周数有交集（通过位运算检查周状态摘要是否有共同的'1'）。
        
        ## 参数
        
        - `other` (`Arrangement`): 另一个课程安排对象。
        
        ## 返回

        - `bool`: 如果存在时间冲突返回 `True`，否则返回 `False`。
        """

        # 同时满足这三个条件：在一星期里的同一天，课程节次有交集，上课周数有交集
        return self.weekDay == other.weekDay and \
            not (self.endUnit < other.startUnit or other.endUnit < self.startUnit) and \
            self.weekStateDigit & other.weekStateDigit


    def commuteTime(self, other: "Arrangement|Room|Building") -> float:
        r"""
        从这个安排`self`的地点到另一个安排`other`的预期时间（单位：分钟）。

        假设整理东西离开教室，再找到并到达一个空教室要2分钟。
        """

        # 如果这个安排是在线教学的
        if self.isOnline:
            return 2

        # 如果`other`也是`Arrangement`类型
        if isinstance(other, type(self)):

            # 如果`other`是线上教学的
            if other.isOnline:
                return 2

            # 从教室到教室的时间，取第一间教室
            return self.rooms[0].commuteTime(other.rooms[0])

        # 如果`other`是`Room`或`Building`类型
        if isinstance(other, Room | Building):
            return self.rooms[0].commuteTime(other)
