r"""
errors
"""


class EnterFailure(Exception):
    """Raised when unable to enter the course selection entrance."""
    pass


class EntranceNotFoundError(EnterFailure):
    """Raised when there is no course selection entrance."""
    pass


class EntranceNotOpenedError(EnterFailure):
    """Raised when there is no course selection entrance opened."""
    pass


class HTMLError(Exception):
    """Raised when the structure of an HTML document is unexpected."""
    
    def __init__(self, message:str = "the HTML document is unexpected", html:str = None):
        r"""
        ## 参数

        - `message`：错误信息。
        - `html`：引发该错误的 HTML 文档字符串。
        """

        self.message = message
        self.html = html
        super().__init__(self.message)


class LoginError(Exception):
    """Raised when there is an error logging into the website."""
    pass


class QueryError(Exception):
    """Raised when an error occurs in the response to a course query."""

    def __init__(self, message:str = "an error occurs in the response to a course query", query_parameters:dict[str, str] = None):
        r"""
        ## 参数

        - `message`：错误信息。
        - `query_parameters`：该次查询时发送的数据。
        """

        self.message = message
        self.query_parameters = None
        if self.query_parameters is not None:
            self.message += f": {query_parameters}"
        super().__init__(self.message)
