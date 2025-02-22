r"""
排课表主程序。

function: arrange_schedule
"""

from math import prod
import os
from time import asctime
from itertools import combinations, product

from config.constants import RESULT_PATH
from config.user import COURSE_CODES, TAGS_COUNT, SELECTED_COURSES_COUNT
from config.user import FULL_OK
from config.user import MAX_SCHEDULES_TO_OUTPUT
from src.model.course import Course
from src.model.course_group import CourseGroup
from src.model.time_table import TimeTable
from src.util.log import log
from src.core.uis_login import uis_login
from src.core.std_election_course import enter_std_elect_course_page, query_lesson
from src.util import timer


def initialize():
    r"""
    初始化选课系统登录并进入课程选择页面。

    该函数执行用户登录操作，并导航至选课页面，获取必要的选课信息。
    
    此函数依赖于外部定义的 `uis_login` 和 `enter_std_elect_course_page` 函数，
    它们分别负责处理实际的登录过程和进入选课页面后的数据获取。

    ## 返回

    - `dict`：包含以下键的字典：
            - `"session"`：进入了选课界面的会话对象，用于维持与选课系统服务器的通信。
            - `"phase"`：当前选课阶段的信息或标识，如`"第三轮"`。
            - `"query_lesson_url"`：查询课程列表所必需的URL地址，如`"https://xk.fudan.edu.cn/xk/stdElectCourse!queryLesson.action?profileId=3045"`。
    """

    # 进行登录、进入页面等操作
    session = uis_login()
    data = enter_std_elect_course_page(session)

    return {
        "session": session,
        "phase": data["phase"],
        "query_lesson_url": data["query_lesson_url"],
    }


def classify(session:"Session", phase:str, query_lesson_url:str):
    r"""
    查询课程，并将课程分类到相应的 `code` 下，再将 `code` 归类到相应的 `tag` 下。

    该函数首先通过给定的 `session` 和查询 URL 对指定课程代码的课程进行查询，
    然后根据课程代码对查询结果进行过滤和归类。最后，依据预定义的标签（`tag`）对课程代码进行分组。
    
    ## 参数

    - `session`（`requests.Session`）：登录会话对象，用于发送请求。
    - `phase`（`str`）：当前选课阶段的标识符，如“第一轮”、“第二轮”等。
    - `query_lesson_url`（`str`）：查询课程列表所必需的URL地址。

    ## 返回

    - `dict`：包含以下结构的字典：
        ```python
        {
            "tag1": {
                "code1": (
                    course1,
                    course2,
                    ...
                ),
                "code2": ...,
            },
            "tag2": ...,
            ...
        }
        ```
        其中，每个 `course` 是一个 `Course` 类的实例，包含了从 JSON 数据解析出的课程信息。

    ## 异常

    - `UserWarning`：如果配置的 `SELECTED_COURSES_COUNT` 值不正确、某个标签下没有足够的课程等情况时抛出。
    """

    # 查询课程，并将课程归入响应的`code`类
    course_codes = {}
    for code in COURSE_CODES:
        # 发送查询请求
        query_result = query_lesson(session = session, url = query_lesson_url, course_code = code)

        # 设置全局选课人数
        Course.lessonId2Counts |= query_result["lessonId2Counts"]

        # 创建`Course`对象
        courses = [Course.fromJSON(lessonJSON) for lessonJSON in query_result["lessonJSONs"]]

        # 检查常量`SELECTED_COURSES_COUNT`的正确性
        if len(courses) < SELECTED_COURSES_COUNT:
            raise UserWarning(f"你可能输入了错误的`SELECTED_COURSES_COUNT`值：{SELECTED_COURSES_COUNT}。请到 config.user.py 中重新设置。")

        # 过滤掉代码不对的课、选满了的课
        course_codes[code] = [
            courses[index]
            for index in range(len(courses))
            if courses[index].courseCode == code and ( # 代码要正确
                index < SELECTED_COURSES_COUNT or # 如果这门课已经选了，就不用管它满没满
                phase not in ("第二轮", "第三轮") or # 如果是第一轮选课，也不用管它满没满
                FULL_OK or # 如果你觉得满了也没关系，那也不用管它满没满
                courses[index].probability == 1 # 没满
            )
        ]

    # 根据标签，将课程代码进行分组
    tags = {tag: {} for tag in TAGS_COUNT}
    for (code, tag) in COURSE_CODES.items():
        if tag in tags:
            tags[tag][code] = course_codes[code]

    # 检查每个 tag 下的课程代码数量是否能满足 TAGS_COUNT 的数量要求
    for (tag, course_codes) in tags.items():
        if sum(map(bool, course_codes.values())) < TAGS_COUNT[tag]:
            raise UserWarning(f"标签“{tag}”下没有足够的课程。")

    log("classify: 课程归类完毕。")
    return tags


