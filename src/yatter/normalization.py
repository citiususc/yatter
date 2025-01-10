import copy
from .constants import *
key_mapping = {
    YARRRML_MAPPINGS: [YARRRML_MAPPING, 'm'],
    YARRRML_SUBJECTS: ['subject', 's'],
    YARRRML_PREDICATES: ['predicate', 'p'],
    'inversepredicates': ['inversepredicate', 'i'],
    YARRRML_OBJECTS: ['object', 'o'],
    YARRRML_PREDICATEOBJECT: ['po'],
    YARRRML_FUNCTION: ['fn', 'f'],
    YARRRML_PARAMETERS: ['pms'],
    YARRRML_PARAMETER: ['pm'],
    YARRRML_VALUE: ['v'],
    YARRRML_AUTHORS: ['author', 'a'],
    YARRRML_TARGETS: ['target', 't'],
    YARRRML_GRAPHS: ['graph', 'g'],
    YARRRML_SOURCES: ['source', 'src']
}


def normalize_yaml(data):
    if isinstance(data, dict):
        new_data = dict()
        for key, value in data.items():
            new_key = get_normalized_key(key)
            if new_key == YARRRML_AUTHORS and isinstance(value, list):
                new_data[new_key] = expand_authors(value)
            elif new_key == YARRRML_SOURCES:
                new_data[new_key] = expand_sources(value)
            elif new_key == YARRRML_TARGETS:
                new_data[new_key] = expand_targets(value, data.get(YARRRML_TARGETS, {}))
            elif new_key == YARRRML_PREDICATEOBJECT:
                new_data[new_key] = expand_predicateobjects(value)
            elif new_key == YARRRML_SUBJECTS:
                new_data[new_key] = expand_subjects(value, data.get(YARRRML_TARGETS, {}))
            elif new_key == YARRRML_PARAMETERS:
                new_data[new_key] = expand_parameters(value)
            else:
                new_data[new_key] = normalize_yaml(value)


        return new_data

    elif isinstance(data, list):
        new_list = list()
        for item in data:
            new_list.append(normalize_yaml(item))
        return new_list
    return data


def get_normalized_key(key):
    for normalized_key, variants in key_mapping.items():
        if key == normalized_key or key in variants:
            return normalized_key
    return key


def expand_authors(authors):
    expanded_authors = list()
    for author in authors:
        if isinstance(author, str):
            expanded_author = dict()
            parts = author.split()
            name = []
            email = None
            website = None
            for part in parts:
                if isinstance(part, str):
                    if part.startswith("http://") or part.startswith("https://"):
                        expanded_authors.append(part)
                        break
                    elif part.startswith("<") and part.endswith(">"):
                        email = part.strip("<>")
                    elif part.startswith("(") and part.endswith(")"):
                        website = part.strip("()")
                    else:
                        name.append(part)
            if name:
                expanded_author['name'] = " ".join(name)
            if email:
                expanded_author['email'] = email
            if website:
                expanded_author['website'] = website
            if expanded_author:
                expanded_authors.append(expanded_author)
        else:
            expanded_authors.append(author)
    return expanded_authors


def expand_sources(sources):
    def expand_source_item(source):
        if isinstance(source, list):
            if len(source) == 2 and isinstance(source[0], str) and '~' in source[0]:
                access, reference = source[0].split('~')
                if '-' in reference:
                    reference = reference.split('-')
                    return {
                        YARRRML_ACCESS: access,
                        YARRRML_REFERENCE_FORMULATION: reference[1],
                        YARRRML_STRUCTURE_DEFINER: reference[0],
                        YARRRML_ITERATOR: source[1]
                    }
                else:
                    return {
                        YARRRML_ACCESS: access,
                        YARRRML_REFERENCE_FORMULATION: reference,
                        YARRRML_ITERATOR: source[1]
                    }
            elif len(source) == 1 and isinstance(source[0], str) and '~' in source[0]:
                access, reference = source[0].split('~')
                if '-' in reference:
                    reference = reference.split('-')
                    return {
                        YARRRML_ACCESS: access,
                        YARRRML_REFERENCE_FORMULATION: reference[1] ,
                        YARRRML_STRUCTURE_DEFINER: reference[0],
                    }
                else:
                    return {
                        YARRRML_ACCESS: access,
                        YARRRML_REFERENCE_FORMULATION: reference,
                    }
        elif isinstance(source, dict):
            for key, val in source.items():
                if isinstance(val, list) and len(val) == 2 and '~' in val[0]:
                    access, reference = val[0].split('~')
                    return {key: {YARRRML_ACCESS: access, YARRRML_REFERENCE_FORMULATION: reference, YARRRML_ITERATOR: val[1]}}
                else:
                    return normalize_yaml(source)

        return source

    if isinstance(sources, str):
        sources = [sources]
    if isinstance(sources, list):
        return [expand_source_item(src) for src in sources]
    elif isinstance(sources, dict):
        expanded_sources = dict()
        if YARRRML_ACCESS in sources:
            expanded_sources= [sources]
        else:
            for key, src in sources.items():
                expanded_sources[key] = expand_source_item(src)
        return expanded_sources
    return sources


