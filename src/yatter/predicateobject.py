import rdflib
from .constants import *
from .graph import add_inverse_graph
from .source import add_source, add_table
from .subject import add_subject
from .termmap import generate_rml_termmap, generate_cc_termmap, generate_rml_termmap_text
from .mapping import prefixes
from ruamel.yaml import YAML


def add_predicate_object_maps(data, mapping, mapping_format):
    po_template = ""
    mapping_data = data.get(YARRRML_MAPPINGS).get(mapping)
    if YARRRML_PREDICATEOBJECT in mapping_data:
        pom_text = "\t" + R2RML_PREDICATE_OBJECT_MAP + " [\n"
        for predicate_object_map in mapping_data.get(YARRRML_PREDICATEOBJECT):
            po_template += pom_text + add_predicate_object(data, mapping, predicate_object_map, mapping_format) + "\n"
    else:
        logger.warning("The triples map " + mapping + " does not have predicate object maps defined")
    return po_template


def add_predicate_object(data, mapping, predicate_object, mapping_format=RML_URI):
    template = ""

    predicate_list = []
    predicate_list.extend(predicate_object.get(YARRRML_PREDICATES))
    for pm in predicate_list:
        pm_value = pm
        execution = False
        if YARRRML_VALUE in pm and type(pm) is dict:
            pm_value = pm[YARRRML_VALUE]
        elif YARRRML_FUNCTION in pm:
            pm_value = pm[YARRRML_FUNCTION]
            execution = True
        template += generate_rml_termmap(R2RML_PREDICATE, R2RML_PREDICATE_CLASS, pm_value, "\t\t\t")
        if execution:
            template = template.replace(R2RML_CONSTANT + " \"" + pm_value + "\"", RML_EXECUTION + " <" + pm_value + ">")
        if YARRRML_TARGETS in pm:
            template = template[0:-3] + "\t" + RML_LOGICAL_TARGET + " <" + pm[YARRRML_TARGETS] + ">\n\t\t];\n"

    object_maps = predicate_object.get(YARRRML_OBJECTS)
    for om in object_maps:
        object_value = om.get(YARRRML_VALUE)
        if YARRRML_GATHER in om and YARRRML_GATHER_AS in om:
            gather=om[YARRRML_GATHER]
            if isinstance(gather, list):
                gather = gather[0]
            if YARRRML_MAPPING in gather or YARRRML_CONDITION in gather:
                template += ref_cc_mapping(data, mapping, gather, YARRRML_MAPPING, R2RML_PARENT_TRIPLESMAP, mapping_format)
                if YARRRML_GATHER_AS in om and om[YARRRML_GATHER_AS] in YARRRML_GATHER_AS_OPTIONS:
                    template += "\t\t\t" + RML_CC_GATHER_AS + " rdf:" + om[YARRRML_GATHER_AS].capitalize() + ";\n"
                if YARRRML_VALUE in om:
                    text = om.get('value', '')
                    term_map, text = generate_rml_termmap_text(text, mapping_format)
                    if term_map == STAR_QUOTED:
                        if 'quoted' in text:
                            template += "\t\t\t" + term_map + " <" + text[YARRRML_QUOTED] + "_0>;\n"
                        else:
                            template += "\t\t\t" +  term_map + " <" + text[YARRRML_NON_ASSERTED] + "_0>;\n"
                    elif term_map != "rr:constant":
                        template += "\t\t\t" +  term_map + " \"" + text + "\";\n"
                    else:
                        if text.startswith("http"):
                            template += "\t\t\t" +  term_map + " <" + text + ">;\n"
                        else:
                            if ":" in text or "<" in text:
                                template +=  "\t\t\t" + term_map + " " + text + ";\n"
                            else:
                                template += "\t\t\t" +  term_map + " \"" + text + "\";\n"
                template += "\n\t\t];\n"
            else:
                template += generate_cc_termmap(STAR_OBJECT, R2RML_OBJECT_CLASS, om, "\t\t\t", mapping_format) + "\n\t\t];\n"

            if YARRRML_TYPE in om:
                if om.get(YARRRML_TYPE) == 'iri':
                    template = template[0:len(template) - 6] + "\t\t\t" + R2RML_TERMTYPE + " " + R2RML_IRI + "\n\t\t];\n"
                elif om.get(YARRRML_TYPE) == 'blank':
                    template = template[0:len(template) - 6] + "\t\t\t" + R2RML_TERMTYPE + " " + R2RML_BLANK_NODE + "\n\t\t];\n"
                elif om.get(YARRRML_TYPE) == 'literal':
                    template = template[0:len(template) - 6] + "\t\t\t" + R2RML_TERMTYPE + " " + R2RML_LITERAL + "\n\t\t];\n"
        elif object_value is not None:
            rml_map_class, rml_map, r2rml_map = None, None, None
            if mapping_format == STAR_URI:
                rml_property = STAR_OBJECT
            else:
                rml_property = R2RML_OBJECT
            template += generate_rml_termmap(rml_property, R2RML_OBJECT_CLASS, object_value, "\t\t\t", mapping_format)

            optional_value = None
            if YARRRML_DATATYPE in om:
                optional_value = om[YARRRML_DATATYPE]
                rml_map = RML_DATATYPE_MAP
                rml_map_class = RML_DATATYPE_MAP_CLASS
                r2rml_map = R2RML_DATATYPE
            if YARRRML_LANGUAGE in om:
                if '$(' in om[YARRRML_LANGUAGE]:
                    optional_value = om[YARRRML_LANGUAGE]
                else:
                    optional_value = '"' + om[YARRRML_LANGUAGE] + '"'
                rml_map = RML_LANGUAGE_MAP
                rml_map_class = RML_LANGUAGE_MAP_CLASS
                r2rml_map = R2RML_LANGUAGE
            if optional_value is not None:
                if "$(" in optional_value:
                    template = template[0:len(template) - 5] + generate_rml_termmap(rml_map,
                                                                                    rml_map_class,
                                                                                    optional_value,
                                                                                    "\t\t\t\t",
                                                                                    mapping_format) + "\t\t];\n"

                else:
                    template = template[0:len(template) - 5] + "\t\t\t" + r2rml_map + " " + optional_value + "\n\t\t];\n"

            elif YARRRML_TARGETS in om:
                template = template[0:len(template) - 5] + "\t\t\t" + RML_LOGICAL_TARGET + " <" + om[YARRRML_TARGETS] + ">\n\t\t];\n"
            if YARRRML_TYPE in om:
                if om.get(YARRRML_TYPE) == 'iri':
                    template = template[0:len(template) - 5] + "\t\t\t" + R2RML_TERMTYPE + " " + R2RML_IRI + "\n\t\t];\n"
                elif om.get(YARRRML_TYPE) == 'blank':
                    template = template[0:len(template) - 5] + "\t\t\t" + R2RML_TERMTYPE + " " + R2RML_BLANK_NODE + "\n\t\t];\n"
                elif om.get(YARRRML_TYPE) == 'literal':
                    template = template[0:len(template) - 5] + "\t\t\t" + R2RML_TERMTYPE + " " + R2RML_LITERAL + "\n\t\t];\n"

        elif YARRRML_MAPPING in om or YARRRML_NON_ASSERTED in om or YARRRML_QUOTED in om:
            if YARRRML_MAPPING in om:
                template += ref_mapping(data, mapping, om, YARRRML_MAPPING, R2RML_PARENT_TRIPLESMAP, mapping_format)
            elif YARRRML_NON_ASSERTED in om:
                if YARRRML_CONDITION in om:
                    template += ref_mapping(data, mapping, om, YARRRML_NON_ASSERTED, STAR_QUOTED, mapping_format)
                else:
                    template += generate_rml_termmap(STAR_OBJECT, STAR_CLASS, om, "\t\t\t", mapping_format)
            else:
                template += ref_mapping(data, mapping, om, YARRRML_QUOTED, STAR_QUOTED, mapping_format)

        else:
            object_value = om

            if mapping_format == STAR_URI:
                template += generate_rml_termmap(STAR_OBJECT, R2RML_OBJECT_CLASS,
                                                 object_value, "\t\t\t", mapping_format)
            elif YARRRML_FUNCTION in om:
                template += generate_rml_termmap(R2RML_OBJECT, R2RML_OBJECT_CLASS, om[YARRRML_FUNCTION], "\t\t\t",
                                                 mapping_format)
                template = template.replace(R2RML_CONSTANT + " \"" + om[YARRRML_FUNCTION] + "\"",
                                            RML_EXECUTION + " <" + om.get(YARRRML_FUNCTION) + ">")
            else:
                template += generate_rml_termmap(R2RML_OBJECT, R2RML_OBJECT_CLASS,
                                                 object_value, "\t\t\t", mapping_format)
            if type(om) is dict:
                if YARRRML_DATATYPE in om:
                    template = template[0:len(template) - 5] + "\t\t\t" + R2RML_DATATYPE + " " \
                               + om.get(YARRRML_DATATYPE) + "\n\t\t];\n"
                if YARRRML_LANGUAGE in om:
                    template = template[0:len(template) - 5] + "\t\t\t" + R2RML_LANGUAGE + " \"" \
                               + om.get(YARRRML_LANGUAGE) + "\"\n\t\t];\n"
                if YARRRML_TYPE in om:
                    if om.get(YARRRML_TYPE) == "iri":
                        iri = True
                    elif om.get(YARRRML_TYPE) == "literal":
                        template = template[0:len(template) - 5] + "\t\t\t" + R2RML_TERMTYPE + " " \
                                   + R2RML_LITERAL + "\n\t\t];\n"
                    elif om.get(YARRRML_TYPE) == YARRRML_BLANK:
                        template = template[0:len(template) - 5] + "\t\t\t" + R2RML_TERMTYPE + " " \
                                   + R2RML_BLANK_NODE + "\n\t\t];\n"
                if YARRRML_TARGETS in om:
                    template = template[0:len(template) - 5] + "\t\t\t" + RML_LOGICAL_TARGET + " <" + om.get(
                        YARRRML_TARGETS) + ">\n\t\t];\n"

            if YARRRML_IRI in om:
                template = template[0:len(template) - 5] + "\t\t\t" + R2RML_TERMTYPE + " " \
                           + R2RML_IRI + "\n\t\t];\n"

    if YARRRML_GRAPHS in predicate_object:
        graph_list = predicate_object.get(YARRRML_GRAPHS)
        for graph in graph_list:
            graph_value = graph
            if YARRRML_VALUE in graph:
                graph_value = graph[YARRRML_VALUE]
            template += generate_rml_termmap(R2RML_GRAPH_MAP, R2RML_GRAPH_CLASS, graph_value, "\t\t\t")
            if YARRRML_TARGETS in graph:
                template = template[0:-3] + "\t" + RML_LOGICAL_TARGET + " <" + graph[
                    YARRRML_TARGETS] + ">\n\t\t];\n"

    return template + "\t];"


