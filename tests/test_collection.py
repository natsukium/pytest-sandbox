import urllib.request

url = "https://www.example.com"
req = urllib.request.Request(url)
urllib.request.urlopen(req)


def test_collection():
    raise RuntimeError("Network access is prohibited in the sandbox")
