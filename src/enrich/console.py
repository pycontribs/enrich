"""Module that helps integrating with rich library."""
import io
import sys
from typing import IO, Any, List, Union

import rich.console as rich_console
from rich.ansi import AnsiDecoder


# Base on private utility class from
# https://github.com/willmcgugan/rich/blob/master/rich/progress.py#L476
class FileProxy(io.TextIOBase):
    """Wraps a file (e.g. sys.stdout) and redirects writes to a console."""

    def __init__(self, console: rich_console.Console, file: IO[str]) -> None:
        super().__init__()
        self.__console = console
        self.__file = file
        self.__buffer: List[str] = []

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__file, name)

    def write(self, text: Union[str, bytes]) -> int:
        buffer = self.__buffer
        lines: List[str] = []

        while text:
            if isinstance(text, bytes):
                text = text.decode()
            line, new_line, text = text.partition("\n")
            if new_line:
                lines.append("".join(buffer) + line)
                del buffer[:]
            else:
                buffer.append(line)
                break
        if lines:
            console = self.__console
            with console:
                output = "\n".join(lines)
                console.print(output, markup=False, emoji=False, highlight=False)
        return len(text)

    def flush(self) -> None:
        buffer = self.__buffer
        if buffer:
            self.__console.print("".join(buffer))
            del buffer[:]


class Console(rich_console.Console):
    """Extends rich Console class.

    redirect: True
    soft_wrap: False
    """

    def __init__(self, *args: str, **kwargs: Any) -> None:
        self.redirect = kwargs.get("redirect", False)
        if "redirect" in kwargs:
            del kwargs["redirect"]

        self.soft_wrap = kwargs.get("soft_wrap", False)
        if "soft_wrap" in kwargs:
            del kwargs["soft_wrap"]

        super().__init__(*args, **kwargs)
        self.extended = True
        if self.redirect:
            sys.stdout = FileProxy(self, sys.stdout)  # type: ignore
            sys.stderr = FileProxy(self, sys.stderr)  # type: ignore

    # https://github.com/python/mypy/issues/4441
    def print(self, *args, **kwargs) -> None:  # type: ignore
        """Print override that respects user soft_wrap preference."""
        # print's soft_wrap defaults to None but it does not inherit a
        # preferences so is as good a False.
        # https://github.com/willmcgugan/rich/pull/347/files
        if self.soft_wrap and "soft_wrap" not in kwargs:
            kwargs["soft_wrap"] = self.soft_wrap

        # Currently rich is unable to render ANSI escapes with print so if
        # we detect their presence, we decode them.
        # https://github.com/willmcgugan/rich/discussions/404
        if "\033" in args[0]:
            text = format(*args) + "\n"
            decoder = AnsiDecoder()
            args = list(decoder.decode(text))  # type: ignore
        super().print(*args, **kwargs)