def expand_targets(targets, root_targets={}):
    def expand_target_item(target):
        if isinstance(target, str) and target in root_targets:
            return root_targets[target]
        elif isinstance(target, list) and len(target) >= 1:
            expanded_target = dict()
            access_type = target[0].split('~')
            expanded_target[YARRRML_ACCESS] = access_type[0]
            if len(access_type) > 1:
                expanded_target[YARRRML_TYPE] = access_type[1]
            if len(target) > 1:
                expanded_target[YARRRML_SERIALIZATION] = target[1]
            if len(target) > 2:
                expanded_target[YARRRML_COMPRESSION] = target[2]
            return expanded_target
        elif isinstance(target, dict):
            return normalize_yaml(target)
        return target

    if isinstance(targets, list):
        return list([expand_target_item(t) for t in targets])
    elif isinstance(targets, dict):
        expanded_targets = dict()
        for key, tgt in targets.items():
            expanded_targets[key] = expand_target_item(tgt)
        return expanded_targets
    return targets


def expand_subjects(subjects, root_targets):
    expanded_subjects = list()
    if isinstance(subjects, str):
        expanded_subjects.append(dict({YARRRML_VALUE: subjects}))
    elif isinstance(subjects, list):
        for subject in subjects:
            expanded_subject = dict()
            if isinstance(subject, str):
                if "~" in subject:
                    expanded_subject[YARRRML_GATHER] = subject.split('~')[0]
                    expanded_subject[YARRRML_GATHER_AS] = subject.split('~')[1]
                else:
                    expanded_subject[YARRRML_VALUE] = subject
            elif isinstance(subject, dict):
                if YARRRML_VALUE in subject:
                    expanded_subject[YARRRML_VALUE] = subject.get(YARRRML_VALUE, '')
                if YARRRML_TARGETS in subject:
                    expanded_subject[YARRRML_TARGETS] = expand_targets(subject[YARRRML_TARGETS], root_targets)
                if YARRRML_QUOTED in subject:
                    expanded_subject[YARRRML_QUOTED] = subject.get(YARRRML_QUOTED, '')
                if YARRRML_NON_ASSERTED in subject:
                    expanded_subject[YARRRML_NON_ASSERTED] = subject.get(YARRRML_NON_ASSERTED, '')
                    if YARRRML_CONDITION in subject:
                        expanded_subject[YARRRML_CONDITION] = subject.get(YARRRML_CONDITION, '')
                        if YARRRML_PARAMETERS in subject[YARRRML_CONDITION]:
                            expanded_subject[YARRRML_CONDITION][YARRRML_PARAMETERS] = expand_parameters(expanded_subject[YARRRML_CONDITION].get(YARRRML_PARAMETERS, ''))
                if YARRRML_EMPTY in subject:
                    expanded_subject[YARRRML_EMPTY] = subject.get(YARRRML_EMPTY, '')
                if YARRRML_GATHER in subject:
                    expanded_subject[YARRRML_GATHER] = subject.get(YARRRML_GATHER, '')
                    if YARRRML_GATHER_AS in subject:
                        expanded_subject[YARRRML_GATHER_AS] = subject.get(YARRRML_GATHER_AS, '')
                if YARRRML_STRATEGY in subject:
                    expanded_subject[YARRRML_STRATEGY] = subject.get(YARRRML_STRATEGY, '')
            expanded_subjects.append(expanded_subject)
    elif isinstance(subjects, dict):
        expanded_subjects = [subjects]
    return expanded_subjects


