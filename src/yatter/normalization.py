from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap as ordereddict, CommentedSeq


def normalize_yaml(data):
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
        'authors': ['author', 'a']
    }

    def get_normalized_key(key):
        for normalized_key, variants in key_mapping.items():
            if key == normalized_key or key in variants:
                return normalized_key
        return key

    def expand_authors(authors):
        expanded_authors = CommentedSeq()
        for author in authors:
            if isinstance(author, str):
                expanded_author = ordereddict()
                parts = author.split()
                name = []
                email = None
                website = None
                for part in parts:
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
            if isinstance(source, list) and len(source) == 2 and '~' in source[0]:
                expanded_source = ordereddict()
                access, reference = source[0].split('~')
                expanded_source['access'] = access
                expanded_source['referenceFormulation'] = reference
                expanded_source['iterator'] = source[1]
                return expanded_source
            elif isinstance(source, dict):
                return normalize_yaml(source)
            else:
                return source

        expanded_sources = CommentedSeq() if isinstance(sources, list) else ordereddict()

        if isinstance(sources, dict):
            for key, source in sources.items():
                expanded_sources[key] = expand_source_item(source)
        elif isinstance(sources, list):
            for source in sources:
                expanded_sources.append(expand_source_item(source))

        return expanded_sources

    def expand_targets(targets):
        def expand_target_item(target):
            if isinstance(target, list) and len(target) >= 1:
                expanded_target = ordereddict()
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
            else:
                return target

        expanded_targets = CommentedSeq() if isinstance(targets, list) else ordereddict()

        if isinstance(targets, dict):
            for key, target in targets.items():
                expanded_targets[key] = expand_target_item(target)
        elif isinstance(targets, list):
            for target in targets:
                expanded_targets.append(expand_target_item(target))

        return expanded_targets

    def expand_subjects(subjects):
        expanded_subjects = CommentedSeq()
        if isinstance(subjects, str):
            expanded_subjects.append(ordereddict({'value': subjects}))
        elif isinstance(subjects, list):
            for subject in subjects:
                if isinstance(subject, str):
                    expanded_subjects.append(ordereddict({'value': subject}))
                elif isinstance(subject, dict):
                    expanded_subjects.append(subject)
        return expanded_subjects
    def expand_predicateobjects(predicateobjects):

        expanded_predicateobjects = CommentedSeq()
        for po in predicateobjects:
            if isinstance(po, list):
                if isinstance(po[0], str):
                    po[0] = [po[0]]
                if isinstance(po[1], str):
                    po[1] = [po[1]]
                predicates_list, objects_list = po[0], po[1]

                for pred in predicates_list:
                    expanded_po = ordereddict()
                    expanded_po['predicates'] = CommentedSeq()
                    expanded_po['predicates'].append(ordereddict({'value': pred}))

                    expanded_po['objects'] = CommentedSeq()
                    for obj in objects_list:
                        object_expansion = ordereddict()
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
                            object_expansion['value'] = obj
                        if len(po) > 2 and isinstance(po[2], str):
                            if "~" in po[2]:
                                lang, dtype = po[2].split("~")
                                object_expansion['language'] = lang
                            else:
                                object_expansion['datatype'] = po[2]
                        expanded_po['objects'].append(object_expansion)

                    expanded_predicateobjects.append(expanded_po)

            elif isinstance(po, dict):
                expanded_po = ordereddict()

                for key, value in po.items():
                    if key == 'p':
                        expanded_po['predicates'] = value
                    elif key == 'o':
                        expanded_po['objects'] = normalize_yaml(value)
                    else:
                        expanded_po[key] = normalize_yaml(value)

                expanded_predicateobjects.append(expanded_po)

        return expanded_predicateobjects

    def expand_parameters(parameters):
        expanded_parameters = CommentedSeq()
        for param in parameters:
            expanded_param = ordereddict()
            if isinstance(param, list) and len(param) == 2:
                expanded_param['parameter'] = param[0]
                expanded_param['value'] = param[1]
            else:
                expanded_param = normalize_yaml(param)
            expanded_parameters.append(expanded_param)
        return expanded_parameters

    if isinstance(data, dict):
        new_data = ordereddict()
        for key, value in data.items():
            new_key = get_normalized_key(key)
            if new_key == 'authors' and isinstance(value, list):
                new_data[new_key] = expand_authors(value)
            elif new_key == 'sources':
                new_data[new_key] = expand_sources(value)
            elif new_key == 'targets':
                new_data[new_key] = expand_targets(value)
            elif new_key == 'predicateobjects':
                new_data[new_key] = expand_predicateobjects(value)
            elif new_key == 'subjects':
                new_data[new_key] = expand_subjects(value)
            else:
                new_data[new_key] = normalize_yaml(value)
        return new_data
    elif isinstance(data, list):
        new_list = CommentedSeq()
        for item in data:
            new_list.append(normalize_yaml(item))
        return new_list
    else:
        return data
