from pathlib import Path

from rdflib import Graph, Namespace, RDF
from rdflib.compare import isomorphic
from ruamel.yaml import YAML

import yatter


def test_yarrrml_io_tc_0006():
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
    assert list(Graph().parse(data=actual, format="turtle").subjects(RDF.type, Namespace("http://w3id.org/rml/").LogicalTarget))