def expand_predicateobjects(predicateobjects):
    expanded_predicateobjects = list()

    for po in predicateobjects:
        if isinstance(po, list):
            expanded_po = dict()
            if len(po) == 3:

                second_value = po[1]
                if '~' in second_value:
                    expanded_po[YARRRML_PREDICATES] = [{YARRRML_VALUE: po[0]}]
                    if "\"" in po[2]:
                        expanded_po[YARRRML_OBJECTS] = [{YARRRML_EMPTY: po[2]}]
                    else:
                        third_value = "\"" + po[2] + "\""
                        expanded_po[YARRRML_OBJECTS] = [{YARRRML_EMPTY: third_value}]
                    if second_value.split('~')[1] in YARRRML_GATHER_AS_OPTIONS:
                        expanded_po[YARRRML_OBJECTS][0][YARRRML_GATHER] = second_value.split('~')[0]
                        expanded_po[YARRRML_OBJECTS][0][YARRRML_GATHER_AS] = second_value.split('~')[1]

                else:
                    expanded_po[YARRRML_PREDICATES] = [{YARRRML_VALUE: po[0]}]
                    expanded_po[YARRRML_OBJECTS] = [{YARRRML_VALUE: po[1]}]

                    third_value = po[2]
                    if '~' in third_value:
                        if third_value.endswith('lang'):
                            expanded_po[YARRRML_OBJECTS][0][YARRRML_LANGUAGE] = third_value.split('~')[0]
                        elif third_value.split('~')[1] in YARRRML_GATHER_AS_OPTIONS:
                            expanded_po[YARRRML_OBJECTS][0][YARRRML_GATHER] = third_value.split('~')[0]
                            expanded_po[YARRRML_OBJECTS][0][YARRRML_GATHER_AS] = third_value.split('~')[1]
                    else:
                        expanded_po[YARRRML_OBJECTS][0][YARRRML_DATATYPE] = third_value

                expanded_predicateobjects.append(expanded_po)

            elif len(po) == 2:
                if isinstance(po[0], str):
                    po[0] = [po[0]]
                if isinstance(po[1], str):
                    po[1] = [po[1]]

                predicates_list, objects_list = po[0], po[1]

                for pred in predicates_list:
                    expanded_po = dict()
                    expanded_po[YARRRML_PREDICATES] = [{YARRRML_VALUE: pred}]
                    expanded_po[YARRRML_OBJECTS] = []

                    for obj in objects_list:
                        object_expansion = {}
                        if isinstance(obj, str) and '~' in obj:
                            obj_value, obj_type = obj.split('~')

                            if obj_type in YARRRML_GATHER_AS_OPTIONS:
                                object_expansion[YARRRML_GATHER_AS] = obj_type
                                object_expansion[YARRRML_GATHER] = obj_value
                            elif obj_type == "lang":
                                object_expansion[YARRRML_LANGUAGE] = obj_type
                                object_expansion[YARRRML_VALUE] = obj_value
                            else:
                                object_expansion[YARRRML_TYPE] = obj_type
                                object_expansion[YARRRML_VALUE] = obj_value
                        elif isinstance(obj, dict) and YARRRML_FUNCTION in obj:
                            object_expansion[YARRRML_FUNCTION] = obj[YARRRML_FUNCTION]
                            if YARRRML_PARAMETERS in obj:
                                object_expansion[YARRRML_PARAMETERS] = expand_parameters(obj[YARRRML_PARAMETERS])
                        else:
                            if isinstance(obj, dict):
                                if YARRRML_VALUE in obj:
                                    object_expansion.update(obj)
                            else:
                                object_expansion[YARRRML_VALUE] = obj

                        expanded_po[YARRRML_OBJECTS].append(object_expansion)

                    expanded_predicateobjects.append(expanded_po)
        elif isinstance(po, dict):
            expanded_po = {}

            if YARRRML_PREDICATES in po and YARRRML_OBJECTS in po:
                if isinstance(po[YARRRML_PREDICATES], str):
                    po[YARRRML_PREDICATES] = [po[YARRRML_PREDICATES]]
                if isinstance(po[YARRRML_OBJECTS], str):
                    po[YARRRML_OBJECTS] = [po[YARRRML_OBJECTS]]

                for pred in po[YARRRML_PREDICATES]:
                    expanded_po = dict()
                    if isinstance(pred, dict) and YARRRML_VALUE in pred:
                        expanded_po[YARRRML_PREDICATES] = po[YARRRML_PREDICATES]
                    else:
                        expanded_po[YARRRML_PREDICATES] = [{YARRRML_VALUE: pred}]

                    expanded_po[YARRRML_OBJECTS] = []
                    for obj in po[YARRRML_OBJECTS]:
                        object_expansion = {}
                        if isinstance(obj, dict):
                            if YARRRML_FUNCTION in obj and YARRRML_PARAMETERS in obj:
                                object_expansion[YARRRML_FUNCTION] = obj[YARRRML_FUNCTION]
                                object_expansion[YARRRML_PARAMETERS] = expand_parameters(obj[YARRRML_PARAMETERS])
                            elif YARRRML_MAPPING in obj or YARRRML_CONDITION in obj:
                                if YARRRML_MAPPING in obj:
                                    object_expansion[YARRRML_MAPPING] = obj[YARRRML_MAPPING]
                                if YARRRML_CONDITION in obj:
                                    condition_temp = obj[YARRRML_CONDITION]
                                    if isinstance(condition_temp, dict):
                                        condition_temp = [condition_temp]
                                    object_expansion[YARRRML_CONDITION] = [
                                        {
                                            **condition,
                                            YARRRML_PARAMETERS: expand_parameters(condition[YARRRML_PARAMETERS])
                                        } if YARRRML_PARAMETERS in condition else condition
                                        for condition in condition_temp
                                    ]
                            else:
                                if YARRRML_VALUE in obj:
                                    object_expansion[YARRRML_VALUE] = obj[YARRRML_VALUE]
                                if YARRRML_DATATYPE in obj:
                                    object_expansion[YARRRML_DATATYPE] = obj[YARRRML_DATATYPE]
                        elif isinstance(obj, list) and len(obj) == 2 and '~' in obj[1]:
                            object_expansion[YARRRML_VALUE] = obj[0]
                            object_expansion[YARRRML_LANGUAGE] = obj[1].split('~')[0]
                        elif isinstance(obj, list) and len(obj) == 2:
                            object_expansion[YARRRML_VALUE] = obj[0]
                            object_expansion[YARRRML_DATATYPE] = obj[1]
                        else:
                            object_expansion[YARRRML_VALUE] = obj

                        expanded_po[YARRRML_OBJECTS].append(object_expansion)

                    expanded_predicateobjects.append(expanded_po)

            elif 'p' in po and 'o' in po:
                if not isinstance(po['p'], list):
                    po['p'] = [po['p']]

                objects = po['o'] if isinstance(po['o'], list) else [po['o']]
                expanded_po[YARRRML_PREDICATES] = []

                for p in po['p']:
                    if YARRRML_FUNCTION in p:
                        expanded_predicate = {YARRRML_FUNCTION: p[YARRRML_FUNCTION]}
                        if YARRRML_PARAMETERS in p:
                            expanded_parameters = expand_parameters(p[YARRRML_PARAMETERS])
                            expanded_predicate.append(expanded_parameters)
                    else:
                        expanded_predicate = {YARRRML_VALUE: p}

                    expanded_po[YARRRML_PREDICATES].append(expanded_predicate)

                expanded_po[YARRRML_OBJECTS] = []

                for o in objects:
                    object_expansion = {}

                    if isinstance(o, dict):
                        if YARRRML_FUNCTION in o and YARRRML_PARAMETERS in o:
                            object_expansion[YARRRML_FUNCTION] = o[YARRRML_FUNCTION]
                            object_expansion[YARRRML_PARAMETERS] = expand_parameters(o[YARRRML_PARAMETERS])
                        elif YARRRML_MAPPING in o or YARRRML_CONDITION in o:
                            if YARRRML_MAPPING in o:
                                object_expansion[YARRRML_MAPPING] = o[YARRRML_MAPPING]
                            if YARRRML_CONDITION in o:
                                condition_temp = o[YARRRML_CONDITION]
                                if isinstance(condition_temp, dict):
                                    condition_temp = [condition_temp]
                                object_expansion[YARRRML_CONDITION] = [
                                    {
                                        **condition,
                                        YARRRML_PARAMETERS: expand_parameters(condition[YARRRML_PARAMETERS])
                                    } if YARRRML_PARAMETERS in condition else condition
                                    for condition in condition_temp
                                ]
                        elif YARRRML_GATHER in o:
                            if isinstance(o[YARRRML_GATHER], list):
                                object_expansion[YARRRML_GATHER] = []
                                for gather_value in o[YARRRML_GATHER]:
                                    if isinstance(gather_value, str) and '~' in gather_value:
                                        gather_entry = {
                                            YARRRML_GATHER: gather_value.split('~')[0],
                                            YARRRML_GATHER_AS: gather_value.split('~')[1]
                                        }
                                        object_expansion[YARRRML_GATHER].append(gather_entry)
                                    elif isinstance(gather_value, str):
                                        gather_entry = {
                                            YARRRML_GATHER: gather_value
                                        }
                                        object_expansion[YARRRML_GATHER].append(gather_entry)
                                    elif isinstance(gather_value, dict):
                                        gather_entry = {}
                                        if YARRRML_MAPPING in gather_value or YARRRML_CONDITION in gather_value:
                                            if YARRRML_MAPPING in gather_value:
                                                gather_entry[YARRRML_MAPPING] = gather_value[YARRRML_MAPPING]
                                            if YARRRML_CONDITION in gather_value:
                                                condition_temp = gather_value[YARRRML_CONDITION]
                                                if isinstance(condition_temp, dict):
                                                    condition_temp = [condition_temp]
                                                gather_entry[YARRRML_CONDITION] = [
                                                    {
                                                        **condition,
                                                        YARRRML_PARAMETERS: expand_parameters(condition[YARRRML_PARAMETERS])
                                                    } if YARRRML_PARAMETERS in condition else condition
                                                    for condition in condition_temp
                                                ]

                                            object_expansion[YARRRML_GATHER].append(gather_entry)
                                        else:
                                            object_expansion[YARRRML_GATHER].append(gather_value)

                            else:
                                object_expansion[YARRRML_GATHER] = o[YARRRML_GATHER]
                            object_expansion[YARRRML_GATHER_AS] = o[YARRRML_GATHER_AS]
                            if YARRRML_VALUE in o:
                                object_expansion[YARRRML_VALUE] = o[YARRRML_VALUE]
                            if YARRRML_TYPE in o:
                                object_expansion[YARRRML_TYPE] = o[YARRRML_TYPE]
                            if YARRRML_EMPTY in o:
                                object_expansion[YARRRML_EMPTY] = o[YARRRML_EMPTY]
                            if YARRRML_STRATEGY in o:
                                object_expansion[YARRRML_STRATEGY] = o[YARRRML_STRATEGY]
                        else:
                            object_expansion.update(o)
                    else:
                        object_expansion[YARRRML_VALUE] = o

                    if YARRRML_EMPTY in object_expansion:
                        if object_expansion[YARRRML_EMPTY] is True:
                            object_expansion[YARRRML_EMPTY] = "\"true\""
                        elif object_expansion[YARRRML_EMPTY] is False:
                            object_expansion[YARRRML_EMPTY] = "\"false\""
                    expanded_po[YARRRML_OBJECTS].append(object_expansion)

                expanded_predicateobjects.append(expanded_po)

            if 'graph' in po:
                expanded_po[YARRRML_GRAPHS] = [po['graph']]
            if YARRRML_GRAPHS in po:
                expanded_po[YARRRML_GRAPHS] = [po[YARRRML_GRAPHS]]

    return expanded_predicateobjects


