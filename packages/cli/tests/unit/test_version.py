import example_cli


def test_version_is_defined() -> None:
    assert isinstance(example_cli.__version__, str)
