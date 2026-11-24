from pathlib import Path

import pytest
from rdflib import Graph

import yatter


def test_yarrrml_core_tc_inv_0006():
    graph = Graph().parse(Path(__file__).parent / "mapping.ttl", format="turtle")
    with pytest.raises(yatter.InvalidMappingError, match="logical sources"):
        yatter.inverse_translate(graph)
