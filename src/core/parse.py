r"""
此文件中的函数专门用于 src.core.std_election_course.py 中的响应页面的解析、提取信息。

function: parse_std_elect_course_page
function: parse_std_elect_course_default_page
function: simplify_phase
function: jsonfy_query_response
"""

import json
import re

from bs4 import BeautifulSoup

from config.constants import BASE_URL
from config.constants import PHASES_INFORMATION
from src.model.error import EntranceNotFoundError, EntranceNotOpenedError, HTMLError
from src.util.log import log


def parse_std_elect_course_page(html: str) -> dict[str, str]:
    r"""
    解析学生选课页面，并提取有关当前选课阶段和选课入口ID的信息。

    ## 参数

    - `html`：（`str`）包含选课页面内容的 HTML 字符串。解析的页面的一个示例见：static/html/case/stdElectCourse.html

    ## 返回

    - `dict`: 包含两个键值对的一个字典：
        - `"phase"`：当前选课阶段的描述字符串，例如 `"2024-2025 学年 2 学期 第三轮"`。
        - `"action_url"`：点击“进入选课”后，表单被提交的目标 URL，例如`"https://xk.fudan.edu.cn/xk/stdElectCourse!defaultPage.action"`。
        - `"electionProfile.id"`：当前开放的选课配置文件的 ID，用于标识特定的选课活动。例如 `"3045"`。
    

    ## 异常
    
    - `EntranceNotFoundError`：如果在页面中找不到任何选课通知板，即当前没有选课入口。
    - `EntranceNotOpenedError`：如果找到的选课通知板中不包含有效的`"electionProfile.id"`输入元素，即当前没有开放的选课入口。

    ## 注意

    - 在调用此函数前，请确保传入的 HTML 字符串是有效的，并且是从正确的选课页面获取的。
    """

    # 要返回的数据
    data = {}

    # 解析 html 文档
    soup = BeautifulSoup(html, "html.parser")

    # 提取最上面的选课通知板
    notice_div = soup.find("div", {"id":"electIndexNotice0"})

    # 如果没有找到选课通知板，说明当前没有任何选课入口
    if notice_div is None:
        log("parse_std_elect_course_page：没有找到任何选课入口")
        raise EntranceNotFoundError("There is no course selection entrance.")

    # 提取本次选课的阶段，如`"2024-2025 学年 2 学期 第三轮"`
    data["phase"] = notice_div.find("h2").text

    # 选课表单
    elect_course_form = notice_div.find("form", {"name":"stdElectCourseIndexForm0"})

    # 表单被提交的目标 URL
    data["action_url"] = BASE_URL + elect_course_form["action"]

    # 提取藏有 "electionProfile.id" 的 <input> 元素
    input_tag = elect_course_form.find("input", {"name":"electionProfile.id"})

    # 如果没有找到该元素，说明当前没有开放的选课入口
    if input_tag is None:
        log("parse_std_elect_course_page：没有开放的选课入口")
        raise EntranceNotOpenedError("There is no course selection entrance opened.")

    # 提取 electionProfile.id 的值，如"3045"
    data["electionProfile.id"] = input_tag["value"]

    return data


def parse_std_elect_course_default_page(html: str) -> dict[str, str]:
    r"""
    解析学生选课默认页面的 HTML，提取并返回包含查询课程 API 的 URL。

    该函数接收一个 HTML 字符串作为输入，通过`BeautifulSoup`库解析此 HTML，
    并查找特定 ID 的`<script>`标签来获取查询课程的 API 地址。最终，将 API 地址
    以字典的形式返回。

    ## 参数

    - `html`: 需要解析的学生选课默认页面的 HTML 内容。解析的页面的一个示例见：static/html/case/stdElectCourse!defaultPage.html

    ## 返回

    - `dict[str, str]`：包含查询课程 API URL 的字典，键名为`"query_lesson_url"`。

    ## 异常

    - `HTMLError`：如果 HTML 中找不到指定 ID 的 <script> 元素。

    ## 注意

    - 此函数假设 HTML 文档中存在 ID 为 "queryLesson_script" 的 <script> 元素。

    ## 示例

    >>> sample_html = '<html><body><script id="queryLesson_script" type="text/javascript" src="/xk/stdElectCourse!queryLesson.action?profileId=3025"></script></body></html>'
    >>> result = parse_std_elect_course_default_page(sample_html)
    >>> print(result)
    {'query_lesson_url': 'https://xk.fudan.edu.cn/xk/stdElectCourse!queryLesson.action?profileId=3025'}
    """

    # 要解析出并返回的数据
    outcome = {}

    # 解析 html 文档
    soup = BeautifulSoup(html, 'html.parser')

    # 提取存有查询课程的 API 的 <script> 元素
    query_lesson_script = soup.find("script", {"id": "queryLesson_script"})

    # 如果找不到该元素，则报错
    if query_lesson_script is None:
        log(f'parse_std_elect_course_default_page：解析页面失败，没有找到 <script id="queryLesson_script"> 元素。\n{html}')
        raise HTMLError('expected <script id="queryLesson_script"> not found in this HTML document', html)

    # 提取查询课程的 API ，例如"https://xk.fudan.edu.cn/xk/stdElectCourse!queryLesson.action?profileId=3025"
    outcome["query_lesson_url"] = BASE_URL + query_lesson_script["src"]

    return outcome


