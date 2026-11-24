from pathlib import Path

from ruamel.yaml import YAML

from yatter.constants import RML_CORE_URI
from yatter.predicateobject import add_predicate_object


def test_yarrrml_core_tc_0012():
    directory = Path(__file__).parent
    with (directory / "mapping.yml").open() as source:
        mapping = YAML(typ="safe", pure=True).load(source)
    assert add_predicate_object({}, "person", mapping, RML_CORE_URI) == (
        directory / "expected.txt"
    ).read_text().rstrip("\n")