def expand_parameters(parameters):
    expanded_parameters = list()
    for param in parameters:
        expanded_param = dict()
        if isinstance(param, list):
            if len(param) == 2:
                expanded_param[YARRRML_PARAMETER] = param[0]
                expanded_param[YARRRML_VALUE] = param[1]
            elif len(param) == 3:
                expanded_param[YARRRML_PARAMETER] = param[0]
                expanded_param[YARRRML_VALUE] = param[1]

        else:
            expanded_param = normalize_yaml(param)
        expanded_parameters.append(expanded_param)
    return expanded_parameters


def switch_mappings(data, external_sources, external_targets):
    sources_root = data.get(YARRRML_SOURCES, {})
    for source_name, source_value in sources_root.items():
        if source_name not in external_sources:
            external_sources[source_name] = copy.deepcopy(source_value)
        if YARRRML_MAPPINGS not in external_sources[source_name]:
            external_sources[source_name][YARRRML_MAPPINGS] = []
    targets_root = data.get(YARRRML_TARGETS, {})
    for target_name, target_value in targets_root.items():
        if target_name not in external_targets:
            external_targets[target_name] = copy.deepcopy(target_value)

    def replace_references(mapping_name, mapping_content):
        if YARRRML_SOURCES in mapping_content:
            expanded_sources = list()
            for source_ref in mapping_content[YARRRML_SOURCES]:
                if isinstance(source_ref, str) and source_ref in sources_root:
                    source = sources_root[source_ref]
                    expanded_sources.append(dict(source))
                    if source_ref in external_sources:
                        if mapping_name not in external_sources[source_ref][YARRRML_MAPPINGS]:
                            external_sources[source_ref][YARRRML_MAPPINGS].append(mapping_name)
                else:
                    expanded_sources.append(source_ref)


            mapping_content[YARRRML_SOURCES] = expanded_sources

        if YARRRML_SUBJECTS in mapping_content:
            for subject in mapping_content[YARRRML_SUBJECTS]:
                if isinstance(subject, dict):
                    if YARRRML_TARGETS in subject:
                        subject[YARRRML_TARGETS] = expand_targets_with_identifiers(subject[YARRRML_TARGETS], targets_root)

        if YARRRML_GRAPHS in mapping_content:
            for graph in mapping_content[YARRRML_GRAPHS]:
                if isinstance(graph, dict):
                    if YARRRML_TARGETS in graph:
                        graph[YARRRML_TARGETS] = expand_targets_with_identifiers(graph[YARRRML_TARGETS], targets_root)

        if YARRRML_PREDICATEOBJECT in mapping_content:
            po = mapping_content[YARRRML_PREDICATEOBJECT][0]
            if YARRRML_OBJECTS in po:
                for object in po[YARRRML_OBJECTS]:
                    if isinstance(object, dict):
                        if YARRRML_TARGETS in object:
                            object[YARRRML_TARGETS] = expand_targets_with_identifiers(object[YARRRML_TARGETS], targets_root)

    if YARRRML_MAPPINGS in data:
        for mapping_name, mapping_content in data[YARRRML_MAPPINGS].items():
            replace_references(mapping_name, mapping_content)

    if YARRRML_SOURCES in data:
        del data[YARRRML_SOURCES]
    if YARRRML_TARGETS in data:
        del data[YARRRML_TARGETS]

    return data


