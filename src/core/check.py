r"""
此文件中的函数专门用于 src.core.std_election_course.py 中的响应页面的检查。

function: check_enter_response
function: check_query_response
"""

from config.constants import ENTER_FAIL_INFORMATION, QUERY_ERROR_INFORMATION
from src.model.error import EnterFailure, QueryError


def check_enter_response(response_text: str):
    r"""
    检查“进入选课界面”操作的响应文本，判断是否出现特定错误信息。

    如果在响应文本中检测到与不在选课时间或选课限制相关的错误信息，
    则抛出相应的异常。该函数假设输入的响应文本是中文。

    ## 参数

    - `response_text`：（`str`）服务器返回的响应文本，用于检查是否包含特定的错误消息。待检查的页面的示例见：
        - static/html/case/stdElectCourse!defaultPage.html （这是成功的）。

    ## 异常

    - `EnterFailure`：当响应文本中包含`"不在选课时间内"`或`"选课限制"`时抛出。错误信息分别为`"outside selection period"`和`"parameter error"`。

    ## 示例

    >>> check_enter_response("操作 失败:\n不在选课时间内")
    Traceback (most recent call last):
        ...
    EnterFailure: outside selection period

    >>> check_enter_response("选课限制")
    Traceback (most recent call last):
        ...
    EnterFailure: parameter error
    """

    for (feature, prompt) in ENTER_FAIL_INFORMATION.items():
        if feature in response_text:
            raise EnterFailure(prompt)


def check_query_response(response_text, query_parameters):
    r"""
    检查查询课程操作的响应文本，判断是否出现特定错误信息。

    ## 参数

    - `response_text`：（`str`）服务器返回的响应文本，用于检查是否包含特定的错误消息。
    - `query_parameters`：（`dic[str, str]`）发送给服务器的查询参数，用于异常处理。

    ## 异常

    - `QueryError`：当响应文本中包含以下信息时：
        - `"error lessonNo length"`：`message="the lesson_no requires at least 6 characters"`，课程序号至少需要输入6个字符。
        - `"error courseCode length"`：`message="the course_code requires at least 6 characters"`，课程代码至少需要输入6个字符。
        - `"error courseName length"`：`message="the course_name requires at least 4 characters or 2 Chinese characters"`，课程名称至少需要输入4个字符或2个汉字。
        - `"error no lessons"`：`message="At present, it is the peak stage of course selection. Please enter the precise lesson_no, course_code, and course_name to query."`，目前为选课高峰阶段，请输入精确的课程序号，课程代码，课程名称查询。
    """

    for (feature, prompt) in QUERY_ERROR_INFORMATION.items():
        if feature in response_text:
            raise QueryError(prompt, query_parameters = query_parameters)
