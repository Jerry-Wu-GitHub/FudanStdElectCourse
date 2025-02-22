r"""
与时间有关的类。
"""

from datetime import date, datetime
from re import finditer

from src.util.verify_parameters import type_verifier


class DateDuration():
    r"""
    日期段类用于表示和操作一个由开始日期和结束日期定义的日期段。

    ## 属性

    - `start: date`：时间段的开始日期。
    - `end: date`：时间段的结束日期。
    - `dateFormat: str`：日期格式化字符串，默认为`"%Y-%m-%d"`，用于定义日期对象如何被格式化成字符串。
    
    ## 示例

    ```python
    >>> from datetime import date
    >>> date_duration = DateDuration(date(2025, 1, 1), date(2025, 12, 31))
    >>> print(date_duration.start)
    2025-01-01
    ```
    """

    @type_verifier
    def __init__(self, start:date, end:date, dateFormat:str = r"%Y-%m-%d"):
        r"""
        初始化`DateDuration`实例。

        ## 参数

        - `start`（`date`）：时间段的开始日期。必须小于或等于结束日期。
        - `end`（`date`）：时间段的结束日期。必须大于或等于开始日期。
        - `dateFormat`（`str`，可选）：日期格式化字符串。默认是`"%Y-%m-%d"`。
        
        ## 异常

        - `ValueError`：如果开始日期晚于结束日期。
        """

        # 确保开始时间在结束时间之前
        if start > end:
            raise ValueError(f"`start` ({start}) cannot be later than `end` ({end})")

        # 给属性赋值
        self.start = start
        self.end = end
        self.dateFormat = dateFormat


    def __repr__(self):
        parameters = ", ".join((f"{para_name}={repr(value)}" for (para_name, value) in self.__dict__.items()))
        return f"{type(self).__name__}({parameters})"


    def __str__(self):
        r"""
        返回`self.strftime()`。
        """

        return self.strftime()


    def __hash__(self) -> int:
        return hash((self.start, self.end, self.dateFormat))


    @type_verifier
    def strftime(self, dateFormat:str|None = None) -> str:
        r"""
        根据指定或默认的日期格式，生成日期段的字符串表示。

        ## 参数

        - `dateFormat`（`str|None`，可选）：用于日期部分格式化的字符串。如果未提供，则使用实例化时设置的日期格式。

        ## 返回

        - `str`：日期段的字符串表示，格式为`"开始日期 ~ 结束日期"`。
        
        ## 示例
        
        ```python
        >>> from datetime import date
        >>> startDate = date(2025, 2, 15)
        >>> endDate = date(2025, 2, 16)
        >>> duration = DateDuration(startTime, endTime)
        >>> print(duration.strftime())
        2025-02-15 ~ 2025-02-16
        ```
        """

        # 补全参数
        if dateFormat is None:
            dateFormat = self.dateFormat

        # 生成开始日期的字符串和结束日期的字符串
        startDateString = self.start.strftime(dateFormat)
        endDateString = self.end.strftime(dateFormat)

        return f"{startDateString} ~ {endDateString}"


    @staticmethod
    @type_verifier
    def strptime(string: str, dateFormat: str = r"%Y-%m-%d") -> "DateDuration":
        """
        将包含两个日期（开始和结束）的字符串转换为`DateDuration`对象。

        ## 参数

        - `string`（`str`）：包含按照`dateFormat`格式的开始和结束日期的字符串。
        - `dateFormat`（`str`，可选）：日期格式化字符串，默认是`"%Y-%m-%d"`。支持`%Y`、`%m`和`%d`的模式来表示年、月和日。

        ## 返回

        - `DateDuration`：一个基于解析出的开始和结束日期的新实例。

        ## 注意

        - 字符串中的日期必须与提供的`dateFormat`相匹配。
        - 目前实现假设字符串中仅包含两个日期，并且这两个日期是按顺序给出的（即先开始日期后结束日期）。

        ## 示例

        ```python
        >>> date_duration = strptime("2025-01-01 ~ 2025-12-31")
        >>> print(date_duration.start)
        2025-01-01
        ```
        """

        # 构建正则表达式模式，用于提取年、月、日
        pattern = dateFormat.replace(r"%Y", r"(?P<Y>\d{1,4})") \
                            .replace(r"%m", r"(?P<m>\d{1,2})") \
                            .replace(r"%d", r"(?P<d>\d{1,2})")

        # 查找字符串中与模式匹配的所有日期
        matches = tuple(finditer(pattern, string))

        # 提取并创建开始和结束日期对象
        start = date(*(int(matches[0].group(name)) for name in ("Y", "m", "d")))
        end = date(*(int(matches[1].group(name)) for name in ("Y", "m", "d")))

        # 返回新的 DateDuration 实例
        return DateDuration(start=start, end=end, dateFormat=dateFormat)


    def is_conflict_with(self, other:"DateDuration") -> bool:
        """
        判断当前时间段是否与另一个时间段有冲突（即存在重叠）。

        ## 参数

        - `other`（`DateDuration`）：另一个时间段实例。

        ## 返回

        - `bool`：如果两个时间段存在重叠，则返回`True`；否则返回`False`。
        """

        # 当前时间段的结束时间大于另一个时间段的开始时间，且另一个时间段的结束时间大于当前时间段的开始时间，则表示两个时间段存在重叠
        return not (self.end <= other.start or other.end <= self.start)


