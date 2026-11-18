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
