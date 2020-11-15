# enrich

Enriched extends rich functionality with a set of changes that were not
accepted as contributions to rich itself.

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
