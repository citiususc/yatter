import copy

from .constants import *
from .errors import InvalidMappingError
from .normalization_expansion import expand_targets, normalize_yaml


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
    if isinstance(targets, dict) or isinstance(targets, str):
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
                subject[YARRRML_TARGETS] = expand_targets_with_identifiers(
                    subject[YARRRML_TARGETS], targets_root
                )

    if YARRRML_GRAPHS in mapping_content:
        for graph in mapping_content[YARRRML_GRAPHS]:
            if isinstance(graph, dict) and YARRRML_TARGETS in graph:
                graph[YARRRML_TARGETS] = expand_targets_with_identifiers(
                    graph[YARRRML_TARGETS], targets_root
                )

    if YARRRML_PREDICATEOBJECT in mapping_content:
        for predicate_object in mapping_content[YARRRML_PREDICATEOBJECT]:
            if YARRRML_OBJECTS not in predicate_object:
                continue
            for obj in predicate_object[YARRRML_OBJECTS]:
                if isinstance(obj, dict) and YARRRML_TARGETS in obj:
                    obj[YARRRML_TARGETS] = expand_targets_with_identifiers(
                        obj[YARRRML_TARGETS], targets_root
                    )


def normalize(data, external_sources, external_targets):
    data = normalize_yaml(copy.deepcopy(data))

    if data.get(YARRRML_MAPPINGS):
        for mapping in data[YARRRML_MAPPINGS]:
            mapping_data = data[YARRRML_MAPPINGS][mapping]
            if YARRRML_PREDICATEOBJECT in mapping_data:
                for predicate_object_map in mapping_data[YARRRML_PREDICATEOBJECT]:
                    if YARRRML_OBJECTS not in predicate_object_map:
                        logger.error(
                            "There isn't a valid object key (object, objects, o) "
                            "correctly specified in POM %s",
                            predicate_object_map,
                        )
                        raise InvalidMappingError(
                            "Add or change the key of the object in the indicated POM"
                        )

                    if YARRRML_PREDICATES not in predicate_object_map:
                        logger.error(
                            "There isn't a valid predicate key "
                            "(predicate, predicates, p) correctly specified in POM %s",
                            predicate_object_map,
                        )
                        raise InvalidMappingError(
                            "Add or change the key of the predicate in the indicated POM"
                        )
            if YARRRML_SUBJECTS not in mapping_data:
                mapping_data[YARRRML_SUBJECTS] = list()

    switch_mappings(data, external_sources, external_targets)
    return data
