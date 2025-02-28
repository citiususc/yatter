import rdflib
from .constants import *
from .graph import add_inverse_graph
from .source import add_source, add_table
from .subject import add_subject
from .termmap import generate_rml_termmap, generate_cc_termmap, generate_rml_termmap_text
from ruamel.yaml import YAML


def add_predicate_object_maps(data, mapping, mapping_format):
    mapping_data = data.get(YARRRML_MAPPINGS).get(mapping)
    predicate_objects = mapping_data.get(YARRRML_PREDICATEOBJECT, [])

    po_template = [
        f"\t{R2RML_PREDICATE_OBJECT_MAP} [\n{add_predicate_object(data, mapping, predicate_object_map, mapping_format)}\n"
        for predicate_object_map in predicate_objects
    ]
    return "".join(po_template)


def append_term(template, line, remove_chars=5):
    """Elimina los últimos 'remove_chars' caracteres de 'template' y añade 'line'."""
    return template[:-remove_chars] + line


def get_term_type_str(om, indent3, indent2):
    """Genera la cadena correspondiente al termType según el valor de YARRRML_TYPE en 'om'."""
    type_val = om.get(YARRRML_TYPE)
    if type_val == 'iri':
        return f"{indent3}{R2RML_TERMTYPE} {R2RML_IRI}\n{indent2}];\n"
    elif type_val == 'blank':
        return f"{indent3}{R2RML_TERMTYPE} {R2RML_BLANK_NODE}\n{indent2}];\n"
    elif type_val == 'literal':
        return f"{indent3}{R2RML_TERMTYPE} {R2RML_LITERAL}\n{indent2}];\n"
    return ""


def apply_term_type(template, om, indent3, indent2, remove_chars=5):
    """Aplica la configuración del termType a 'template' si YARRRML_TYPE está presente."""
    term_type_str = get_term_type_str(om, indent3, indent2)
    if term_type_str:
        template = append_term(template, term_type_str, remove_chars)
    return template


def append_logical_target(template, target, indent3, indent2, remove_chars=5):
    """Agrega la línea del logical target a 'template' reemplazando los últimos caracteres."""
    return append_term(template, f"{indent3}{RML_LOGICAL_TARGET} <{target}>\n{indent2}];\n", remove_chars)


def process_single_predicate(pm, indent3, indent2):
    """Procesa un único predicado y retorna la cadena resultante."""
    template = ""
    pm_value = pm
    execution = False
    if isinstance(pm, dict) and YARRRML_VALUE in pm:
        pm_value = pm[YARRRML_VALUE]
    elif YARRRML_FUNCTION in pm:
        pm_value = pm[YARRRML_FUNCTION]
        execution = True

    template += generate_rml_termmap(R2RML_PREDICATE, R2RML_PREDICATE_CLASS, pm_value, indent3)
    if execution:
        template = template.replace(
            R2RML_CONSTANT + " \"" + pm_value + "\"",
            RML_EXECUTION + " <" + pm_value + ">"
        )
    if YARRRML_TARGETS in pm:
        template = append_logical_target(template, pm[YARRRML_TARGETS], indent3, indent2, remove_chars=3)
    return template


