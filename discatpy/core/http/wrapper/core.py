"""
The MIT License (MIT)

Copyright (c) 2022-present EmreTech

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from dataclasses import KW_ONLY, dataclass
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from ...file import BasicFile
from ...types import MISSING, MissingOr, MissingType, Snowflake
from ...utils import _create_fn, _indent_all_text, _from_import

__all__ = (
    "APIEndpointData",
    "CoreMixin",
)


@dataclass
class APIEndpointData:
    method: Literal["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"]
    path: str
    _: KW_ONLY
    format_args: Optional[Dict[str, MissingOr[Any]]] = None
    param_args: Optional[List[Union[
        Tuple[str],
        Tuple[str, Any],
        Tuple[str, Any, Any],
    ]]] = None
    supports_reason: bool = False
    supports_files: bool = False


def _generate_args(data: APIEndpointData):
    func_args = ["self"]

    if data.format_args is not None:
        for name, annotation in data.format_args.items():
            arg = f"{name}"
            if not isinstance(annotation, MissingType):
                arg += f": {annotation.__name__}"

            func_args.append(arg)

    if data.param_args is not None:
        func_args.append("*")

        for arg in data.param_args:
            str_arg = ""
            if len(arg) >= 1:
                arg_name = arg[0]
                str_arg += arg_name
            if len(arg) >= 2:
                # Pyright doesn't understand that this if statement only applies to two tuples
                arg_annotation = arg[1]  # type: ignore
                str_arg += f": {arg_annotation.__name__}"  # type: ignore
            if len(arg) == 3:
                arg_default = arg[2]
                str_arg += f" = {arg_default}"

            func_args.append(str_arg)

    return func_args


def _generate_body(data: APIEndpointData):
    body: List[str] = []
    params_dict_name = "{0}_params"

    if data.param_args is not None:
        params_dict_name = params_dict_name.format("query" if data.method == "GET" else "json")
        body.append(f"{params_dict_name}: Dict[str, Any] = {{}}")

        template_if_statment = 'if {0} is not MISSING:\n                {1}["{0}"] = {0}'

        for arg in data.param_args:
            arg_name = str(arg[0])

            if data.supports_reason and arg_name == "reason":
                continue

            body.append(template_if_statment.format(arg_name, params_dict_name))

    request_line = f'return await self.request("{data.method}", "{data.path}", '

    if data.format_args is not None:
        url_format_params = "{"
        for arg_name in data.format_args.keys():
            url_format_params += f'"{arg_name}": {arg_name}, '
        url_format_params += "}"

        request_line += f"{url_format_params}, "

    if data.param_args is not None:
        request_line += f"{params_dict_name}={params_dict_name}, "

    if data.supports_reason:
        request_line += f"reason=reason, "

    request_line += ")"

    body.append(request_line)
    return _indent_all_text(body)


class CoreMixinMeta(type):
    def __new__(cls, name: str, bases: Tuple[type], attrs: Dict[str, Any], **kwargs: Any):
        orig_keys = list(attrs.keys())

        for k in orig_keys:
            v = attrs.get(k)

            if isinstance(v, APIEndpointData):
                if v.supports_reason:
                    if v.param_args is None:
                        v.param_args = []
                    v.param_args.append(("reason", Optional[str], None))

                if v.supports_files:
                    if v.param_args is None:
                        v.param_args = []
                    v.param_args.append(("files", MissingOr[List[BasicFile]], MISSING))

                func_args = _generate_args(v)
                func_body = _generate_body(v)

                func_locals = {
                    "Snowflake": Snowflake,
                    "MISSING": MISSING,
                    "_Missing": MissingType,
                    "MissingOr": MissingOr,
                    "BasicFile": BasicFile,
                }
                _from_import(
                    "typing",
                    func_locals,
                    [
                        "Any",
                        "Dict",
                        "List",
                        "Optional",
                        "Tuple",
                        "Type",
                        "Union",
                    ],
                )
                _from_import("discord_typings", func_locals)
                _from_import(
                    "datetime",
                    func_locals,
                    [
                        "datetime",
                    ],
                )

                func = _create_fn(k, func_args, func_body, locals=func_locals, asynchronous=True)
                attrs[k] = func

        return super(CoreMixinMeta, cls).__new__(cls, name, bases, attrs, **kwargs)


class CoreMixin(metaclass=CoreMixinMeta):
    pass