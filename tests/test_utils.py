import pytest
from pytest_sandbox.exceptions import NetworkAccessError
from pytest_sandbox.utils import extract_all_exceptions, unfold


def test_unfold():
    def f(x: int):
        if x > 5:
            return None
        else:
            return x, x + 1

    assert list(unfold(f, 0)) == [0, 1, 2, 3, 4, 5]


def test_extract_all_exceptions():
    def raise_exception_chain():
        try:
            raise ValueError("step2") from AttributeError("step1")
        except ValueError as exc:
            raise RuntimeError("step3") from exc

    with pytest.raises(Exception) as e:
        raise_exception_chain()

    chain = list(extract_all_exceptions(e.value))

    assert len(chain) == 3

    for actually, expect in zip(chain, [RuntimeError, ValueError, AttributeError]):
        assert isinstance(actually, expect)


def test_nested_network_access_error():
    def raise_exception_chain():
        try:
            raise NetworkAccessError("step2") from AttributeError("step1")
        except NetworkAccessError as exc:
            raise RuntimeError("step3") from exc

    with pytest.raises(Exception) as e:
        raise_exception_chain()

    assert not isinstance(e.value, NetworkAccessError)
    assert isinstance(e.value, RuntimeError)


def test_extract_nested_network_access_error():
    def raise_exception_chain():
        try:
            raise NetworkAccessError("step2") from AttributeError("step1")
        except NetworkAccessError as exc:
            raise RuntimeError("step3") from exc

    with pytest.raises(Exception) as e:
        raise_exception_chain()

    assert any(map(lambda x: isinstance(x, NetworkAccessError), extract_all_exceptions(e.value)))
