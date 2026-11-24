from pathlib import Path

from deepdiff import DeepDiff
from rdflib import Graph
from ruamel.yaml import YAML

import yatter


def test_yarrrml_core_tc_inv_0002():
    directory = Path(__file__).parent
    graph = Graph().parse(directory / "mapping.ttl", format="turtle")
    with (directory / "mapping.yml").open() as source:
        expected = YAML(typ="safe", pure=True).load(source)
    actual = yatter.inverse_translate(graph)

    assert not DeepDiff(expected["mappings"], actual["mappings"], ignore_order=True)
    assert yatter.translate(expected) == (directory / "expected.ttl").read_text()
