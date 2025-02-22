r"""
课程查询功能。

function: enter_std_elect_course_page 将一个已登录的`requests.Session`对象进入选课页面。
function: query_lesson 通过一个已进入选课页面的`requests.Session`对象向指定的查询 URL 发送查询课程请求。
"""

from time import sleep

from requests import Session, HTTPError

from config.constants import XK_STD_ELECT_COURSE_URL, QUERY_INTERVAL_TIME
from src.model.error import EnterFailure, QueryError
from src.core.check import check_enter_response, check_query_response
from src.core.parse import parse_std_elect_course_page, parse_std_elect_course_default_page
from src.core.parse import simplify_phase, jsonfy_query_response
from src.util.log import log
from src.util.file import write_to_file


def enter_std_elect_course_page(session: Session) -> {"phase": str, "query_lesson_url": str}:
    r"""
    通过给定的会话对象（已登录）访问选课入口页面，并尝试进入选课系统。

    此函数首先向选课入口网页发送一个 GET 请求，然后解析返回的 HTML 文档，
    获取当前选课阶段、选课表单提交的目标 URL 和选课配置文件 ID。接着，使用这些信息
    发送一个 POST 请求以进入选课页面。最后，检查进入选课页面是否成功，并提取查询课程的 API URL。

    ## 参数

    - `session`：（`requests.Session`）一个成功进行 UIS 登录的会话对象，用于发起 HTTP 请求。

    ## 返回

    - 字典，有以下键：
        - `"phase"`：当前选课阶段的简短的描述字符串，例如 `"第三轮"`。
        - `"query_lesson_url"`：查询课程的 API URL。

    ## 异常

    - `EntranceNotFoundError`：如果在页面中找不到任何选课通知板，即当前没有选课入口。
    - `EntranceNotOpenedError`：如果找到的选课通知板中不包含有效的 `"electionProfile.id"` 输入元素，即当前没有开放的选课入口。
    - `EnterFailure`：当响应文本中包含特定错误信息（例如“不在选课时间内”或“选课限制”）时抛出。
    - `HTMLError`：如果服务器返回的 HTML 不符合预期。

    ## 注意

    - 在调用此函数之前，请确保 `session` 对象已经过正确的认证并且有效。
    - 此函数依赖于 `parse_std_elect_course_page` 和 `check_enter_response` 函数来解析网页内容和处理响应结果。

    ## 示例

    >>> import requests
    >>> session = requests.Session()
    # 假设这里有一些代码对 session 进行了认证...
    >>> query_lesson_api_url = enter_std_elect_course_page(session)
    >>> print(query_lesson_api_url)
    'https://xk.fudan.edu.cn/xk/stdElectCourse!queryLesson.action?profileId=3025'
    """

    # 返回的数据
    outcome = {}

    # 向选课入口网页发送 GET 请求
    response = session.get(XK_STD_ELECT_COURSE_URL)
    write_to_file(r"tmp\stdElectCourse.action.html", response.text)

    # 解析网页，获取数据
    data = parse_std_elect_course_page(response.text)
    log(f"获得数据：{repr(data)}")
    outcome["phase"] = simplify_phase(data["phase"])

    # 发送 POST 请求，进入该选课入口
    response = session.post(data["action_url"], data = {
        "electionProfile.id": data["electionProfile.id"]
    })
    write_to_file(r"tmp\stdElectCourse!defaultPage.action.html", response.text)

    # 检查进入情况
    try:
        check_enter_response(response.text)
    except EnterFailure as error:
        log(f"enter_std_elect_course_page：进入选课入口失败：{str(error)}")
        raise error from error

    # 提取查询课程的 API ，例如"https://xk.fudan.edu.cn/xk/stdElectCourse!queryLesson.action?profileId=3025"
    outcome["query_lesson_url"] = parse_std_elect_course_default_page(response.text)["query_lesson_url"]

    return outcome


