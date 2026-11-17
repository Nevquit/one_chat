"""空追踪适配器：本地开发与测试的默认实现。

``TracePort`` 要求 ``span`` 返回上下文管理器；这里只做占位，
不产生任何网络请求，也不记录敏感数据。
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any


class NoopTrace:
    """实现 ``TracePort``：进入即返回，失败与耗时都不上报。"""

    @contextmanager
    def span(self, name: str, **attributes: Any) -> Iterator[None]:
        yield
