import pytest


@pytest.mark.network
def test_allow_network(pytester: pytest.Pytester):
    file = pytester.makepyfile("""
        import urllib.request

        import pytest


        def test_urllib():
            req = urllib.request.Request("https://www.example.com")
            with urllib.request.urlopen(req) as res:
                assert res.status == 200
    """)

    result = pytester.runpytest(file, "-v", "--allow-network")
    result.stdout.fnmatch_lines(["*test_urllib PASSED*"])
    assert result.ret == 0
