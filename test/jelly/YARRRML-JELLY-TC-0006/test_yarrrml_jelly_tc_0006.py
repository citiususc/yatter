"""
Tests for yatter jelly integration for input output.
For PR #99: feat(cli): support for Jelly format for input/output
"""

import pytest
import types
from pathlib import Path
import os

import rdflib
pytest.importorskip("pyjelly")
from yatter.cli import parse_inputs, write_results, inverse_translation
from ruamel.yaml import YAML
from deepdiff import DeepDiff
from rdflib import compare

def _mimic_args(**kwargs):
    return types.SimpleNamespace(**kwargs)

def test_write_results_roundtrip_to_yaml(tmp_path: Path):
    output_mapping_path = str(tmp_path / 'output_mapping.yml')
    args = _mimic_args(input_mapping_path=str(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'jelly_mapping_test_jelly.jelly')),
                       output_mapping_path=output_mapping_path, merge_mapping=None,
                       format=None)

    parsed_format, parsed_data = parse_inputs(args)
    mapping_content = inverse_translation(parsed_data, parsed_format)
    assert isinstance(mapping_content, dict)
    write_results(args, mapping_content)

    expected_mapping_f = YAML(typ='safe', pure=True)
    expected_mapping = expected_mapping_f.load(open(output_mapping_path))

    assert isinstance(mapping_content, dict)
    assert expected_mapping == mapping_content

