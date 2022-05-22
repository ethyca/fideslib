from __future__ import annotations

from logging import LogRecord
from numbers import Number
from typing import Any, Mapping, Union

MASKED = "MASKED"


class NotPii(str):
    """whitelist non pii data"""


def get_fides_log_record_factory(log_pii: bool = True) -> Any:
    """intercepts default LogRecord for custom handling of params"""

    def factory(
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: str,
        args: Union[tuple[Any, ...], Mapping[str, Any]],
        exc_info: Any,
        func: str = None,
        sinfo: str = None,
    ) -> LogRecord:
        new_args = args
        if not log_pii:
            new_args = tuple(_mask_pii_for_logs(arg) for arg in args)
        return LogRecord(
            name=name,
            level=level,
            pathname=fn,
            lineno=lno,
            msg=msg,
            args=new_args,
            exc_info=exc_info,
            func=func,
            sinfo=sinfo,
        )

    return factory


def _mask_pii_for_logs(parameter: Any) -> Any:
    """
    :param parameter: param that contains possible pii
    :return: depending on ENV config, returns masked pii param.
    Don't mask numeric values as this can throw errors in consumers
    format strings.
    """

    if isinstance(parameter, (NotPii, Number)):
        return parameter

    return MASKED
