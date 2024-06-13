from __future__ import annotations

import http.client
from typing import Any

import pytest
from _pytest.nodes import Node
from _pytest.reports import BaseReport
from pytest import CallInfo

from .exceptions import NetworkAccessError


def pytest_addoption(parser: pytest.Parser):
    group = parser.getgroup("sandbox", "sandbox test helper")
    group.addoption("--allow-network", action="store_true", help="Allow network access", default=False)


def guard(*args: Any, **kwargs: Any):
    raise NetworkAccessError("Network access is prohibited in sandbox")


@pytest.hookimpl
def pytest_sessionstart(session: pytest.Session):
    monkeypatch = pytest.MonkeyPatch()
    session._monkeypatch = monkeypatch  # pyright: ignore [reportAttributeAccessIssue]
    if session.config.getoption("--allow-network"):
        return
    monkeypatch.setattr(http.client.HTTPConnection, "__init__", guard)
    try:
        import aiohttp

        monkeypatch.setattr(aiohttp.ClientSession, "__init__", guard)
    except ImportError:
        ...
    try:
        import httpcore

        # inspired by respx
        # https://github.com/lundberg/respx/blob/1f55faa934ed821cdc0f29186d28ad4614493673/respx/mocks.py#L262-L272
        monkeypatch.setattr(httpcore._sync.connection.HTTPConnection, "handle_request", guard)
        monkeypatch.setattr(httpcore._async.connection.AsyncHTTPConnection, "handle_async_request", guard)

    except ImportError:
        ...
    try:
        from fsspec.implementations.http import HTTPFileSystem

        monkeypatch.setattr(HTTPFileSystem, "__init__", guard)
    except ImportError:
        ...
    try:
        import pycares

        monkeypatch.setattr(pycares.Channel, "__init__", guard)
    except ImportError:
        ...


@pytest.hookimpl
def pytest_sessionfinish(session: pytest.Session):
    session._monkeypatch.undo()  # pyright: ignore [reportAttributeAccessIssue]


@pytest.hookimpl
def pytest_exception_interact(node: Node, call: CallInfo[Any], report: BaseReport):
    """

    Args:
        node:
        call:
        report:
    """
    if call.excinfo is None:
        return

    if (call.excinfo.type is NetworkAccessError) and isinstance(report, pytest.CollectReport):
        report.outcome = "skipped"
        print(f"\n{report.nodeid}: skipped because network access is forbidden in sandbox")


@pytest.hookimpl
def pytest_runtest_call(item: pytest.Item):
    """

    Args:
        item:
    """
    try:
        item.runtest()
    except NetworkAccessError:
        pytest.xfail("Network Access is forbidden in sandbox")
