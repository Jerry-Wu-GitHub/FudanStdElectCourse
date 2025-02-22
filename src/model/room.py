r"""
class: Room
"""

from importlib import import_module

from config.constants import BUILDING_CODES, DORMITORY_CODE
from src.model.building import Building

BUILDING_CODES = tuple(sorted(BUILDING_CODES, reverse = True))


class Room():
    r"""
    教室类。

    ## 属性

    - `campus: src.model.Campus.Campus`：教室所在的校区，如`Campus('H')`。
    - `code: str`：教室代码，如`"HGX507"`。
    - `building: src.model.Building.Building`：教室所在的楼，如`Building('HGX')`。
    - `floor: int`：楼层数，如`5`。
    - `nearestCanteen: Building`：距离这间教室最近的食堂，如`Building('H本部食堂')`。
    - `number: str`：房间序号，如`"07"`。
    """

    rooms = {}

    def __init__(self, code:str):
        r"""
        初始化。

        ## 参数

        - `code`（`str`）：教室的代码，如`"HGX507"`。
        """

        self.code = code
        self._parseCode(code)
        self.nearestCanteen = self.building.nearestCanteen


    def _parseCode(self, code:str) -> None:
        """
        解析教室代码以提取建筑、楼层和房间编号信息。

        ## 参数

        - `code`（`str`）：教室的代码字符串，例如 `"HGX507"`。

        ## 异常

        - `ValueError`：当无法识别教学楼或楼层时抛出。
        """
        index = 0

        # 提取楼层信息
        for building_code in BUILDING_CODES:
            if code.startswith(building_code):
                self.building = Building.getBuildings()[building_code]
                index += len(building_code)
                break
        else:
            # 没有找到预定义的教学楼
            raise ValueError(f"unknown building which this room belongs to: {code}")

        # 如果除了楼的信息还有别的信息，那就是楼层和序号了
        if len(code) > index:
            try:
                # 提取楼层信息
                self.floor = int(code[index])
            except ValueError as error:
                # 提取失败
                raise ValueError(f"unknown floor which this room is on: {code}") from error

            # 提取序号信息
            self.number = code[index + 1 : ]
        else:
            # 没有提供楼层和序号信息，那就用默认值
            self.floor = 1
            self.number = ""


    def __eq__(self, other:"Room") -> bool:
        return self.code == other.code


    def __hash__(self) -> int:
        return hash(self.code)


    def __repr__(self) -> str:
        return f"Room({repr(self.code)})"


    def __str__(self) -> str:
        return self.code


    @classmethod
    def fromString(cls, code:str) -> "Room":
        r"""
        根据给定的房间代码字符串创建并返回一个 `Room` 实例。如果实例已存在，则直接返回缓存的实例。

        ## 参数

        - `code`（`str`）：房间代码字符串，例如 `"HGX507"`。

        ## 返回

        - `Room`：对应于给定房间代码的新 `Room` 实例或从缓存中获取的现有实例。

        ## 缓存机制

        此方法使用内部字典 `Room.rooms` 来存储已经创建的 `Room` 实例以避免重复创建相同房间的实例。
        """

        # 如果已经创建过了该房间对象
        if code in cls.rooms:
            # 直接返回已经创建过了的实例
            return cls.rooms[code]

        # 创建实例
        room = cls(code)

        # 存储实例，避免重复创建
        cls.rooms[code] = room

        return room


    def commuteTime(self, other: "Arrangement|Room|Building") -> float:
        r"""
        从这间教室`self`到另一间教室`other`的预期时间（单位：分钟）。

        假设上下一层楼要15秒。

        假设收拾东西离开教室要1分钟。
        """

        # 如果`other`也是`Room`类型的
        if isinstance(other, type(self)):

            # 同一间教室
            if self == other:
                return 0

            # 同一栋楼
            if self.building == other.building:
                return abs(self.floor - other.floor) * 0.25 + 1

            # 不是同一栋楼
            return (self.floor + other.floor - 2) * 0.25 + 1 + self.building.commuteTime(other.building)

        # 如果`other`是`Building`类型的
        if isinstance(other, Building):

            # 下到一楼
            return (self.floor - 1) * 0.25 + 1 + self.building.commuteTime(other)

        # 如果`other`是`Arrangement`类型的
        Arrangement = import_module("src.model.arrangement").Arrangement
        if isinstance(other, Arrangement):
            return other.commuteTime(self)



# 添加寝室
Room.dormitory = Room.fromString(DORMITORY_CODE)
Room.rooms[DORMITORY_CODE] = Room.dormitory
