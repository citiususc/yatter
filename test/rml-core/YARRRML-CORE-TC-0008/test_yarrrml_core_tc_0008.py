import os

from deepdiff import DeepDiff
from ruamel.yaml import YAML

from yatter import merge_mappings


def test_yarrrml_core_tc_0008_merge_all_mapping_ids():
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


def test_merge_mappings_allows_missing_optional_sections():
    directory = os.path.dirname(os.path.realpath(__file__))
    yaml = YAML(typ="safe", pure=True)
    with open(os.path.join(directory, "mapping_input_without_prefixes.yml")) as file:
        mapping_without_prefixes = yaml.load(file)
    with open(os.path.join(directory, "mapping_input_without_mappings.yml")) as file:
        mapping_without_mappings = yaml.load(file)
    with open(os.path.join(directory, "mapping_output_optional_sections.yml")) as file:
        expected = yaml.load(file)

    merged = yaml.load(
        merge_mappings([mapping_without_prefixes, mapping_without_mappings])
    )

    assert merged == expected
