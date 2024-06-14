import sys

import pytest
from pytest_sandbox.exceptions import NetworkAccessError
from pytest_sandbox.utils import expand_exception_group, extract_all_exceptions, has_exception_group, unfold

if (sys.version_info < (3, 11)) and has_exception_group:
    from exceptiongroup import ExceptionGroup


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


@pytest.mark.skipif(not has_exception_group, reason="ExceptionGroup is added in Python3.11")
def test_expand_exception_group():
    """Basic test for expand_exception_group"""
    e: pytest.ExceptionInfo[ExceptionGroup[Exception]]
    with pytest.raises(ExceptionGroup) as e:
        raise ExceptionGroup("raise exception group", [ValueError("exception1"), RuntimeError("exception2")])

    excs = list(expand_exception_group(e.value))
    assert len(excs) == 3

    for actually, expect in zip(excs, [ExceptionGroup, ValueError, RuntimeError]):
        assert isinstance(actually, expect)


@pytest.mark.skipif(not has_exception_group, reason="ExceptionGroup is added in Python3.11")
def test_expand_exception_group_recursive():
    """Nested ExceptionGroup test for expand_exception_group

    It is expected that the all exceptions included ExceptionGroup
    are in a flatten sequence.
    """

    def exception_tree(depth: int):
        def loop(eg: ExceptionGroup[Exception] | Exception, cnt: int) -> ExceptionGroup[Exception] | Exception:
            if cnt >= depth:
                return eg
            else:
                return loop(
                    ExceptionGroup(f"exception group {cnt}", [eg, RuntimeError(f"leaf exception {cnt}")]), cnt + 1
                )

        return loop(ValueError("origin exception"), 0)

    depth = 3
    e: pytest.ExceptionInfo[ExceptionGroup[Exception]]
    with pytest.raises(ExceptionGroup) as e:
        raise exception_tree(depth)

    excs = list(expand_exception_group(e.value))

    # (ExceptionGroup + leaf RuntimeError) * depth + origin ValueError
    assert len(excs) == depth * 2 + 1
    assert len(list(filter(lambda x: isinstance(x, ExceptionGroup), excs))) == depth
    assert len(list(filter(lambda x: isinstance(x, RuntimeError), excs))) == depth
    assert len(list(filter(lambda x: isinstance(x, ValueError), excs))) == 1


def test_expand_exception_group_without_group():
    """Without ExceptionGroup test for expand_exception_group

    expand_exception_group can receive an Exception and return it.
    This behavior is compatible with Python 3.10 or older version.
    """
    with pytest.raises(RuntimeError) as e:
        raise RuntimeError("step2") from ValueError("step1")

    excs = list(expand_exception_group(e.value))

    assert len(excs) == 1
    assert isinstance(excs[0], RuntimeError)
