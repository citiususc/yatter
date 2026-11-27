from .constants import *
from .vocabulary import turtle_term
from .source import add_source, add_table
from .subject import add_subject
from .termmap import (
    _append_term_map_content,
    _append_term_map_property,
    _format_term_map_value,
    _term_for_format,
    generate_cc_termmap,
    generate_graph_termmap,
    generate_rml_termmap,
    generate_rml_termmap_text,
    get_rml_termtype,
)
from .errors import InvalidMappingError
from .inverse_predicateobject import add_inverse_pom


def add_predicate_object_maps(data, mapping, mapping_format):
    mapping_data = data[YARRRML_MAPPINGS][mapping]
    if YARRRML_PREDICATEOBJECT not in mapping_data:
        logger.warning("The triples map " + mapping + " does not have predicate object maps defined")
        return ""
    return "".join(
        "\t" + _term_for_format(R2RML_PREDICATE_OBJECT_MAP, mapping_format) + " [\n"
        + add_predicate_object(data, mapping, pom, mapping_format) + "\n"
        for pom in mapping_data[YARRRML_PREDICATEOBJECT]
    )


def add_predicate_object(data, mapping, predicate_object, mapping_format=RML_OLD_NAMESPACE):
    predicates = "".join(
        _generate_predicate_map(predicate, mapping_format)
        for predicate in predicate_object[YARRRML_PREDICATES]
    )
    objects = _generate_object_maps(
        data, mapping, predicate_object[YARRRML_OBJECTS], mapping_format
    )
    graphs = "".join(
        generate_graph_termmap(graph, "\t\t\t", mapping_format)
        for graph in predicate_object.get(YARRRML_GRAPHS, [])
    )
    return predicates + objects + graphs + "\t];"


