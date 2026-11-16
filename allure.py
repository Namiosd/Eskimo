"""
Lightweight fallback module for `allure` when `allure-pytest` is not installed.
Provides no-op step context managers, decorators, and attachment helpers so tests
and IDE type-checkers work seamlessly without requiring external network packages.
"""

from typing import Any, Callable


class _StepContext:
    def __init__(self, title: str = "", *args: Any, **kwargs: Any) -> None:
        self.title = title

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        return func

    def __enter__(self) -> "_StepContext":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        return False


def step(title: str = "", *args: Any, **kwargs: Any) -> _StepContext:
    return _StepContext(title, *args, **kwargs)


def _noop_decorator(*args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def _wrap(func: Callable[..., Any]) -> Callable[..., Any]:
        return func
    return _wrap


feature = _noop_decorator
story = _noop_decorator
title = _noop_decorator
severity = _noop_decorator
issue = _noop_decorator
description = _noop_decorator


def attach(body: Any = None, name: str = "", attachment_type: Any = None, extension: str = "") -> None:
    return None


class attachment_type:
    TEXT = "text/plain"
    PNG = "image/png"
    XML = "application/xml"
    HTML = "text/html"
    JSON = "application/json"


class severity_level:
    BLOCKER = "blocker"
    CRITICAL = "critical"
    NORMAL = "normal"
    MINOR = "minor"
    TRIVIAL = "trivial"
