import rdflib
from .constants import *
from .graph import add_inverse_graph
from .source import add_source, add_table
from .subject import add_subject
from .termmap import (
    _append_term_map_content,
    _append_term_map_property,
    _format_term_map_value,
    generate_cc_termmap,
    generate_graph_termmap,
    generate_rml_termmap,
    generate_rml_termmap_text,
    get_rml_termtype,
)
from ruamel.yaml import YAML


def add_predicate_object_maps(data, mapping, mapping_format):
    mapping_data = data[YARRRML_MAPPINGS][mapping]
    if YARRRML_PREDICATEOBJECT not in mapping_data:
        logger.warning("The triples map " + mapping + " does not have predicate object maps defined")
        return ""
    return "".join(
        "\t" + R2RML_PREDICATE_OBJECT_MAP + " [\n"
        + add_predicate_object(data, mapping, pom, mapping_format) + "\n"
        for pom in mapping_data[YARRRML_PREDICATEOBJECT]
    )


def add_predicate_object(data, mapping, predicate_object, mapping_format=RML_URI):
    predicates = "".join(
        _generate_predicate_map(predicate)
        for predicate in predicate_object[YARRRML_PREDICATES]
    )
    objects = _generate_object_maps(
        data, mapping, predicate_object[YARRRML_OBJECTS], mapping_format
    )
    graphs = "".join(
        generate_graph_termmap(graph, "\t\t\t")
        for graph in predicate_object.get(YARRRML_GRAPHS, [])
    )
    return predicates + objects + graphs + "\t];"


def _generate_predicate_map(predicate):
    value = predicate
    execution = False
    if isinstance(predicate, dict) and YARRRML_VALUE in predicate:
        value = predicate[YARRRML_VALUE]
    elif YARRRML_FUNCTION in predicate:
        value = predicate[YARRRML_FUNCTION]
        execution = True
    template = generate_rml_termmap(
        R2RML_PREDICATE, R2RML_PREDICATE_CLASS, value, "\t\t\t"
    )
    if execution:
        template = template.replace(
            R2RML_CONSTANT + " \"" + value + "\"", RML_EXECUTION + " <" + value + ">"
        )
    if YARRRML_TARGETS in predicate:
        template = _append_term_map_property(
            template, "\t\t\t", RML_LOGICAL_TARGET,
            "<" + predicate[YARRRML_TARGETS] + ">",
        )
    return template


def _generate_object_maps(data, mapping, object_maps, mapping_format):
    return "".join(
        _generate_object_map(data, mapping, obj, mapping_format)
        for obj in object_maps
    )


def _generate_object_map(data, mapping, obj, mapping_format):
    if YARRRML_GATHER in obj and YARRRML_GATHER_AS in obj:
        return _generate_collection_object(data, mapping, obj, mapping_format)
    if obj.get(YARRRML_VALUE) is not None:
        return _generate_value_object(obj, mapping_format)
    if YARRRML_MAPPING in obj:
        return ref_mapping(
            data, mapping, obj, YARRRML_MAPPING, R2RML_PARENT_TRIPLESMAP, mapping_format
        )
    if YARRRML_NON_ASSERTED in obj:
        if YARRRML_CONDITION in obj:
            return ref_mapping(
                data, mapping, obj, YARRRML_NON_ASSERTED, STAR_QUOTED, mapping_format
            )
        return generate_rml_termmap(STAR_OBJECT, STAR_CLASS, obj, "\t\t\t", mapping_format)
    if YARRRML_QUOTED in obj:
        return ref_mapping(data, mapping, obj, YARRRML_QUOTED, STAR_QUOTED, mapping_format)
    return _generate_other_object(obj, mapping_format)


