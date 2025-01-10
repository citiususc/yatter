from .constants import *
from .termmap import generate_rml_termmap, generate_cc_termmap
from .graph import add_inverse_graph
import rdflib


## Adds a subject or set of subjects to the given TriplesMap
def add_subject(data, mapping, mapping_format):
    rml_subjects = []

    if YARRRML_SUBJECTS in data.get(YARRRML_MAPPINGS).get(mapping):
        subject = data.get(YARRRML_MAPPINGS).get(mapping).get(YARRRML_SUBJECTS)
    else:
        raise Exception("ERROR: no subjects in mapping " + mapping)

    for individual_subject in subject:
        if YARRRML_QUOTED in individual_subject or YARRRML_NON_ASSERTED in individual_subject:
            if YARRRML_CONDITION in individual_subject:
                from .predicateobject import ref_mapping
                if YARRRML_NON_ASSERTED in individual_subject:
                    subject_termmap = ref_mapping(data, mapping, individual_subject, YARRRML_NON_ASSERTED, STAR_QUOTED,
                                                  mapping_format)
                else:
                    subject_termmap = ref_mapping(data, mapping, individual_subject, YARRRML_QUOTED, STAR_QUOTED,
                                                  mapping_format)
                subject_termmap = subject_termmap.replace(R2RML_REFOBJECT_CLASS, STAR_CLASS).replace(STAR_OBJECT,
                                                                                                     STAR_SUBJECT).replace(
                    "\t\t\t\t", "\t\t\t\t\t").replace("\t\t", "\t")
            else:
                subject_termmap = generate_rml_termmap(STAR_SUBJECT, STAR_CLASS, individual_subject, "\t\t")
        elif mapping_format == STAR_URI:
            subject_termmap = generate_rml_termmap(STAR_SUBJECT, R2RML_SUBJECT_CLASS, individual_subject, "\t\t")
        elif YARRRML_GATHER in individual_subject:
            subject_termmap = generate_cc_termmap(STAR_SUBJECT, R2RML_SUBJECT_CLASS, individual_subject, "\t\t\t", mapping_format) + "\n\t\t];\n"

        else:
            subject_value = individual_subject
            if YARRRML_VALUE in individual_subject and type(individual_subject) is dict:
                subject_value = individual_subject.get(YARRRML_VALUE)
            elif YARRRML_FUNCTION in individual_subject:
                subject_value = individual_subject.get(YARRRML_FUNCTION)

            subject_termmap = generate_rml_termmap(R2RML_SUBJECT, R2RML_SUBJECT_CLASS, subject_value, "\t\t",
                                                   mapping_format)

            if YARRRML_FUNCTION in individual_subject:
                subject_termmap = subject_termmap.replace(R2RML_CONSTANT + " \"" + subject_value + "\"",
                                                          RML_EXECUTION + " <" + individual_subject.get(
                                                              YARRRML_FUNCTION) + ">")

            if YARRRML_TARGETS in individual_subject:
                subject_termmap = subject_termmap[0:-3] + "\t" + RML_LOGICAL_TARGET + " <" + individual_subject[
                    YARRRML_TARGETS] + ">\n\t];\n"

            if isinstance(individual_subject, dict) and YARRRML_TYPE in individual_subject:
                if individual_subject.get(YARRRML_TYPE) == YARRRML_BLANK:
                    subject_termmap = subject_termmap[
                                      0:-3] + "\t" + R2RML_TERMTYPE + " " + R2RML_BLANK_NODE + "\n\t];\n"

        rml_subjects.append(subject_termmap)

    if YARRRML_GRAPHS in data.get(YARRRML_MAPPINGS).get(mapping):
        graphs = data.get(YARRRML_MAPPINGS).get(mapping).get(YARRRML_GRAPHS)
    else:
        graphs = []

    if type(graphs) != list:
        graphs = [graphs]

    for graph in graphs:
        graph_value = graph
        if YARRRML_VALUE in graph:
            graph_value = graph[YARRRML_VALUE]
        graph_termmap = generate_rml_termmap(R2RML_GRAPH_MAP, R2RML_GRAPH_CLASS, graph_value, "\t\t\t")
        if YARRRML_TARGETS in graph:
            graph_termmap = graph_termmap[0:-3] + "\t" + RML_LOGICAL_TARGET + " <" + graph[
                YARRRML_TARGETS] + ">\n\t\t];\n"
        rml_subjects = list(map(lambda subject: subject[0:-4] + graph_termmap + "\t];\n", rml_subjects))

    return rml_subjects


def add_inverse_subject(tm, rdf_mapping):
    query = f'SELECT ?subject_value  WHERE {{ <{tm}> {R2RML_SUBJECT} ?subject . ' \
            f'?subject {R2RML_TEMPLATE}|{R2RML_COLUMN}|{RML_REFERENCE}|{R2RML_CONSTANT} ?subject_value' \
            f'}} '

    subject = [tm[rdflib.Variable('subject_value')].value for tm in rdf_mapping.query(query).bindings]
    if len(subject) > 1:
        logger.error("There are more than one subject in your mapping")
        raise Exception("A mapping defines one and only one subjectMap")
    else:
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
