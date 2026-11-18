import os

from ruamel.yaml import YAML

from yatter.function import generate_function


def test_multiple_nested_function_parameters():
    directory = os.path.dirname(os.path.realpath(__file__))
    yaml = YAML(typ="safe", pure=True)
    with open(os.path.join(directory, "mapping.yml")) as input_file:
        function = yaml.load(input_file)
    with open(os.path.join(directory, "expected.txt")) as expected_file:
        expected = expected_file.read()

    translated = generate_function(function, "function_person", {"local_id": 0})

    assert [line.rstrip() for line in translated.rstrip("\n").splitlines()] == [
        line.rstrip() for line in expected.rstrip("\n").splitlines()
    ]
