"""Module that helps integrating with rich library."""
import io
import os
import sys
from typing import IO, Any, List, TextIO, Union

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
    """Extends rich Console class."""

    def __init__(
        self, *args: str, redirect: bool = True, soft_wrap: bool = True, **kwargs: Any
    ) -> None:
        """
        enrich console does soft-wrapping by default and this diverge from
        original rich console which does not, creating hard-wraps instead.
        """
        self.redirect = redirect
        self.soft_wrap = soft_wrap

        # Unless user already mentioning terminal preference, we use our
        # heuristic to make an informed decision.
        if "force_terminal" not in kwargs:
            kwargs["force_terminal"] = should_do_markup(
                stream=kwargs.get("file", sys.stdout)
            )

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
        if args and isinstance(args[0], str) and "\033" in args[0]:
            text = format(*args) + "\n"
            decoder = AnsiDecoder()
            args = list(decoder.decode(text))  # type: ignore
        super().print(*args, **kwargs)


# Based on Ansible implementation
def to_bool(value: Any) -> bool:
    """Return a bool for the arg."""
    if value is None or isinstance(value, bool):
        return bool(value)
    if isinstance(value, str):
        value = value.lower()
    if value in ("yes", "on", "1", "true", 1):
        return True
    return False


def should_do_markup(stream: TextIO = sys.stdout) -> bool:
    """Decide about use of ANSI colors."""
    py_colors = None

    # https://xkcd.com/927/
    for env_var in ["PY_COLORS", "CLICOLOR", "FORCE_COLOR", "ANSIBLE_FORCE_COLOR"]:
        value = os.environ.get(env_var, None)
        if value is not None:
            py_colors = to_bool(value)
            break

    # If deliverately disabled colors
    if os.environ.get("NO_COLOR", None):
        return False

    # User configuration requested colors
    if py_colors is not None:
        return to_bool(py_colors)

    term = os.environ.get("TERM", "")
    if "xterm" in term:
        return True

    if term == "dumb":
        return False

    # Use tty detection logic as last resort because there are numerous
    # factors that can make isatty return a misleading value, including:
    # - stdin.isatty() is the only one returning true, even on a real terminal
    # - stderr returting false if user user uses a error stream coloring solution
    return stream.isatty()
