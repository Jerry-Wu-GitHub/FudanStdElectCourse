r"""
课程组类。

class: CourseGroup
"""

from itertools import combinations

from config.constants import COURSE_QUANTITY_LIMIT
from src.model.course import Course


class CourseGroup():
    r"""
    由一些课程组成的集合，有添加课程并检查冲突的功能。

    ## 属性

    - `courses: list[Course]`：包含这个课程表中的课程的列表。
    - `isConflict: bool`：该课程表里的课程有没有冲突。
    - `limitedCoursesCount: dict[str, int]`：某一数量受限制的类型（键，正则表达式）的课的数量（值）。
    """

    def __init__(self, courses:list[Course]|None = None):
        """
        初始化一个新的课程组实例。

        初始化过程中会自动检查课程之间的冲突，并更新`isConflict`属性。

        ## 参数

        - `courses`（`list[Course]`，可选）：一个`Course`对象的列表，默认为`None`，此时将初始化一个空的课程列表。
        """

        if courses is None:
            courses = []

        self.courses = list(courses)

        # 某一数量受限制的类型的课的数量
        self.limitedCoursesCount = {
            pattern: sum(
                course.matchNo(pattern)
                for course in courses
            )
            for pattern in COURSE_QUANTITY_LIMIT
        }

        # 检查任意两门课程是否冲突，或者数量受限制的类型的课的数量超过了限制
        self.isConflict = any(
            pairs[0].is_conflict_with(pairs[1])
            for pairs in combinations(courses, 2)
        ) or any(
            self.limitedCoursesCount[pattern] > limit
            for (pattern, limit) in COURSE_QUANTITY_LIMIT.items()
        )


    def __iter__(self):
        r"""
        迭代。
        """

        return iter(self.courses)


    def __repr__(self) -> str:
        return f"{type(self).__name__}(courses={repr(self.courses)})"


    __str__ = __repr__


    def append(self, course: Course) -> bool:
        r"""
        将课程添加到课程组中，并检查新添加的课程是否与已有课程存在时间冲突（包括上课时间和期末考试时间）。

        ## 参数

        - `course`（`Course`）：要添加的课程实例。

        ## 返回

        - `bool`: 如果添加此课程后存在冲突（时间或数量），则返回`True`；如果无冲突，则返回`False`。

        ## 注意

        - 此方法会更新课程表实例的`is_conflict`属性，表示当前课程表是否存在任何课程间的时间冲突。
        """

        # 检测时间冲突，更新是否冲突的状态
        self.isConflict = self.isConflict or any(
            course.is_conflict_with(otherCourse)
            for otherCourse in self.courses
        )

        # 检测最大选课门数限制冲突
        for (pattern, limit) in COURSE_QUANTITY_LIMIT.items():
            self.limitedCoursesCount[pattern] += course.matchNo(pattern)
            self.isConflict = self.isConflict or (self.limitedCoursesCount[pattern] > limit)

        # 添加课程
        self.courses.append(course)

        # 返回是否冲突的状态
        return self.isConflict
