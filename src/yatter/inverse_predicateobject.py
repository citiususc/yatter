import rdflib
from ruamel.yaml import YAML

from .constants import *
from .errors import InvalidMappingError
from .graph import add_inverse_graph
from .termmap import _term_for_format
from .core_inverse import read_predicate_object_maps


def add_inverse_pom(mapping_id, rdf_mapping, classes, prefixes, mapping_format=RML_OLD_URI):
    if mapping_format == RML_URI:
        return read_predicate_object_maps(rdf_mapping, mapping_id, classes)
    yarrrml_poms = []
    yaml = YAML()
    for c in classes:
        yarrrml_pom = yaml.seq([RDF_TYPE, find_prefixes(c.toPython(), prefixes)])
        yarrrml_pom.fa.set_flow_style()
        yarrrml_poms.append(yarrrml_pom)

    for row in rdf_mapping.query(_inverse_pom_query(mapping_id, mapping_format)):
        predicate = _inverse_predicate(row, mapping_id, prefixes)
        if row['parentTriplesMap']:
            pom = _inverse_reference_object(row, predicate, yaml)
        else:
            pom = _inverse_value_object(row, predicate, mapping_id, prefixes, mapping_format)
        if isinstance(pom, list):
            pom = yaml.seq(pom)
            pom.fa.set_flow_style()
        yarrrml_poms.append(pom)
    return yarrrml_poms


def _inverse_pom_query(mapping_id, mapping_format=RML_OLD_URI):
    term = lambda value: _term_for_format(value, mapping_format)
    expression_path = "|".join(dict.fromkeys(
        [term(R2RML_TEMPLATE), term(R2RML_COLUMN), term(R2RML_CONSTANT), RML_REFERENCE]
    ))
    simple_path = "|".join(dict.fromkeys(
        [term(R2RML_TEMPLATE), term(R2RML_CONSTANT), RML_REFERENCE]
    ))
    query = f'SELECT ?predicate ?predicateValue ?object ?objectValue ?termtype ?datatype ?datatypeMapValue ' \
            f'?language ?languageMapValue ?parentTriplesMap ?child ?parent ?graphValue' \
            f' WHERE {{ ' \
            f'<{mapping_id}> {term(R2RML_PREDICATE_OBJECT_MAP)} ?predicateObjectMap . ' \
            f'?predicateObjectMap {term(R2RML_PREDICATE)}|{term(R2RML_SHORTCUT_PREDICATE)} ?predicate .' \
            f'OPTIONAL {{ ?predicate {expression_path} ?predicateValue . }}' \
            f'?predicateObjectMap {term(R2RML_OBJECT)}|{term(R2RML_SHORTCUT_OBJECT)} ?object .' \
            f' {{ OPTIONAL {{ ?predicateObjectMap {term(R2RML_GRAPH)} ?graphValue .}}' \
            f' }} UNION {{' \
            f' OPTIONAL {{ ' \
            f' ?predicateObjectMap {term(R2RML_GRAPH_MAP)} ?graphMap . ' \
            f' ?graphMap {simple_path} ?graphValue .}} }}' \
            f'OPTIONAL {{ ' \
            f'?object {expression_path} ?objectValue .' \
            f'OPTIONAL {{ ?object {term(R2RML_TERMTYPE)} ?termtype . }}' \
            f'OPTIONAL {{ ?object {term(R2RML_DATATYPE)} ?datatype .}} ' \
            f'OPTIONAL {{ ' \
            f' ?object {RML_DATATYPE_MAP} ?datatypeMap .' \
            f' ?datatypeMap {simple_path} ?datatypeMapValue .}} ' \
            f'OPTIONAL {{ ?object {term(R2RML_LANGUAGE)} ?language .}} ' \
            f'OPTIONAL {{ ' \
            f' ?object {RML_LANGUAGE_MAP} ?languageMap .' \
            f' ?languageMap {simple_path} ?languageMapValue .}} }} ' \
            f'OPTIONAL {{ ?object {term(R2RML_PARENT_TRIPLESMAP)} ?parentTriplesMap .' \
            f'OPTIONAL {{ ' \
            f'?object {term(R2RML_JOIN_CONITION)} ?join_condition .' \
            f'?join_condition {term(R2RML_CHILD)} ?child .' \
            f'?join_condition {term(R2RML_PARENT)} ?parent }} }}' \
            f'}}'

    return query


