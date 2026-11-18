import os

import yatter
from ruamel.yaml import YAML


def test_imtc009():
    directory = os.path.dirname(os.path.realpath(__file__))
    yaml = YAML(typ="safe", pure=True)
    with open(os.path.join(directory, "mapping.yml")) as input_file:
        mapping = yaml.load(input_file)
    with open(os.path.join(directory, "mapping.ttl")) as expected_file:
        expected = expected_file.read()

    translated = yatter.translate(mapping)

    assert translated == expected
