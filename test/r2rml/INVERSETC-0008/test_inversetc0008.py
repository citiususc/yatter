import os

import pytest
import rdflib

from yatter.constants import RML_URI
from yatter.source import add_inverse_source


def test_inversetc0008():
    directory = os.path.dirname(os.path.realpath(__file__))
    mapping_id = rdflib.URIRef("http://example.com/LogicalSource")
    graph = rdflib.Graph()
    graph.parse(os.path.join(directory, "mapping.ttl"), format="turtle")
    graph.bind("rr", rdflib.Namespace("http://www.w3.org/ns/r2rml#"))
    graph.bind("rml", rdflib.Namespace(RML_URI))
    with open(os.path.join(directory, "expected_error.txt")) as expected_file:
        expected_error = expected_file.read().strip()

    with pytest.raises(ValueError) as error:
        add_inverse_source(mapping_id, graph, RML_URI)

    assert str(error.value) == expected_error
