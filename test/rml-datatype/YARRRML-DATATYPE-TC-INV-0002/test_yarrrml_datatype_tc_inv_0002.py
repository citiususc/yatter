import os

from rdflib import Graph, URIRef
from ruamel.yaml import YAML

from yatter.predicateobject import add_inverse_pom
from yatter.constants import RML_CORE_URI


def test_yarrrml_datatype_tc_inv_0002():
    directory = os.path.dirname(os.path.realpath(__file__))
    graph = Graph().parse(os.path.join(directory, "mapping.ttl"), format="turtle")
    yaml = YAML(typ="safe", pure=True)
    with open(os.path.join(directory, "mapping.yml")) as expected_file:
        expected = yaml.load(expected_file)

    translated = add_inverse_pom(
        URIRef("http://example.com/person"), graph, [], {"ex": "http://example.com/"}, RML_CORE_URI
    )

    assert translated == expected
