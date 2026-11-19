"""
Tests for yatter jelly integration for input output.
For PR #99: feat(cli): support for Jelly format for input/output
"""
from unittest import expectedFailure

import pytest
import types
from pathlib import Path
import os

import rdflib
pytest.importorskip("pyjelly")
from yatter.cli import parse_inputs, translate,write_results
from rdflib import Graph
from rdflib import compare

def _mimic_args(**kwargs):
    return types.SimpleNamespace(**kwargs)

def test_write_results_roundtrip_to_jelly(tmp_path: Path):
    output_mapping_path = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output_mapping.jelly'))
    args = _mimic_args(input_mapping_path=str(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'jelly_mapping_test_yml.yml')),
                       output_mapping_path=output_mapping_path,
                       merge_mapping=None,
                       format=None)

    parsed_format, parsed_data = parse_inputs(args)
    mapping_content = translate(parsed_data, parsed_format)
    assert isinstance(mapping_content, str)
    write_results(args, mapping_content)

    translated_mapping = Graph()
    translated_mapping.parse(output_mapping_path, format='jelly')

    expected_mapping = Graph()
    expected_mapping.parse(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'jelly_mapping_test_jelly.jelly'), format='jelly')

    assert isinstance(translated_mapping, rdflib.Graph)
    assert isinstance(expected_mapping, rdflib.Graph)
    assert compare.isomorphic(translated_mapping, expected_mapping)

