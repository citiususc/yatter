import os

from deepdiff import DeepDiff
from ruamel.yaml import YAML

from yatter import merge_mappings


def test_yarrrmltc0023_merge_all_mapping_ids():
    yaml = YAML(typ="safe", pure=True)
    directory = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(directory, "mapping_input1.yml")) as file:
        first_mapping = yaml.load(file)
    with open(os.path.join(directory, "mapping_input2.yml")) as file:
        second_mapping = yaml.load(file)
    with open(os.path.join(directory, "mapping_output.yml")) as file:
        expected_mapping = yaml.load(file)

    merged_mapping = yaml.load(merge_mappings([first_mapping, second_mapping]))
    diff = DeepDiff(expected_mapping, merged_mapping, ignore_order=True)

    assert not diff
