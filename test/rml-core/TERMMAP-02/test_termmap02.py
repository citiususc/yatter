import os

from ruamel.yaml import YAML

from yatter.constants import RML_URI
from yatter.subject import add_subject


def test_subject_map_with_target_and_term_type():
    directory = os.path.dirname(os.path.realpath(__file__))
    yaml = YAML(typ="safe", pure=True)
    with open(os.path.join(directory, "mapping.yml")) as input_file:
        mapping = yaml.load(input_file)
    with open(os.path.join(directory, "expected.txt")) as expected_file:
        expected = expected_file.read()

    translated = add_subject(mapping, "person", RML_URI)

    assert translated == [expected]
