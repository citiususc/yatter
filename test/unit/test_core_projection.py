from pathlib import Path

import pytest
from rdflib import BNode, Graph, Namespace, RDF, URIRef
from rdflib.compare import isomorphic
from ruamel.yaml import YAML

import yatter


ROOT = Path(__file__).parents[1] / "rml-core"
RR = Namespace("http://www.w3.org/ns/r2rml#")
OLD = Namespace("http://semweb.mmlab.be/ns/rml#")
RML = Namespace("http://w3id.org/rml/")
CASES = sorted(path.parent for path in ROOT.glob("YARRRML-CORE-TC-[0-9]*/mapping.ttl"))


def mapping_components(graph, triples_maps, core):
    result = Graph()
    pending = list(triples_maps)
    visited = set()
    while pending:
        node = pending.pop()
        if node in visited:
            continue
        visited.add(node)
        for predicate, value in graph.predicate_objects(node):
            if predicate in (RR.logicalTable, OLD.logicalSource, RML.logicalSource):
                continue
            if isinstance(value, BNode):
                pending.append(value)
            if not core:
                if str(predicate).startswith(str(RR)):
                    local = str(predicate)[len(str(RR)):]
                    predicate = RML.reference if local == "column" else RML[local]
                elif str(predicate).startswith(str(OLD)):
                    predicate = RML[str(predicate)[len(str(OLD)):]]
                if (predicate == RDF.type or predicate == RML.termType) and str(value).startswith(str(RR)):
                    value = RML[str(value)[len(str(RR)):]]
            result.add((node, predicate, value))
    return result


@pytest.mark.parametrize("case", CASES, ids=lambda path: path.name)
def test_core_mapping(case):
    with (case / "mapping.yml").open() as source:
        mapping = YAML(typ="safe", pure=True).load(source)
    actual = yatter.translate(mapping)
    expected = (case / "mapping.ttl").read_text()

    assert actual == expected
    actual_graph = Graph().parse(data=actual, format="turtle")
    expected_graph = Graph().parse(data=expected, format="turtle")
    assert isomorphic(actual_graph, expected_graph)

    maps = list(actual_graph.subjects(RDF.type, RML.TriplesMap))
    assert maps
    for triples_map in maps:
        source = actual_graph.value(triples_map, RML.logicalSource)
        assert source is not None
        assert isinstance(actual_graph.value(source, RML.source), (BNode, URIRef))
        assert actual_graph.value(triples_map, RML.subjectMap) is not None

    number = int(case.name[-4:])
    if number <= 11:
        original = ROOT.parent / "rml-old" / f"YARRRML-CORE_OLD-TC-{number:04d}" / "mapping.ttl"
    else:
        original = ROOT.parent / "r2rml" / f"YARRRML-R2RML-TC-{number - 12:04d}" / "mapping.ttl"
    original_graph = Graph().parse(original, format="turtle")
    original_maps = list(original_graph.subjects(RDF.type, RR.TriplesMap))
    assert len(maps) == len(original_maps)
    assert isomorphic(
        mapping_components(actual_graph, maps, core=True),
        mapping_components(original_graph, original_maps, core=False),
    )
