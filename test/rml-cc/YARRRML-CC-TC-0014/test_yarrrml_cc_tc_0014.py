from pathlib import Path

from rdflib import Graph, Namespace, RDF
from rdflib.collection import Collection
from ruamel.yaml import YAML

import yatter


def test_yarrrml_cc_tc_0014():
    directory = Path(__file__).parent
    with (directory / "mapping.yml").open() as source:
        mapping = YAML(typ="safe", pure=True).load(source)
    actual = yatter.translate(mapping)
    assert actual == (directory / "mapping.ttl").read_text()

    graph = Graph().parse(data=actual, format="turtle")
    rml = Namespace("http://w3id.org/rml/")
    head = next(graph.objects(None, rml.gather))
    assert {str(graph.value(item, rml.reference)) for item in Collection(graph, head)} == {
        "$.v1.*", "$.v2.*"
    }
    assert (None, rml.gatherAs, RDF.List) in graph
