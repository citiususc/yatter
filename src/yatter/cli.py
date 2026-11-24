from ruamel.yaml import YAML
import argparse
from rdflib import Graph
from . import translate, inverse_translation, merge_mappings
from .constants import *
from pyjelly.integrations.rdflib.serialize import SerializerOptions, StreamParameters



def write_results(args, mapping):
    if isinstance(mapping, str):
        if args.output_mapping_path.endswith('.jelly'):
            # Jelly file saved by parsing to graph and serialization.
            g = Graph()
            g.parse(data=mapping)
            options = SerializerOptions(params=StreamParameters(namespace_declarations=True))
            g.serialize(args.output_mapping_path, format='jelly', options=options)
        else:
            with open(args.output_mapping_path, "w") as output_file:
                output_file.write(mapping)
    elif isinstance(mapping, dict):
        with open(args.output_mapping_path, "wb") as f:
            yaml = YAML()
            yaml.width = 3000
            yaml.default_flow_style = False
            yaml.dump(mapping, f)


def parse_inputs(args):
    input_format = RML_CORE_URI
    yaml = YAML(typ='safe', pure=True)
    if args.input_mapping_path and args.output_mapping_path:
        if args.input_mapping_path.endswith('.yml') or args.input_mapping_path.endswith('.yaml'):
            with open(args.input_mapping_path) as f:
                input_data = yaml.load(f)
        elif args.input_mapping_path.endswith('.ttl') or args.input_mapping_path.endswith(
                '.rml') or args.input_mapping_path.endswith('.r2rml'):
            input_data = Graph()
            input_data.parse(args.input_mapping_path, format='turtle')
        elif args.input_mapping_path.endswith('.jelly'):
            input_data = Graph()
            input_data.parse(args.input_mapping_path, format='jelly')
        else:
            logger.error("Input mapping does not have a valid extension (.yml, .yaml, .ttl, .rml, .r2rml or .jelly)")
            raise ValueError("Change your mapping extension to a valid one")

        input_format = {
            None: RML_CORE_URI,
            "RML": RML_CORE_URI,
            "RML-OLD": RML_URI,
            "R2RML": R2RML_URI,
        }[args.format]
    elif args.merge_mapping:
        input_data = []
        for mapping in args.merge_mapping:
            with open(mapping) as f:
                input_data.append(yaml.load(f))
    else:
        logger.error("No correct arguments, run python3 -m yatter -h to see the help")
        raise ValueError("No correct arguments, run python3 -m yatter -h to see the help")

    return input_format, input_data


def define_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_mapping_path", required=False, help="Input mapping path in YARRRML or RML")
    parser.add_argument("-o", "--output_mapping_path", required=False, help="Output path for the generated mapping")
    parser.add_argument("-m", "--merge_mapping", nargs="*", required=False, help="List of mappings to be merged")
    parser.add_argument("-f", "--format", required=False,
                        choices=("RML", "RML-OLD", "R2RML"),
                        help="Mapping format (RML by default)")
    return parser


def main():
    args = define_args().parse_args()
    mapping_format, mapping_data = parse_inputs(args)
    if type(mapping_data) is Graph:
        mapping_content = inverse_translation(mapping_data, mapping_format)
    elif args.merge_mapping:
        mapping_content = merge_mappings(mapping_data)
    else:
        mapping_content = translate(mapping_data, mapping_format)
    if mapping_content is None:
        return 1
    else:
        write_results(args, mapping_content)
        return 0


