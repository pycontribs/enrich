"""Tests related to enriched RichHandler"""
import io
import logging
import re
from typing import Tuple, Union

import pytest

from enrich.console import Console
from enrich.logging import RichHandler


def strip_ansi_escape(text: Union[str, bytes]) -> str:
    """Remove all ANSI escapes from string or bytes.

    If bytes is passed instead of string, it will be converted to string
    using UTF-8.
    """
    if isinstance(text, bytes):
        text = text.decode("utf-8")

    return re.sub(r"\x1b[^m]*m", "", text)


@pytest.fixture(name="rich_logger")
def rich_logger_fixture() -> Tuple[logging.Logger, logging.Handler]:
    """Returns tuple with logger and handler to be tested."""
    rich_handler = RichHandler(
        console=Console(
            file=io.StringIO(),
            force_terminal=True,
            width=80,
            color_system="truecolor",
            soft_wrap=True,
        ),
        enable_link_path=False,
    )

    logging.basicConfig(
        level="NOTSET", format="%(message)s", datefmt="[DATE]", handlers=[rich_handler]
    )
    rich_log = logging.getLogger("rich")
    rich_log.addHandler(rich_handler)
    return (rich_log, rich_handler)


def test_logging(rich_logger) -> None:
    """Test that logger does not wrap."""

    (logger, rich_handler) = rich_logger

    text = 10 * "x"  # a long text that would likely wrap on a normal console
    logger.error("%s %s", text, 123)

    # verify that the long text was not wrapped
    output = strip_ansi_escape(rich_handler.console.file.getvalue())
    assert text in output
    assert "ERROR" in output
    assert "\n" not in output[:-1]


if __name__ == "__main__":
    handler = RichHandler(
        console=Console(
            force_terminal=True,
            width=55510,  # this is expected to have no effect
            color_system="truecolor",
            soft_wrap=True,
        ),
        enable_link_path=False,
        show_time=True,
        show_level=True,
        show_path=True,
    )
    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        # datefmt="[DATE]",
        handlers=[handler],
    )
    log = logging.getLogger("rich")
    # log.addHandler(handler)
    data = {"foo": "text", "bar": None, "number": 123}
    log.error("This was a long error")
    log.warning("This was warning %s apparently", 123)
    log.info("Having info is good")
    log.debug("Some kind of debug message %s", None)
    log.info("Does this dictionary %s render ok?", data)
