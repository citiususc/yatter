__author__ = "David Chaves-Fraga"
__credits__ = ["David Chaves-Fraga"]

__license__ = "Apache-2.0"
__maintainer__ = "David Chaves-Fraga"
__email__ = "david.chaves@upm.es"
__name__ = "YARRRML-R2RML-TC-INV-0001 based on YARRRMLTC-0001"


import os
from ruamel.yaml import YAML
import yatter
from rdflib.graph import Graph
import rdflib
from deepdiff import DeepDiff
from yatter.constants import RML_OLD_URI
from yatter.source import get_logical_source
R2RML_URI = 'http://www.w3.org/ns/r2rml#'


def test_yarrrml_r2rml_tc_inv_0001():
    yaml = YAML(typ='safe', pure=True)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.yml')) as file:
        expected_mapping = yaml.load(file)

    input_mapping = Graph()
    mapping_path = input_mapping.parse(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.ttl'), format="ttl")
    translated_mapping = yaml.load(str(yatter.inverse_translation(mapping_path, mapping_format=R2RML_URI)))

    ddiff = DeepDiff(expected_mapping['mappings'], translated_mapping['mappings'], ignore_order=True)

    if ddiff:
        assert False
    else:
        assert True


def test_inverse_translate_alias():
    translated_mapping = yatter.inverse_translate(Graph())

    assert translated_mapping["mappings"] == {}


def test_inverse_csv_source():
    graph = Graph()
    logical_source = rdflib.URIRef("http://example.com/LogicalSource")
    graph.add((
        logical_source,
        rdflib.Namespace(RML_OLD_URI).source,
        rdflib.Literal("data.csv"),
    ))

    assert get_logical_source(logical_source, graph) == ["data.csv~csv"]
