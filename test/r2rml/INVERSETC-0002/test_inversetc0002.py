__author__ = "David Chaves-Fraga"
__credits__ = ["David Chaves-Fraga"]

__license__ = "Apache-2.0"
__maintainer__ = "David Chaves-Fraga"
__email__ = "david.chaves@upm.es"
__name__ = "INVERSETC-0002 based on YARRRMLTC-0003"


import os
from ruamel.yaml import YAML
import yatter
from rdflib.graph import Graph
from deepdiff import DeepDiff
R2RML_URI = 'http://www.w3.org/ns/r2rml#'


def test_inversetc0002():
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