def ref_mapping(data, mapping, om, yarrrml_key, ref_type_property, mapping_format):
    list_mappings = []
    template = ""
    object = R2RML_OBJECT
    for mappings in data.get(YARRRML_MAPPINGS):
        list_mappings.append(mappings)

    mapping_join = om.get(yarrrml_key)

    if mapping_join in list_mappings:
        subject_list = add_subject(data, mapping_join, mapping_format)
        if mapping_format == R2RML_URI:
            source_list = add_table(data, mapping_join)
        else:
            if mapping_format == STAR_URI:
                object = STAR_OBJECT
            source_list, external_references = add_source(data, mapping_join)

        number_joins_rml = len(subject_list) * len(source_list)
        for i in range(number_joins_rml):
            template += "\t\t" + object + \
                        " [\n\t\t\ta " + R2RML_REFOBJECT_CLASS + \
                        ";\n\t\t\t" + ref_type_property + " <" + mapping_join + "_" + str(i) + ">;\n"
            if YARRRML_CONDITION in om:
                conditions = om.get(YARRRML_CONDITION)
                if type(conditions) is not list:
                    conditions = [conditions]
                for condition in conditions:
                    if YARRRML_PARAMETERS in condition:
                        list_parameters = condition.get(YARRRML_PARAMETERS)
                        if len(list_parameters) == 2:

                            try:
                                child = list_parameters[0]['value'].replace('"', r'\"').replace("$(", '"').replace(")",
                                                                                                                   '"')
                                parent = list_parameters[1]['value'].replace('"', r'\"').replace("$(", '"').replace(")",
                                                                                                                    '"')

                            except Exception as e:
                                logger.error("ERROR: Parameters not normalized correctly")

                            template += "\t\t\t" + R2RML_JOIN_CONITION + \
                                        " [\n\t\t\t\t" + R2RML_CHILD + " " + child + \
                                        ";\n\t\t\t\t" + R2RML_PARENT + " " + parent + ";\n\t\t\t];\n"

                        else:
                            logger.error("Error in reference mapping another mapping in mapping " + mapping)
                            raise Exception("Only two parameters can be indicated (child and parent)")
                template += "\t\t];\n"
            else:
                template += "\n\t\t]\n"

    else:
        logger.error("Error in reference another mapping in mapping " + mapping)
        raise Exception("Review how is defined the reference to other mappings")

    return template

