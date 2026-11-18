from ruamel.yaml import YAML

import rdflib

from yatter import inverse_translate, merge_mappings
from yatter.constants import RML_URI
from yatter.normalization import normalize, normalize_yaml
from yatter.source import get_logical_source


def test_predicate_function_parameters_are_normalized():
    data = {
        "po": [
            {
                "p": {
                    "function": "grel:test",
                    "parameters": [["param", "$(value)"]],
                },
                "o": "result",
            }
        ]
    }

    normalized = normalize_yaml(data)

    predicate = normalized["predicateobjects"][0]["predicates"][0]
    assert predicate["function"] == "grel:test"
    assert predicate["parameters"] == [
        {"parameter": "param", "value": "$(value)"}
    ]


def test_merge_mappings_includes_ids_from_every_document():
    mapping_data = [
        {
            "prefixes": {"ex": "http://example.com/"},
            "mappings": {"first": {"s": "http://example.com/first"}},
        },
        {
            "prefixes": {"foaf": "http://xmlns.com/foaf/0.1/"},
            "mappings": {"second": {"s": "http://example.com/second"}},
        },
    ]

    merged = merge_mappings(mapping_data)
    parsed = YAML(typ="safe", pure=True).load(merged)

    assert set(parsed["mappings"]) == {"first", "second"}


def test_inverse_translate_alias_is_available():
    graph = rdflib.Graph()

    translated = inverse_translate(graph)

    assert translated["mappings"] == {}


def test_inverse_source_detects_csv_extension():
    graph = rdflib.Graph()
    logical_source = rdflib.URIRef("http://example.com/LogicalSource")
    graph.add((
        logical_source,
        rdflib.Namespace(RML_URI).source,
        rdflib.Literal("data.csv"),
    ))

    assert get_logical_source(logical_source, graph) == ["data.csv~csv"]


def test_target_expansion_checks_every_predicate_object():
    data = {
        "targets": {
            "output": {
                "access": "output.ttl",
                "serialization": "turtle",
            }
        },
        "mappings": {
            "person": {
                "po": [
                    {"p": "ex:first", "o": "first"},
                    {
                        "p": "ex:second",
                        "o": {"value": "second", "targets": ["output"]},
                    },
                ]
            }
        },
    }

    normalized = normalize(data, {}, {})
    objects = normalized["mappings"]["person"]["predicateobjects"][1]["objects"]

    assert objects[0]["targets"] == [{"output": {
        "access": "output.ttl",
        "serialization": "turtle",
    }}]
