import sys
from typing import Callable, Iterator, TypeVar

if sys.version_info >= (3, 11):
    has_exception_group = True
else:
    try:
        from exceptiongroup import ExceptionGroup

        has_exception_group = True
    except ImportError:
        # dummy class for compatibility
        class ExceptionGroup: ...

        has_exception_group = False

S = TypeVar("S")
T = TypeVar("T")


def unfold(f: Callable[[S], tuple[T, S] | None], state: S) -> Iterator[T]:
    if s := f(state):
        value, _state = s
        yield value
        yield from unfold(f, _state)
    else:
        return


def extract_all_exceptions(exc: BaseException) -> Iterator[BaseException]:
    def f(e: BaseException | None):
        if e is None:
            return None
        elif e.__context__:
            return e, e.__context__
        elif e.__cause__:
            return e, e.__cause__
        else:
            return e, None

    return unfold(f, exc)


def expand_exception_group(exc: Exception) -> Iterator[Exception]:
    # def f_compat(es: tuple[Exception, ...]):
    #     if len(es) == 0:
    #         return None
    #     else:
    #         return es[0], es[1:]
    #
    # if compat:
    #     return unfold(f_compat, (exc,))

    def f(es: tuple[Exception, ...]):
        if len(es) == 0:
            return None
        elif isinstance(es[0], ExceptionGroup):
            e: ExceptionGroup[Exception] = es[0]
            return e, (*es[1:], *e.exceptions)
        else:
            return es[0], es[1:]

    return unfold(f, (exc,))
