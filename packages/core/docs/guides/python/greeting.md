# Greeting

`greet` builds a greeting. It is the library's example function: replace it with your own, keeping the shape of this page for each feature.

```python
from example_package import greet

greet("Ada")        # 'Hello, Ada!'
greet("  Ada  ")    # 'Hello, Ada!'  (surrounding whitespace is removed)
```

## Signature

```python
def greet(name: str) -> str: ...
```

| Argument | Meaning |
| --- | --- |
| `name` | Who to greet. Leading and trailing whitespace is removed. |

Returns the text `Hello, <name>!`.

## Errors

| Exception | When |
| --- | --- |
| `ValueError` | `name` is empty or only whitespace. The message is `name must not be empty`. |

```python
try:
    greet(" ")
except ValueError as error:
    print(error)    # name must not be empty
```

## Used by

The `hello` command of [`example-cli`](../../../../cli/docs/guides/cli/hello.md) calls `greet`, prints the result and turns the `ValueError` into exit code 1.
