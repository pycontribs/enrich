"""Implements enriched RichHandler."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from rich.logging import RichHandler as OriginalRichHandler
from rich.text import Text, TextType

if TYPE_CHECKING:
    from collections.abc import Iterable

    from rich.console import Console, ConsoleRenderable


# Based on https://github.com/willmcgugan/rich/blob/master/rich/_log_render.py
class FluidLogRender:  # pylint: disable=too-few-public-methods
    """Renders log by not using columns and avoiding any wrapping."""

    # pylint: disable=too-many-arguments
    def __init__(  # noqa: PLR0913
        self,
        show_time: bool = False,
        show_level: bool = False,
        show_path: bool = True,
        time_format: str = "[%x %X]",
        omit_repeated_times: bool = True,
    ) -> None:
        """Construcs instance."""
        self.show_time = show_time
        self.show_level = show_level
        self.show_path = show_path
        self.time_format = time_format
        self.omit_repeated_times = omit_repeated_times
        self._last_time: str | None = None

    def __call__(  # pylint: disable=too-many-arguments # noqa: PLR0913
        self,
        console: Console,  # noqa: ARG002
        renderables: Iterable[ConsoleRenderable],
        log_time: datetime | None = None,
        time_format: str | None = None,
        level: TextType = "",
        path: str | None = None,
        line_no: int | None = None,
        link_path: str | None = None,
    ) -> Text:
        """Call."""
        result = Text()
        if self.show_time:
            if log_time is None:
                log_time = datetime.now(tz=timezone.utc)
            log_time_display = log_time.strftime(time_format or self.time_format) + " "
            if self.omit_repeated_times and log_time_display == self._last_time:
                result += Text(" " * len(log_time_display))
            else:
                result += Text(log_time_display)
                self._last_time = log_time_display
        if self.show_level:
            if not isinstance(level, Text):
                level = Text(level)
            # CRITICAL is the longest identifier from default set.
            if len(level) < 9:  # noqa: PLR2004
                level += " " * (9 - len(level))
            result += level

        for elem in renderables:
            result += elem

        if self.show_path and path:
            path_text = Text(" ", style="repr.filename")
            path_text.append(
                path,
                style=f"link file://{link_path}" if link_path else "",
            )
            if line_no:
                path_text.append(f":{line_no}")
            result += path_text

        return result


class RichHandler(OriginalRichHandler):
    """Enriched handler that does not wrap."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create the handler."""
        super().__init__(*args, **kwargs)
        # RichHandler constructor does not allow custom renderer
        # https://github.com/willmcgugan/rich/issues/438
        self._log_render = FluidLogRender(
            show_time=kwargs.get("show_time", False),
            show_level=kwargs.get("show_level", True),
            show_path=kwargs.get("show_path", False),
            omit_repeated_times=kwargs.get("omit_repeated_times", True),
        )  # type: ignore
