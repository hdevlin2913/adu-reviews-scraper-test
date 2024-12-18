import inspect
from functools import partial, wraps
from typing import Any, Callable

import asyncer
import typer
from typer.models import CommandFunctionType


class AsyncTyper(typer.Typer):
    @staticmethod
    def maybe_run_async(decorator: Any, f: Callable) -> Any:
        if inspect.iscoroutinefunction(f):

            @wraps(f)
            def runner(*args, **kwargs) -> Any:  # type: ignore
                return asyncer.runnify(f)(*args, **kwargs)

            decorator(runner)
        else:
            decorator(f)
        return f

    def callback(self, *args, **kwargs) -> Callable[[CommandFunctionType], CommandFunctionType]:  # type: ignore
        decorator = super().callback(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)

    def command(self, *args, **kwargs) -> Callable[[CommandFunctionType], CommandFunctionType]:  # type: ignore
        decorator = super().command(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)