def _generate_collection_object(data, mapping, obj, mapping_format):
    gather = obj[YARRRML_GATHER]
    if isinstance(gather, list):
        gather = gather[0]
    if YARRRML_MAPPING in gather or YARRRML_CONDITION in gather:
        template = ref_cc_mapping(
            data, mapping, gather, YARRRML_MAPPING, R2RML_PARENT_TRIPLESMAP, mapping_format
        )
        if obj[YARRRML_GATHER_AS] in YARRRML_GATHER_AS_OPTIONS:
            template += "\t\t\t" + RML_CC_GATHER_AS + " rdf:" + obj[YARRRML_GATHER_AS].capitalize() + ";\n"
        if YARRRML_VALUE in obj:
            term_map, text = generate_rml_termmap_text(obj[YARRRML_VALUE], mapping_format)
            template += "\t\t\t" + term_map + " " + _format_term_map_value(term_map, text) + ";\n"
        template += "\n\t\t];\n"
    else:
        template = generate_cc_termmap(
            STAR_OBJECT, R2RML_OBJECT_CLASS, obj, "\t\t\t", mapping_format
        ) + "\n\t\t];\n"
    return _append_object_term_type(template, obj)


def _generate_value_object(obj, mapping_format):
    rml_property = STAR_OBJECT if mapping_format == STAR_URI else R2RML_OBJECT
    template = generate_rml_termmap(
        rml_property, R2RML_OBJECT_CLASS, obj[YARRRML_VALUE], "\t\t\t", mapping_format
    )
    optional_value = None
    if YARRRML_DATATYPE in obj:
        optional_value = obj[YARRRML_DATATYPE]
        rml_map, rml_class, shortcut = RML_DATATYPE_MAP, RML_DATATYPE_MAP_CLASS, R2RML_DATATYPE
    if YARRRML_LANGUAGE in obj:
        optional_value = obj[YARRRML_LANGUAGE]
        if "$(" not in optional_value:
            optional_value = '"' + optional_value + '"'
        rml_map, rml_class, shortcut = RML_LANGUAGE_MAP, RML_LANGUAGE_MAP_CLASS, R2RML_LANGUAGE

    if optional_value is not None:
        if "$(" in optional_value:
            content = generate_rml_termmap(
                rml_map, rml_class, optional_value, "\t\t\t\t", mapping_format
            )
            template = _append_term_map_content(template, "\t\t\t", content)
        else:
            template = _append_term_map_property(template, "\t\t\t", shortcut, optional_value)
    elif YARRRML_TARGETS in obj:
        template = _append_term_map_property(
            template, "\t\t\t", RML_LOGICAL_TARGET, "<" + obj[YARRRML_TARGETS] + ">"
        )
    return _append_object_term_type(template, obj)


def _append_object_term_type(template, obj):
    if YARRRML_TYPE in obj:
        term_type = get_rml_termtype(obj[YARRRML_TYPE])
        if term_type:
            return _append_term_map_property(template, "\t\t\t", R2RML_TERMTYPE, term_type)
    return template


def _generate_other_object(obj, mapping_format):
    if mapping_format == STAR_URI:
        template = generate_rml_termmap(STAR_OBJECT, R2RML_OBJECT_CLASS, obj, "\t\t\t", mapping_format)
    elif YARRRML_FUNCTION in obj:
        value = obj[YARRRML_FUNCTION]
        template = generate_rml_termmap(R2RML_OBJECT, R2RML_OBJECT_CLASS, value, "\t\t\t", mapping_format)
        template = template.replace(
            R2RML_CONSTANT + " \"" + value + "\"", RML_EXECUTION + " <" + value + ">"
        )
    else:
        template = generate_rml_termmap(R2RML_OBJECT, R2RML_OBJECT_CLASS, obj, "\t\t\t", mapping_format)
    if isinstance(obj, dict):
        if YARRRML_DATATYPE in obj:
            template = _append_term_map_property(template, "\t\t\t", R2RML_DATATYPE, obj[YARRRML_DATATYPE])
        if YARRRML_LANGUAGE in obj:
            template = _append_term_map_property(
                template, "\t\t\t", R2RML_LANGUAGE, "\"" + obj[YARRRML_LANGUAGE] + "\""
            )
        template = _append_object_term_type(template, obj)
        if YARRRML_TARGETS in obj:
            template = _append_term_map_property(
                template, "\t\t\t", RML_LOGICAL_TARGET, "<" + obj[YARRRML_TARGETS] + ">"
            )
    if YARRRML_IRI in obj:
        template = _append_term_map_property(template, "\t\t\t", R2RML_TERMTYPE, R2RML_IRI)
    return template


def _resolve_mapping_join(data, mapping, mapping_join):
    if mapping_join not in data.get(YARRRML_MAPPINGS, {}):
        logger.error("Error in reference another mapping in mapping " + mapping)
        raise Exception("Review how is defined the reference to other mappings")

    return mapping_join


