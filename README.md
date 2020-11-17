# enrich

Enriched extends [rich](https://pypi.org/project/rich/) library functionality
with a set of changes that were not accepted to rich itself.

## Console with redirect support

Our Console class adds one additional option to rich.Console in order to
redirect `sys.stdout` and `sys.stderr` streams using a FileProxy.

```python
from enrich.console import Console
import sys

console = Console(
    redirect=True,  # <-- not supported by rich.cosole.Console
    record=True)
sys.write("foo")

# this assert would have passed without redirect=True
assert console.export_text() == "foo"
```

## Console with implicit soft wrapping

If you want to produce fluid terminal output, one where the client terminal
decides where to wrap the text instead of the application, you can now
tell the Console constructor the soft_wrap preference.

```python
from enrich.console import Console
import sys

console = Console(soft_wrap=True)
console.print(...)  # no longer need to pass soft_wrap to each print
```

## Console.print can also deal with ANSI escapes

Extends Rich Console to detect if original text already had ANSI escapes and
decodes it before processing it. This solves the case where printing
output captured from other processes that contained ANSI escapes would brake.
[upstream-404](https://github.com/willmcgugan/rich/discussions/404)

## Soft-wrapping logger

Rich logger assumes that you always have a fixed width console and it does
wrap logged output according to it. Our alternative logger does exactly the
opposite: it ignores the columns of the current console and prints output
using a Console with soft wrapping enabled.

The result are logged lines that can be displayed on any terminal or web
page as they will allow the client to decide when to perform the wrapping.

```python
import logging
from enrich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")
log.info("Text that we do not want pre-wrapped by logger: %s", 100 * "x")
```
