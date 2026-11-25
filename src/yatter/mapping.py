from contextvars import ContextVar
from .constants import *
from .errors import InvalidMappingError
from .termmap import _term_for_format

prefixes_context = ContextVar("yatter_prefixes", default=None)


def get_prefixes():
    return prefixes_context.get() or {}


def add_mapping(mapping, mappings, it, mapping_format=RML_OLD_URI):
    map_template = "<" + mapping + "_" + str(it) + "> a "
    if mappings[mapping]:
        if mappings[mapping] == "non_asserted":
            map_template += STAR_NON_ASSERTED_CLASS + ", "
    map_template += _term_for_format(R2RML_TRIPLES_MAP, mapping_format) + ";\n\n"
    return map_template


def add_prefix(data, mapping_format=RML_OLD_URI):
    template = []
    common_prefixes = []
    prefixes_context.set({})
    if YARRRML_PREFIXES in data:
        prefixes_context.set(data.get(YARRRML_PREFIXES))
        prefixes = data.get(YARRRML_PREFIXES)
        for prefix in prefixes:
            prefix_uri = data.get(YARRRML_PREFIXES).get(prefix)
            if mapping_format == RML_URI and prefix == "rml" and prefix_uri != RML_URI:
                raise InvalidMappingError("The rml prefix is reserved for RML-Core")
            check_common_prefixes(prefix_uri, common_prefixes)
            template.append(RML_PREFIX + " " + prefix + ": <" + prefix_uri + ">.\n")

    if mapping_format != RML_URI and "r2rml" not in common_prefixes:
        template.append(RML_PREFIX + " " + R2RML_TERM_PREFIX + " <" + R2RML_URI + ">.\n")
    if mapping_format == RML_URI:
        if data.get(YARRRML_PREFIXES, {}).get("rml") != RML_URI:
            template.append(RML_PREFIX + " " + RML_TERM_PREFIX + " <" + RML_URI + ">.\n")
    elif "rml" not in common_prefixes:
        template.append(RML_PREFIX + " " + RML_TERM_PREFIX + " <" + RML_OLD_URI + ">.\n")
    if "rdf" not in common_prefixes:
        template.append(RML_PREFIX + " " + RDF_TERM_PREFIX + " <" + RDF_URI + ">.\n")
    if "rdfs" not in common_prefixes:
        template.append(RML_PREFIX + " " + RDFS_TERM_PREFIX + " <" + RDFS_URI + ">.\n")
    if "xsd" not in common_prefixes:
        template.append(RML_PREFIX + " " + XSD_TERM_PREFIX + " <" + XSD_URI + ">.\n")
    if "ql" not in common_prefixes:
        template.append(RML_PREFIX + " " + QL_TERM_PREFIX + " <" + QL_URI + ">.\n")
    if "d2rq" not in common_prefixes:
        template.append(RML_PREFIX + " " + D2RQ_TERM_PREFIX + " <" + D2RQ_URI + ">.\n")
    if "foaf" not in common_prefixes:
        template.append(RML_PREFIX + " " + FOAF_TERM_PREFIX + " <" + FOAF_URI + ">.\n")
    if "schema" not in common_prefixes:
        template.append(RML_PREFIX + " " + SCHEMA_TERM_PREFIX + " <" + SCHEMA_URI + ">.\n")
    if "formats" not in common_prefixes:
        template.append(RML_PREFIX + " " + FORMATS_TERM_PREFIX + " <" + FORMATS_URI + ">.\n")
    if mapping_format != RML_URI and "comp" not in common_prefixes:
        template.append(RML_PREFIX + " " + COMPRESSION_TERM_PREFIX + " <" + COMPRESSION_URI + ">.\n")
    if "void" not in common_prefixes:
        template.append(RML_PREFIX + " " + VOID_TERM_PREFIX + " <" + VOID_URI + ">.\n")
    if mapping_format != RML_URI and "fnml" not in common_prefixes:
        template.append(RML_PREFIX + " " + FNML_TERM_PREFIX + " <" + FNML_URI + ">.\n")
    if "grel" not in common_prefixes:
        template.append(RML_PREFIX + " " + GREL_TERM_PREFIX + " <" + GREL_URI + ">.\n")
    if "base" not in common_prefixes:
        template.append(RML_BASE + " <" + EXAMPLE_URI + ">.\n")

    template.append("\n\n")

    return "".join(template)


def check_common_prefixes(prefix_uri, common_prefixes):
    if prefix_uri == R2RML_URI:
        common_prefixes.append("r2rml")
    elif prefix_uri == RML_OLD_URI:
        common_prefixes.append("rml")
    elif prefix_uri == RDF_URI:
        common_prefixes.append("rdf")
    elif prefix_uri == QL_URI:
        common_prefixes.append("ql")
    elif prefix_uri == D2RQ_URI:
        common_prefixes.append("d2rq")
    elif prefix_uri == RDFS_URI:
        common_prefixes.append("rdfs")
    elif prefix_uri == XSD_URI:
        common_prefixes.append("xsd")
    elif prefix_uri == FOAF_URI:
        common_prefixes.append("foaf")
    elif prefix_uri == SCHEMA_URI:
        common_prefixes.append("schema")
    elif prefix_uri == FORMATS_URI:
        common_prefixes.append("formats")
    elif prefix_uri == COMPRESSION_URI:
        common_prefixes.append("comp")
    elif prefix_uri == VOID_URI:
        common_prefixes.append("void")
    elif prefix_uri == FNML_URI:
        common_prefixes.append("fnml")
    elif prefix_uri == GREL_URI:
        common_prefixes.append("grel")


def add_inverse_prefix(rdf_mapping):
    prefixes = {}
    for prefix, uri in rdf_mapping.namespaces():
        if prefix:
            prefixes[prefix] = uri.toPython()
    return prefixes


def get_non_asserted_mappings(yarrrml_data, mapping_format):
    mappings = dict.fromkeys(list(yarrrml_data.get(YARRRML_MAPPINGS).keys()))
    for mapping in yarrrml_data.get(YARRRML_MAPPINGS):
        keys = yarrrml_data.get(YARRRML_MAPPINGS).get(mapping).keys()
        for key in keys:
            if type(yarrrml_data.get(YARRRML_MAPPINGS).get(mapping).get(key)) is list:
                for value in yarrrml_data.get(YARRRML_MAPPINGS).get(mapping).get(key):
                    if type(value) is dict:
                        star_data = [value]
                        if YARRRML_OBJECTS in value:
                            star_data = value[YARRRML_OBJECTS]
                        for val in star_data:
                            if YARRRML_NON_ASSERTED in val:
                                mappings[val[YARRRML_NON_ASSERTED]] = "non_asserted"
                                mapping_format = STAR_URI
                            elif YARRRML_QUOTED in val:
                                mapping_format = STAR_URI

    return mappings, mapping_format


def merge_mapping_section_by_key(key, yarrrml_list):
    output = {key: {}}
    for yarrrml_mapping in yarrrml_list:
        output[key] = output[key] | yarrrml_mapping
    return output
