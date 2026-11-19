import os

from deepdiff import DeepDiff
from ruamel.yaml import YAML

from yatter.normalization import normalize_yaml


def test_yarrrml_norm_tc_0019():
    yaml = YAML(typ="safe", pure=True)
    directory = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(directory, "mapping.yml")) as file:
        data = yaml.load(file)
    with open(os.path.join(directory, "mapping_normalized.yml")) as file:
        expected = yaml.load(file)

    normalized = normalize_yaml(data)

    assert not DeepDiff(expected, normalized, ignore_order=True)
