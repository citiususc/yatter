from .constants import *


def add_logical_targets(yarrrml_data, external_targets, mapping_format=RML_OLD_URI):
    logical_targets = []
    for target in external_targets:
        logical_targets.extend(generate_logical_target(external_targets.get(target), target, mapping_format))
    for mapping in yarrrml_data.get(YARRRML_MAPPINGS):
        mapping_data = yarrrml_data.get(YARRRML_MAPPINGS).get(mapping)
        add_internal_logical_target(mapping, mapping_data, logical_targets, external_targets, mapping_format=mapping_format)
    return logical_targets


def add_internal_logical_target(mapping_id, mapping_data, internal_targets, external_targets, local_target_id=0, mapping_format=RML_OLD_URI):
    keys = mapping_data.keys()
    for key in keys:
        if type(mapping_data[key]) is list:
            for i in range(len(mapping_data[key])):
                value = mapping_data[key][i]
                if YARRRML_TARGETS in value:
                    target_value = value[YARRRML_TARGETS]
                    if type(target_value) is dict or type(target_value) is list:
                        external_targets_keys = [external_targets.get(external_target) for external_target in external_targets]
                        for target_yaml_data in target_value:
                            if YARRRML_ACCESS not in target_yaml_data:
                                target_id, target_yaml_data = target_yaml_data.popitem()
                            if not target_yaml_data in external_targets_keys:
                                logical_target_id = "logical_target_" + mapping_id + "_" + str(local_target_id)
                                internal_targets.extend(generate_logical_target(target_yaml_data, logical_target_id, mapping_format))
                                mapping_data[key][i][YARRRML_TARGETS] = logical_target_id
                                local_target_id += 1
                            else:
                                mapping_data[key][i][YARRRML_TARGETS] = target_id
                else:
                    if type(value) is list:
                        for v in value:
                            if type(v) is dict:
                                add_internal_logical_target(mapping_id, v, internal_targets, external_targets, local_target_id, mapping_format)
                    elif type(value) is dict:
                        add_internal_logical_target(mapping_id, value, internal_targets, external_targets, local_target_id, mapping_format)
        elif type(mapping_data[key]) is dict and YARRRML_TARGETS in mapping_data[key]:
            target_value = mapping_data[key][YARRRML_TARGETS]
            logical_target_id = "logical_target_" + mapping_id + "_" + str(local_target_id)
            internal_targets.extend(generate_logical_target(target_value, logical_target_id, mapping_format))
            mapping_data[key][YARRRML_TARGETS] = logical_target_id
            local_target_id += 1


def generate_logical_target(target_yaml_data, id_target, mapping_format=RML_OLD_URI):
    logical_targets = []
    output_type = None
    format = None
    compression = None
    target_yaml_data_list = target_yaml_data
    if isinstance(target_yaml_data_list, dict):
        target_yaml_data_list = [target_yaml_data]
    for target_yaml_data in target_yaml_data_list:
        logical_target = ["<" + id_target + "> a " + RML_LOGICAL_TARGET_CLASS + ";\n"]

        access = target_yaml_data[YARRRML_ACCESS]
        if YARRRML_TYPE in target_yaml_data:
            output_type = target_yaml_data[YARRRML_TYPE]
        if YARRRML_SERIALIZATION in target_yaml_data:
            format = FORMATS_TERM_PREFIX + YARRRML_OUTPUT_FORMAT[target_yaml_data[YARRRML_SERIALIZATION]]
        if YARRRML_COMPRESSION in target_yaml_data:
            compression = (RML_TERM_PREFIX if mapping_format == RML_URI else COMPRESSION_TERM_PREFIX) + target_yaml_data[YARRRML_COMPRESSION]

        logical_target.append("\t " + RML_TARGET + " [\n\t\t")

        if output_type == YARRRML_TARGET_SPARQL:
            target_description = SPARQL_ENDPOINT + " <" + access + ">;\n\t\t" + SPARQL_SUPPORTED_LANGUAGE + " " + SPARQL_11_UPDATE
        elif output_type == YARRRML_TARGET_DCAT:
            target_description = "a " + DCAT_DATASET + ";\n\t\t" + DCAT_DATA_DUMP + " <" + access + ">"
        else:
            target_description = "a " + VOID_DATASET + ";\n\t\t" + VOID_DATA_DUMP + " <" + access + ">"
        if compression and mapping_format == RML_URI:
            target_description += ";\n\t\t" + RML_COMPRESSION + " " + compression
        logical_target.append(target_description + "\n\t];\n")

        if format:
            logical_target.append("\t " + RML_SERIALIZATION + " " + format + ";")
        else:
            logical_target.append("\t " + RML_SERIALIZATION + " " + FORMATS_NQUADS + ";")

        if compression and mapping_format != RML_URI:
            logical_target.append("\n\t " + RML_COMPRESSION + " " + compression + ";")
        logical_targets.append("".join(logical_target)[0:-1] + ".\n\n")
    return logical_targets