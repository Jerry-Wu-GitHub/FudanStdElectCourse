r"""
function: verify_type: Verify whether the given object meets the expected type.
"""

import importlib
from inspect import getfullargspec
from types import FunctionType, UnionType, GenericAlias
from functools import wraps


def _throw_TypeError(object_name: str, class_name: str, got: str, from_error: BaseException = None):
    r"""
    抛出一个`TypeError`异常，指出某个对象的类型不匹配预期的类型。

    ## 参数

    - `object_name`（str）：对象的名称或描述。
    - `class_name`（str）：期望的对象类型名称。
    - `got`（str）：实际得到的对象类型名称。

    ## 抛出

    - `TypeError`：当对象的实际类型与期望类型不符时抛出此异常。错误消息包含对象名称、期望的类型和实际得到的类型。
    
    ## 示例
    
    ```python
    >>> throw_TypeError("user_id", "int", "str")
    Traceback (most recent call last):
        ...
    TypeError: `user_id` expected to be of type `int`, but got `str`
    ```
    """

    raise TypeError(f"`{object_name}` expected to be of type `{class_name}`, but got `{got}`") from from_error


def _extract_class(classinfo) -> set:
    """
    从给定的`classinfo`中提取类型信息。如果`classinfo`是联合类型（`types.UnionType`），则返回其中所有类型的集合；如果`classinfo`是`tuple`类型，则递归地将其转换为集合；否则，将该类型单独作为一个集合返回。

    ## 参数

    - `classinfo`：类型、类型联合或类型元组，指定要提取的类信息。

    ## 返回

    - `set`：包含提取出的所有类型的集合。

    示例:
    
    ```python
    >>> _extract_class(str)
    {<class 'str'>}
    >>> _extract_class(str | int) # 解压
    {<class 'int'>, <class 'str'>}
    >>> _extract_class(list[str])
    {list[str]}
    >>> _extract_class((str|int, int|list[str])) # 去重，递归
    {<class 'int'>, list[str], <class 'str'>}
    >>> _extract_class((str|int, (int, list|str)))
    {<class 'int'>, <class 'str'>, <class 'list'>}
    ```
    """

    # 如果`classinfo`是联合类型（`types.UnionType`）
    if isinstance(classinfo, UnionType):
        # 返回其中所有类型的集合
        return set(classinfo.__args__)

    # 如果`classinfo`是`tuple`类型
    if isinstance(classinfo, tuple):
        # 递归地将其转换为集合
        return set.union(*map(_extract_class, classinfo))

    # 将该类型单独地放入一个集合并返回
    return {classinfo}


def _get_class_name(classinfo):
    r"""
    获取类型信息的名称表示形式。支持基础类型、类型联合以及通用别名类型的名称提取。
    
    ## 参数

    - `classinfo`：可以是Python的基础类型、类型联合（如 `str | int`）、通用别名类型（如 `list[str]`）或包含这些类型的元组。

    ## 返回

    - 一个字符串，表示输入类型的名称。对于联合类型和元组，返回它们用“" | "”分隔的形式。
    
    ## 异常

    - `TypeError`：如果`classinfo`的类型不被支持。

    ## 示例

    ```python
    >>> _get_class_name(str)
    'str'
    >>> _get_class_name(str | int)
    'str | int'
    >>> _get_class_name(list[str])
    'list[str]'
    >>> _get_class_name((str, int))
    'int | str'
    >>> _get_class_name((str, int | str, (int, list[int])))
    'list[int] | int | str'
    ```
    """

    # 如果`classinfo`是 Python的基础类型
    if isinstance(classinfo, type):
        # 直接返回类型名
        return classinfo.__name__

    # 如果`types.UnionType`或`types.GenericAlias`类型
    if isinstance(classinfo, UnionType) or isinstance(classinfo, GenericAlias):
        # 直接返回它的字符串表示形式，如`"str | int"`、`"list[str]"`
        return str(classinfo)

    # 如果`classinfo`是`tuple`类型
    if isinstance(classinfo, tuple):
        # 铺平`classinfo`所含的类，去重
        classes = _extract_class(classinfo)
        # 对每个类递归地调用`_get_class_name`，并以`" | "`链接各个类名
        return " | ".join(map(_get_class_name, classes))
    
    # `classinfo`的类型错误，报错
    raise TypeError(f"The type of `classinfo` should be `type`, `types.UnionType`, `types.GenericAlias`, or a `tuple` composed of these, but got {type(classinfo).__name__}.")


