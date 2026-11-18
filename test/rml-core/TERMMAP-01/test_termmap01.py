import os

from ruamel.yaml import YAML

from yatter.predicateobject import add_predicate_object


def test_object_map_with_language_and_term_type():
    directory = os.path.dirname(os.path.realpath(__file__))
    yaml = YAML(typ="safe", pure=True)
    with open(os.path.join(directory, "mapping.yml")) as input_file:
        predicate_object = yaml.load(input_file)
    with open(os.path.join(directory, "expected.txt")) as expected_file:
        expected = expected_file.read().rstrip("\n")

    translated = add_predicate_object({}, "person", predicate_object)

    assert translated == expected
