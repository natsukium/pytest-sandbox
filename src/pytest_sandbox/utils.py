from typing import Callable, Iterator, TypeVar

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
