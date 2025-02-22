r"""
class: ExamTime
"""

from re import search
from datetime import datetime

from config.constants import EXAM_START_WEEK, EXAM_END_WEEK
from config.constants import WEEKDAY_MAPPING
from src.util.verify_parameters import type_verifier
from src.model.datetime_duration import TimeDuration


class ExamTime(TimeDuration):
    r"""
    期末考试时间类。

    ## 示例

    >>> string = "2025-06-13 15:30-17:30 第17周 星期五"
    >>> examTime = ExamTime.fromString(string)
    >>> print(examTime)
    2025-06-13 15:30-17:30 第17周 星期五
    >>> print(repr(examTime))
    ExamTime(datetime.datetime(2025, 6, 13, 15, 30), datetime.datetime(2025, 6, 13, 17, 30), 17, 4)
    """

    @type_verifier
    def __init__(self, start:datetime|None = None, end:datetime|None = None, week:int|None = None, weekday:int|None = None):
        r"""
        初始化考试时间对象。

        ## 参数

        - `start`（`datetime|None`）：考试开始时间。默认为`None`。
        - `end`（`datetime|None`）：考试结束时间。默认为`None`。
        - `week`（`int|None`）：考试所在的学期周次。默认为`None`。
        - `weekday`（`int|None`）：考试所在周的星期几（0 表示周一）。默认为`None`。

        ## 注意

        - 如果仅设置了`start`或`end`其中之一，则该值会被同时赋给`start`和`end`。
        - `week`应为非负值，表示学期中的第几周。默认第一周为第`1`周。
        - `weekday`：使用整数表示星期几，默认`0`表示周一。

        ## 异常

        - `ValueError`：如果`week`小于`0`。

        ## 警告

        - 如果考试安排在早于通常开始周次（`EXAM_START_WEEK`）的周。
        - 如果考试安排在晚于通常结束周次（`EXAM_END_WEEK`）的周。
        """

        # 检查参数`week`
        if week is not None:
            self._checkExamWeek(week)

        # 补全参数`start`、`end`
        if bool(start) + bool(end) == 1:
            start = end = start or end

        self.week = week
        self.weekday = weekday

        if start and end:
            TimeDuration.__init__(self, start, end, timeFormat = r"%H:%M")
        else:
            self.start = start
            self.end = end


    def __hash__(self) -> int:
        return hash((self.start, self.end))


    def __repr__(self) -> str:
        r"""
        返回一个表示`ExamTime`对象的字符串，该字符串可以用来重新创建这个对象。

        ## 返回

        - `str`：包含类名和所有参数值的字符串表示形式。

        ## 示例

        ```python
        "ExamTime(datetime.datetime(2025, 6, 13, 15, 30), datetime.datetime(2025, 6, 13, 17, 30), 17, 4)"
        ```
        """

        # 构造该对象所需的参数的值
        paramValues = map(repr, (self.start, self.end, self.week, self.weekday))

        # 构造该对象的字符串
        return f"{type(self).__name__}({', '.join(paramValues)})"


    def __str__(self) -> str:
        r"""
        提供`ExamTime`对象的可读字符串表示，包括考试的时间、学期周次及星期几的信息。

        ## 返回

        - `str`：根据对象属性组合而成的可读字符串，包含开始时间、结束时间、学期周次和星期几（如果已设置）。

        ## 示例

        ```python
        2025-06-13 15:30-17:30 第17周 星期五
        ```
        """

        stringInfo = []

        # 时间信息，例如：`"2025-06-13 15:30-17:30"`
        if self.start and self.end:
            stringInfo.append(self.strftime())

        # 周次信息，例如：`"第17周"`
        if self.week is not None:
            stringInfo.append(f"第{self.week}周")

        # 星期信息，例如：`"星期五"`
        if self.weekday is not None:
            stringInfo.append(f"星期{WEEKDAY_MAPPING[self.weekday]}")

        # 以空格分隔
        return " ".join(stringInfo)


    @staticmethod
    def _checkExamWeek(week:int) -> None:
        r"""
        检查考试周次的合法性与合理性。

        ## 参数

        - `week`（int）：要检查的考试周次。

        ## 异常

        - `ValueError`：如果`week`小于`0`。

        ## 警告

        - 如果考试安排在早于`config.constants.EXAM_START_WEEK`的周次。
        - 如果考试安排在晚于`config.constants.EXAM_END_WEEK`的周次。
        """

        # 检查参数`week`的合法性
        if week < 0:
            raise ValueError("`week` is at least `0`.")

        # 检查参数`week`的合理性
        if week < EXAM_START_WEEK:
            print(f"Warning: The exam in the {week}th week may be too early. Generally, exams are held at {EXAM_START_WEEK}th week or later.")
        elif week > EXAM_END_WEEK:
            print(f"Warning: The exam in the {week}th week may be too late. Generally, exams are held at {EXAM_END_WEEK}th week or earlier.")


    @classmethod
    def fromString(cls, string:str = "") -> "ExamTime":
        r"""
        从给定的字符串解析出一个 `ExamTime` 对象。

        支持的字符串格式包括：
        - 空字符串：""。
        - 完整的时间信息字符串，例如："2025-06-17 08:30-10:30 第18周 星期二"。

        ## 参数

        - `string`（str）：需要解析的字符串。默认为`""`。

        ## 返回

        - `ExamTime`：解析后生成的 `ExamTime` 对象。

        ## 异常

        - `ValueError`：如果传入的字符串格式不正确或无法匹配预期模式。
        """

        # 处理空字符串的情况
        if string == "":
            return ExamTime()

        # 定义日期时间的正则表达式模式
        datetimePattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}-\d{2}:\d{2}"

        # 根据`config.constants.WEEKDAY_MAPPING`构建中文星期几的字符集
        weekdayNames = "".join(name for name in WEEKDAY_MAPPING if isinstance(name, str))

        # 构造完整的正则表达式模式
        pattern = fr"(?P<datetimeInfo>{datetimePattern}) 第(?P<weekInfo>\d{{1,2}})周 星期(?P<weekdayInfo>[{weekdayNames}])"

        # 使用正则表达式搜索输入字符串
        match = search(pattern, string)
        if not match:
            raise ValueError(f"failed to parse `string`: {string}")

        # 解析日期时间信息
        timeDuration = TimeDuration.strptime(match["datetimeInfo"], timeFormat = r"%H:%M", simplified = True)
        start = timeDuration.start
        end = timeDuration.end

        # 解析周次的信息
        week = int(match["weekInfo"])

        # 解析星期几的信息
        weekday = WEEKDAY_MAPPING[match["weekdayInfo"]]

        # 返回新的 ExamTime 实例
        return ExamTime(start=start, end=end, week=week, weekday=weekday)


    def is_conflict_with(self, other: "ExamTime") -> bool:
        """
        检查当前考试时间是否与另一个考试时间 `other` 发生冲突。

        ## 参数

        `other`（ExamTime）：另一个 `ExamTime` 实例，用于比较是否存在时间冲突。

        ## 返回

        - `bool`：
            - `True`如果存在时间冲突。
            - `False`：如果双方时间不冲突，或者有任何一方缺少开始或结束时间。
        """

        # 仅当两个考试时间段都有明确的开始和结束时间时，才进行冲突检查
        if self.start and self.end and other.start and other.end:
            # 调用`TimeDuration`类的方法来检查时间冲突
            return TimeDuration.is_conflict_with(self, other)

        # 如果有任何一方缺少开始或结束时间，则默认认为不冲突
        return False
