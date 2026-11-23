# example-package

Core library of the example command line tool: all the logic, typed, and it never prints or exits, so any front end can reuse it.

```python
from example_package import greet

greet("Ada")  # "Hello, Ada!"
```

Rename it to your project's import name. See the [development guide](../../docs/development.md).
