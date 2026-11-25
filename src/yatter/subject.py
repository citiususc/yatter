from .constants import *
from .errors import InvalidMappingError
from .termmap import (
    _append_term_map_content,
    _append_term_map_property,
    _term_for_format,
    generate_cc_termmap,
    generate_graph_termmap,
    generate_rml_termmap,
    get_rml_termtype,
)
from .graph import add_inverse_graph
from .core_inverse import RML as CORE, read_expression, read_function, read_gather, read_graph_map, read_targets
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
        if mapping_format == RML_URI:
            rml_subjects.append(
                f"\t{_term_for_format(R2RML_SUBJECT, mapping_format)} [\n"
                f"\t\ta {_term_for_format(R2RML_SUBJECT_CLASS, mapping_format)};\n"
                f"\t\t{_term_for_format(R2RML_TERMTYPE, mapping_format)} "
                f"{_term_for_format(R2RML_BLANK_NODE, mapping_format)};\n\t];\n"
            )
        else:
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
        graph_termmap = generate_graph_termmap(graph, "\t\t\t", mapping_format)
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
            _term_for_format(R2RML_CONSTANT, mapping_format) + " \"" + value + "\"",
            _term_for_format(RML_EXECUTION, mapping_format) + " <" + subject[YARRRML_FUNCTION] + ">",
        )
    if YARRRML_TARGETS in subject:
        termmap = _append_term_map_property(
            termmap, "\t\t", RML_LOGICAL_TARGET,
            "<" + subject[YARRRML_TARGETS] + ">",
        )
    if isinstance(subject, dict) and YARRRML_TYPE in subject:
        if get_rml_termtype(subject[YARRRML_TYPE]) == R2RML_BLANK_NODE:
            termmap = _append_term_map_property(
                termmap, "\t\t", _term_for_format(R2RML_TERMTYPE, mapping_format),
                _term_for_format(R2RML_BLANK_NODE, mapping_format)
            )
    return termmap


def add_inverse_subject(tm, rdf_mapping, mapping_format=RML_OLD_URI):
    if mapping_format == RML_URI:
        return add_inverse_core_subject(tm, rdf_mapping)
    term = lambda value: _term_for_format(value, mapping_format)
    expression_path = "|".join(dict.fromkeys(
        [term(R2RML_TEMPLATE), term(R2RML_COLUMN), RML_REFERENCE, term(R2RML_CONSTANT)]
    ))
    query = f'SELECT ?subject_value  WHERE {{ <{tm}> {term(R2RML_SUBJECT)} ?subject . ' \
            f'?subject {expression_path} ?subject_value' \
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

    yarrrml_subject = {YARRRML_SUBJECT_SHORT: subject}

    query = f'SELECT ?class_value  WHERE {{ <{tm}> {term(R2RML_SUBJECT)} ?subject . ' \
            f'?subject {term(R2RML_CLASS)} ?class_value }} '
    classes = [tm[rdflib.Variable('class_value')] for tm in rdf_mapping.query(query).bindings]

    query = f'SELECT ?graph_value  WHERE {{ <{tm}> {term(R2RML_SUBJECT)} ?subject . ' \
            f'{{ ?subject {term(R2RML_GRAPH)} ?graph_value .  }}' \
            f' UNION ' \
            f' {{ ?subject {term(R2RML_GRAPH_MAP)} ?graph_map .' \
            f' ?graph_map {expression_path} ?graph_value  }} }} '
    graph_values = [tm[rdflib.Variable('graph_value')] for tm in rdf_mapping.query(query).bindings]

    if graph_values:
        yarrrml_subject.update(add_inverse_graph(graph_values))

    return yarrrml_subject, classes


def add_inverse_core_subject(tm, rdf_mapping):
    subject_maps = list(rdf_mapping.objects(tm, CORE.subjectMap))
    subjects = list(rdf_mapping.objects(tm, CORE.subject))
    if len(subject_maps) + len(subjects) != 1:
        raise InvalidMappingError("A mapping must define exactly one subject map")
    if subjects:
        return {YARRRML_SUBJECT_SHORT: str(subjects[0])}, []
    subject_map = subject_maps[0]
    term_type = rdf_mapping.value(subject_map, CORE.termType)
    has_expression = any(rdf_mapping.value(subject_map, predicate) is not None
                         for predicate in (CORE.constant, CORE.reference, CORE.template))
    execution = rdf_mapping.value(subject_map, CORE.functionExecution)
    if execution is not None:
        subject = {YARRRML_SUBJECT_SHORT: read_function(rdf_mapping, execution)}
    elif rdf_mapping.value(subject_map, CORE.gather) is not None:
        subject = {YARRRML_SUBJECT_SHORT: read_gather(rdf_mapping, subject_map)}
    elif not has_expression and term_type == CORE.BlankNode:
        subject = {}
    else:
        value = read_expression(rdf_mapping, subject_map)
        if term_type == CORE.BlankNode:
            subject = {YARRRML_SUBJECT_SHORT: {YARRRML_VALUE: value, YARRRML_TYPE: YARRRML_BLANK}}
        else:
            subject = {YARRRML_SUBJECT_SHORT: value}
    classes = list(rdf_mapping.objects(subject_map, CORE["class"]))
    graph_values = list(rdf_mapping.objects(subject_map, CORE.graph))
    for graph_map in rdf_mapping.objects(subject_map, CORE.graphMap):
        graph_values.append(read_graph_map(rdf_mapping, graph_map))
    if graph_values:
        subject[YARRRML_GRAPHS] = [str(value) if isinstance(value, rdflib.URIRef) else value
                                   for value in graph_values]
    targets = read_targets(rdf_mapping, subject_map)
    if targets:
        current = subject.get(YARRRML_SUBJECT_SHORT)
        if current is None:
            raise InvalidMappingError("Targets on anonymous subjects cannot be represented")
        if not isinstance(current, dict):
            current = {YARRRML_VALUE: current}
        current[YARRRML_TARGETS] = targets
        subject[YARRRML_SUBJECT_SHORT] = [current]
    return subject, classes