def _get_mapping_join_cardinality(data, mapping_join, mapping_format):
    subject_list = add_subject(data, mapping_join, mapping_format)
    if mapping_format == R2RML_URI:
        source_list = add_table(data, mapping_join)
    else:
        source_list, _ = add_source(data, mapping_join)
    return len(subject_list) * len(source_list)


def _format_join_conditions(om, mapping, indentation):
    if YARRRML_CONDITION not in om:
        return ""

    conditions = om[YARRRML_CONDITION]
    if not isinstance(conditions, list):
        conditions = [conditions]

    template = ""
    for condition in conditions:
        if YARRRML_PARAMETERS not in condition:
            continue
        parameters = condition[YARRRML_PARAMETERS]
        if len(parameters) != 2:
            logger.error("Error in reference mapping another mapping in mapping " + mapping)
            raise Exception("Only two parameters can be indicated (child and parent)")

        try:
            child = parameters[0]['value'].replace('"', r'\"').replace("$(", '"').replace(")", '"')
            parent = parameters[1]['value'].replace('"', r'\"').replace("$(", '"').replace(")", '"')
        except (KeyError, AttributeError, TypeError):
            logger.error("ERROR: Parameters not normalized correctly")
            raise

        template += indentation + R2RML_JOIN_CONITION + \
                    " [\n" + indentation + "\t" + R2RML_CHILD + " " + child + \
                    ";\n" + indentation + "\t" + R2RML_PARENT + " " + parent + \
                    ";\n" + indentation + "];\n"
    return template


def ref_mapping(data, mapping, om, yarrrml_key, ref_type_property, mapping_format):
    template = ""
    object_property = R2RML_OBJECT
    mapping_join = _resolve_mapping_join(data, mapping, om.get(yarrrml_key))
    number_joins_rml = _get_mapping_join_cardinality(data, mapping_join, mapping_format)
    if mapping_format == STAR_URI:
        object_property = STAR_OBJECT

    for i in range(number_joins_rml):
        template += "\t\t" + object_property + \
                    " [\n\t\t\ta " + R2RML_REFOBJECT_CLASS + \
                    ";\n\t\t\t" + ref_type_property + " <" + mapping_join + "_" + str(i) + ">;\n"
        if YARRRML_CONDITION in om:
            template += _format_join_conditions(om, mapping, "\t\t\t")
            template += "\t\t];\n"
        else:
            template += "\n\t\t]\n"

    return template

def ref_cc_mapping(data, mapping, om, yarrrml_key, ref_type_property, mapping_format):
    template = ""
    object_property = R2RML_OBJECT
    mapping_join = _resolve_mapping_join(data, mapping, om.get(yarrrml_key))
    number_joins_rml = _get_mapping_join_cardinality(data, mapping_join, mapping_format)
    if mapping_format == STAR_URI:
        object_property = STAR_OBJECT

    for i in range(number_joins_rml):
        template += "\t\t" + object_property + \
                    " [\n\t\t\ta " + R2RML_OBJECT_CLASS + ";\n\t\t\t" + RML_CC_GATHER + \
                    " (\n\t\t\t\t[\n\t\t\t\t\t" + ref_type_property + " <" + mapping_join + "_" + str(i) + ">;\n"
        template += _format_join_conditions(om, mapping, "\t\t\t\t\t")
        template += "\t\t\t\t]\n\t\t\t);\n"
    return template


def add_inverse_pom(mapping_id, rdf_mapping, classes, prefixes):
    yarrrml_poms = []
    yaml = YAML()
    for c in classes:
        yarrrml_pom = yaml.seq(['rdf:type', find_prefixes(c.toPython(), prefixes)])
        yarrrml_pom.fa.set_flow_style()
        yarrrml_poms.append(yarrrml_pom)

    for row in rdf_mapping.query(_inverse_pom_query(mapping_id)):
        predicate = _inverse_predicate(row, mapping_id, prefixes)
        if row['parentTriplesMap']:
            pom = _inverse_reference_object(row, predicate, yaml)
        else:
            pom = _inverse_value_object(row, predicate, mapping_id, prefixes)
        if isinstance(pom, list):
            pom = yaml.seq(pom)
            pom.fa.set_flow_style()
        yarrrml_poms.append(pom)
    return yarrrml_poms


