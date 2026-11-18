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
            if len(source) in (1, 2) and isinstance(source[0], str) and '~' in source[0]:
                access, reference = source[0].split('~')
                expanded_source = {YARRRML_ACCESS: access}
                if '-' in reference:
                    reference = reference.split('-')
                    expanded_source[YARRRML_REFERENCE_FORMULATION] = reference[1]
                    expanded_source[YARRRML_STRUCTURE_DEFINER] = reference[0]
                else:
                    expanded_source[YARRRML_REFERENCE_FORMULATION] = reference
                if len(source) == 2:
                    expanded_source[YARRRML_ITERATOR] = source[1]
                return expanded_source
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


def expand_targets(targets, root_targets=None):
    if root_targets is None:
        root_targets = {}

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


def _expand_join_reference(value):
    expanded = {}
    if YARRRML_MAPPING in value:
        expanded[YARRRML_MAPPING] = value[YARRRML_MAPPING]
    if YARRRML_CONDITION in value:
        conditions = value[YARRRML_CONDITION]
        if isinstance(conditions, dict):
            conditions = [conditions]
        expanded[YARRRML_CONDITION] = [
            {
                **condition,
                YARRRML_PARAMETERS: expand_parameters(condition[YARRRML_PARAMETERS]),
            }
            if YARRRML_PARAMETERS in condition else condition
            for condition in conditions
        ]
    return expanded


def _expand_gather_object(obj):
    gather = obj[YARRRML_GATHER]
    if isinstance(gather, list):
        expanded_gather = []
        for item in gather:
            if isinstance(item, str):
                if '~' in item:
                    parts = item.split('~')
                    expanded_gather.append({
                        YARRRML_GATHER: parts[0],
                        YARRRML_GATHER_AS: parts[1],
                    })
                else:
                    expanded_gather.append({YARRRML_GATHER: item})
            elif isinstance(item, dict):
                if YARRRML_MAPPING in item or YARRRML_CONDITION in item:
                    expanded_gather.append(_expand_join_reference(item))
                else:
                    expanded_gather.append(item)
        gather = expanded_gather

    expanded = {
        YARRRML_GATHER: gather,
        YARRRML_GATHER_AS: obj[YARRRML_GATHER_AS],
    }
    for key in (YARRRML_VALUE, YARRRML_TYPE, YARRRML_EMPTY, YARRRML_STRATEGY):
        if key in obj:
            expanded[key] = obj[key]
    return expanded


def _expand_abbreviated_object(obj):
    if not isinstance(obj, dict):
        expanded = {YARRRML_VALUE: obj}
    elif YARRRML_FUNCTION in obj and YARRRML_PARAMETERS in obj:
        expanded = {
            YARRRML_FUNCTION: obj[YARRRML_FUNCTION],
            YARRRML_PARAMETERS: expand_parameters(obj[YARRRML_PARAMETERS]),
        }
    elif YARRRML_MAPPING in obj or YARRRML_CONDITION in obj:
        expanded = _expand_join_reference(obj)
    elif YARRRML_GATHER in obj:
        expanded = _expand_gather_object(obj)
    else:
        expanded = dict(obj)

    if expanded.get(YARRRML_EMPTY) is True:
        expanded[YARRRML_EMPTY] = '"true"'
    elif expanded.get(YARRRML_EMPTY) is False:
        expanded[YARRRML_EMPTY] = '"false"'
    return expanded


def _expand_list_object(obj):
    if isinstance(obj, str) and '~' in obj:
        value, obj_type = obj.split('~')
        if obj_type in YARRRML_GATHER_AS_OPTIONS:
            return {YARRRML_GATHER_AS: obj_type, YARRRML_GATHER: value}
        if obj_type == "lang":
            return {YARRRML_LANGUAGE: obj_type, YARRRML_VALUE: value}
        return {YARRRML_TYPE: obj_type, YARRRML_VALUE: value}
    if isinstance(obj, dict):
        if YARRRML_FUNCTION in obj:
            expanded = {YARRRML_FUNCTION: obj[YARRRML_FUNCTION]}
            if YARRRML_PARAMETERS in obj:
                expanded[YARRRML_PARAMETERS] = expand_parameters(obj[YARRRML_PARAMETERS])
            return expanded
        return dict(obj) if YARRRML_VALUE in obj else {}
    return {YARRRML_VALUE: obj}


def _expand_explicit_object(obj):
    if isinstance(obj, dict):
        if YARRRML_FUNCTION in obj and YARRRML_PARAMETERS in obj:
            return {
                YARRRML_FUNCTION: obj[YARRRML_FUNCTION],
                YARRRML_PARAMETERS: expand_parameters(obj[YARRRML_PARAMETERS]),
            }
        if YARRRML_MAPPING in obj or YARRRML_CONDITION in obj:
            return _expand_join_reference(obj)
        return {
            key: obj[key]
            for key in (YARRRML_VALUE, YARRRML_DATATYPE)
            if key in obj
        }
    if isinstance(obj, list) and len(obj) == 2:
        if '~' in obj[1]:
            return {YARRRML_VALUE: obj[0], YARRRML_LANGUAGE: obj[1].split('~')[0]}
        return {YARRRML_VALUE: obj[0], YARRRML_DATATYPE: obj[1]}
    return {YARRRML_VALUE: obj}


