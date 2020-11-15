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