def _inverse_term_value(value, prefixes):
    if not value.startswith("http"):
        return '$(' + value + ')'
    if "{" not in value:
        return find_prefixes(value, prefixes)
    return value.replace('{', '$(').replace('}', ')')


def _inverse_predicate(row, mapping_id, prefixes):
    predicate = row['predicateValue'] or row['predicate']
    if not predicate:
        logger.error("ERROR: There is POM without predicate map defined")
        raise InvalidMappingError("Review your mapping " + str(mapping_id))
    return find_prefixes(_inverse_term_value(predicate.toPython(), prefixes), prefixes)


def _inverse_reference_object(row, predicate, yaml):
    obj = {YARRRML_MAPPING: row['parentTriplesMap'].split("/")[-1]}
    if row['child']:
        parameters = []
        for name, value in ((YARRRML_JOIN_CHILD_PARAMETER, row['child']),
                            (YARRRML_JOIN_PARENT_PARAMETER, row['parent'])):
            parameter = yaml.seq([name, '$(' + value + ')'])
            parameter.fa.set_flow_style()
            parameters.append(parameter)
        obj[YARRRML_CONDITION] = {YARRRML_FUNCTION: YARRRML_EQUAL, YARRRML_PARAMETERS: parameters}
    return {YARRRML_PREDICATE_SHORT: predicate, YARRRML_OBJECT_SHORT: obj}


def _inverse_value_object(row, predicate, mapping_id, prefixes, mapping_format=RML_OLD_URI):
    value = row['objectValue'] or row['object']
    if not value:
        logger.error("There is not object for a given predicate")
        raise InvalidMappingError("Review your mapping " + str(mapping_id))
    value = _inverse_term_value(value.toPython(), prefixes)
    iri_namespace = RML_URI if mapping_format == RML_URI else R2RML_URI
    if row['termtype'] == rdflib.URIRef(iri_namespace + "IRI"):
        value += YARRRML_IRI
    if row['graphValue']:
        pom = {YARRRML_PREDICATE_SHORT: predicate, YARRRML_OBJECT_SHORT: value}
        pom.update(add_inverse_graph([row['graphValue']]))
    else:
        pom = [predicate, value]

    datatype = None
    if row[YARRRML_DATATYPE]:
        datatype = find_prefixes(row[YARRRML_DATATYPE].toPython(), prefixes)
    elif row['datatypeMapValue']:
        datatype = _inverse_map_value(row['datatypeMapValue'])
    language = None
    if row[YARRRML_LANGUAGE]:
        language = row[YARRRML_LANGUAGE].toPython() + YARRRML_LANG
    elif row['languageMapValue']:
        language = _inverse_map_value(row['languageMapValue'])
    for key, optional_value in ((YARRRML_DATATYPE, datatype), (YARRRML_LANGUAGE, language)):
        if optional_value:
            if key == YARRRML_DATATYPE:
                optional_value = find_prefixes(optional_value, prefixes)
            if isinstance(pom, list):
                pom.append(optional_value)
            else:
                pom[key] = optional_value
    return pom


def _inverse_map_value(value):
    if not value.startswith("http"):
        return '$(' + value + ')'
    return value.replace('{', '$(').replace('}', ')')


def find_prefixes(text, prefixes):
    prefix = list({i for i in prefixes if text.startswith(prefixes[i])})
    if len(prefix) > 0:
        text = text.replace(prefixes[prefix[0]], prefix[0] + ":")
    return text
