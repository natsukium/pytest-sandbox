from __future__ import annotations

import socket
from typing import Any, Callable, Generator, NoReturn

import pytest
from _pytest.nodes import Node
from _pytest.reports import BaseReport
from pluggy import Result
from pytest import CallInfo

from .exceptions import NetworkAccessError
from .utils import extract_all_exceptions


def pytest_addoption(parser: pytest.Parser):
    group = parser.getgroup("sandbox", "sandbox test helper")
    group.addoption("--allow-network", action="store_true", help="Allow network access", default=False)


def xfail(*args: Any, **kwargs: Any):
    pytest.xfail("Network access is prohibited in sandbox")


def raise_error(*args: Any, **kwargs: Any):
    raise NetworkAccessError("Network access is prohibited in sandbox")


def patch(monkeypatch: pytest.MonkeyPatch, block_method: Callable[[Any], NoReturn] = raise_error):
    monkeypatch.setattr(socket.socket, "connect", block_method)
    monkeypatch.setattr(socket.socket, "connect_ex", block_method)
    # monkeypatch.setattr(http.client.HTTPConnection, "__init__", block_method)
    # try:
    #     import aiohttp
    #
    #     monkeypatch.setattr(aiohttp.ClientSession, "__init__", block_method)
    # except ImportError:
    #     ...
    # try:
    #     import httpcore
    #
    #     # inspired by respx
    #     # https://github.com/lundberg/respx/blob/1f55faa934ed821cdc0f29186d28ad4614493673/respx/mocks.py#L262-L272
    #     monkeypatch.setattr(httpcore._sync.connection.HTTPConnection, "handle_request", block_method)
    #     monkeypatch.setattr(httpcore._async.connection.AsyncHTTPConnection, "handle_async_request", block_method)
    #
    # except ImportError:
    #     ...
    # try:
    #     from fsspec.implementations.http import HTTPFileSystem
    #
    #     monkeypatch.setattr(HTTPFileSystem, "__init__", block_method)
    # except ImportError:
    #     ...
    try:
        import pycares

        monkeypatch.setattr(pycares.Channel, "__init__", block_method)
    except ImportError:
        ...


@pytest.hookimpl
def pytest_collection(session: pytest.Session):
    monkeypatch = pytest.MonkeyPatch()
    session._monkeypatch = monkeypatch  # pyright: ignore [reportAttributeAccessIssue]
    if session.config.getoption("--allow-network"):
        return
    patch(monkeypatch)


@pytest.hookimpl
def pytest_collection_finish(session: pytest.Session):
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


@pytest.fixture(scope="session", autouse=True)
def xfail_network(pytestconfig: pytest.Config):
    if pytestconfig.getoption("--allow-network"):
        yield
    else:
        monkeypatch = pytest.MonkeyPatch()
        patch(monkeypatch)

        yield

        monkeypatch.undo()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[Any]
) -> Generator[None, Result[pytest.TestReport], pytest.TestReport]:
    result = yield
    report = result.get_result()
    if call.excinfo is not None:
        for exc in extract_all_exceptions(call.excinfo.value):
            if isinstance(exc, ExceptionGroup):
                report.outcome = "skipped"
                report.wasxfail = "Network access is forbidden in sandbox"

            if isinstance(exc, NetworkAccessError):
                report.outcome = "skipped"
                report.wasxfail = "Network access is forbidden in sandbox"
    return report


# @pytest.hookimpl
# def pytest_runtest_call(item: pytest.Item):
#     """
#
#     Args:
#         item:
#     """
#     try:
#         item.runtest()
#     except NetworkAccessError:
#         pytest.xfail("Network Access is forbidden in sandbox")
