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
    try:
        import requests
    except ImportError:
        pytest.skip("requests is not installed")

    requests.get(url)
    raise RuntimeError("Network access is prohibited in the sandbox")


@pytest.mark.asyncio
async def test_aiohttp(url: str):
    try:
        import aiohttp
    except ImportError:
        pytest.skip("aiohttp is not installed")

    async with aiohttp.ClientSession() as session:
        await session.get(url)
    raise RuntimeError("Network access is prohibited in the sandbox")


def test_httpx(url: str):
    try:
        import httpx
    except ImportError:
        pytest.skip("httpx is not installed")

    httpx.get(url)
    raise RuntimeError("Network access is prohibited in the sandbox")


@pytest.mark.asyncio
async def test_httpx_async(url: str):
    try:
        import httpx
    except ImportError:
        pytest.skip("httpx is not installed")

    async with httpx.AsyncClient() as client:
        await client.get(url)
    raise RuntimeError("Network access is prohibited in the sandbox")
