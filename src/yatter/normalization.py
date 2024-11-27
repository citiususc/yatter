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
    'targets': ['target', 't']
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
        if isinstance(source, list) and len(source) == 2 and isinstance(source[0], str) and '~' in source[0]:
            access, reference = source[0].split('~')
            expanded_source = dict()
            expanded_source['access'] = access
            expanded_source['referenceFormulation'] = reference
            expanded_source['iterator'] = source[1]
            return expanded_source
        elif len(source) == 1 and isinstance(source[0], str) and '~' in source[0]:
            access, reference = source[0].split('~')
            expanded_source = dict()
            expanded_source['access'] = access
            expanded_source['referenceFormulation'] = reference
            return expanded_source
        elif isinstance(source, dict):
            for key, val in source.items():
                if isinstance(val, list) and len(val) == 2 and '~' in val[0]:
                    access, reference = val[0].split('~')
                    expanded_source = dict()
                    expanded_source[key] = dict({
                        'access': access,
                        'referenceFormulation': reference,
                        'iterator': val[1]
                    })
                    return expanded_source
                else:
                    return normalize_yaml(source)
        return source

    if isinstance(sources, list):
        return list([expand_source_item(src) for src in sources])
    elif isinstance(sources, dict):
        expanded_sources = dict()
        for key, src in sources.items():
            expanded_sources[key] = expand_source_item(src)
        return expanded_sources
    return sources


def expand_targets(targets, root_targets):
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
                expanded_subject['value'] = subject.get('value', '')
                if 'targets' in subject:
                    expanded_subject['targets'] = expand_targets(subject['targets'], root_targets)
            expanded_subjects.append(expanded_subject)
    return expanded_subjects


def expand_predicateobjects(predicateobjects):
    expanded_predicateobjects = list()

    for po in predicateobjects:
        if isinstance(po, list) and len(po) == 3:
            expanded_po = dict()
            expanded_po['predicates'] = list([dict({'value': po[0]})])
            expanded_po['objects'] = list([dict({'value': po[1]})])

            third_value = po[2]
            if '~' in third_value:
                expanded_po['objects'][0]['language'] = third_value.split('~')[0]
            else:
                expanded_po['objects'][0]['datatype'] = third_value

            expanded_predicateobjects.append(expanded_po)

        elif isinstance(po, dict) and 'predicates' in po and 'objects' in po:
            if isinstance(po['predicates'], str):
                po['predicates'] = [po['predicates']]
            if isinstance(po['objects'], str):
                po['objects'] = [po['objects']]

            for pred in po['predicates']:
                expanded_po = dict()
                if isinstance(pred, dict) and 'value' in pred:
                    expanded_po['predicates'] = po['predicates']
                else:
                    expanded_po['predicates'] = list([dict({'value': pred})])

                expanded_po['objects'] = list()
                for obj in po['objects']:
                    object_expansion = dict()
                    if isinstance(obj, dict) and 'function' in obj:
                        object_expansion['function'] = obj['function']
                        if 'parameters' in obj:
                            object_expansion['parameters'] = expand_parameters(obj['parameters'])
                    elif isinstance(obj, dict) and 'value' in obj:
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

        elif isinstance(po, list) and len(po) >= 2:
            if isinstance(po[0], str):
                po[0] = [po[0]]
            if isinstance(po[1], str):
                po[1] = [po[1]]
            predicates_list, objects_list = po[0], po[1]

            for pred in predicates_list:
                expanded_po = dict()
                expanded_po['predicates'] = list()
                expanded_po['predicates'].append(dict({'value': pred}))

                expanded_po['objects'] = list()
                for obj in objects_list:
                    object_expansion = dict()
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
                        if isinstance(obj, dict) and 'value' in obj:
                            object_expansion.update(obj)
                        else:
                            object_expansion['value'] = obj

                    expanded_po['objects'].append(object_expansion)

                expanded_predicateobjects.append(expanded_po)

        elif isinstance(po, dict):
            expanded_po = dict()

            if 'p' in po and 'o' in po:
                for key, value in po.items():
                    if key == 'p':
                        expanded_po['predicates'] = [{'value': value}]
                    elif key == 'o':
                        expanded_po['objects'] = []
                        for o in value:
                            object_expansion = dict()
                            if isinstance(o, dict) and 'mapping' in o and 'condition' in o:
                                object_expansion['mapping'] = o['mapping']
                                if 'condition' in o:
                                    object_expansion['condition'] = o['condition']

                                    if 'parameters' in o['condition']:
                                        object_expansion['condition']['parameters'] = expand_parameters(
                                            o['condition']['parameters'])

                                expanded_po['objects'].append(object_expansion)
                            else:
                                expanded_po['objects'].append({'value': o})

            expanded_predicateobjects.append(expanded_po)

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


def switch_mappings(data):
    sources_root = data.get('sources', {})
    targets_root = data.get('targets', {})

    def replace_references(mapping_content):
        if 'sources' in mapping_content:
            expanded_sources = list()
            for source_ref in mapping_content['sources']:
                if isinstance(source_ref, str) and source_ref in sources_root:
                    expanded_sources.append(dict({source_ref: sources_root[source_ref]}))
                else:
                    expanded_sources.append(source_ref)
            mapping_content['sources'] = expanded_sources

        if 'subjects' in mapping_content:
            expanded_subjects = list()
            for subject in mapping_content['subjects']:
                expanded_subject = dict()
                if isinstance(subject, str):
                    expanded_subject['value'] = subject
                elif isinstance(subject, dict):
                    expanded_subject['value'] = subject.get('value', '')
                    if 'targets' in subject:
                        expanded_subject['targets'] = expand_targets_with_identifiers(subject['targets'], targets_root)
                expanded_subjects.append(expanded_subject)
            mapping_content['subjects'] = expanded_subjects

    if 'mappings' in data:
        for mapping_name, mapping_content in data['mappings'].items():
            replace_references(mapping_content)

    if 'sources' in data:
        del data['sources']
    if 'targets' in data:
        del data['targets']

    return data


def expand_targets_with_identifiers(targets, root_targets):
    expanded_targets = list()
    for target in targets:
        if isinstance(target, str) and target in root_targets:
            expanded_targets.append(dict({target: root_targets[target]}))
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
            expanded_targets.append(expanded_target)
        elif isinstance(target, dict):
            expanded_targets.append(target)
    return expanded_targets


def normalize(data):
    data = normalize_yaml(data)
    switch_mappings(data)
    return data
