import os
from ruamel.yaml import YAML
from deepdiff import DeepDiff
from yatter.normalization import normalize, switch_mappings

R2RML_URI = 'http://www.w3.org/ns/r2rml#'


def convert_comment_seq_to_list(data):
    from ruamel.yaml.comments import CommentedSeq
    if isinstance(data, CommentedSeq):
        return [convert_comment_seq_to_list(item) for item in data]
    elif isinstance(data, list):
        return [convert_comment_seq_to_list(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_comment_seq_to_list(value) for key, value in data.items()}
    else:
        return data


def test_normkeys07():
    yaml = YAML(typ='safe', pure=True)

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping_normalized.yml')) as file:
        expected_mapping = yaml.load(file)

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.yml')) as file:
        data = yaml.load(file)
    added_sources, added_targets = {}, {}

    expected_mapping = convert_comment_seq_to_list(expected_mapping)
    normalized_mapping = normalize(data,added_sources, added_targets)

    ddiff = DeepDiff(expected_mapping, normalized_mapping, ignore_order=True)

    if ddiff:
        assert False
    else:
        assert True
