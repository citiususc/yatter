from pathlib import Path

from rdflib import Graph
from rdflib.compare import isomorphic
from ruamel.yaml import YAML

import yatter


def test_yarrrml_core_tc_0025():
    directory = Path(__file__).parent
    with (directory / "mapping.yml").open() as source:
        mapping = YAML(typ="safe", pure=True).load(source)
    actual = yatter.translate(mapping)
    expected = (directory / "mapping.ttl").read_text()

    assert actual == expected
    assert isomorphic(
        Graph().parse(data=actual, format="turtle"),
        Graph().parse(data=expected, format="turtle"),
    )
