from .constants import *
from .termmap import generate_rml_termmap, _term_for_format


def add_functions(yarrrml_data, mapping_format=RML_OLD_NAMESPACE):
    functions = []
    for mapping, mapping_data in yarrrml_data[YARRRML_MAPPINGS].items():
        context = {"local_id": 0}
        add_internal_function(mapping, mapping_data, functions, context, mapping_format)
    return functions


def add_internal_function(mapping_id, mapping_data, functions, context, mapping_format=RML_OLD_NAMESPACE):
    for key, value in mapping_data.items():
        if isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, dict) and YARRRML_FUNCTION in item:
                    value[index] = _replace_function(mapping_id, item, functions, context, mapping_format)
                elif isinstance(item, list):
                    for child in item:
                        if isinstance(child, dict):
                            add_internal_function(mapping_id, child, functions, context, mapping_format)
                elif isinstance(item, dict):
                    add_internal_function(mapping_id, item, functions, context, mapping_format)
        elif isinstance(value, dict) and YARRRML_FUNCTION in value:
            mapping_data[key] = _replace_function(mapping_id, value, functions, context, mapping_format)


def _replace_function(mapping_id, value, functions, context, mapping_format=RML_OLD_NAMESPACE):
    result = transform_function(mapping_id, value, functions, context, mapping_format)
    if isinstance(result, dict):
        return result
    if isinstance(result, str):
        value[YARRRML_FUNCTION] = result
    return value

def transform_function(mapping_id, function_value, functions, context, mapping_format=RML_OLD_NAMESPACE):
    function_return = None
    if function_value[YARRRML_FUNCTION].replace(" ","").startswith(YARRRML_JOIN+"("):
        function_return = generate_extended_join(function_value[YARRRML_FUNCTION])
    elif function_value[YARRRML_FUNCTION] != YARRRML_EQUAL:
        function_id = "function_" + mapping_id
        function_return = function_id + "_" + str(context["local_id"])
        function = generate_function(function_value, function_id, context, mapping_format)
        functions.append(function + ("\n" if mapping_format == RML_NAMESPACE else ""))
        context["local_id"] += 1  # different functions in the same TM

    return function_return

def generate_function(function_yarrrml_data, id_function, context, mapping_format=RML_OLD_NAMESPACE):
    function_name = function_yarrrml_data[YARRRML_FUNCTION]
    if YARRRML_PARAMETERS not in function_yarrrml_data:
        function_yarrrml_data, function_name = split_in_line_function(function_name)
    rml_function = [
        "<" + id_function + "_" + str(context["local_id"]) + "> a "
        + _term_for_format(RML_EXECUTION_CLASS, mapping_format) + ";\n\t"
        + _term_for_format(RML_FUNCTION, mapping_format) + " " + function_name
        + (" ;\n" if mapping_format == RML_NAMESPACE else " ; \n")
    ]
    nested_functions = []
    if YARRRML_PARAMETERS in function_yarrrml_data:
        rml_function.append("\t" + _term_for_format(RML_INPUT, mapping_format) + "\n")
        for param in function_yarrrml_data[YARRRML_PARAMETERS]:
            rml_function.append(
                _generate_function_input(param, id_function, context, nested_functions, mapping_format)
            )
    result = "".join(rml_function)[:-2] + ".\n\n" + "".join(nested_functions)
    return result.rstrip("\n") + "\n" if mapping_format == RML_NAMESPACE else result


def _generate_function_input(param, id_function, context, nested_functions, mapping_format=RML_OLD_NAMESPACE):
    if isinstance(param, list):
        param = {YARRRML_PARAMETER: param[0], YARRRML_VALUE: param[1]}
    result = "\t\t[\n\t\t\ta " + _term_for_format(RML_INPUT_CLASS, mapping_format) + ";\n"
    result += "\t\t\t" + _term_for_format(RML_PARAMETER, mapping_format) + " " + param[YARRRML_PARAMETER] + ";\n"
    if YARRRML_VALUE in param:
        value = param[YARRRML_VALUE]
        if YARRRML_FUNCTION in value:
            context["local_id"] += 1
            result += (
                "\t\t\t" + _term_for_format(RML_VALUE_MAP, mapping_format) + "[\n\t\t\t\t" + _term_for_format(RML_EXECUTION, mapping_format) + " <"
                + id_function + "_" + str(context["local_id"]) + ">;\n\t\t\t];\n"
            )
            function = generate_function(value, id_function, context, mapping_format)
            nested_functions.append(function + ("\n" if mapping_format == RML_NAMESPACE else ""))
        else:
            result += generate_rml_termmap(
                RML_VALUE_MAP, RML_VALUE_MAP_CLASS, value, "\t\t\t\t", mapping_format
            )
    return result + "\t\t],\n"



def split_in_line_function(function_in_line):
    parameters = {YARRRML_PARAMETERS: []}
    function_name = function_in_line.split("(")[0]
    function_in_line=function_in_line.replace(function_name, "").replace("(","",1).rsplit(")",1)[0]
    in_line_params = function_in_line.split(",")

    for param in in_line_params:
        extended_param = {}
        param_values = param.split("=",1)
        extended_param[YARRRML_PARAMETER] = param_values[0].strip()
        param_value = param_values[1].strip()

        if param_value.startswith("$("):
            extended_param[YARRRML_VALUE] = param_value
        else:
            value, internal_function_name = split_in_line_function(param_value)
            extended_param[YARRRML_VALUE] = {YARRRML_FUNCTION: internal_function_name, YARRRML_PARAMETERS: value[YARRRML_PARAMETERS]}

        parameters[YARRRML_PARAMETERS].append(extended_param)


    return parameters,function_name


def generate_extended_join(yarrrml_data):
    extended_join = {}
    data=yarrrml_data.replace(yarrrml_data.split("(")[0], "").replace("(","",1).rsplit(")",1)[0].split(",",1)
    if YARRRML_NON_ASSERTED in data[0]:
        extended_join[YARRRML_NON_ASSERTED] = data[0].split("=")[1]
    elif YARRRML_QUOTED in data[0]:
        extended_join[YARRRML_QUOTED] = data[0].split("=")[1]
    elif YARRRML_MAPPING in data[0] and "=" in data[0]:
        extended_join[YARRRML_MAPPING] = data[0].split("=")[1]
    else:
        extended_join[YARRRML_MAPPING] = data[0]

    equals = data[1].split(YARRRML_EQUAL)
    equals = list(filter(lambda val: val != ' ', equals))

    if equals:
        extended_join[YARRRML_CONDITION] = []

    for value in equals:
        parameters = []
        for param_name, condition in zip(
            [YARRRML_JOIN_CHILD_PARAMETER, YARRRML_JOIN_PARENT_PARAMETER],
            value.replace("(", "", 1).rsplit(")", 1)[0].split(","),
        ):
            parameters.append({
                YARRRML_PARAMETER: param_name,
                YARRRML_VALUE: condition
            })
        extended_join[YARRRML_CONDITION].append({
            YARRRML_FUNCTION: YARRRML_EQUAL,
            YARRRML_PARAMETERS: parameters
        })

    return extended_join



