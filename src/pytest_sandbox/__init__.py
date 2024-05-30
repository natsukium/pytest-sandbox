from __future__ import annotations

import http.client
from typing import Any

import pytest

__version__ = "0.0.1"


def pytest_addoption(parser: pytest.Parser):
    group = parser.getgroup("sandbox", "sandbox test helper")
    group.addoption("--allow-network", action="store_true", help="Allow network access", default=False)


def xfail(*args: Any, **kwargs: Any):
    pytest.xfail("try to access network")


@pytest.fixture(scope="session", autouse=True)
def xfail_http(pytestconfig: pytest.Config):
    if pytestconfig.getoption("--allow-network"):
        yield

    else:
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(http.client.HTTPConnection, "__init__", xfail)

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
            monkeypatch.setattr(aiohttp.ClientSession, "__init__", xfail)

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
            monkeypatch.setattr(httpcore.Request, "__init__", xfail)

            yield

            monkeypatch.undo()

        except ImportError:
            yield