def process_object_map_with_gather(om, data, mapping, mapping_format, indent2, indent3, indent4):
    """Procesa un object map que contiene gather y gather_as."""
    template = ""
    gather = om[YARRRML_GATHER]
    if isinstance(gather, list):
        gather = gather[0]
    if YARRRML_MAPPING in gather or YARRRML_CONDITION in gather:
        template += ref_cc_mapping(data, mapping, gather, YARRRML_MAPPING, R2RML_PARENT_TRIPLESMAP, mapping_format)
        if om.get(YARRRML_GATHER_AS) in YARRRML_GATHER_AS_OPTIONS:
            template += f"{indent3}{RML_CC_GATHER_AS} rdf:{om[YARRRML_GATHER_AS].capitalize()};\n"
        if YARRRML_VALUE in om:
            text = om.get('value', '')
            term_map, text = generate_rml_termmap_text(text, mapping_format)
            if term_map == STAR_QUOTED:
                if 'quoted' in text:
                    template += f"{indent3}{term_map} <{text[YARRRML_QUOTED]}_0>;\n"
                else:
                    template += f"{indent3}{term_map} <{text[YARRRML_NON_ASSERTED]}_0>;\n"
            elif term_map != "rr:constant":
                template += f"{indent3}{term_map} \"{text}\";\n"
            else:
                if text.startswith("http"):
                    template += f"{indent3}{term_map} <{text}>;\n"
                else:
                    if ":" in text or "<" in text:
                        template += f"{indent3}{term_map} {text};\n"
                    else:
                        template += f"{indent3}{term_map} \"{text}\";\n"
        template += f"\n{indent2}];\n"
    else:
        template += generate_cc_termmap(STAR_OBJECT, R2RML_OBJECT_CLASS, om, indent3, mapping_format) + f"\n{indent2}];\n"

    template = apply_term_type(template, om, indent3, indent2, remove_chars=6)
    return template


def process_object_map_with_value(om, mapping_format, indent2, indent3, indent4):
    """Procesa un object map cuyo valor se especifica con YARRRML_VALUE."""
    template = ""
    object_value = om.get(YARRRML_VALUE)
    rml_property = STAR_OBJECT if mapping_format == STAR_URI else R2RML_OBJECT
    template += generate_rml_termmap(rml_property, R2RML_OBJECT_CLASS, object_value, indent3, mapping_format)

    optional_value = None
    rml_map = rml_map_class = r2rml_map = None
    if YARRRML_DATATYPE in om:
        optional_value = om[YARRRML_DATATYPE]
        rml_map = RML_DATATYPE_MAP
        rml_map_class = RML_DATATYPE_MAP_CLASS
        r2rml_map = R2RML_DATATYPE
    if YARRRML_LANGUAGE in om:
        lang = om[YARRRML_LANGUAGE]
        optional_value = lang if "$(" in lang else f"\"{lang}\""
        rml_map = RML_LANGUAGE_MAP
        rml_map_class = RML_LANGUAGE_MAP_CLASS
        r2rml_map = R2RML_LANGUAGE

    if optional_value is not None:
        if "$(" in optional_value:
            termmap_str = generate_rml_termmap(rml_map, rml_map_class, optional_value, indent4, mapping_format)
            template = append_term(template, termmap_str, remove_chars=5) + f"{indent2}];\n"
        else:
            template = append_term(template, f"{indent3}{r2rml_map} {optional_value}\n{indent2}];\n", remove_chars=5)
    elif YARRRML_TARGETS in om:
        template = append_logical_target(template, om[YARRRML_TARGETS], indent3, indent2, remove_chars=5)

    template = apply_term_type(template, om, indent3, indent2, remove_chars=5)
    return template


def process_object_map_with_mapping(om, data, mapping, mapping_format, indent3, indent2):
    """Procesa un object map que utiliza mapping, non_asserted o quoted."""
    template = ""
    if YARRRML_MAPPING in om:
        template += ref_mapping(data, mapping, om, YARRRML_MAPPING, R2RML_PARENT_TRIPLESMAP, mapping_format)
    elif YARRRML_NON_ASSERTED in om:
        if YARRRML_CONDITION in om:
            template += ref_mapping(data, mapping, om, YARRRML_NON_ASSERTED, STAR_QUOTED, mapping_format)
        else:
            template += generate_rml_termmap(STAR_OBJECT, STAR_CLASS, om, indent3, mapping_format)
    else:
        template += ref_mapping(data, mapping, om, YARRRML_QUOTED, STAR_QUOTED, mapping_format)
    return template


