from pathlib import Path

from ruamel.yaml import YAML

from yatter.constants import RML_URI
from yatter.subject import add_subject


def test_yarrrml_io_tc_0008():
    directory = Path(__file__).parent
    with (directory / "mapping.yml").open() as source:
        mapping = YAML(typ="safe", pure=True).load(source)
    assert add_subject(mapping, "person", RML_URI) == [(directory / "expected.txt").read_text()]
