r"""
class: Building
"""

from importlib import import_module

from config.constants import CANTEEN_CODES, TEACHING_BUILDING_CODES, DORMITORY_BUILDING_CODES, BUILDING_CODES
from config.constants import BUILDING_NAMES, BUILDING_LOCATIONS
from src.util.geography import degrees_to_meters
from src.model.campus import Campus


class Building():
    r"""
    复旦大学的楼。

    ## 实例属性

    - `code: str`：楼的代码。
    - `isCanteen: bool`（只读）：这栋楼是否是食堂。
    - `isDormitoryBuilding: bool`（只读）：这栋楼是否是宿舍楼。
    - `isTeachingBuilding: bool`（只读）：这栋楼是否是教学楼。
    - `name: str`：楼的名称。
    - `nearestCanteen: Building`：距离这栋楼最近的食堂，如`Building('H本部食堂')`。
    - `location: (float, float)`：`(经度, 纬度)`，楼的正门的经纬度。

    ## 类属性

    - `buildings: dict[str:Building]`（只读）：存储了复旦大学的一些楼，以`code:Building实例`对的形式储存。
    - `canteens: dict[str:Building]`：存储了复旦大学的食堂，以`code:Building实例`对的形式储存。
    - `dormitoryBuildings: dict[str:Building]`：存储了复旦大学的宿舍楼，以`code:Building实例`对的形式储存。
    - `teachingBuildings: dict[str:Building]`：存储了复旦大学的教学楼，以`code:Building实例`对的形式储存。
    """

    canteens = {}
    teachingBuildings = {}
    dormitoryBuildings = {}

    def __init__(self, code:str):
        r"""
        根据建筑代码初始化`Building`实例。

        ## 参数:

        - `code: str`：建筑代码，必须是预定义代码之一。
        
        ## 异常:

        - `ValueError`: 当提供的代码未被识别时抛出。
        """

        if code not in BUILDING_CODES:
            raise ValueError(f"unknown building code: {code}")
        if code[0] not in Campus.campuses:
            raise ValueError(f"unknown campus which this building belongs to: {code}")

        self.code = code
        self.campus = Campus.campuses[code[0]]
        self.name = BUILDING_NAMES[code]
        self.location = BUILDING_LOCATIONS[code]

        # 检查楼的类型
        if self.isCanteen:
            # 离这栋楼最近的食堂
            self.nearestCanteen = self
        else:
            # 离这栋楼最近的食堂
            self.nearestCanteen = min(Building.canteens.values(), key = self.manhattanDistance)


    def __eq__(self, other):
        return self.code == other.code


    def __hash__(self):
        return hash(self.code)


    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.code)})"


    def __str__(self) -> str:
        return f"{self.name}"


    @property
    def isCanteen(self) -> bool:
        r"""
        返回这栋楼是不是食堂。
        """

        return self.code in CANTEEN_CODES


    @property
    def isTeachingBuilding(self) -> bool:
        r"""
        返回这栋楼是否是教学楼。
        """

        return self.code in TEACHING_BUILDING_CODES


    @property
    def isDormitoryBuilding(self) -> bool:
        r"""
        返回这栋楼是否是寝室楼。
        """

        return self.code in DORMITORY_BUILDING_CODES


    @classmethod
    def getBuildings(cls) -> dict[str, "Building"]:
        r"""
        返回已创建的所有楼对象。
        """

        return cls.canteens | cls.teachingBuildings | cls.dormitoryBuildings


    @classmethod
    def fromCode(cls, code) -> "Building":
        r"""
        从`code`创建`Building`实例。

        如果之前已经用相同的`code`创建过了，就直接返回已经创建的。
        """

        # 检查是否已经创建了该实例
        if code in cls.getBuildings():
            return cls.getBuildings()[code]

        # 创建新实例
        building = Building(code)

        # 给对象分类
        if building.isCanteen:
            cls.canteens[code] = building
        elif building.isTeachingBuilding:
            cls.teachingBuildings[code] = building
        elif building.isDormitoryBuilding:
            cls.dormitoryBuildings[code] = building

        # 返回新创建的对象
        return building


    def manhattanDistance(self, other: "Building") -> float:
        r"""
        计算与另一栋楼的曼哈顿距离。

        ## 参数

        - `other: Building`：另一个 `Building` 实例。

        ## 返回

        - `float`：两栋楼之间的曼哈顿距离，单位为米。
        """

        return sum(degrees_to_meters(*self.location, *other.location))


    def commuteTime(self, other: "Building") -> float:
        r"""
        从这栋楼到另一栋楼`other`的预期时间。

        假设骑自行车的最快速度为 150m/min，距离越长速度越快。

        假设取自行车和停自行车共要1分钟。
        """

        # 如果`other`也是`Building`类型的
        if isinstance(other, type(self)):

            # 从校区到校区的通勤时间
            if self.campus != other.campus:
                return self.campus.commuteTime(other.campus)

            # 在同一个校区里通勤
            distance = self.manhattanDistance(other)
            if distance <= 100: # 如果距离小于100米就步行
                # 步行速度约 60m/min
                return distance / 60
            return distance/150 - 12/(distance/100 + 3) + 4 + 1

        # 如果`other`是`Room`或`Arrangement`类型
        Room = import_module("src.model.room").Room
        Arrangement = import_module("src.model.arrangement").Arrangement
        if isinstance(other, Room | Arrangement):
            return other.commuteTime(self)



# 创建复旦大学的食堂
for code in CANTEEN_CODES:
    Building.fromCode(code)

# 创建复旦大学的教学楼
for code in TEACHING_BUILDING_CODES:
    Building.fromCode(code)

# 创建复旦大学的寝室楼
for code in DORMITORY_BUILDING_CODES:
    Building.fromCode(code)
