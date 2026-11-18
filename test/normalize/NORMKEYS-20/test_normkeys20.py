import os

from ruamel.yaml import YAML

from yatter.normalization import normalize


def test_target_expansion_checks_every_predicate_object():
    yaml = YAML(typ="safe", pure=True)
    directory = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(directory, "mapping.yml")) as file:
        data = yaml.load(file)

    normalized = normalize(data, {}, {})
    objects = normalized["mappings"]["person"]["predicateobjects"][1]["objects"]

    assert objects[0]["targets"] == [{
        "output": {
            "access": "output.ttl",
            "serialization": "turtle",
        }
    }]
