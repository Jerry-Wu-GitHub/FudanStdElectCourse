r"""
This library implements UIS login to course selection websites.

The response situation encountered is as follows:
- static/html/case/login_fail.html
- static/html/case/quickly_click.html
"""

from time import sleep

from requests import Session
from bs4 import BeautifulSoup

from config.constants import XK_LOGIN_URL as URL
from config.constants import LOGIN_FORM_ID, LOGIN_FAIL_INFORMATION, LOGIN_INTERVAL_TIME
from config.user import USERNAME, PASSWORD
from src.model.error import LoginError
from src.util.log import log


def parse_login_form(html: str, login_form_id: str) -> dict[str, str]:
    r"""
    解析给定的HTML字符串，从中提取登录表单的相关信息并返回一个包含表单数据的字典。
    
    该函数会查找具有特定ID（通过 `login_form_id` 标识）的 <form> 元素，并从该元素下所有的 <input> 子元素中抽取 'name' 和 'value' 属性，将它们作为键值对存入最终返回的字典中。这通常用于自动化处理网页登录过程中的表单提交步骤。
    
    ## 参数

    - `html` （`str`）：包含登录表单的HTML页面内容的字符串形式。解析的响应文本示例：
        - static/html/case/login.html

    ## 返回

    - `dict[str, str]`：一个字典，包含了从指定登录表单中提取的所有输入字段的名称和对应的值。字典的键是输入字段的名称（`name`属性），值为对应输入字段的值（`value`属性）。

    ## 注意

    - 在调用此函数之前，需确保已正确定义 `login_form_id` 或者直接在 `find` 方法中使用正确的表单ID字符串。
    - 如果输入字段没有 'value' 属性，则该键值对不会被包含在返回的字典中，除非进行额外的错误检查和处理。
    - 此函数假定HTML结构是正确且预期的。如果HTML不遵循预期格式，可能需要增强错误处理逻辑。
    """

    # 解析 html 文档
    soup = BeautifulSoup(html, "html.parser")

    # 提取登录时提交的 <form> 元素
    login_form_tag = soup.find("form", {"id":login_form_id})

    # 提取该 <form> 元素下的所有 <input> 元素
    input_tags = login_form_tag.find_all("input")

    # 提取要提交的表单数据
    payload = {input_tag["name"]: input_tag.get("value", "") for input_tag in input_tags}

    return payload


def check_login_response(response_text: str):
    r"""
    检查登录响应文本以确定登录尝试是否成功。

    该函数接收一个字符串参数 `response_text`，代表从登录请求返回的响应文本。
    根据响应文本的内容，函数会抛出不同类型的 `LoginError` 异常来表示不同的错误情况，
    这些情况包括但不限于用户名或密码错误、需要输入验证码以及系统处于维护状态。

    ## 参数

    - `response_text` (`str`)：登录请求后服务器返回的响应文本。检查的响应文本示例：
        - static/html/case/home.html （成功登录）。
        - static/html/case/login_fail.html （用户名或密码错误）。
        - static/html/case/quickly_click.html （点击过快）。

    ## 异常

    - `LoginError`：当检测到登录失败的情况时，例如：
        - "用户名或密码错误" 字符串出现在 `response_text` 中，则抛出异常并设置错误信息为 "用户名或密码错误"。
        - "请输入验证码" 字符串出现在 `response_text` 中，则抛出异常并设置错误信息为 "需要输入验证码"。
        - "网络维护中" 字符串出现在 `response_text` 中，则抛出异常并设置错误信息为 "系统维护中"。
        - "请不要过快点击" 字符串出现在 `response_text` 中，则抛出异常并设置错误信息为 "click too quickly"。

    ## 示例

    >>> try:
    ...     check_login_response("登录失败，用户名或密码错误")
    ... except LoginError as e:
    ...     print(e)
    用户名或密码错误
    """

    for (feature, prompt) in LOGIN_FAIL_INFORMATION.items():
        if feature in response_text:
            raise LoginError(prompt)


def uis_login(username:str = USERNAME, password:str = PASSWORD) -> Session:
    r"""
    通过提供的用户名和密码登录到选课系统。

    此函数将尝试使用给定的用户名和密码进行登录，并处理“请不要过快点击”的登录错误。
    如果登录成功，该函数会返回一个维持登录状态的会话对象。如果登录过程中遇到其他错误，则抛出相应的异常。

    ## 参数

    - `username` （`str`）：用户名。
    - `password` （`str`）：密码。

    ## 返回

    - `requests.Session`：一个已登录的会话对象，可以用于后续的请求以保持登录状态。

    ## 异常

    - `LoginError`: 当登录失败时抛出此异常。
    """

    # 创建一个会话对象以维持会话状态
    session = Session()

    # 发送GET请求获取登录页面
    response = session.get(URL)

    # 获取表单数据
    payload = parse_login_form(response.text, LOGIN_FORM_ID)
    payload["username"] = username
    payload["password"] = password

    sleep_time = LOGIN_INTERVAL_TIME
    while True:
        # 发送POST请求进行登录
        response = session.post(URL, data=payload)
        log("uis_login：发送登录请求")

        # 处理登录错误
        try:
            # 检验登录是否成功
            check_login_response(response.text)
            break
        except LoginError as error:
            if str(error) == "click too quickly":
                sleep(sleep_time) # 等待一会，否则会发生“请不要过快点击”
                sleep_time *= 2
                continue
            log(f"uis_login：登录失败：{str(error)}")
            raise error from error

    log("uis_login：登录成功")
    return session


if __name__ == "__main__":
    uis_login()
    print("密码正确")