def _inverse_pom_query(mapping_id):
    query = f'SELECT ?predicate ?predicateValue ?object ?objectValue ?termtype ?datatype ?datatypeMapValue ' \
            f'?language ?languageMapValue ?parentTriplesMap ?child ?parent ?graphValue' \
            f' WHERE {{ ' \
            f'<{mapping_id}> {R2RML_PREDICATE_OBJECT_MAP} ?predicateObjectMap . ' \
            f'?predicateObjectMap {R2RML_PREDICATE}|{R2RML_SHORTCUT_PREDICATE} ?predicate .' \
            f'OPTIONAL {{ ?predicate {R2RML_TEMPLATE}|{R2RML_COLUMN}|{R2RML_CONSTANT}|{RML_REFERENCE} ?predicateValue . }}' \
            f'?predicateObjectMap {R2RML_OBJECT}|{R2RML_SHORTCUT_OBJECT} ?object .' \
            f' {{ OPTIONAL {{ ?predicateObjectMap {R2RML_GRAPH} ?graphValue .}}' \
            f' }} UNION {{' \
            f' OPTIONAL {{ ' \
            f' ?predicateObjectMap {R2RML_GRAPH_MAP} ?graphMap . ' \
            f' ?graphMap {R2RML_TEMPLATE}|{R2RML_CONSTANT}|{RML_REFERENCE} ?graphValue .}} }}' \
            f'OPTIONAL {{ ' \
            f'?object {R2RML_TEMPLATE}|{R2RML_COLUMN}|{R2RML_CONSTANT}|{RML_REFERENCE} ?objectValue .' \
            f'OPTIONAL {{ ?object {R2RML_TERMTYPE} ?termtype . }}' \
            f'OPTIONAL {{ ?object {R2RML_DATATYPE} ?datatype .}} ' \
            f'OPTIONAL {{ ' \
            f' ?object {RML_DATATYPE_MAP} ?datatypeMap .' \
            f' ?datatypeMap {R2RML_TEMPLATE}|{R2RML_CONSTANT}|{RML_REFERENCE} ?datatypeMapValue .}} ' \
            f'OPTIONAL {{ ?object {R2RML_LANGUAGE} ?language .}} ' \
            f'OPTIONAL {{ ' \
            f' ?object {RML_LANGUAGE_MAP} ?languageMap .' \
            f' ?languageMap {R2RML_TEMPLATE}|{R2RML_CONSTANT}|{RML_REFERENCE} ?languageMapValue .}} }} ' \
            f'OPTIONAL {{ ?object {R2RML_PARENT_TRIPLESMAP} ?parentTriplesMap .' \
            f'OPTIONAL {{ ' \
            f'?object {R2RML_JOIN_CONITION} ?join_condition .' \
            f'?join_condition {R2RML_CHILD} ?child .' \
            f'?join_condition {R2RML_PARENT} ?parent }} }}' \
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
        raise Exception("Review your mapping " + str(mapping_id))
    return find_prefixes(_inverse_term_value(predicate.toPython(), prefixes), prefixes)


def _inverse_reference_object(row, predicate, yaml):
    obj = {'mapping': row['parentTriplesMap'].split("/")[-1]}
    if row['child']:
        parameters = []
        for name, value in (('str1', row['child']), ('str2', row['parent'])):
            parameter = yaml.seq([name, '$(' + value + ')'])
            parameter.fa.set_flow_style()
            parameters.append(parameter)
        obj['condition'] = {'function': 'equal', 'parameters': parameters}
    return {'p': predicate, 'o': obj}


def _inverse_value_object(row, predicate, mapping_id, prefixes):
    value = row['objectValue'] or row['object']
    if not value:
        logger.error("There is not object for a given predicate")
        raise Exception("Review your mapping " + str(mapping_id))
    value = _inverse_term_value(value.toPython(), prefixes)
    if row['termtype'] == rdflib.URIRef(R2RML_IRI):
        value += '~iri'
    if row['graphValue']:
        pom = {'p': predicate, 'o': value}
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
        language = row[YARRRML_LANGUAGE].toPython() + "~lang"
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
