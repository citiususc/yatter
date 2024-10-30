import os
from ruamel.yaml import YAML
from deepdiff import DeepDiff
from yatter.normalization import normalize_yaml

R2RML_URI = 'http://www.w3.org/ns/r2rml#'


def convert_to_dict(data):
    from ruamel.yaml.comments import CommentedMap
    if isinstance(data, CommentedMap):
        return {key: convert_to_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_dict(item) for item in data]
    else:
        return data


def test_normkeys05():
    yaml = YAML(typ='safe', pure=True)

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping_normalized.yml')) as file:
        expected_mapping = yaml.load(file)

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.yml')) as file:
        data = yaml.load(file)
        normalized_mapping = normalize_yaml(data)

    expected_mapping = convert_to_dict(expected_mapping)
    normalized_mapping = convert_to_dict(normalized_mapping)
    print(expected_mapping)
    print(normalized_mapping)
    ddiff = DeepDiff(expected_mapping, normalized_mapping, ignore_order=True)

    if ddiff:
        assert False
    else:
        assert True