def query_lesson(session:Session, url:str, *, lesson_no:str = "", course_code:str = "", course_name:str = ""):
    r"""
    `query_lesson` 函数用于查询课程信息。它通过登录选课系统，进入选课页面，并调用查询课程的 API，根据用户提供的课程序号、课程代码或课程名称等参数，返回匹配的课程信息。

    ## 参数

    - `session`：（`requests.Session`）已经进入了选课界面的`Session`对象，用于发送查询请求。
    - `url`：（`str`）发送查询请求的目标 API URL 。
    - `lesson_no`：（`str`，可选）课程序号。默认为空字符串。
    - `course_code`：（`str`，可选）课程代码。默认为空字符串。
    - `course_name`：（`str`，可选）课程名称。默认为空字符串。

    **注意**：至少需要提供一个参数（`lesson_no`、`course_code` 或 `course_name`）用于查询。

    ## 返回

    返回一个字典，包含以下两个键值对：

    - `"lessonJSONs"`：（`list[dict[str, object]]`）查询到的课程 JSON 数据列表。每个课程的 JSON 数据包含课程的详细信息，如课程名称、课程序号、授课教师等。
    - `"lessonId2Counts"`：（`dict[str, dict[str, int]]`）每个课程 ID 对应的统计信息字典。例如，课程的选课人数等。

    ## 异常

    - `LoginError`：如果登录选课系统失败。
    - `EnterFailure`：如果进入选课页面失败，例如不在选课时间内或选课限制。
    - `HTMLError`：如果从选课页面获取查询课程的 API URL 失败。
    - `QueryError`：如果查询课程操作失败，例如查询参数不符合要求或查询返回的响应文本格式不符合预期。

    ## 注意

    1. 在调用此函数之前，请确保选课系统处于开放状态，且当前用户可以成功登录。
    2. 查询参数（`lesson_no`、`course_code`、`course_name`）的输入应符合选课系统的规范。例如，课程序号和课程代码通常需要至少 6 个字符，课程名称至少需要 4 个字符或 2 个汉字。
    3. 如果查询结果为空，可能是因为查询参数不准确或当前没有匹配的课程。请检查输入参数或在选课系统中手动确认。
    4. 此函数依赖于 `uis_login` 函数进行登录操作，依赖于 `enter_std_elect_course_page` 函数进入选课页面，并依赖于 `check_query_response` 和 `jsonfy_query_response` 函数处理查询结果。

    ## 示例

    ```python
    # 查询课程序号为 "123456" 的课程
    result = query_lesson(lesson_no="123456")
    print(result)

    # 查询课程代码为 "CS101" 的课程
    result = query_lesson(course_code="CS101")
    print(result)

    # 查询课程名称包含 "计算机" 的课程
    result = query_lesson(course_name="计算机")
    print(result)
    ```
    """

    # 打包要发送的查询数据
    data = {
        "lessonNo": lesson_no,
        "courseCode": course_code,
        "courseName": course_name
    }

    sleep_time = QUERY_INTERVAL_TIME
    while True:
        # 发送POST请求以查询课程
        response = session.post(url, data = data)
        log(f"query_lesson: 发送查询请求：{data}")
        write_to_file(r"tmp\stdElectCourse!queryLesson.action.html", response.text, mode = "w")

        # 检查请求是否成功
        try:
            response.raise_for_status()
        except HTTPError as error:
            log(f"query_lesson：请求查询课程失败：{str(error)}")
            raise error from error

        # 检查响应的内容是否有错误
        try:
            check_query_response(response.text, data)
            break
        except QueryError as error:
            if str(error) == "click too quickly":
                sleep(sleep_time) # 等待一会，否则会发生“请不要过快点击”
                sleep_time *= 2
                continue
            log(f"query_lesson：查询课程信息失败：{str(error)}")
            raise error from error

    # 将返回的文本解析为 Python 对象
    try:
        result_data = jsonfy_query_response(response.text)
    except ValueError as error:
        log(f"query_lesson：提取课程信息失败：{str(error)}")
        raise error from error

    return result_data
