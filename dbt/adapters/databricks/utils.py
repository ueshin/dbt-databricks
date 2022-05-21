import functools
import inspect
from typing import Any, Callable, Type, TypeVar

from jinja2.runtime import Undefined


T = TypeVar("T")


def remove_undefined(v: Any) -> Any:
    return None if isinstance(v, Undefined) else v


def undefined_proof(cls: Type[T]) -> Type[T]:
    for name, func in inspect.getmembers(cls, inspect.isfunction):
        if name.startswith("_"):
            continue
        try:
            isstatic = isinstance(inspect.getattr_static(cls, name), staticmethod)
        except AttributeError:
            isstatic = False
        wrapped_function = _wrap_function(func)
        setattr(cls, name, staticmethod(wrapped_function) if isstatic else wrapped_function)

    return cls


def _wrap_function(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        new_args = [remove_undefined(arg) for arg in args]
        new_kwargs = {key: remove_undefined(value) for key, value in kwargs.items()}
        return func(*new_args, **new_kwargs)

    return wrapper