class TimeDuration(DateDuration):
    r"""
    时间段类。
    """

    @type_verifier
    def __init__(self, start:datetime, end:datetime, dateFormat:str = r"%Y-%m-%d", timeFormat:str = r"%H:%M:%S"):
        r"""
        时间段类，用于表示和操作特定的时间段。

        ## 参数

        - `start`（`datetime.datetime`）：表示时间段开始的`datetime`对象。
        - `end`（`datetime.datetime`）：表示时间段结束的`datetime`对象。必须晚于或等于开始时间。
        - `dateFormat`（`str`，可选）：用于日期格式化的字符串，默认为`"%Y-%m-%d"`。
        - `timeFormat`（`str`，可选）：用于时间格式化的字符串，默认为`"%H:%M:%S"`。

        ## 异常

        - ValueError: 如果`start`晚于`end`。

        ## 示例
        
        ```python
        >>> from datetime import datetime
        >>> startTime = datetime(2025, 2, 15, 9, 0)
        >>> endTime = datetime(2025, 2, 15, 17, 0)
        >>> duration = TimeDuration(startTime, endTime)
        >>> print(duration)
        ```
        """

        DateDuration.__init__(self, start = start, end = end, dateFormat = dateFormat)

        # 给属性赋值
        self.timeFormat = timeFormat


    def __hash__(self) -> int:
        return hash((self.start, self.end, self.dateFormat, self.timeFormat))


    @type_verifier
    def strftime(self, dateFormat:str|None = None, timeFormat:str|None = None, *, autoSimplify:bool = True) -> str:
        r"""
        根据指定或默认的日期和时间格式，生成时间段的字符串表示。

        ## 参数

        - `dateFormat`（`str|None`，可选）：用于日期部分格式化的字符串。如果未提供，则使用实例化时设置的日期格式。
        - `timeFormat`（`str|None`，可选）：用于时间部分格式化的字符串。如果未提供，则使用实例化时设置的时间格式。
        - `autoSimplify`（`bool`，关键字参数）：如果开始和结束日期相同，是否简化输出，默认为`True`。

        ## 返回

        - `str`：时间段的字符串表示。
            - 如果`autoSimplify`开启且开始和结束日期相同，则返回“开始日期 开始时间-结束时间”格式的字符串；
            - 否则，返回“开始日期 开始时间 - 结束日期 结束时间”格式的字符串。
        
        ## 示例
        
        ```python
        >>> from datetime import datetime
        >>> startTime = datetime(2025, 2, 15, 9, 30)
        >>> endTime = datetime(2025, 2, 15, 17, 30)
        >>> duration = TimeDuration(startTime, endTime)
        >>> print(duration.strftime())
        2025-02-15 09:30-17:30
        >>> print(duration.strftime(timeFormat="%H:%M:%S"))
        2025-02-15 09:30:00-17:30:00
        >>> endTimeDifferentDay = datetime(2025, 2, 16, 17, 30)
        >>> durationDifferentDay = TimeDuration(startTime, endTimeDifferentDay)
        >>> print(durationDifferentDay.strftime())
        2025-02-15 09:30 - 2025-02-16 17:30
        ```
        """

        # 补全参数
        if dateFormat is None:
            dateFormat = self.dateFormat
        if timeFormat is None:
            timeFormat = self.timeFormat

        startDateString = self.start.strftime(dateFormat)
        startTimeString = self.start.strftime(timeFormat)
        endDateString = self.end.strftime(dateFormat)
        endTimeString = self.end.strftime(timeFormat)

        if autoSimplify and (startDateString == endDateString):
            string = f"{startDateString} {startTimeString}-{endTimeString}"
        else:
            string = f"{startDateString} {startTimeString} - {endDateString} {endTimeString}"

        return string


    @staticmethod
    @type_verifier
    def strptime(string:str, dateFormat:str = r"%Y-%m-%d", timeFormat:str = r"%H:%M:%S", *, simplified:bool = True) -> "TimeDuration":
        r"""
        从字符串解析并创建一个`TimeDuration`对象。

        此方法用于将特定格式的字符串转换为开始和结束时间，进而生成一个`TimeDuration`对象。
        
        字符串应包含日期和时间信息，且如果简化模式开启（`simplified=True`），则仅需提供一次日期，开始时间和结束时间可直接跟在日期后，详见`strftime`函数。
        
        ## 参数

        - `string`（`str`）：包含日期时间信息的字符串。
        - `dateFormat`（`str`，可选）：日期部分的格式化字符串，默认为`"%Y-%m-%d"`。
        - `timeFormat`（`str`，可选）：时间部分的格式化字符串，默认为`"%H:%M:%S"`。
        - `simplified`（`bool`，关键字参数）：如果设置为`True`（默认），则假定输入字符串中的日期部分对于开始和结束时间是相同的，并且仅需要提供一次。

        ## 返回

        - `TimeDuration`：包含解析出的开始和结束时间的时间段对象。

        ## 注意

        - 输入字符串必须严格按照指定格式构造，确保正确地分隔日期、开始时间和结束时间。
        - 时间格式化字符串应当准确反映输入字符串中时间表示的方法。

        ## 示例

        ```python
        >>> # 当简化模式开启，并且开始与结束日期相同
        >>> duration = TimeDuration.strptime('2025-02-15 09:30-17:30')
        >>> print(duration)
        
        >>> # 当简化模式关闭或开始与结束日期不同
        >>> duration = TimeDuration.strptime('2025-02-15 09:30 - 2025-02-16 17:30', simplified=False)
        >>> print(duration)
        ```
        """

        # 日期时间格式
        datetimeFormat = f"{dateFormat} {timeFormat}"

        # 计算“日期”和“时间”部分的字符串长度
        dateLength = len(dateFormat) + dateFormat.count("%Y") * 2 # `%Y`表示四位数年份，占四格
        timeLength = len(timeFormat)
        datetimeLength = dateLength + timeLength + 1 # 加一个空格

        # 开始时间
        start = datetime.strptime(string[ : datetimeLength], datetimeFormat)

        # 结束时间
        if simplified:
            end = datetime.strptime(string[:dateLength + 1] + string[-timeLength:], datetimeFormat)
        else:
            end = datetime.strptime(string[-datetimeLength:], datetimeFormat)

        return TimeDuration(start = start, end = end)