def verify_type(object:object, object_name:str, classinfo:type|UnionType|GenericAlias|tuple) -> None:
    r"""
    验证给定对象`object`是否属于预期的类型或类型元组`classinfo`。如果对象的类型不匹配，则抛出`TypeError`异常。

    ## 参数

    - `object`（`object`）：要验证类型的对象。
    - `object_name`（`str`）：对象的名称，用于在错误消息中标识对象。
    - `classinfo`（`type | UnionType | GenericAlias | tuple`）：可以是Python的基础类型、类型联合（如 `str | int`）、通用别名类型（如 `list[str]`）或包含这些类型的元组。

    ## 返回

    无返回值（`None`）。如果类型检查失败，则会抛出`TypeError`异常。

    ## 异常

    - `TypeError`：如果`classinfo`的类型不符合条件。
    - `TypeError`：当`object`不是`classinfo`所指定的类型之一时。

    ## 示例

    ```python
    >>> print(verify_type(1, "one", int))
    None
    >>> print(verify_type(1, "one", str))
    TypeError: `one` expected to be of type `str`, but got `1`
    >>> print(verify_type(1, "one", int | str))
    None
    >>> print(verify_type([1], "a_list", list[int]))
    None
    >>> print(verify_type([1], "a_list", list[str]))
    TypeError: `a_list` expected to be of type `list[str]`, but got `[1]`
    >>> print(verify_type([1], "a_list", list[int|str]))
    None
    >>> print(verify_type([1], "a_list", list[int] | list[str]))
    None
    >>> print(verify_type([1], "a_list", (list[int], list[str])))
    None
    >>> print(verify_type([1, []], "a_list", (list[int], list[str])))
    TypeError: `a_list` expected to be of type `list[int] | list[str]`, but got `[1, []]`
    ```
    """

    got_error = False

    # 如果`classinfo`是`type`类型
    if isinstance(classinfo, type):
        # 检查类型
        if not isinstance(object, classinfo):
            got_error = True
            from_error = None

    # 如果`classinfo`是联合（`types.UnionType`）类型
    elif isinstance(classinfo, UnionType):
        try:
            # 递归检查`object`是否是`classinfo.__args__`中的一个类型
            verify_type(object, object_name, classinfo.__args__)
        except TypeError as error:
            got_error = True
            from_error = error

    # 如果`classinfo`是通用泛型（`types.GenericAlias`）类型
    elif isinstance(classinfo, GenericAlias):
        # 检查`object`自身的类型
        try:
            verify_type(object, object_name, classinfo.__origin__)
        except TypeError as error:
            got_error = True
            from_error = error

        # 检查`object`内的元素的类型
        for elem in object:
            try:
                verify_type(elem, "", classinfo.__args__)
            except TypeError as error:
                got_error = True
                from_error = error

    # 如果`classinfo`是`tuple`类型
    elif isinstance(classinfo, tuple):
        for cls in classinfo:
            try:
                verify_type(object, "", cls)
                break
            except TypeError:
                pass
        else:
            got_error = True
            from_error = None

    # 传递给本检查函数的参数类型不正确
    else:
        _throw_TypeError("classinfo", "type | UnionType | GenericAlias | tuple", repr(classinfo))

    # 如果在之前的检查中出现了类型不匹配的错误
    if got_error:
        class_name = _get_class_name(classinfo)
        got = repr(object)
        _throw_TypeError(object_name, class_name, got, from_error)