def _generate_predicate_map(predicate, mapping_format=RML_OLD_NAMESPACE):
    value = predicate
    execution = False
    if isinstance(predicate, dict) and YARRRML_VALUE in predicate:
        value = predicate[YARRRML_VALUE]
    elif YARRRML_FUNCTION in predicate:
        value = predicate[YARRRML_FUNCTION]
        execution = True
    template = generate_rml_termmap(
        R2RML_PREDICATE, R2RML_PREDICATE_CLASS, value, "\t\t\t",
        RML_OLD_NAMESPACE if mapping_format == R2RML_NAMESPACE else mapping_format
    )
    if execution:
        template = template.replace(
            _term_for_format(R2RML_CONSTANT, mapping_format) + " \"" + value + "\"",
            _term_for_format(RML_EXECUTION, mapping_format) + " <" + value + ">"
        )
    if YARRRML_TARGETS in predicate:
        template = _append_term_map_property(
            template, "\t\t\t", turtle_term(RML_LOGICAL_TARGET),
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
            template += "\t\t\t" + turtle_term(RML_CC_GATHER_AS) + " " + RDF_TERM_PREFIX + obj[YARRRML_GATHER_AS].capitalize() + ";\n"
        if YARRRML_VALUE in obj:
            term_map, text = generate_rml_termmap_text(obj[YARRRML_VALUE], mapping_format)
            template += "\t\t\t" + _term_for_format(term_map, mapping_format) + " " + _format_term_map_value(term_map, text) + ";\n"
        template += "\n\t\t];\n"
    else:
        template = generate_cc_termmap(
            STAR_OBJECT, R2RML_OBJECT_CLASS, obj, "\t\t\t", mapping_format
        ) + "\n\t\t];\n"
    return _append_object_term_type(template, obj, mapping_format)


def _generate_value_object(obj, mapping_format):
    rml_property = STAR_OBJECT if mapping_format == STAR_URI else R2RML_OBJECT
    template = generate_rml_termmap(
        rml_property, R2RML_OBJECT_CLASS, obj[YARRRML_VALUE], "\t\t\t", mapping_format,
        literal_constant=obj.get(YARRRML_TYPE) == YARRRML_LITERAL_TYPE,
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
            template = _append_term_map_property(template, "\t\t\t", _term_for_format(shortcut, mapping_format), optional_value)
    if YARRRML_TARGETS in obj:
        template = _append_term_map_property(
            template, "\t\t\t", turtle_term(RML_LOGICAL_TARGET), "<" + obj[YARRRML_TARGETS] + ">"
        )
    return _append_object_term_type(template, obj, mapping_format)


def _append_object_term_type(template, obj, mapping_format=RML_OLD_NAMESPACE):
    if YARRRML_TYPE in obj:
        term_type = get_rml_termtype(obj[YARRRML_TYPE])
        if term_type:
            return _append_term_map_property(
                template, "\t\t\t", _term_for_format(R2RML_TERMTYPE, mapping_format),
                _term_for_format(term_type, mapping_format)
            )
    return template


def _generate_other_object(obj, mapping_format):
    if mapping_format == STAR_URI:
        template = generate_rml_termmap(STAR_OBJECT, R2RML_OBJECT_CLASS, obj, "\t\t\t", mapping_format)
    elif YARRRML_FUNCTION in obj:
        value = obj[YARRRML_FUNCTION]
        template = generate_rml_termmap(R2RML_OBJECT, R2RML_OBJECT_CLASS, value, "\t\t\t", mapping_format)
        template = template.replace(
            _term_for_format(R2RML_CONSTANT, mapping_format) + " \"" + value + "\"",
            _term_for_format(RML_EXECUTION, mapping_format) + " <" + value + ">"
        )
    else:
        template = generate_rml_termmap(R2RML_OBJECT, R2RML_OBJECT_CLASS, obj, "\t\t\t", mapping_format)
    if isinstance(obj, dict):
        if YARRRML_DATATYPE in obj:
            template = _append_term_map_property(template, "\t\t\t", _term_for_format(R2RML_DATATYPE, mapping_format), obj[YARRRML_DATATYPE])
        if YARRRML_LANGUAGE in obj:
            template = _append_term_map_property(
                template, "\t\t\t", _term_for_format(R2RML_LANGUAGE, mapping_format), "\"" + obj[YARRRML_LANGUAGE] + "\""
            )
        template = _append_object_term_type(template, obj, mapping_format)
        if YARRRML_TARGETS in obj:
            template = _append_term_map_property(
                template, "\t\t\t", turtle_term(RML_LOGICAL_TARGET), "<" + obj[YARRRML_TARGETS] + ">"
            )
    if YARRRML_IRI in obj:
        template = _append_term_map_property(template, "\t\t\t", _term_for_format(R2RML_TERMTYPE, mapping_format), _term_for_format(R2RML_IRI, mapping_format))
    return template


def _resolve_mapping_join(data, mapping, mapping_join):
    if mapping_join not in data.get(YARRRML_MAPPINGS, {}):
        logger.error("Error in reference another mapping in mapping " + mapping)
        raise InvalidMappingError("Review how is defined the reference to other mappings")

    return mapping_join


def _get_mapping_join_cardinality(data, mapping_join, mapping_format):
    subject_list = add_subject(data, mapping_join, mapping_format)
    if mapping_format == R2RML_NAMESPACE:
        source_list = add_table(data, mapping_join)
    else:
        source_list, _ = add_source(data, mapping_join, mapping_format=mapping_format)
    return len(subject_list) * len(source_list)


def _format_join_conditions(om, mapping, indentation, mapping_format=RML_OLD_NAMESPACE):
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
            raise InvalidMappingError("Only two parameters can be indicated (child and parent)")

        try:
            child = parameters[0][YARRRML_VALUE].replace('"', r'\"').replace("$(", '"').replace(")", '"')
            parent = parameters[1][YARRRML_VALUE].replace('"', r'\"').replace("$(", '"').replace(")", '"')
        except (KeyError, AttributeError, TypeError) as error:
            logger.error("ERROR: Parameters not normalized correctly")
            raise InvalidMappingError(
                "Join parameters were not normalized correctly"
            ) from error

        template += indentation + _term_for_format(R2RML_JOIN_CONITION, mapping_format) + \
                    " [\n" + indentation + "\t" + _term_for_format(R2RML_CHILD, mapping_format) + " " + child + \
                    ";\n" + indentation + "\t" + _term_for_format(R2RML_PARENT, mapping_format) + " " + parent + \
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
        template += "\t\t" + _term_for_format(object_property, mapping_format) + \
                    " [\n\t\t\ta " + _term_for_format(R2RML_REFOBJECT_CLASS, mapping_format) + \
                    ";\n\t\t\t" + _term_for_format(ref_type_property, mapping_format) + " <" + mapping_join + "_" + str(i) + ">;\n"
        if YARRRML_CONDITION in om:
            template += _format_join_conditions(om, mapping, "\t\t\t", mapping_format)
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
        template += "\t\t" + _term_for_format(object_property, mapping_format) + \
                    " [\n\t\t\ta " + _term_for_format(R2RML_OBJECT_CLASS, mapping_format) + ";\n\t\t\t" + turtle_term(RML_CC_GATHER) + \
                    " (\n\t\t\t\t[\n\t\t\t\t\t" + _term_for_format(ref_type_property, mapping_format) + " <" + mapping_join + "_" + str(i) + ">;\n"
        template += _format_join_conditions(om, mapping, "\t\t\t\t\t", mapping_format)
        template += "\t\t\t\t]\n\t\t\t);\n"
    return template
