__author__ = "Marino Gonzalez Garcia"
__credits__ = ["Marino Gonzalez Garcia"]

__license__ = "Apache-2.0"
__maintainer__ = "David Chaves-Fraga"
__email__ = "david.chaves@upm.es"


import os
from ruamel.yaml import YAML
import yatter
from rdflib.graph import Graph
from rdflib import compare
R2RML_URI = 'http://www.w3.org/ns/r2rml#'


def test_r2rml_yarrrmltc0016():
    expected_mapping = Graph()
    expected_mapping.parse(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.ttl'), format="ttl")

    translated_mapping = Graph()
    yaml = YAML(typ='safe', pure=True)
    mapping_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.yml')
    translated_mapping.parse(data=yatter.translate(yaml.load(open(mapping_path)), mapping_format=R2RML_URI), format="ttl")
    translated_mapping.serialize(destination="mapping.rml.ttl",format="ttl")

    assert compare.isomorphic(expected_mapping, translated_mapping)