def get_builtin_member(path_list:list[str]) -> object:
    r"""
    根据给定的路径列表访问内置成员。
    
    ## 参数

    - `path_list`：元素为字符串的列表，指示如何按顺序访问成员。
    
    ## 返回

    - 成员对象（可以是模块、类、方法等）。

    ## 异常

    - `AttributeError`：如果找不到。

    ## 示例

    ```python
    print(get_member(["print"]))  # <built-in function print>
    print(get_member(["str"]))  # <class 'str'>
    print(get_member(["str", "split"]))  # <method 'split' of 'str' objects>
    ```
    """

    # 从内置命名空间开始查找
    current = __builtins__

    for path_item in path_list:
        current = getattr(current, path_item)

    return current


def get_library_member(path_list:list[str]) -> object:
    r"""
    返回标准库或扩展库中的成员。
    
    ## 参数

    - `path_list`：元素为字符串的列表，指示如何按顺序访问成员。
    
    ## 返回

    - 成员对象（可以是模块、类、方法等）。

    ## 异常

    - `AttributeError`：如果找不到。

    ## 示例

    ```python
    print(dynamic_import(["math"]))  # <module 'math' from '...'>
    print(dynamic_import(["os", "path"]))  # <module 'ntpath' from '...' >
    print(dynamic_import(["os", "path", "isdir"]))  # <function isdir at ...>
    print(dynamic_import(["datetime", "date", "today"]))  # <built-in method today of type object at ...>
    ```
    """

    # 初始化第一个模块名称并导入
    module_name = path_list[0]
    module = importlib.import_module(module_name)

    # 如果只有模块名，则直接返回模块
    if len(path_list) == 1:
        return module

    # 初始化当前对象为已导入的模块
    current = module

    # 遍历剩余路径元素
    for item in path_list[1:]:
        current = getattr(current, item)

    return current


def get_member(string:str) -> object:
    r"""
    返回内置的、标准库或扩展库中的成员。
    
    ## 参数

    - `string`：该成员的字符串访问形式，如`"int"`、`"os.path"`、`"str | int"`。
    
    ## 返回

    - 成员对象（可以是模块、类、方法等）。

    ## 异常

    - `ValueError`：如果找不到。

    ## 注意

    - 函数实现中使用了`eval`尝试直接对`string`进行解析，所以请确保`string`不含恶意代码。
    """

    try:
        # 内置的、以及其他奇奇怪怪的
        return eval(string)
    except NameError:
        pass

    path_list = string.split(".")

    try:
        # 尝试从内置对象中搜索该对象
        return get_builtin_member(path_list)
    except AttributeError:
        # 内置的里面找不到
        pass

    try:
        # 尝试从标准库或本机已安装的扩展库里搜索该对象
        return get_library_member(path_list)
    except AttributeError:
        # 库里面找不到
        pass

    # 找不到
    raise ValueError(f"Unable to find the specified object: {path_list}")


