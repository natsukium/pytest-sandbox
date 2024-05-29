import pytest


@pytest.fixture(autouse=True)
def xfail_http():
    """Override and disable the default fixture.

    Yields: nothing

    """
    yield
