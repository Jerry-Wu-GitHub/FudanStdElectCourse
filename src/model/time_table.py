r"""
class: TimeTable
"""

import csv
from math import prod
from functools import cache

from scipy.stats import gmean

from config.constants import COURSES_COUNT, MAX_CLASSES_PER_DAY
from config.constants import COURSE_TIME, TABLE_HEADING
from config.user import COMMUTE_TIME_WEIGHT, COURSE_SCORE_WEIGHT
from src.model.course_group import CourseGroup
from src.model.arrangement import Arrangement
from src.model.course import Course
from src.model.room import Room


class TimeTable(CourseGroup):
    r"""
    课程表类。

    ## 属性

    - `courses: list[Course]`：包含这个课程表中的课程的列表。
    - `isConflict: bool`：该课程表里的课程有没有冲突。
    - `limitedCoursesCount: dict[str, int]`：某一数量受限制的类型（键，正则表达式）的课的数量（值）。
    - `probability: float`：当前选上该课表的可能性。
    """

    def __init__(self, courses:list[Course]|None = None):
        """
        初始化一个新的课程表实例。

        初始化过程中会自动检查课程之间的冲突，并更新`isConflict`属性。

        ## 参数

        - `courses`（`list[Course]`，可选）：一个`Course`对象的列表，默认为`None`，此时将初始化一个空的课程列表。
        """

        CourseGroup.__init__(self, courses)


    @property
    def probability(self) -> float:
        r"""
        当前选上该课表的可能性。
        """

        return prod(course.probability for course in self.courses)


    def toArrangementTable(self) -> list[list[Arrangement|None]]:
        r"""
        将`TimeTable`对象转换为安排表。

        返回一个二维表格，代表一周的课程安排。每个有效元素是课程的具体安排（`Arrangement`对象），无效元素为`None`用于占位。
        
        表格格式：
        - 星期一对应索引`0`，第一节课对应索引`0`。
        - `arrangementTable[n][m]`表示星期`n+1`第`m+1`节课的安排。
        
        ## 返回

        - `list[list[Arrangement|None]]`：二维列表形式的课程安排表。

        ## 注意

        - 如果该课表的课在安排时间上有冲突，可能导致生成的表格上的某些单元格被意外覆盖。
        """

        # 创建空表格，全是`None`
        arrangementTable = [
            [None] * MAX_CLASSES_PER_DAY for _ in range(7)
        ]

        # 遍历每一个安排
        for course in self.courses:
            for arrangement in course.arrangements:
                # 将这个安排填入表格的相应位置
                for unit in range(arrangement.startUnit - 1, arrangement.endUnit):
                    arrangementTable[arrangement.weekDay][unit] = arrangement

        # 返回表格
        return arrangementTable


    def toStringTable(self) -> list[list[""]]:
        r"""
        将课程表转换为字符串形式的安排表。

        返回一个二维表格，其中包含课程信息的字符串。没有安排的单元格内容为空字符串。
        每个课程的字符串格式为`"[课程序号]课程名[教室代码]"`。
        
        表格格式：
        - 星期一对应索引`0`，第一节课对应索引`0`。
        - `stringTable[n][m]`表示星期`n+1`第`m+1`节课的信息。
        
        ## 返回

        - `list[list[str]]`：二维列表形式的字符串化课程安排表，未安排课程的位置为空字符串。

        ## 注意

        - 如果该课表的课在安排时间上有冲突，可能导致生成的表格上的某些单元格被意外覆盖。
        """

        # 创建空表格，全是空字符串
        stringTable = [
            [""] * MAX_CLASSES_PER_DAY for _ in range(7)
        ]

        # 遍历每一个安排
        for course in self.courses:
            for arrangement in course.arrangements:
                # 将这个安排的`"[课程序号]课程名[教室代码]"`形式的字符串填入表格的相应位置
                for unit in range(arrangement.startUnit - 1, arrangement.endUnit):
                    stringTable[arrangement.weekDay][unit] = arrangement.getCourseString()

        # 返回表格
        return stringTable


    def toCsv(self, path, mode:str = 'a', newline:str = '') -> None:
        """
        将课程表导出为 CSV 文件。

        表格格式：
        - 转置后的表格，其中每一列对应一周中的某一天（周一至周日）。
        - 第一行为表头信息（来自`TABLE_HEADING`），接下来的每一行对应一天中的某一节课时段，包含时间段（来自`COURSE_TIME`）和该时段对应的课程信息（如果有）。

        ## 参数

        - `path`（`str）：CSV文件的保存路径。
        - `mode`（`str`，可选）：文件打开模式（默认为追加模式`'a'`）。
        - `newline`（`str`，可选）：指定在换行时应使用的换行符（默认为空字符串`''`，适用于不同操作系统间的兼容性）。

        ## 注意

        - 该方法依赖于`toStringTable`方法生成的二维字符串列表来构建内容。
        """

        # 将字符串表格转置，这样表格的一列就对应一个 weekday
        csvTableBody = list(zip(*self.toStringTable()))

        # 初始化内容列表，首先添加表头
        content = [
            [
                f"通勤时间：{round(self.getCommuteTime())}", "",
                f"课程得分：{round(self.getCourseScore(), 3)}", "",
                f"综合得分：{round(self.getScore(), 3)}", "",
            ],
            TABLE_HEADING,
        ]

        # 遍历每个上课时段，构建每行的内容
        for unit in range(MAX_CLASSES_PER_DAY):
            # 合并时段与对应星期的课程信息
            content.append(COURSE_TIME[unit] + list(csvTableBody[unit]))

        # 表格最后下面加个空行
        content.append([])

        # 写入到指定路径的CSV文件中
        with open(path, mode = mode, newline = newline, encoding = "gbk") as file:
            writer = csv.writer(file)
            writer.writerows(content)


    @cache
    def getCommuteTime(self) -> float:
        r"""
        返回该课程表预期的一周通勤时间（`float`，以分钟为单位）。

        遍历一周中每一天的课程安排，计算从寝室出发到各上课地点、食堂以及最终返回寝室的总通勤时间。

        对于每一天：
        - 从寝室开始，前往最近的食堂吃早餐。
        - 遍历当天的每节课安排，如果是实体课则计算到教室的通勤时间，并在上午或下午课程结束后去最近的食堂用餐。
        - 一天的课程全部结束后，计算从最后一处地点返回寝室的通勤时间。
        """

        # 记录总通勤时间
        commuteTime = 0

        # 遍历每一天的安排
        for weekdayArrangements in self.toArrangementTable():
            # 从寝室出发
            last = Room.dormitory

            # 先找好最近的食堂
            nearestCanteen = last.nearestCanteen

            # 去食堂吃早饭
            commuteTime += last.commuteTime(nearestCanteen)
            last = nearestCanteen

            # 遍历当天的每一个安排
            for (slot, arrangement) in enumerate(weekdayArrangements, start = 1):
                # 这里第一节课对应的`slot`等于`1`

                # 如果这节课有安排（要上课）
                if arrangement: # 如果`arrangement`不是`None`

                    # 计算从`last`（上一个地方）到`arrangement`的通勤时间
                    commuteTime += last.commuteTime(arrangement)

                    # 找到最近的食堂
                    if not arrangement.isOnline:
                        nearestCanteen = arrangement.nearestCanteen

                    last = arrangement

                # 如果这节课是上午或下午的最后一节课
                if slot in (
                    COURSES_COUNT["morning"],
                    COURSES_COUNT["morning"] + COURSES_COUNT["afternoon"]
                ):

                    # 去食堂吃午/晚饭
                    commuteTime += last.commuteTime(nearestCanteen)
                    last = nearestCanteen

            # 一天的课结束了，该回寝室了
            commuteTime += last.commuteTime(Room.dormitory)

        # 返回一周的总通勤时间（分钟）
        return commuteTime


    @cache
    def getCourseScore(self) -> float:
        r"""
        计算这个课程表的课程的得分。

        将这个课程表内所有课程的得分按照学分进行加权，计算几何平均。
        """

        return gmean(
            [course.score for course in self.courses],
            weights = [course.credits for course in self.courses]
        )


    def getScore(self, *, commuteTimeWeight:float = COMMUTE_TIME_WEIGHT, courseScoreWeight:float = COURSE_SCORE_WEIGHT) -> float:
        r"""
        返回这个课程表的综合得分。

        ## 参数

        - `commuteTimeWeight`：通勤时间所占的权重，默认为`1.0`。
        - `courseScoreWeight`：课程得分所占的权重，默认为`1.0`。

        ## 计算公式

        记通勤时间（单位：小时）为 $t$ ，课程得分为 $s$ ，通勤时间所占的权重为 $w_t$ ，课程得分所占的权重为 $w_s$ ，则返回

        $$
        {((\frac{1}{t})^{w_t} \times {s}^{w_s})} ^ {\frac{1}{w_t + w_s}}
        $$
        """

        return gmean(
            (1 / self.getCommuteTime() * 60, self.getCourseScore()),
            weights = (commuteTimeWeight, courseScoreWeight)
        )