def process_default_object_map(om, mapping_format, indent3, indent2):
    """Procesa el object map en el caso por defecto."""
    template = ""
    # En este caso 'om' puede ser el valor directo o un dict con YARRRML_VALUE.
    object_value = om if not isinstance(om, dict) else om.get(YARRRML_VALUE)
    if mapping_format == STAR_URI:
        template += generate_rml_termmap(STAR_OBJECT, R2RML_OBJECT_CLASS, object_value, indent3, mapping_format)
    elif YARRRML_FUNCTION in om:
        template += generate_rml_termmap(R2RML_OBJECT, R2RML_OBJECT_CLASS, om[YARRRML_FUNCTION], indent3, mapping_format)
        template = template.replace(
            R2RML_CONSTANT + " \"" + om[YARRRML_FUNCTION] + "\"",
            RML_EXECUTION + " <" + om.get(YARRRML_FUNCTION) + ">"
        )
    else:
        template += generate_rml_termmap(R2RML_OBJECT, R2RML_OBJECT_CLASS, object_value, indent3, mapping_format)
    if isinstance(om, dict):
        if YARRRML_DATATYPE in om:
            template = append_term(template, f"{indent3}{R2RML_DATATYPE} {om.get(YARRRML_DATATYPE)}\n{indent2}];\n")
        if YARRRML_LANGUAGE in om:
            template = append_term(template, f"{indent3}{R2RML_LANGUAGE} \"{om.get(YARRRML_LANGUAGE)}\"\n{indent2}];\n")
        template = apply_term_type(template, om, indent3, indent2, remove_chars=5)
        if YARRRML_TARGETS in om:
            template = append_logical_target(template, om.get(YARRRML_TARGETS), indent3, indent2, remove_chars=5)
    if isinstance(om, dict) and YARRRML_IRI in om:
        template = append_term(template, f"{indent3}{R2RML_TERMTYPE} {R2RML_IRI}\n{indent2}];\n", remove_chars=5)
    return template


def process_graphs(predicate_object, indent3, indent2, indent1):
    """Procesa la sección de graphs (si existen) y retorna la cadena resultante."""
    template = ""
    if YARRRML_GRAPHS in predicate_object:
        for graph in predicate_object.get(YARRRML_GRAPHS, []):
            graph_value = graph[YARRRML_VALUE] if isinstance(graph, dict) and YARRRML_VALUE in graph else graph
            template += generate_rml_termmap(R2RML_GRAPH_MAP, R2RML_GRAPH_CLASS, graph_value, indent3)
            if YARRRML_TARGETS in graph:
                template = append_logical_target(template, graph[YARRRML_TARGETS], indent3, indent2, remove_chars=3)
    return template


def add_predicate_object(data, mapping, predicate_object, mapping_format=RML_URI):
    """Función principal que orquesta el procesamiento de predicados, object maps y graphs."""
    indent1 = "\t"
    indent2 = "\t\t"
    indent3 = "\t\t\t"
    indent4 = "\t\t\t\t"
    template = ""

    # Procesar la lista de predicados
    for pm in predicate_object.get(YARRRML_PREDICATES, []):
        template += process_single_predicate(pm, indent3, indent2)

    # Procesar cada object map
    for om in predicate_object.get(YARRRML_OBJECTS, []):
        if YARRRML_GATHER in om and YARRRML_GATHER_AS in om:
            template += process_object_map_with_gather(om, data, mapping, mapping_format, indent2, indent3, indent4)
        elif YARRRML_VALUE in om:
            template += process_object_map_with_value(om, mapping_format, indent2, indent3, indent4)
        elif any(key in om for key in [YARRRML_MAPPING, YARRRML_NON_ASSERTED, YARRRML_QUOTED]):
            template += process_object_map_with_mapping(om, data, mapping, mapping_format, indent3, indent2)
        else:
            template += process_default_object_map(om, mapping_format, indent3, indent2)

    # Procesar la sección de graphs
    template += process_graphs(predicate_object, indent3, indent2, indent1)

    return template + f"{indent1}];"

def get_list_mappings(data):
    """Obtiene la lista de mappings desde los datos."""
    return data.get(YARRRML_MAPPINGS, [])


def generate_ref_object_header(mapping_join, index, ref_type_property, obj_type):
    """Genera la cabecera del objeto de referencia para un join dado."""
    return (
        f"\t\t{obj_type} [\n"
        f"\t\t\ta {R2RML_REFOBJECT_CLASS};\n"
        f"\t\t\t{ref_type_property} <{mapping_join}_{index}>;\n"
    )


