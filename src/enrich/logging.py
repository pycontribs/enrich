"""Implements enriched RichHandler"""
from datetime import datetime
from typing import TYPE_CHECKING, Iterable, Optional

from rich.logging import RichHandler as OriginalRichHandler
from rich.text import Text, TextType

if TYPE_CHECKING:
    from rich.console import Console, ConsoleRenderable


# Based on https://github.com/willmcgugan/rich/blob/master/rich/_log_render.py
class FluidLogRender:  # pylint: disable=too-few-public-methods
    """Renders log by not using columns and avoiding any wrapping."""

    def __init__(
        self,
        show_time: bool = False,
        show_level: bool = False,
        show_path: bool = True,
        time_format: str = "[%x %X]",
    ) -> None:
        self.show_time = show_time
        self.show_level = show_level
        self.show_path = show_path
        self.time_format = time_format
        self._last_time: Optional[str] = None

    def __call__(  # pylint: disable=too-many-arguments
        self,
        console: "Console",
        renderables: Iterable["ConsoleRenderable"],
        log_time: datetime = None,
        time_format: str = None,
        level: TextType = "",
        path: str = None,
        line_no: int = None,
        link_path: str = None,
    ) -> Text:

        result = Text()
        if self.show_time:
            if log_time is None:
                log_time = datetime.now()
            log_time_display = log_time.strftime(time_format or self.time_format) + " "
            if log_time_display == self._last_time:
                result += Text(" " * len(log_time_display))
            else:
                result += Text(log_time_display)
                self._last_time = log_time_display
        if self.show_level:
            if not isinstance(level, Text):
                level = Text(level)
            if len(level) < 8:
                level += " " * (8 - len(level))
            result += level

        for elem in renderables:
            result += elem

        if self.show_path and path:
            path_text = Text(" ", style="repr.filename")
            path_text.append(
                path, style=f"link file://{link_path}" if link_path else ""
            )
            if line_no:
                path_text.append(f":{line_no}")
            result += path_text

        return result


class RichHandler(OriginalRichHandler):
    """Enriched handler that does not wrap."""

    def __init__(self, *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)
        # RichHandler constructor does not allow custom renderer
        # https://github.com/willmcgugan/rich/issues/438
        self._log_render = FluidLogRender(
            show_time=kwargs.get("show_time", False),
            show_level=kwargs.get("show_level", True),
            show_path=kwargs.get("show_path", False),
        )
