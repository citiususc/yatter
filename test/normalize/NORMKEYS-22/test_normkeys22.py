import os

from ruamel.yaml import YAML

from yatter.normalization import normalize


def test_normalization_does_not_mutate_input():
    directory = os.path.dirname(os.path.realpath(__file__))
    yaml = YAML(typ="safe", pure=True)

    with open(os.path.join(directory, "mapping.yml")) as input_file:
        mapping = yaml.load(input_file)
    with open(
        os.path.join(directory, "mapping_after_normalization.yml")
    ) as expected_file:
        expected = yaml.load(expected_file)

    normalize(mapping, {}, {})

    assert mapping == expected
