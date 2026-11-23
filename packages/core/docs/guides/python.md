# Python guide

How to use `example-package` from your own code.

```bash
pip install example-package
# or
uv add example-package
```

Requires Python 3.11 or newer. The package is fully typed.

```python
from example_package import __version__, greet

print(greet("Ada"))   # Hello, Ada!
print(__version__)
```

## The public API

Everything in `example_package.__all__` is public and follows [Semantic Versioning](https://semver.org/):

| Name | What it is | Guide |
| --- | --- | --- |
| `greet(name)` | Return a greeting for a name. | [Greeting](python/greeting.md) |
| `__version__` | The installed version, as a string. | |

Anything else, and any name starting with `_`, is internal and may change without notice.

## Conventions

- The library never prints and never exits. It returns values or raises exceptions.
- Invalid input raises `ValueError` with a message you can show to a user.
- Nothing is read from the environment or the file system unless a function's guide says so.

## Adding a guide

Write one page per feature under `guides/python/`, linked from the table above. Show a short example, list the arguments and what is returned, and name the exceptions it raises.
