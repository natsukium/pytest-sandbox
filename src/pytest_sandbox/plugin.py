from __future__ import annotations

import http.client
from typing import Any

import pytest

from .exceptions import NetworkAccessError


def pytest_addoption(parser: pytest.Parser):
    group = parser.getgroup("sandbox", "sandbox test helper")
    group.addoption("--allow-network", action="store_true", help="Allow network access", default=False)


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


def guard(*args: Any, **kwargs: Any):
    raise NetworkAccessError("Network access is prohibited in sandbox")


@pytest.fixture(scope="session", autouse=True)
def xfail_http(pytestconfig: pytest.Config):
    if pytestconfig.getoption("--allow-network"):
        yield

    else:
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(http.client.HTTPConnection, "__init__", guard)

        yield

        monkeypatch.undo()


@pytest.fixture(scope="session", autouse=True)
def xfail_aiohttp(pytestconfig: pytest.Config):
    if pytestconfig.getoption("--allow-network"):
        yield
    else:
        try:
            import aiohttp

            monkeypatch = pytest.MonkeyPatch()
            monkeypatch.setattr(aiohttp.ClientSession, "__init__", guard)

            yield

            monkeypatch.undo()

        except ImportError:
            yield


@pytest.fixture(scope="session", autouse=True)
def xfail_httpcore(pytestconfig: pytest.Config):
    if pytestconfig.getoption("--allow-network"):
        yield
    else:
        try:
            import httpcore

            monkeypatch = pytest.MonkeyPatch()
            # inspired by respx
            # https://github.com/lundberg/respx/blob/1f55faa934ed821cdc0f29186d28ad4614493673/respx/mocks.py#L262-L272
            monkeypatch.setattr(httpcore._sync.connection.HTTPConnection, "handle_request", guard)
            monkeypatch.setattr(httpcore._async.connection.AsyncHTTPConnection, "handle_async_request", guard)

            yield

            monkeypatch.undo()

        except ImportError:
            yield


@pytest.fixture(scope="session", autouse=True)
def xfail_fsspec(pytestconfig: pytest.Config):
    if pytestconfig.getoption("--allow-network"):
        yield
    else:
        try:
            from fsspec.implementations.http import HTTPFileSystem

            monkeypatch = pytest.MonkeyPatch()
            monkeypatch.setattr(HTTPFileSystem, "__init__", guard)

            yield

            monkeypatch.undo()

        except ImportError:
            yield


@pytest.fixture(scope="session", autouse=True)
def xfail_pycares(pytestconfig: pytest.Config):
    if pytestconfig.getoption("--allow-network"):
        yield
    else:
        try:
            import pycares

            monkeypatch = pytest.MonkeyPatch()
            monkeypatch.setattr(pycares.Channel, "__init__", guard)

            yield

            monkeypatch.undo()

        except ImportError:
            yield