def ref_cc_mapping(data, mapping, om, yarrrml_key, ref_type_property, mapping_format):
    list_mappings = []
    template = ""
    object = R2RML_OBJECT
    for mappings in data.get(YARRRML_MAPPINGS):
        list_mappings.append(mappings)

    mapping_join = om.get(yarrrml_key)

    if mapping_join in list_mappings:
        subject_list = add_subject(data, mapping_join, mapping_format)
        if mapping_format == R2RML_URI:
            source_list = add_table(data, mapping_join)
        else:
            if mapping_format == STAR_URI:
                object = STAR_OBJECT
            source_list, external_references = add_source(data, mapping_join)

        number_joins_rml = len(subject_list) * len(source_list)
        for i in range(number_joins_rml):
            template += "\t\t" + object + \
                        " [\n\t\t\ta " + R2RML_OBJECT_CLASS + ";\n\t\t\t" + RML_CC_GATHER + \
                        " (\n\t\t\t\t[\n\t\t\t\t\t" + ref_type_property + " <" + mapping_join + "_" + str(i) + ">;\n"
            if YARRRML_CONDITION in om:
                conditions = om.get(YARRRML_CONDITION)
                if type(conditions) is not list:
                    conditions = [conditions]
                for condition in conditions:
                    if YARRRML_PARAMETERS in condition:
                        list_parameters = condition.get(YARRRML_PARAMETERS)
                        if len(list_parameters) == 2:

                            try:
                                child = list_parameters[0]['value'].replace('"', r'\"').replace("$(", '"').replace(")",
                                                                                                                   '"')
                                parent = list_parameters[1]['value'].replace('"', r'\"').replace("$(", '"').replace(")",
                                                                                                                    '"')

                            except Exception as e:
                                logger.error("ERROR: Parameters not normalized correctly")

                            template += "\t\t\t\t\t" + R2RML_JOIN_CONITION + \
                                        " [\n\t\t\t\t\t\t" + R2RML_CHILD + " " + child + \
                                        ";\n\t\t\t\t\t\t" + R2RML_PARENT + " " + parent + ";\n\t\t\t\t\t];\n"

                        else:
                            logger.error("Error in reference mapping another mapping in mapping " + mapping)
                            raise Exception("Only two parameters can be indicated (child and parent)")
                template += "\t\t\t\t]\n\t\t\t);\n"
            else:
                template += "\t\t\t\t]\n\t\t\t);\n"

    else:
        logger.error("Error in reference another mapping in mapping " + mapping)
        raise Exception("Review how is defined the reference to other mappings")


    return template


