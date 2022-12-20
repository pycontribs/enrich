"""Tests for rich module."""
import io
import sys

import pytest
from pytest_mock import MockFixture

from enrich.console import Console, should_do_markup


def test_rich_console_ex() -> None:
    """Validate that ConsoleEx can capture output from print() calls."""
    console = Console(record=True, redirect=True)
    console.print("alpha")
    print("beta")
    sys.stdout.write("gamma\n")
    sys.stderr.write("delta\n")
    # While not supposed to happen we want to be sure that this will not raise
    # an exception. Some libraries may still sometimes send bytes to the
    # streams, notable example being click.
    # sys.stdout.write(b"epsilon\n")  # type: ignore
    text = console.export_text()
    assert text == "alpha\nbeta\ngamma\ndelta\n"


def test_rich_console_ex_ansi() -> None:
    """Validate that ANSI sent to sys.stdout does not become garbage in record."""
    print()
    console = Console(force_terminal=True, record=True, redirect=True)
    console.print("[green]this from Console.print()[/green]", style="red")

    text = console.export_text(clear=False)
    assert "this from Console" in text

    html = console.export_html(clear=False)
    assert "#008000" in html


def test_console_soft_wrap() -> None:
    """Assures long prints on console are not wrapped when requested."""
    console = Console(
        file=io.StringIO(), width=20, record=True, soft_wrap=True, redirect=False
    )
    text = 21 * "x"
    console.print(text, end="")
    assert console.file.getvalue() == text  # type: ignore
    result = console.export_text()
    assert text in result


def test_console_print_ansi() -> None:
    """Validates that Console.print() with ANSI does not make break them."""
    console = Console(force_terminal=True, record=True, soft_wrap=True, redirect=True)
    text = "\033[92mfuture is green!\033[0m"
    console.print(text)
    text_result = console.export_text(clear=False)
    assert "future is green!" in text_result
    html_result = console.export_html()
    assert "#00ff00" in html_result


def test_markup_detection_pycolors0() -> None:
    """Assure PY_COLORS=0 disables markup."""
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("PY_COLORS", "0")
        assert not should_do_markup()


def test_markup_detection_pycolors1() -> None:
    """Assure PY_COLORS=1 enables markup."""
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("PY_COLORS", "1")
        assert should_do_markup()


def test_markup_detection_tty_yes(mocker: MockFixture) -> None:
    """Assures TERM=xterm enables markup."""
    mocker.patch("sys.stdout.isatty", return_value=True)
    mocker.patch("os.environ", {"TERM": "xterm"})
    assert should_do_markup()
    mocker.resetall()
    mocker.stopall()


def test_markup_detection_tty_no(mocker: MockFixture) -> None:
    """Assures that if no tty is reported we disable markup."""
    mocker.patch("os.environ", {})
    mocker.patch("sys.stdout.isatty", return_value=False)
    assert not should_do_markup()
    mocker.resetall()
    mocker.stopall()


if __name__ == "__main__":
    test_console_print_ansi()
