import os

from ruamel.yaml import YAML

from yatter.function import generate_function
from yatter.constants import RML_URI


def test_yarrrml_fnml_tc_0012():
    directory = os.path.dirname(os.path.realpath(__file__))
    yaml = YAML(typ="safe", pure=True)
    with open(os.path.join(directory, "mapping.yml")) as input_file:
        function = yaml.load(input_file)
    with open(os.path.join(directory, "expected.txt")) as expected_file:
        expected = expected_file.read()

    translated = generate_function(function, "function_person", {"local_id": 0}, RML_URI)
    assert translated == expected
