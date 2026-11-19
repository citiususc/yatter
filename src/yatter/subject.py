from .constants import *
from .errors import InvalidMappingError
from .termmap import (
    _append_term_map_content,
    _append_term_map_property,
    generate_cc_termmap,
    generate_graph_termmap,
    generate_rml_termmap,
    get_rml_termtype,
)
from .graph import add_inverse_graph
import rdflib


def add_subject(data, mapping, mapping_format):
    mapping_data = data[YARRRML_MAPPINGS][mapping]
    if YARRRML_SUBJECTS not in mapping_data:
        raise InvalidMappingError("ERROR: no subjects in mapping " + mapping)

    rml_subjects = [
        _generate_subject(data, mapping, subject, mapping_format)
        for subject in mapping_data[YARRRML_SUBJECTS]
    ]
    if not rml_subjects:
        rml_subjects.append(
            generate_rml_termmap(
                R2RML_SUBJECT, R2RML_SUBJECT_CLASS, R2RML_BLANK_NODE,
                "\t\t", mapping_format,
            ).replace(R2RML_CONSTANT, R2RML_TERMTYPE)
        )

    graphs = mapping_data.get(YARRRML_GRAPHS, [])
    if not isinstance(graphs, list):
        graphs = [graphs]
    for graph in graphs:
        graph_termmap = generate_graph_termmap(graph, "\t\t\t")
        rml_subjects = [
            _append_term_map_content(subject, "\t\t", graph_termmap)
            for subject in rml_subjects
        ]

    return rml_subjects


def _generate_subject(data, mapping, subject, mapping_format):
    if YARRRML_QUOTED in subject or YARRRML_NON_ASSERTED in subject:
        if YARRRML_CONDITION not in subject:
            return generate_rml_termmap(STAR_SUBJECT, STAR_CLASS, subject, "\t\t")

        from .predicateobject import ref_mapping

        key = YARRRML_NON_ASSERTED if YARRRML_NON_ASSERTED in subject else YARRRML_QUOTED
        termmap = ref_mapping(data, mapping, subject, key, STAR_QUOTED, mapping_format)
        return (
            termmap.replace(R2RML_REFOBJECT_CLASS, STAR_CLASS)
            .replace(STAR_OBJECT, STAR_SUBJECT)
            .replace("\t\t\t\t", "\t\t\t\t\t")
            .replace("\t\t", "\t")
        )

    if mapping_format == STAR_URI:
        return generate_rml_termmap(STAR_SUBJECT, R2RML_SUBJECT_CLASS, subject, "\t\t")
    if YARRRML_GATHER in subject:
        return (
            generate_cc_termmap(
                STAR_SUBJECT, R2RML_SUBJECT_CLASS, subject, "\t\t\t", mapping_format
            )
            + "\n\t\t];\n"
        )

    value = subject
    if isinstance(subject, dict) and YARRRML_VALUE in subject:
        value = subject[YARRRML_VALUE]
    elif YARRRML_FUNCTION in subject:
        value = subject[YARRRML_FUNCTION]

    termmap = generate_rml_termmap(
        R2RML_SUBJECT, R2RML_SUBJECT_CLASS, value, "\t\t", mapping_format
    )
    if YARRRML_FUNCTION in subject:
        termmap = termmap.replace(
            R2RML_CONSTANT + " \"" + value + "\"",
            RML_EXECUTION + " <" + subject[YARRRML_FUNCTION] + ">",
        )
    if YARRRML_TARGETS in subject:
        termmap = _append_term_map_property(
            termmap, "\t\t", RML_LOGICAL_TARGET,
            "<" + subject[YARRRML_TARGETS] + ">",
        )
    if isinstance(subject, dict) and YARRRML_TYPE in subject:
        if get_rml_termtype(subject[YARRRML_TYPE]) == R2RML_BLANK_NODE:
            termmap = _append_term_map_property(
                termmap, "\t\t", R2RML_TERMTYPE, R2RML_BLANK_NODE
            )
    return termmap


def add_inverse_subject(tm, rdf_mapping):
    query = f'SELECT ?subject_value  WHERE {{ <{tm}> {R2RML_SUBJECT} ?subject . ' \
            f'?subject {R2RML_TEMPLATE}|{R2RML_COLUMN}|{RML_REFERENCE}|{R2RML_CONSTANT} ?subject_value' \
            f'}} '

    subject = [tm[rdflib.Variable('subject_value')].value for tm in rdf_mapping.query(query).bindings]
    if len(subject) > 1:
        logger.error("There are more than one subject in your mapping")
        raise InvalidMappingError("A mapping defines one and only one subjectMap")
    if not subject:
        raise InvalidMappingError("A mapping must define one subjectMap")
    subject = subject[0]
    # this means it's a column
    if not subject.startswith("http"):
        subject = '$(' + subject + ')'
    else:
        if '{' in subject:
            subject = subject.replace('{', "$(").replace('}', ')')

    yarrrml_subject = {'s': subject}

    query = f'SELECT ?class_value  WHERE {{ <{tm}> {R2RML_SUBJECT} ?subject . ' \
            f'?subject {R2RML_CLASS} ?class_value }} '
    classes = [tm[rdflib.Variable('class_value')] for tm in rdf_mapping.query(query).bindings]

    query = f'SELECT ?graph_value  WHERE {{ <{tm}> {R2RML_SUBJECT} ?subject . ' \
            f'{{ ?subject {R2RML_GRAPH} ?graph_value .  }}' \
            f' UNION ' \
            f' {{ ?subject {R2RML_GRAPH_MAP} ?graph_map .' \
            f' ?graph_map {R2RML_TEMPLATE}|{R2RML_COLUMN}|{RML_REFERENCE}|{R2RML_CONSTANT} ?graph_value  }} }} '
    graph_values = [tm[rdflib.Variable('graph_value')] for tm in rdf_mapping.query(query).bindings]

    if graph_values:
        yarrrml_subject.update(add_inverse_graph(graph_values))

    return yarrrml_subject, classes
