import sys
from ruamel.yaml import YAML
import argparse
from rdflib import Graph
from . import translate, inverse_translation, merge_mappings
from .constants import *


def write_results(mapping):
    if type(mapping) is str:
        output_file = open(args.output_mapping_path, "w")
        output_file.write(mapping)
        output_file.close()
    elif type(mapping) is dict:
        with open(args.output_mapping_path, "wb") as f:
            yaml = YAML()
            yaml.width = 3000
            yaml.default_flow_style = False
            yaml.dump(mapping, f)


def parse_inputs():
    input_format = RML_URI
    yaml = YAML(typ='safe', pure=True)
    if args.input_mapping_path and args.output_mapping_path:
        if args.input_mapping_path.endswith('.yml') or args.input_mapping_path.endswith('.yaml'):
            with open(args.input_mapping_path) as f:
                input_data = yaml.load(f)
        elif args.input_mapping_path.endswith('.ttl') or args.input_mapping_path.endswith(
                '.rml') or args.input_mapping_path.endswith('.r2rml'):
            input_data = Graph()
            input_data.parse(args.input_mapping_path, format="turtle")
        else:
            sys.tracebacklimit = 0
            logger.error("Input mapping does not have a valid extension (.yml, .yaml, .ttl, .rml, or .r2rml)")
            raise Exception("Change your mapping extension to a valid one")

        if args.format is not None and args.format == "R2RML":
            input_format = R2RML_URI
    elif args.merge_mapping:
        input_data = []
        for mapping in args.merge_mapping:
            with open(mapping) as f:
                input_data.append(yaml.load(f))
    else:
        sys.tracebacklimit = 0
        logger.error("No correct arguments, run python3 -m yatter -h to see the help)")
        raise Exception("")

    return input_format, input_data


def define_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_mapping_path", required=False, help="Input mapping path in YARRRML or RML")
    parser.add_argument("-o", "--output_mapping_path", required=False, help="Output path for the generated mapping")
    parser.add_argument("-m", "--merge_mapping", nargs="*", required=False, help="List of mappings to be merged")
    parser.add_argument("-f", "--format", required=False,
                        help="Mapping input format. Values: R2RML or RML (RML by default)")
    return parser


if __name__ == "__main__":
    args = define_args().parse_args()
    mapping_format, mapping_data = parse_inputs()
    if type(mapping_data) is Graph:
        mapping_content = inverse_translation(mapping_data, mapping_format)
    elif args.merge_mapping:
        mapping_content = merge_mappings(mapping_data)
    else:
        mapping_content = translate(mapping_data, mapping_format)
    write_results(mapping_content)