def generate_join_condition(child, parent):
    """Genera la cadena correspondiente a una condición de join."""
    return (
        f"\t\t\t{R2RML_JOIN_CONITION} [\n"
        f"\t\t\t\t{R2RML_CHILD} {child};\n"
        f"\t\t\t\t{R2RML_PARENT} {parent};\n"
        f"\t\t\t];\n"
    )


def process_conditions_block(conditions, mapping):
    """Procesa la(s) condición(es) de join y devuelve la cadena resultante."""
    template = ""
    if not isinstance(conditions, list):
        conditions = [conditions]
    for condition in conditions:
        if YARRRML_PARAMETERS in condition:
            list_parameters = condition.get(YARRRML_PARAMETERS)
            if len(list_parameters) == 2:
                try:
                    child = (
                        list_parameters[0]['value']
                        .replace('"', r'\"')
                        .replace("$(", '"')
                        .replace(")", '"')
                    )
                    parent = (
                        list_parameters[1]['value']
                        .replace('"', r'\"')
                        .replace("$(", '"')
                        .replace(")", '"')
                    )
                except Exception as e:
                    logger.error("ERROR: Parameters not normalized correctly")
                    child, parent = "", ""
                template += generate_join_condition(child, parent)
            else:
                logger.error("Error in reference mapping another mapping in mapping " + mapping)
                raise Exception("Only two parameters can be indicated (child and parent)")
    return template


def ref_mapping(data, mapping, om, yarrrml_key, ref_type_property, mapping_format):
    """Genera el template para el mapping de referencia a otro mapping."""
    list_mappings = get_list_mappings(data)
    template = []
    obj_type = R2RML_OBJECT  # Valor por defecto
    mapping_join = om.get(yarrrml_key)

    if mapping_join in list_mappings:
        subject_list = add_subject(data, mapping_join, mapping_format)
        if mapping_format == R2RML_URI:
            source_list = add_table(data, mapping_join)
        else:
            if mapping_format == STAR_URI:
                obj_type = STAR_OBJECT
            source_list, external_references = add_source(data, mapping_join)

        number_joins_rml = len(subject_list) * len(source_list)
        for i in range(number_joins_rml):
            template.append(generate_ref_object_header(mapping_join, i, ref_type_property, obj_type))
            if YARRRML_CONDITION in om:
                conditions = om.get(YARRRML_CONDITION)
                template.append(f"{process_conditions_block(conditions, mapping)}\t\t];\n")

            else:
                template.append("\n\t\t]\n")
    else:
        logger.error("Error in reference mapping another mapping in mapping " + mapping)
        raise Exception("Review how is defined the reference to other mappings")

    return "".join(template)

def ref_cc_mapping(data, mapping, om, yarrrml_key, ref_type_property, mapping_format):
    template = ""
    obj_type = R2RML_OBJECT  # Valor por defecto
    list_mappings = get_list_mappings(data)  # Función reutilizada

    mapping_join = om.get(yarrrml_key)

    if mapping_join in list_mappings:
        subject_list = add_subject(data, mapping_join, mapping_format)
        if mapping_format == R2RML_URI:
            source_list = add_table(data, mapping_join)
        else:
            if mapping_format == STAR_URI:
                obj_type = STAR_OBJECT
            source_list, external_references = add_source(data, mapping_join)

        number_joins_rml = len(subject_list) * len(source_list)
        for i in range(number_joins_rml):
            # Cabecera específica para cc mapping
            header = (
                f"\t\t{obj_type} [\n"
                f"\t\t\ta {R2RML_OBJECT_CLASS};\n"
                f"\t\t\t{RML_CC_GATHER} (\n"
                f"\t\t\t\t[\n"
                f"\t\t\t\t\t{ref_type_property} <{mapping_join}_{i}>;\n"
            )
            template += header

            if YARRRML_CONDITION in om:
                conditions = om.get(YARRRML_CONDITION)
                # Reutilizamos process_conditions_block para generar las condiciones
                template += process_conditions_block(conditions, mapping)
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
