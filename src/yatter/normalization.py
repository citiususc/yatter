import copy
from .constants import *
key_mapping = {
    'mappings': ['mapping', 'm'],
    'subjects': ['subject', 's'],
    'predicates': ['predicate', 'p'],
    'inversepredicates': ['inversepredicate', 'i'],
    'objects': ['object', 'o'],
    'predicateobjects': ['po'],
    'function': ['fn', 'f'],
    'parameters': ['pms'],
    'parameter': ['pm'],
    'value': ['v'],
    'authors': ['author', 'a'],
    'targets': ['target', 't'],
    'graphs': ['graph', 'g'],
    'sources': ['source', 'src']
}


def normalize_yaml(data):
    if isinstance(data, dict):
        new_data = dict()
        for key, value in data.items():
            new_key = get_normalized_key(key)
            if new_key == 'authors' and isinstance(value, list):
                new_data[new_key] = expand_authors(value)
            elif new_key == 'sources':
                new_data[new_key] = expand_sources(value)
            elif new_key == 'targets':
                new_data[new_key] = expand_targets(value, data.get('targets', {}))
            elif new_key == 'predicateobjects':
                new_data[new_key] = expand_predicateobjects(value)
            elif new_key == 'subjects':
                new_data[new_key] = expand_subjects(value, data.get('targets', {}))
            elif new_key == 'parameters':
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
                return {
                    'access': access,
                    'referenceFormulation': reference,
                    'iterator': source[1]
                }
            elif len(source) == 1 and isinstance(source[0], str) and '~' in source[0]:
                access, reference = source[0].split('~')
                return {
                    'access': access,
                    'referenceFormulation': reference
                }
        elif isinstance(source, dict):
            for key, val in source.items():
                if isinstance(val, list) and len(val) == 2 and '~' in val[0]:
                    access, reference = val[0].split('~')
                    return {key: {'access': access, 'referenceFormulation': reference, 'iterator': val[1]}}
                else:
                    return normalize_yaml(source)

        return source

    if isinstance(sources, str):
        sources = [sources]
    if isinstance(sources, list):
        return [expand_source_item(src) for src in sources]
    elif isinstance(sources, dict):
        expanded_sources = dict()
        if 'access' in sources:
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
            expanded_target['access'] = access_type[0]
            if len(access_type) > 1:
                expanded_target['type'] = access_type[1]
            if len(target) > 1:
                expanded_target['serialization'] = target[1]
            if len(target) > 2:
                expanded_target['compression'] = target[2]
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
        expanded_subjects.append(dict({'value': subjects}))
    elif isinstance(subjects, list):
        for subject in subjects:
            expanded_subject = dict()
            if isinstance(subject, str):
                expanded_subject['value'] = subject
            elif isinstance(subject, dict):
                if 'value' in subject:
                    expanded_subject['value'] = subject.get('value', '')
                if 'targets' in subject:
                    expanded_subject['targets'] = expand_targets(subject['targets'], root_targets)
                if 'quoted' in subject:
                    expanded_subject['quoted'] = subject.get('quoted', '')
                if 'quotedNonAsserted' in subject:
                    expanded_subject['quotedNonAsserted'] = subject.get('quotedNonAsserted', '')
                    if 'condition' in subject:
                        expanded_subject['condition'] = subject.get('condition', '')
                        if 'parameters' in subject['condition']:
                            expanded_subject['condition']['parameters'] = expand_parameters(expanded_subject['condition'].get('parameters', ''))
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
                expanded_po['predicates'] = [{'value': po[0]}]
                expanded_po['objects'] = [{'value': po[1]}]

                third_value = po[2]
                if '~' in third_value:
                    expanded_po['objects'][0]['language'] = third_value.split('~')[0]
                else:
                    expanded_po['objects'][0]['datatype'] = third_value

                expanded_predicateobjects.append(expanded_po)

            elif len(po) >= 2:
                if isinstance(po[0], str):
                    po[0] = [po[0]]
                if isinstance(po[1], str):
                    po[1] = [po[1]]

                predicates_list, objects_list = po[0], po[1]

                for pred in predicates_list:
                    expanded_po = dict()
                    expanded_po['predicates'] = [{'value': pred}]
                    expanded_po['objects'] = []

                    for obj in objects_list:
                        object_expansion = {}
                        if isinstance(obj, str) and '~' in obj:
                            obj_value, obj_type = obj.split('~')
                            object_expansion['value'] = obj_value
                            if obj_type == "lang":
                                object_expansion['language'] = obj_type
                            else:
                                object_expansion['type'] = obj_type
                        elif isinstance(obj, dict) and 'function' in obj:
                            object_expansion['function'] = obj['function']
                            if 'parameters' in obj:
                                object_expansion['parameters'] = expand_parameters(obj['parameters'])
                        else:
                            if isinstance(obj, dict):
                                if 'value' in obj:
                                    object_expansion.update(obj)
                            else:
                                object_expansion['value'] = obj

                        expanded_po['objects'].append(object_expansion)

                    expanded_predicateobjects.append(expanded_po)
        elif isinstance(po, dict):
            expanded_po = {}

            if 'predicates' in po and 'objects' in po:
                if isinstance(po['predicates'], str):
                    po['predicates'] = [po['predicates']]
                if isinstance(po['objects'], str):
                    po['objects'] = [po['objects']]

                for pred in po['predicates']:
                    expanded_po = dict()
                    if isinstance(pred, dict) and 'value' in pred:
                        expanded_po['predicates'] = po['predicates']
                    else:
                        expanded_po['predicates'] = [{'value': pred}]

                    expanded_po['objects'] = []
                    for obj in po['objects']:
                        object_expansion = {}
                        if isinstance(obj, dict):
                            if 'function' in obj and 'parameters' in obj:
                                object_expansion['function'] = obj['function']
                                object_expansion['parameters'] = expand_parameters(obj['parameters'])
                            elif 'mapping' in obj or 'condition' in obj:
                                if 'mapping' in obj:
                                    object_expansion['mapping'] = obj['mapping']
                                if 'condition' in obj:
                                    condition_temp = obj['condition']
                                    if isinstance(condition_temp, dict):
                                        condition_temp = [condition_temp]
                                    object_expansion['condition'] = [
                                        {
                                            **condition,
                                            'parameters': expand_parameters(condition['parameters'])
                                        } if 'parameters' in condition else condition
                                        for condition in condition_temp
                                    ]
                            else:
                                if 'value' in obj:
                                    object_expansion['value'] = obj['value']
                                if 'datatype' in obj:
                                    object_expansion['datatype'] = obj['datatype']
                        elif isinstance(obj, list) and len(obj) == 2 and '~' in obj[1]:
                            object_expansion['value'] = obj[0]
                            object_expansion['language'] = obj[1].split('~')[0]
                        elif isinstance(obj, list) and len(obj) == 2:
                            object_expansion['value'] = obj[0]
                            object_expansion['datatype'] = obj[1]
                        else:
                            object_expansion['value'] = obj

                        expanded_po['objects'].append(object_expansion)

                    expanded_predicateobjects.append(expanded_po)

            elif 'p' in po and 'o' in po:
                if not isinstance(po['p'], list):
                    po['p'] = [po['p']]

                objects = po['o'] if isinstance(po['o'], list) else [po['o']]
                expanded_po['predicates'] = []

                for p in po['p']:
                    if YARRRML_FUNCTION in p:
                        expanded_predicate = {'function': p[YARRRML_FUNCTION]}
                        if YARRRML_PARAMETERS in p:
                            expanded_parameters = expand_parameters(p[YARRRML_PARAMETERS])
                            expanded_predicate.append(expanded_parameters)
                    else:
                        expanded_predicate = {'value': p}

                    expanded_po['predicates'].append(expanded_predicate)

                expanded_po['objects'] = []

                for o in objects:
                    object_expansion = {}

                    if isinstance(o, dict):
                        if 'function' in o and 'parameters' in o:
                            object_expansion['function'] = o['function']
                            object_expansion['parameters'] = expand_parameters(o['parameters'])
                        elif 'mapping' in o or 'condition' in o:
                            if 'mapping' in o:
                                object_expansion['mapping'] = o['mapping']
                            if 'condition' in o:
                                condition_temp = o['condition']
                                if isinstance(condition_temp, dict):
                                    condition_temp = [condition_temp]
                                object_expansion['condition'] = [
                                    {
                                        **condition,
                                        'parameters': expand_parameters(condition['parameters'])
                                    } if 'parameters' in condition else condition
                                    for condition in condition_temp
                                ]
                        else:
                            object_expansion.update(o)
                    else:
                        object_expansion['value'] = o

                    expanded_po['objects'].append(object_expansion)

                expanded_predicateobjects.append(expanded_po)

            if 'graph' in po:
                expanded_po['graphs'] = [po['graph']]
            if 'graphs' in po:
                expanded_po['graphs'] = [po['graphs']]

    return expanded_predicateobjects