def combine_courses(tags:dict[str, dict]):
    r"""
    尝试所有可能的组合来安排课程表。

    此函数接收一个包含课程标签及其对应课程代码的字典，尝试通过各种组合方式将这些课程进行分组，
    以生成不冲突的课程表组合。它首先对每个标签下的课程代码进行组合，然后进一步对这些组合进行处理，
    以确保所选课程之间没有时间冲突。最后，返回所有可能的、无冲突的课程组合列表。

    ## 参数

    - `tags`（`dict[str, dict]`）：包含课程标签及其对应课程代码的字典，结构如下：
        ```python
        {
            "tag1": {
                "code1": (
                    course1,
                    course2,
                    ...
                ),
                "code2": ...,
            },
            "tag2": ...,
            ...
        }
        ```
        其中，每个 `course` 是一个代表课程的对象或数据结构。

    ## 返回

    - `list`：所有可能的、无冲突的课程组合列表。每个组合是一个元组，其中包含了多个课程对象。这些课程在 Tag 组内是无时间冲突的。

    ## 注意

    - 函数内部使用了组合 (`combinations`) 和笛卡尔积 (`product`) 来生成所有可能的课程组合，并检查是否存在时间冲突。
    - 在第一轮选课时，或者在 `FULL_OK=True`时，此过程可能会消耗较长时间（例如：10秒）并产生大量的组合。
    """

    # 展开最内层，将课程代码进行组合
    tags_comb = {
        tag: combinations(course_codes.values(), r = TAGS_COUNT[tag])
        for (tag, course_codes) in tags.items()
    }

    # 展开第二层，将课程进行组合
    tags_prod = {}
    for (tag, code_combinations) in tags_comb.items():
        tags_prod[tag] = ()
        for code_combination in code_combinations:
            course_groups = tuple(
                courses
                for courses in product(*code_combination)
                if not CourseGroup(courses).isConflict
            )
            tags_prod[tag] += course_groups

    # 计算一共有多少种组合
    combinitions_count = prod(len(code_combinations) for code_combinations in tags_prod.values())
    print(f"请耐心等待大约 {round(combinitions_count / 8.5e5)} 秒")

    # 展开第三层，将 tag 进行组合
    course_combinitions = [
        sum(course_group_combinition, ())
        for course_group_combinition in product(*tags_prod.values())
    ]

    # 计算一共有多少种组合
    count = len(course_combinitions)
    if combinitions_count != count:
        print(f"Warning: combine_courses 的第三层展开可能出现了错误（预期 {combinitions_count} ，实际 {count} ）")
    log(f"arrange_schedule: 课程组合完毕，共有 {count} 种 Tag 组内无冲突的组合。")

    return course_combinitions


def arrange_schedule():
    r"""
    安排课程表，筛选出没有时间冲突的课表，并根据评分排序输出前若干个结果到CSV文件。

    该函数首先通过调用 `classify` 和 `initialize` 函数初始化课程信息并分类课程，
    然后使用 `combine_courses` 函数生成所有可能的课程组合。接着，它遍历每个课程组合，
    创建相应的课表对象，并过滤掉存在时间冲突的课表。最后，对剩余的无冲突课表按照评分进行排序，
    并将排名前 `MAX_SCHEDULES_TO_OUTPUT` 的课表输出到一个CSV文件中。

    ## 返回
    
    - 无直接返回值。但是，该函数会生成一个包含排名前 `MAX_SCHEDULES_TO_OUTPUT` 的课程表的CSV文件。

    ## 注意

    - 在第一轮选课时，或者在 `FULL_OK=True`时，此过程可能会比较耗时（如：1小时），请确保有充足的计算资源和时间。
    - 输出的CSV文件路径基于当前时间命名，位于 `result` 目录下，并使用GBK编码。

    ## 示例

    ```python
    >>> arrange_schedule()
    ...
    已处理了 0 个课程表：0.00%
    ...
    arrange_schedule: 共有 15 种没有冲突的课程表。
    排名前 10 的课程表已经记录完成，在 result\Thu Feb 20 09：48：00 2025.csv 文件里。
    """

    tags = classify(**initialize())
    course_combinitions = combine_courses(tags)
    count = len(course_combinitions)

    # 创建课表，留下没有冲突的课表
    time_tables = []
    timer.reset()
    for (index, time_table) in enumerate(map(TimeTable, course_combinitions)):
        if timer.read() > 10:
            print(f"已处理了 {index} 个课程表：{round(index / count * 100, 2)}%")
            timer.reset()

        # 将刚刚创建的课表添加到列表中
        if not time_table.isConflict:
            time_tables.append(time_table)
    log(f"arrange_schedule: 共有{len(time_tables)}种没有冲突的课程表。")

    # 按照得分进行排序
    time_tables.sort(key = TimeTable.getScore, reverse = True)

    # 输出课表
    output_csv(time_tables)


def output_csv(time_tables: list[TimeTable]) -> str:
    r"""
    将前 `MAX_SCHEDULES_TO_OUTPUT` 名的课程表输出到 csv 文件。

    ## 参数

    - `time_tables: list[TimeTable]`：已经排好序了的课程表列表。

    ## 返回

    - 输出的 .csv 文件的相对路径。
    """

    # 确保输出文件夹存在
    if not os.path.isdir(RESULT_PATH):
        os.makedirs(RESULT_PATH)

    # 创建输出文件
    now_time = asctime().replace(':', '：')
    csv_path = os.path.join(RESULT_PATH, f"{now_time}.csv")
    with open(csv_path, mode = "w", encoding="gbk"):
        pass

    # 输出前`MAX_SCHEDULES_TO_OUTPUT`名
    for (index, time_table) in enumerate(time_tables):
        if index >= MAX_SCHEDULES_TO_OUTPUT:
            break
        time_table.toCsv(csv_path)

    log(f"排名前 {index} 的课程表已经记录完成，在 {csv_path} 文件里。")
    os.startfile(csv_path)
    return csv_path