def simplify_phase(phase_text: str) -> str:
    r"""
    解析`phase_text`中的选课阶段信息。

    ## 参数

    - `phase_text`：（`str`）包含选课阶段信息的字符串，如`"2024-2025 学年 2 学期 第三轮"`。

    ## 返回

    - `str`：对选课阶段的简洁描述，如`"第三轮"`。

    ## 异常

    - `ValueError`：如果找不到阶段特征。
    """

    # 尝试寻找
    for (feature, phase) in PHASES_INFORMATION.items():
        if feature in phase_text:
            return phase

    # 找不到就报错
    raise ValueError(f"Unable to find information about the course selection phase in {phase_text}")


def jsonfy_query_response(response_text:str) -> {"lessonJSONs":list[dict[str, object]], "lessonId2Counts":dict[str, dict[str, int]]}:
    r"""
    从给定的 `response_text` 中提取并解析 `lessonJSONs` 和 `lessonId2Counts` 数据。
    
    ## 参数

    - `response_text`（`str`）：包含需要解析数据的响应文本。格式示例参考：static/javascript/case/query_result.js
    
    ## 返回
    
    - `dict`：包含两个键值对的对象：
        - `"lessonJSONs"`（`list[dict[str, object]]`）：解析后的课程 JSON 数据列表。
        - `"lessonId2Counts"`（`dict[str, dict[str, int]]`）：每个课程 ID 对应的统计信息字典。
    
    ## 异常

    - `ValueError`：当在 `response_text` 中无法匹配到 `lessonJSONs` 或 `lessonId2Counts`，或者它们的字符串内容不符合 JSON 编码格式时抛出。
    
    ## 注意

    - `response_text` 应遵循特定的格式，其中 `lessonJSONs` 和 `lessonId2Counts` 分别通过正则表达式模式匹配和提取。
    - 在处理 `lessonId2Counts_string` 时，会进行特定的替换（如将单引号替换成双引号）以确保其符合标准的 JSON 格式要求。
    - 该函数假设 `response_text` 包含有效的 JavaScript 代码片段，从中可以提取出目标 JSON 字符串。
    """

    # 正则匹配模式
    lessonJSONs_pattern = r"var\s+lessonJSONs\s*=\s*(\[.*?\])\s*;"
    lessonId2Counts_pattern = r"window\s*\.\s*lessonId2Counts\s*=\s*({.*?})\s*(?:;|$)"

    # 开始匹配
    lessonJSONs_match = re.search(lessonJSONs_pattern, response_text, re.DOTALL) # re.DOTALL 使 `.` 匹配包括换行符在内的一切字符
    lessonId2Counts_match = re.search(lessonId2Counts_pattern, response_text, re.DOTALL)

    # 检查匹配结果
    if lessonJSONs_match is None:
        raise ValueError(f"cannot match `lessonJSONs` ({lessonJSONs_pattern}) in `response_text`: {response_text}")
    if lessonId2Counts_match is None:
        raise ValueError(f"cannot match `lessonId2Counts` ({lessonId2Counts_pattern}) in `response_text`: {response_text}")

    # 获取并处理匹配到的 JSON 字符串
    lessonJSONs_string = lessonJSONs_match.group(1)
    lessonId2Counts_string = lessonId2Counts_match.group(1)
    replacement = {
        "\'": "\"",
        "sc": "\"sc\"",
        "lc": "\"lc\""
    }
    for (old, new) in replacement.items():
        # 将 `lessonId2Counts_string` 转换为标准的 JSON 字符串
        lessonId2Counts_string = lessonId2Counts_string.replace(old, new)

    # 将 JSON 字符串解码为 Python 对象
    try:
        lessonJSONs = json.loads(lessonJSONs_string)
    except json.decoder.JSONDecodeError as error:
        message = f"The string in the `lessonJSONs` section does not conform to the JSON encoding format ({str(error)}) : {lessonJSONs_string}"
        raise ValueError(message) from error
    try:
        lessonId2Counts = json.loads(lessonId2Counts_string)
    except json.decoder.JSONDecodeError as error:
        message = f"The string in the `lessonId2Counts` section does not conform to the JSON encoding format ({str(error)}) : {lessonId2Counts_string}"
        raise ValueError(message) from error

    return {
        "lessonJSONs": lessonJSONs,
        "lessonId2Counts": lessonId2Counts
    }
