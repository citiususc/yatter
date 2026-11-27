from pathlib import Path

import pytest
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef

import yatter


ROOT = Path(__file__).parents[1]
RML = Namespace("http://w3id.org/rml/")
RR = Namespace("http://www.w3.org/ns/r2rml#")
MODULES = ("rml-cc", "rml-datatype", "rml-fnml", "rml-in-memory", "rml-io", "rml-language")
CASES = sorted((ROOT / "rml-core").glob("YARRRML-CORE-TC-[0-9]*/mapping.ttl")) + sorted(
    path for module in MODULES for path in (ROOT / module).glob("YARRRML-*-TC-[0-9]*/mapping.ttl")
    if list(path.parent.glob("test_*.py"))
)


@pytest.mark.parametrize("path", CASES, ids=lambda path: path.parent.name)
def test_core_inverse_can_be_translated(path):
    original = Graph().parse(path)
    inverse = yatter.inverse_translate(original)
    translated = yatter.translate(inverse)
    assert translated is not None
    result = Graph().parse(data=translated, format="turtle")
    assert len(list(result.subjects(RDF.type, RML.TriplesMap))) == len(
        list(original.subjects(RDF.type, RML.TriplesMap))
    )
    for predicate in (RML.function, RML.parameter, RML.gatherAs, RML.path, RML.logicalTarget):
        original_values = list(original.objects(None, predicate))
        translated_values = list(result.objects(None, predicate))
        if predicate == RML.logicalTarget:
            assert len(translated_values) == len(original_values)
        else:
            assert sorted(map(str, translated_values)) == sorted(map(str, original_values))
    for predicate in (RML.constant, RML.reference, RML.template, RML.datatype,
                      RML.language, RML.iterator):
        assert set(original.objects(None, predicate)) == set(result.objects(None, predicate))


def test_inverse_preserves_ambiguous_literal():
    graph = Graph().parse(data="""
        @prefix rml: <http://w3id.org/rml/>.
        <http://example.com/map> a rml:TriplesMap;
          rml:logicalSource [rml:source [rml:path "data.csv"];
                             rml:referenceFormulation rml:CSV];
          rml:subjectMap [rml:constant <http://example.com/subject>];
          rml:predicateObjectMap [
            rml:predicate <http://example.com/predicate>;
            rml:objectMap [rml:constant "https://example.com/with:colon\\\"quoted"]].
    """, format="turtle")
    result = Graph().parse(data=yatter.translate(yatter.inverse_translate(graph)), format="turtle")
    assert Literal('https://example.com/with:colon"quoted') in result.objects(None, RML.constant)


def test_inverse_rejects_unrepresentable_literal():
    graph = Graph().parse(data="""
        @prefix rml: <http://w3id.org/rml/>.
        <http://example.com/map> a rml:TriplesMap;
          rml:logicalSource [rml:source [rml:path "data.csv"];
                             rml:referenceFormulation rml:CSV];
          rml:subjectMap [rml:constant <http://example.com/subject>];
          rml:predicateObjectMap [
            rml:predicate <http://example.com/predicate>;
            rml:objectMap [rml:constant "hello"@en]].
    """, format="turtle")
    with pytest.raises(yatter.InvalidMappingError, match="without loss"):
        yatter.inverse_translate(graph)


def test_database_without_credentials():
    mapping = {
        "mappings": {
            "map": {
                "sources": [{"access": "jdbc:example:db", "query": "SELECT * FROM data"}],
                "s": "http://example.com/$(id)",
                "po": [["http://example.com/value", "$(value)"]],
            }
        }
    }
    graph = Graph().parse(data=yatter.translate(mapping), format="turtle")
    inverse = yatter.inverse_translate(graph)
    source = inverse["mappings"]["map_0"]["sources"][0]
    assert source == {"access": "jdbc:example:db", "query": "SELECT * FROM data"}
    assert yatter.translate(inverse) is not None


def test_inverse_rejects_wrong_profile():
    graph = Graph().parse(
        ROOT / "rml-old/YARRRML-CORE_OLD-TC-0001/mapping.ttl", format="turtle"
    )
    with pytest.raises(yatter.InvalidMappingError, match="selected profile"):
        yatter.inverse_translate(graph)


@pytest.mark.parametrize("number", range(1, 6))
def test_adapted_r2rml_inverse_cases(number):
    path = ROOT / f"r2rml/YARRRML-R2RML-TC-INV-{number:04d}/mapping.ttl"
    original = Graph().parse(path)
    graph = Graph()
    logical_tables = set(original.objects(None, RR.logicalTable))
    for subject, predicate, obj in original:
        if subject in logical_tables or predicate == RR.logicalTable:
            continue
        if str(predicate).startswith(str(RR)):
            name = str(predicate).removeprefix(str(RR))
            predicate = RML.reference if name == "column" else RML[name]
        if predicate in (RDF.type, RML.termType) and str(obj).startswith(str(RR)):
            obj = URIRef(str(RML) + str(obj).removeprefix(str(RR)))
        graph.add((subject, predicate, obj))
    for triples_map, table in original.subject_objects(RR.logicalTable):
        source, access = BNode(), BNode()
        name = original.value(table, RR.tableName) or Literal("Student")
        graph.add((triples_map, RML.logicalSource, source))
        graph.add((source, RML.source, access))
        graph.add((access, RML.path, Literal(f"{name}.csv")))
        graph.add((source, RML.referenceFormulation, RML.CSV))

    translated = yatter.translate(yatter.inverse_translate(graph))
    assert translated is not None
    result = Graph().parse(data=translated, format="turtle")
    for predicate in (RML.constant, RML.reference, RML.template, RML.datatype,
                      RML.child, RML.parent, RML.path):
        assert set(graph.objects(None, predicate)) == set(result.objects(None, predicate))


def test_adapted_invalid_r2rml_inverse_case():
    graph = Graph()
    graph.add((URIRef("http://example.com/LogicalSource"), RDF.type, RML.TriplesMap))
    with pytest.raises(yatter.InvalidMappingError, match="logical sources"):
        yatter.inverse_translate(graph)


def test_predicate_target_survives_inverse_translation():
    path = ROOT / "rml-io/YARRRML-IO-TC-0002/mapping.ttl"
    graph = Graph().parse(path)
    subject = next(graph.subjects(RDF.type, RML.SubjectMap))
    predicate = next(graph.subjects(RDF.type, RML.PredicateMap))
    target = graph.value(subject, RML.logicalTarget)
    graph.remove((subject, RML.logicalTarget, target))
    graph.add((predicate, RML.logicalTarget, target))
    translated = yatter.translate(yatter.inverse_translate(graph))
    assert translated is not None
    result = Graph().parse(data=translated, format="turtle")
    predicate = next(result.subjects(RDF.type, RML.PredicateMap))
    assert result.value(predicate, RML.logicalTarget) is not None