def add_inverse_pom(mapping_id, rdf_mapping, classes, prefixes):
    yarrrml_poms = []
    yaml = YAML()
    for c in classes:
        yarrrml_pom = yaml.seq(['rdf:type', find_prefixes(c.toPython(), prefixes)])
        yarrrml_pom.fa.set_flow_style()
        yarrrml_poms.append(yarrrml_pom)

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

    for tm in rdf_mapping.query(query):
        yarrrml_pom = []
        if tm['predicateValue']:
            predicate = tm['predicateValue'].toPython()
        elif tm['predicate']:
            predicate = tm['predicate'].toPython()
        else:
            logger.error("ERROR: There is POM without predicate map defined")
            raise Exception("Review your mapping " + str(mapping_id))

        if not predicate.startswith("http"):
            predicate = '$(' + predicate + ')'
        elif predicate.startswith("http") and "{" not in predicate:
            predicate = find_prefixes(predicate, prefixes)
        else:
            predicate = predicate.replace('{', '$(').replace('}', ')')

        predicate = find_prefixes(predicate, prefixes)

        if tm['parentTriplesMap']:
            if tm['child']:
                yarrrml_pom = {'p': predicate, 'o': {'mapping': None, 'condition':
                    {'function': 'equal', 'parameters': []}}}
                yarrrml_pom['o']['mapping'] = tm['parentTriplesMap'].split("/")[-1]
                child = yaml.seq(['str1', '$(' + tm['child'] + ')'])
                child.fa.set_flow_style()
                parent = yaml.seq(['str2', '$(' + tm['parent'] + ')'])
                parent.fa.set_flow_style()
                yarrrml_pom['o']['condition']['parameters'].append(child)
                yarrrml_pom['o']['condition']['parameters'].append(parent)
            else:
                yarrrml_pom = {'p': predicate, 'o': {'mapping': tm['parentTriplesMap'].split("/")[-1]}}


        else:
            datatype = None
            language = None

            if tm['objectValue']:  # we have extended objectMap version
                object = tm['objectValue'].toPython()
            elif tm['object']:
                object = tm['object'].toPython()
            else:
                logger.error("There is not object for a given predicate")
                raise Exception("Review your mapping " + str(mapping_id))

            if not object.startswith("http"):
                object = '$(' + object + ')'
            elif object.startswith("http") and "{" not in object:
                object = find_prefixes(object, prefixes)
            else:
                object = object.replace('{', '$(').replace('}', ')')

            if tm['termtype']:
                if tm['termtype'] == rdflib.URIRef(R2RML_IRI):
                    object = object + '~iri'

            if tm['graphValue']:
                graph_value = add_inverse_graph([tm['graphValue']])
                yarrrml_pom = {'p': predicate, 'o': object}
                yarrrml_pom.update(graph_value)
            else:
                yarrrml_pom.append(predicate)
                yarrrml_pom.append(object)

            if tm[YARRRML_DATATYPE]:
                datatype = tm[YARRRML_DATATYPE].toPython()
                prefix = list({i for i in prefixes if datatype.startswith(prefixes[i])})
                if prefix:
                    datatype = datatype.replace(prefixes[prefix[0]], prefix[0] + ":")
            elif tm['datatypeMapValue']:
                datatype = tm['datatypeMapValue']
                if not datatype.startswith("http"):
                    datatype = '$(' + datatype + ')'
                else:
                    datatype.replace('{', '$(').replace('}', ')')
            if tm[YARRRML_LANGUAGE]:
                language = tm[YARRRML_LANGUAGE].toPython() + "~lang"
            elif tm['languageMapValue']:
                language = tm['languageMapValue']
                if not language.startswith("http"):
                    language = '$(' + language + ')'
                else:
                    language.replace('{', '$(').replace('}', ')')

            if type(yarrrml_pom) is list:
                if datatype:
                    datatype = find_prefixes(datatype, prefixes)
                    yarrrml_pom.append(datatype)
                if language:
                    yarrrml_pom.append(language)
            elif type(yarrrml_pom) is dict:
                if datatype:
                    datatype = find_prefixes(datatype, prefixes)
                    yarrrml_pom[YARRRML_DATATYPE] = datatype
                if language:
                    yarrrml_pom[YARRRML_LANGUAGE] = language

        if type(yarrrml_pom) is list:
            yarrrml_pom = yaml.seq(yarrrml_pom)
            yarrrml_pom.fa.set_flow_style()
        yarrrml_poms.append(yarrrml_pom)

    return yarrrml_poms


def find_prefixes(text, prefixes):
    prefix = list({i for i in prefixes if text.startswith(prefixes[i])})
    if len(prefix) > 0:
        text = text.replace(prefixes[prefix[0]], prefix[0] + ":")
    return text
