import pytest

import yatter
from yatter.constants import YARRRML_MAPPINGS
from yatter.errors import InvalidMappingError


def _mapping():
    return {YARRRML_MAPPINGS: {"map": {}}}


def test_translate_returns_none_for_invalid_mapping(monkeypatch):
    def reject_source(*args, **kwargs):
        raise InvalidMappingError("invalid source")

    monkeypatch.setattr(yatter, "normalize", lambda data, *_: data)
    monkeypatch.setattr(yatter, "generate_database_connections", lambda *args: [])
    monkeypatch.setattr(yatter, "add_source", reject_source)

    assert yatter.translate(_mapping()) is None


def test_translate_propagates_unexpected_errors(monkeypatch):
    def fail_unexpectedly(*args, **kwargs):
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr(yatter, "normalize", lambda data, *_: data)
    monkeypatch.setattr(yatter, "generate_database_connections", lambda *args: [])
    monkeypatch.setattr(yatter, "add_source", fail_unexpectedly)

    with pytest.raises(RuntimeError, match="unexpected failure"):
        yatter.translate(_mapping())
