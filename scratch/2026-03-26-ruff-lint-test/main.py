"""Demo module for testing ruff lint rules — all issues fixed."""

import ast
from pathlib import Path

x = 1 + 2
y = [1, 2, 3, 4]
z = {"a": 1, "b": 2}

PI = 3.14159265358979


class MyClass:
    """A simple class with a name attribute."""

    name = "test"

    def __init__(self, name: str) -> None:
        """Initialize with a name."""
        self.name = name

    def my_method(self) -> str:
        """Return the name."""
        return self.name


def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b


def greet(name: str) -> str:
    """Build a greeting message for the given name."""
    return f"Hello {name}"


def process(data: object) -> bool | None:
    """Process data and return a boolean or None."""
    if data is None:
        return True
    if data is True:
        return False
    return None


def check(value: object) -> bool:
    """Check if value is truthy."""
    return bool(value)


def get_item(lst: list[object], idx: int) -> object | None:
    """Get an item from a list by index, returning None if out of range."""
    try:
        return lst[idx]
    except IndexError:
        return None


def concat(*args: object) -> str:
    """Concatenate all arguments into a single string."""
    return "".join(str(a) for a in args)


def maybe_return(value: int) -> int | None:
    """Return value if positive, otherwise None."""
    if value > 0:
        return value
    return None


def no_shadowing(
    items: list[object],
    mapping: dict[str, object],
    kind: str,
) -> tuple[object, ...]:
    """Demonstrate proper naming without shadowing builtins."""
    return items, mapping, kind


def explicit_args(a: int, b: int) -> int:
    """Add two explicitly named arguments."""
    return a + b


numbers = [1, 2, 3]
zero = 0
one = 1


def todo() -> None:
    """Do nothing yet."""  # TODO: implement this


def fixme() -> None:
    """Do nothing yet."""  # FIXME: broken


print("hello")
EXPECTED_SUM = 3
assert x == EXPECTED_SUM  # noqa: S101


def long_function(
    aaaaaa: int,
    bbbbbb: int,
    cccccc: int,
    dddddd: int,
    eeeeee: int,
) -> int:
    """Add five numbers together."""
    return aaaaaa + bbbbbb + cccccc + dddddd + eeeeee


class AnotherClass:
    """A class demonstrating proper magic method implementation."""

    def method(self) -> AnotherClass:
        """Return self."""
        return self

    def __repr__(self) -> str:
        """Return string representation."""
        return "AnotherClass"

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        return True

    def __hash__(self) -> int:
        """Return hash value."""
        return 0


with Path("test.txt").open() as f:
    _ = f.read()

my_dict = {1: "one", 2: "two"}
my_list = [1, 2, 3]
my_type = "hello"

ast.literal_eval("1+1")
