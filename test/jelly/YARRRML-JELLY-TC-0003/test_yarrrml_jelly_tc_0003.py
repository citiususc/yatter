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

def test_parse_inputs_invalid_extension(tmp_path: Path):
    output_mapping_path = str(tmp_path / 'output_mapping.yml')

    args = _mimic_args(input_mapping_path = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'jelly_mapping_test_txt.txt')),
                       output_mapping_path = output_mapping_path,
                       merge_mapping = None,
                       format=None)

    with pytest.raises(Exception) as excinfo:
        parsed_format, parsed_data = parse_inputs(args)

    assert "Change your mapping extension to a valid one" in excinfo.value.args[0]

