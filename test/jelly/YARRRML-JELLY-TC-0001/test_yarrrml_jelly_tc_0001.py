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
from yatter.cli import parse_inputs

def _mimic_args(**kwargs):
    return types.SimpleNamespace(**kwargs)

def test_parse_inputs_acc_jelly(tmp_path: Path):

    output_mapping_path = str(tmp_path / 'output_mapping.yml')
    args = _mimic_args(input_mapping_path = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'jelly_mapping_test_jelly.jelly')),
                       output_mapping_path = output_mapping_path,
                       merge_mapping = None,
                       format=None)

    parsed_format, parsed_data = parse_inputs(args)

    assert isinstance(parsed_data, rdflib.Graph)
    assert isinstance(parsed_format, str)
