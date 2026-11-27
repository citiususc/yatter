from .constants import *
from .mapping import add_prefix, add_mapping, add_inverse_prefix, get_non_asserted_mappings, merge_mapping_section_by_key
from .source import add_source, generate_database_connections, add_table, add_inverse_source
from .subject import add_subject, add_inverse_subject
from .predicateobject import add_predicate_object_maps
from .inverse_predicateobject import add_inverse_pom
from .target import add_logical_targets
from .function import add_functions
from .errors import InvalidMappingError
from .vocabulary import turtle_term
from .normalization import normalize
import rdflib
from rdflib.plugins.parsers.notation3 import BadSyntax
import ruamel.yaml as yaml
from io import StringIO


def translate(yarrrml_data, mapping_format=RML_NAMESPACE):
    if mapping_format not in MAPPING_FORMATS.values():
        raise ValueError(f"Unknown mapping format: {mapping_format}")
    logger.info("Translating YARRRML mapping to [R2]RML")
    try:
        return _translate(yarrrml_data, mapping_format)
    except InvalidMappingError as error:
        logger.error("ERROR: The YARRRML mapping has not been translated")
        logger.error(str(error))
        return None


def _translate(yarrrml_data, mapping_format):
    external_sources = {}
    external_targets = {}
    yarrrml_data = normalize(yarrrml_data, external_sources, external_targets)
    rml_mapping = [add_prefix(yarrrml_data, mapping_format)]
    rml_mapping.extend(generate_database_connections(yarrrml_data, external_sources, mapping_format))
    rml_mapping.extend(add_logical_targets(yarrrml_data, external_targets, mapping_format))
    rml_mapping.extend(add_functions(yarrrml_data, mapping_format))
    external_references = []
    requested_format = mapping_format
    mappings, mapping_format = get_non_asserted_mappings(yarrrml_data, mapping_format)
    if requested_format == RML_NAMESPACE and mapping_format == STAR_URI:
        raise InvalidMappingError("RML-Star is not supported by the RML-Core profile")
    for mapping in yarrrml_data.get(YARRRML_MAPPINGS):
        if mapping_format == R2RML_NAMESPACE:
            source_list = add_table(yarrrml_data, mapping)
        else:
            source_list, mapping_external_references = add_source(
                yarrrml_data, mapping, external_sources, mapping_format
            )
            external_references.extend(mapping_external_references)
        subject_list = add_subject(yarrrml_data, mapping, mapping_format)
        pred = add_predicate_object_maps(yarrrml_data, mapping, mapping_format)
        it = 0
        for source in source_list:
            for subject in subject_list:
                map_aux = add_mapping(mapping, mappings, it, mapping_format)
                if type(source) is list:
                    rml_mapping.append(map_aux + source[0] + subject + pred + source[1])
                else:
                    rml_mapping.append(map_aux + source + subject + pred)
                rml_mapping[len(rml_mapping) - 1] = rml_mapping[len(rml_mapping) - 1][:-2]
                rml_mapping.append(".\n\n\n")
                it = it + 1

    for ref in dict.fromkeys(external_references):
        rml_mapping.append(ref + "\n")

    logger.info("RML content is created!")
    rml_mapping_string = "".join(rml_mapping)
    if mapping_format == RML_NAMESPACE:
        rml_mapping_string = rml_mapping_string.rstrip("\n") + "\n"
    try:
        graph = rdflib.Graph()
        graph.parse(data=rml_mapping_string, format="turtle")
        logger.info("Mapping has been syntactically validated.")
    except BadSyntax as error:
        logger.error("ERROR: There is a syntactic error in the generated mapping")
        logger.error(str(error))
        return None

    logger.info("Translation has finished successfully.")

    return rml_mapping_string


def inverse_translation(rdf_mapping, mapping_format=RML_NAMESPACE):
    if mapping_format not in MAPPING_FORMATS.values():
        raise ValueError(f"Unknown mapping format: {mapping_format}")
    logger.info("Translating [R2]RML mappings to YARRRML")
    yarrrml_mapping = {YARRRML_PREFIXES: {}, YARRRML_MAPPINGS: {}}
    rdf_mapping.bind('rml', rdflib.term.URIRef(
        RML_NAMESPACE if mapping_format == RML_NAMESPACE else RML_OLD_NAMESPACE
    ), replace=True)
    rdf_mapping.bind('rr', rdflib.term.URIRef(R2RML_NAMESPACE), replace=True)
    rdf_mapping.bind('ql', rdflib.term.URIRef(QL_NAMESPACE), replace=True)
    yarrrml_mapping[YARRRML_PREFIXES] = add_inverse_prefix(rdf_mapping)
    query = f'SELECT ?triplesMap WHERE {{ ?triplesMap {turtle_term(RML_LOGICAL_SOURCE)}|{turtle_term(R2RML_LOGICAL_TABLE)} ?source . }} '
    triples_map = [tm[rdflib.Variable('triplesMap')] for tm in rdf_mapping.query(query).bindings]
    if mapping_format == RML_NAMESPACE and not triples_map and len(rdf_mapping):
        raise InvalidMappingError("No RML-Core logical sources found; check the selected profile")

    for tm in triples_map:
        tm_name = tm.split("/")[-1].split("#")[-1]
        if mapping_format == RML_NAMESPACE and tm_name in yarrrml_mapping[YARRRML_MAPPINGS]:
            raise InvalidMappingError(f"Triples maps have the same YARRRML identifier: {tm_name}")
        yarrrml_tm = {YARRRML_SOURCES: [add_inverse_source(tm, rdf_mapping, mapping_format)]}
        subject, classes = add_inverse_subject(tm, rdf_mapping, mapping_format)
        yarrrml_tm.update(subject)
        yarrrml_tm[YARRRML_PREDICATEOBJECT_SHORT] = add_inverse_pom(
            tm, rdf_mapping, classes, yarrrml_mapping[YARRRML_PREFIXES], mapping_format
        )
        yarrrml_mapping[YARRRML_MAPPINGS][tm_name] = yarrrml_tm

    logger.info("Translation has finished successfully.")
    return yarrrml_mapping


def inverse_translate(rdf_mapping, mapping_format=RML_NAMESPACE):
    """Compatibility alias for inverse_translation."""
    return inverse_translation(rdf_mapping, mapping_format)

def merge_mappings(yarrrrml_list):
    combined_mapping = {YARRRML_MAPPINGS: {}}
    prefixes_list = [
        mapping.get(YARRRML_PREFIXES, {}) for mapping in yarrrrml_list
    ]
    combined_mapping = combined_mapping | merge_mapping_section_by_key(YARRRML_PREFIXES, prefixes_list)

    triples_map_ids = dict.fromkeys(
        individual_id
        for mapping in yarrrrml_list
        for individual_id in mapping.get(YARRRML_MAPPINGS, {})
    )
    for individual_id in triples_map_ids:
        mapping_content_list = []
        for mapping in yarrrrml_list:
            if individual_id in mapping.get(YARRRML_MAPPINGS, {}):
                mapping_content_list.append(
                    mapping[YARRRML_MAPPINGS][individual_id]
                )
        combined_mapping[YARRRML_MAPPINGS] = combined_mapping[YARRRML_MAPPINGS] | merge_mapping_section_by_key(individual_id, mapping_content_list)

    stream = StringIO()
    yaml.YAML().dump(combined_mapping, stream)
    return stream.getvalue()