def expand_parameters(parameters):
    expanded_parameters = list()
    for param in parameters:
        expanded_param = dict()
        if isinstance(param, list) and len(param) == 2:
            expanded_param['parameter'] = param[0]
            expanded_param['value'] = param[1]
        else:
            expanded_param = normalize_yaml(param)
        expanded_parameters.append(expanded_param)
    return expanded_parameters


def switch_mappings(data, external_sources, external_targets):
    sources_root = data.get('sources', {})
    for source_name, source_value in sources_root.items():
        if source_name not in external_sources:
            external_sources[source_name] = copy.deepcopy(source_value)
        if 'mappings' not in external_sources[source_name]:
            external_sources[source_name]['mappings'] = []
    targets_root = data.get('targets', {})
    for target_name, target_value in targets_root.items():
        if target_name not in external_targets:
            external_targets[target_name] = copy.deepcopy(target_value)

    def replace_references(mapping_name, mapping_content):
        if 'sources' in mapping_content:
            expanded_sources = list()
            for source_ref in mapping_content['sources']:
                if isinstance(source_ref, str) and source_ref in sources_root:
                    source = sources_root[source_ref]
                    expanded_sources.append(dict(source))
                    if source_ref in external_sources:
                        if mapping_name not in external_sources[source_ref]['mappings']:
                            external_sources[source_ref]['mappings'].append(mapping_name)
                else:
                    expanded_sources.append(source_ref)


            mapping_content['sources'] = expanded_sources

        if 'subjects' in mapping_content:
            for subject in mapping_content['subjects']:
                if isinstance(subject, dict):
                    if 'targets' in subject:
                        subject['targets'] = expand_targets_with_identifiers(subject['targets'], targets_root)

        if 'graphs' in mapping_content:
            for graph in mapping_content['graphs']:
                if isinstance(graph, dict):
                    if 'targets' in graph:
                        graph['targets'] = expand_targets_with_identifiers(graph['targets'], targets_root)

        if 'predicateobjects' in mapping_content:
            po = mapping_content['predicateobjects'][0]
            if 'objects' in po:
                for object in po['objects']:
                    if isinstance(object, dict):
                        if 'targets' in object:
                            object['targets'] = expand_targets_with_identifiers(object['targets'], targets_root)

    if 'mappings' in data:
        for mapping_name, mapping_content in data['mappings'].items():
            replace_references(mapping_name, mapping_content)

    if 'sources' in data:
        del data['sources']
    if 'targets' in data:
        del data['targets']

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
