from .constants import *


def add_logical_targets(yarrrml_data):
    logical_targets = []
    for mapping in yarrrml_data.get(YARRRML_MAPPINGS):
        mapping_data = yarrrml_data.get(YARRRML_MAPPINGS).get(mapping)
        add_internal_logical_target(mapping, mapping_data, logical_targets)
    return logical_targets


def add_internal_logical_target(mapping_id, mapping_data, internal_targets, local_target_id=0):
    keys = mapping_data.keys()
    for key in keys:
        if type(mapping_data[key]) is list:
            for i in range(len(mapping_data[key])):
                value = mapping_data[key][i]
                if YARRRML_TARGETS in value:
                    target_value = value[YARRRML_TARGETS]
                    if type(target_value) is dict or type(target_value) is list:
                        logical_target_id = "logical_target_" + mapping_id + "_" + str(local_target_id)
                        internal_targets.extend(generate_logical_target(target_value, logical_target_id))
                        mapping_data[key][i][YARRRML_TARGETS] = logical_target_id
                        local_target_id += 1
                else:
                    if type(value) is list:
                        for v in value:
                            if type(v) is dict:
                                add_internal_logical_target(mapping_id, v, internal_targets, local_target_id)
                    elif type(value) is dict:
                        add_internal_logical_target(mapping_id, value, internal_targets, local_target_id)
        elif YARRRML_TARGETS in mapping_data[key]:
            target_value = mapping_data[key][YARRRML_TARGETS]
            logical_target_id = "logical_target_" + mapping_id + "_" + str(local_target_id)
            internal_targets.extend(generate_logical_target(target_value, logical_target_id))
            mapping_data[key][YARRRML_TARGETS] = logical_target_id
            local_target_id += 1


def generate_logical_target(target_yaml_data, id_target):
    logical_targets = []
    output_type = None
    format = None
    compression = None
    target_yaml_data_list = target_yaml_data

    for target_yaml_data in target_yaml_data_list:
        logical_target = ["<" + id_target + "> a " + RML_LOGICAL_TARGET_CLASS + ";\n"]
        if YARRRML_ACCESS not in target_yaml_data:
            _, target_yaml_data = target_yaml_data.popitem()

        access = target_yaml_data[YARRRML_ACCESS]
        if YARRRML_TYPE in target_yaml_data:
            output_type = target_yaml_data[YARRRML_TYPE]
        if YARRRML_SERIALIZATION in target_yaml_data:
            format = "formats:" + YARRRML_OUTPUT_FORMAT[target_yaml_data[YARRRML_SERIALIZATION]]
        if YARRRML_COMPRESSION in target_yaml_data:
            compression = "comp:" + target_yaml_data[YARRRML_COMPRESSION]

        logical_target.append("\t " + RML_TARGET + " [\n\t\t")

        if output_type == "sparql":
            logical_target.append("sd:endpoint <" + access + ">;\n\t\tsd:supportedLanguage sd:SPARQL11Update\n\t];\n")
        elif output_type == "dcat":
            logical_target.append("a dcat:Dataset;\n\t\tdcat:dataDump <" + access + ">\n\t];\n")
        else:
            logical_target.append("a void:Dataset;\n\t\tvoid:dataDump <" + access + ">\n\t];\n")

        if format:
            logical_target.append("\t " + RML_SERIALIZATION + " " + format + ";")
        else:
            logical_target.append("\t " + RML_SERIALIZATION + " formats:N-Quads;")

        if compression:
            logical_target.append("\n\t " + RML_COMPRESSION + " " + compression + ";")
        logical_targets.append("".join(logical_target)[0:-1] + ".\n\n")
    return logical_targets