def verify_parameters(func:FunctionType, **parameters) -> None:
    r"""
    验证传递给函数`func`的实际参数是否符合其类型注解。如果某个参数的类型不符合预期，则抛出`TypeError`异常。

    ## 参数

    - `func`（`FunctionType`）：要验证其参数类型的函数。
    - `**parameters`（任意关键字参数）：实际传递给函数`func`的参数值，使用关键字参数的形式指定，关键字为参数名，值为对应的参数值。在`func`的签名中指定了类型的参数名必需在`parameters`中出现，否则引发`ValueError`。

    ## 返回

    - 无返回值（`None`）。如果类型检查失败，则会抛出`TypeError`异常。

    ## 异常

    - `TypeError`: 当实际传递给函数`func`的参数类型与其类型注解不匹配时抛出此异常。

    ## 示例

    ```python
    >>> def f(a:int, b:bool, c:int|float, d:list[str]):
    ...     verify_parameters(f, a=a, b=b, c=c, d=d)
    ...     print("All parameter types are correct.")
    ... 
    >>> f(1, True, 1.0, ["1"])
    All parameter types are correct.
    >>> f(1, True, 1.0, [1])
    TypeError: `d` expected to be of type `list[str]`, but got `[1]`

    >>> def g(a:"int", b:"datetime.date", c:"int|float", d:"list[int] | list[str]"):
    ...     verify_parameters(g, a=a, b=b, c=c, d=d)
    ...     print("All parameter types are correct.")
    ... 
    >>> from datetime import date
    >>> g(1, date.today(), 3.14, ["1"])
    All parameter types are correct.
    >>> g(1, 0, 3.14, ["1"])
    TypeError: `b` expected to be of type `date`, but got `0`
    ```
    """

    # 获取函数`func`的所有参数规格
    fullargspec = getfullargspec(func)

    # 获取函数`func`的默认参数
    if fullargspec.defaults is None: # 非关键字参数
        defaults = {}
    else:
        default_args_count = len(fullargspec.defaults)
        defaults = dict(zip(fullargspec.args[-default_args_count:], fullargspec.defaults))
    if fullargspec.kwonlydefaults is not None: # 关键字参数
        defaults.update(fullargspec.kwonlydefaults)

    # 将`parameters`中没有的默认参数添加到`parameters`中
    parameters = defaults | parameters

    # 获取函数`func`的参数类型注释
    annotations = fullargspec.annotations
    annotations.pop("return", None) # 去掉返回值类型

    # 对于在`func`的签名中指定了类型的参数，如果没有在`parameters`中提供，那么将检验它的默认值，如果它也没有默认值，则引发`ValueError`。
    if not set(parameters.keys()).issuperset(set(annotations.keys())):
        raise ValueError("Not providing complete keyword parameters.")

    # 遍历每一个被注释了的参数
    for (para_name, classinfo) in annotations.items():
        # 如果注释的字符串形式的，就尝试将它解析为 Python 对象
        if isinstance(classinfo, str):
            # 这些对象的访问顺序
            class_names = [class_name.strip() for class_name in classinfo.split("|")]
            classinfo = []
            for class_name in class_names:
                try:
                    # 尝试转换为 Python 对象
                    classinfo.append(get_member(class_name))
                except ValueError:
                    # 转换失败
                    continue
            classinfo = tuple(classinfo)

        # 检验
        # 如果从提供的`parameters`里面找不到，就取函数的默认值
        verify_type(object = parameters[para_name], object_name = para_name, classinfo = classinfo)


def type_verifier(func):
    """
    A decorator for performing strict type checking on function parameters.
    Ensures that the arguments passed to the function match the type annotations specified.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 获取非关键字参数名
        nkwarg_names = getfullargspec(func).args

        # 构造非关键字参数的键值对
        nkwargs = dict(zip(nkwarg_names, args))

        # 将这些键值对也添加到给定参数中，检验参数类型
        verify_parameters(func, **(nkwargs | kwargs))

        # 执行原函数
        return func(*args, **kwargs)
    return wrapper


if __name__ == "__main__":
    # 检验`verify_type`函数

    print(verify_type(1, "one", int)) # None
    #print(verify_type(1, "one", str)) # TypeError: `one` expected to be of type `str`, but got `1`
    print(verify_type(1, "one", int | str)) # None
    print(verify_type([1], "a_list", list[int])) # None
    #print(verify_type([1], "a_list", list[str])) # TypeError: `a_list` expected to be of type `list[str]`, but got `[1]`
    print(verify_type([1], "a_list", list[int|str])) # None
    print(verify_type([1], "a_list", list[int] | list[str])) # None
    print(verify_type([1], "a_list", (list[int], list[str]))) # None
    #print(verify_type([1, []], "a_list", (list[int], list[str]))) # TypeError: `a_list` expected to be of type `list[int] | list[str]`, but got `[1, []]`

    # ------

    # 检验`verify_parameters`函数

    def f(a:int, b:bool, c:int|float, d:list[str]):
        verify_parameters(f, a=a, b=b, c=c, d=d)
        print("All parameter types are correct.")

    f(1, True, 1.0, ["1"]) # All parameter types are correct.
    #f(1, True, 1.0, [1]) # TypeError: `d` expected to be of type `list[str]`, but got `[1]`

    def g(a:"int", b:"datetime.date", c:"int|float", d:"list[int] | list[str]"):
        verify_parameters(g, a=a, b=b, c=c, d=d)
        print("All parameter types are correct.")

    from datetime import date
    g(1, date.today(), 3.14, ["1"]) # All parameter types are correct.
    #g(1, 0, 3.14, ["1"]) # TypeError: `b` expected to be of type `date`, but got `0`