def expand_predicateobjects(predicateobjects):
    result = []
    for po in predicateobjects:
        if isinstance(po, list):
            result.extend(_expand_list_predicateobject(po))
        elif isinstance(po, dict):
            result.extend(_expand_dict_predicateobject(po))
    return result


def _expand_list_predicateobject(po):
    if len(po) == 3:
        return [_expand_triple_predicateobject(po)]
    if len(po) != 2:
        return []
    if isinstance(po[0], str):
        po[0] = [po[0]]
    if isinstance(po[1], str):
        po[1] = [po[1]]
    return [
        {
            YARRRML_PREDICATES: [{YARRRML_VALUE: predicate}],
            YARRRML_OBJECTS: [_expand_list_object(obj) for obj in po[1]],
        }
        for predicate in po[0]
    ]


def _expand_triple_predicateobject(po):
    predicate, value, qualifier = po
    if '~' in value:
        obj = {YARRRML_EMPTY: qualifier if '"' in qualifier else '"' + qualifier + '"'}
        parts = value.split('~')
        if parts[1] in YARRRML_GATHER_AS_OPTIONS:
            obj[YARRRML_GATHER] = parts[0]
            obj[YARRRML_GATHER_AS] = parts[1]
    else:
        obj = {YARRRML_VALUE: value}
        if '~' not in qualifier:
            obj[YARRRML_DATATYPE] = qualifier
        elif qualifier.endswith('lang'):
            obj[YARRRML_LANGUAGE] = qualifier.split('~')[0]
        elif qualifier.split('~')[1] in YARRRML_GATHER_AS_OPTIONS:
            obj[YARRRML_GATHER] = qualifier.split('~')[0]
            obj[YARRRML_GATHER_AS] = qualifier.split('~')[1]
    return {YARRRML_PREDICATES: [{YARRRML_VALUE: predicate}], YARRRML_OBJECTS: [obj]}


def _expand_dict_predicateobject(po):
    result = []
    if YARRRML_PREDICATES in po and YARRRML_OBJECTS in po:
        if isinstance(po[YARRRML_PREDICATES], str):
            po[YARRRML_PREDICATES] = [po[YARRRML_PREDICATES]]
        if isinstance(po[YARRRML_OBJECTS], str):
            po[YARRRML_OBJECTS] = [po[YARRRML_OBJECTS]]
        for predicate in po[YARRRML_PREDICATES]:
            if isinstance(predicate, dict) and YARRRML_VALUE in predicate:
                predicates = po[YARRRML_PREDICATES]
            else:
                predicates = [{YARRRML_VALUE: predicate}]
            result.append({
                YARRRML_PREDICATES: predicates,
                YARRRML_OBJECTS: [
                    _expand_explicit_object(obj) for obj in po[YARRRML_OBJECTS]
                ],
            })
    elif 'p' in po and 'o' in po:
        if not isinstance(po['p'], list):
            po['p'] = [po['p']]
        objects = po['o'] if isinstance(po['o'], list) else [po['o']]
        predicates = []
        for predicate in po['p']:
            if YARRRML_FUNCTION in predicate:
                expanded = {YARRRML_FUNCTION: predicate[YARRRML_FUNCTION]}
                if YARRRML_PARAMETERS in predicate:
                    expanded[YARRRML_PARAMETERS] = expand_parameters(
                        predicate[YARRRML_PARAMETERS]
                    )
            else:
                expanded = {YARRRML_VALUE: predicate}
            predicates.append(expanded)
        result.append({
            YARRRML_PREDICATES: predicates,
            YARRRML_OBJECTS: [_expand_abbreviated_object(obj) for obj in objects],
        })
    if result:
        if 'graph' in po:
            result[-1][YARRRML_GRAPHS] = [po['graph']]
        if YARRRML_GRAPHS in po:
            result[-1][YARRRML_GRAPHS] = [po[YARRRML_GRAPHS]]
    return result


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

        _expand_mapping_targets(mapping_content, targets_root)

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


def _expand_mapping_targets(mapping_content, targets_root):
    if YARRRML_SUBJECTS in mapping_content:
        for subject in mapping_content[YARRRML_SUBJECTS]:
            if isinstance(subject, dict) and YARRRML_TARGETS in subject:
                subject[YARRRML_TARGETS] = expand_targets_with_identifiers(subject[YARRRML_TARGETS], targets_root)

    if YARRRML_GRAPHS in mapping_content:
        for graph in mapping_content[YARRRML_GRAPHS]:
            if isinstance(graph, dict) and YARRRML_TARGETS in graph:
                graph[YARRRML_TARGETS] = expand_targets_with_identifiers(graph[YARRRML_TARGETS], targets_root)

    if YARRRML_PREDICATEOBJECT in mapping_content:
        for predicate_object in mapping_content[YARRRML_PREDICATEOBJECT]:
            if YARRRML_OBJECTS not in predicate_object:
                continue
            for obj in predicate_object[YARRRML_OBJECTS]:
                if isinstance(obj, dict) and YARRRML_TARGETS in obj:
                    obj[YARRRML_TARGETS] = expand_targets_with_identifiers(obj[YARRRML_TARGETS], targets_root)


def normalize(data, external_sources, external_targets):
    data = normalize_yaml(copy.deepcopy(data))

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
            if YARRRML_SUBJECTS not in mapping_data:
                mapping_data[YARRRML_SUBJECTS] = list()

    switch_mappings(data, external_sources, external_targets)
    return data
