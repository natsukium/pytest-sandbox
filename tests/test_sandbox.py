import urllib.request

import pytest


@pytest.fixture
def url() -> str:
    return "https://www.example.com"


def test_urllib(url: str):
    req = urllib.request.Request(url)
    urllib.request.urlopen(req)
    raise RuntimeError("Network access is prohibited in the sandbox")


def test_request(url: str):
    requests = pytest.importorskip("requests")
    requests.get(url)
    raise RuntimeError("Network access is prohibited in the sandbox")


@pytest.mark.asyncio
async def test_aiohttp(url: str):
    aiohttp = pytest.importorskip("aiohttp")
    async with aiohttp.ClientSession() as session:
        await session.get(url)
    raise RuntimeError("Network access is prohibited in the sandbox")


def test_httpx(url: str):
    httpx = pytest.importorskip("httpx")
    httpx.get(url)
    raise RuntimeError("Network access is prohibited in the sandbox")


@pytest.mark.asyncio
async def test_httpx_async(url: str):
    httpx = pytest.importorskip("httpx")
    async with httpx.AsyncClient() as client:
        await client.get(url)
    raise RuntimeError("Network access is prohibited in the sandbox")


try:
    import respx

    @pytest.mark.respx(base_url="https://www.example.com")
    def test_with_marker(respx_mock: respx.MockRouter, url: str):
        httpx = pytest.importorskip("httpx")
        respx_mock.get("/baz/").mock(return_value=httpx.Response(204))
        response = httpx.get(f"{url}/baz/")
        assert response.status_code == 204
except ImportError:
    ...


def test_fsspec_httpfilesystem(url: str):
    pytest.importorskip("fsspec")
    from fsspec.implementations.http import HTTPFileSystem

    fs = HTTPFileSystem()
    # xfail from aiohttp is silently killed and returns None
    assert fs.cat(url) is None
    raise RuntimeError("HTTPFileSystem is not xfailed")
