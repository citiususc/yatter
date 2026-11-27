from pathlib import Path

from rdflib import Graph, Namespace, RDF
from rdflib.compare import isomorphic
from ruamel.yaml import YAML

import yatter


def test_yarrrml_fnml_tc_0003():
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
    graph = Graph().parse(data=actual, format="turtle")
    rml = Namespace("http://w3id.org/rml/")
    assert list(graph.triples((None, rml.functionExecution, None))) or list(graph.triples((None, rml.joinCondition, None)))