def expand_targets_with_identifiers(targets, root_targets):
    expanded_targets = list()
    if isinstance(targets, dict) or isinstance(targets,str):
        targets = [targets]
    for target in targets:
        if isinstance(target, str) and target in root_targets:
            expanded_targets.append(dict({target: root_targets[target]}))
        elif isinstance(target, list) and len(target) >= 1:
            expanded_targets.append(expand_targets(target))
        elif isinstance(target, dict):
            expanded_targets.append(target)
    return expanded_targets


def normalize(data, external_sources, external_targets):
    data = normalize_yaml(data)

    if data.get(YARRRML_MAPPINGS):
        for mapping in data.get(YARRRML_MAPPINGS):

            mapping_data = data.get(YARRRML_MAPPINGS).get(mapping)
            if YARRRML_PREDICATEOBJECT in mapping_data:
                for predicate_object_map in mapping_data.get(YARRRML_PREDICATEOBJECT):
                    if YARRRML_OBJECTS in predicate_object_map:
                        pass
                    else:
                        logger.error(
                            "There isn't a valid object key (object, objects, o) correctly specify in PON " + predicate_object_map)
                        raise Exception("Add or change the key of the object in the indicated POM")

                    if YARRRML_PREDICATES in predicate_object_map:
                        pass
                    else:
                        logger.error(
                            "There isn't a valid predicate key (predicate, predicates, p) correctly specify in PON " + predicate_object_map)
                        raise Exception("Add or change the key of the predicate in the indicated POM")

    switch_mappings(data, external_sources, external_targets)
    return data
