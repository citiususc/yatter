from ruamel.yaml import YAML

from yatter import merge_mappings
from yatter.normalization import normalize_yaml


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
