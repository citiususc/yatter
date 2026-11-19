from .constants import *


## return the type of TermMap based on the input text
def get_termmap_type(text, mapping_format):
    if type(text) in basic_types:
        text = str(text)
    if "$(" in text and ")" in text:
        if text[0] == "$" and text[len(text) - 1] == ")" and text.count("$(") == 1:
            if mapping_format == R2RML_URI:
                return R2RML_COLUMN
            else:
               return RML_REFERENCE
        else:
            return R2RML_TEMPLATE
    elif YARRRML_QUOTED in text or YARRRML_NON_ASSERTED in text:
        return STAR_QUOTED
    else:
        return R2RML_CONSTANT


def get_rml_termtype(term_type):
    return {
        'iri': R2RML_IRI,
        'blank': R2RML_BLANK_NODE,
        YARRRML_BLANK: R2RML_BLANK_NODE,
        'literal': R2RML_LITERAL,
    }.get(term_type)


def _generate_termmap_text(text, mapping_format=RML_URI, gather=False):
    from .mapping import get_prefixes
    prefixes = get_prefixes()
    term_map = get_termmap_type(text[YARRRML_GATHER] if gather else text, mapping_format)
    text = text[YARRRML_GATHER] if gather else text
    if term_map == R2RML_TEMPLATE:
        text = generate_rml_template(text)
        text = text.replace('"', r'\"')
        if ":" in text:
            text_prefix_split = text.split(":")
            if text_prefix_split[0] in prefixes:
                text = prefixes[text_prefix_split[0]] + text_prefix_split[1]
    elif term_map == RML_REFERENCE or term_map == R2RML_COLUMN:
        if gather:
            text = text.replace("$(", "").replace(")", "")
        else:
            text = generate_rml_template(text).replace("{","").replace("}","")
        text = text.replace('"', r'\"')
        if gather:
            text = f'"{text}"'
    elif term_map == R2RML_CONSTANT and text == "a":
        text = RDF_TYPE
    return term_map, text


def generate_cc_termmap_text(text, mapping_format=RML_URI):
    return _generate_termmap_text(text, mapping_format, gather=True)


def generate_rml_termmap_text(text, mapping_format=RML_URI):
    return _generate_termmap_text(text, mapping_format)


def _append_term_map_property(template, indentation, predicate, value):
    return _append_term_map_content(
        template, indentation, indentation + predicate + " " + value + "\n"
    )


def _append_term_map_content(template, indentation, content):
    closing = indentation[:-1] + "];\n"
    if not template.endswith(closing):
        raise ValueError("Term map text does not end with its expected closing")
    body = template[: -len(closing)].rstrip("\n")
    if not body.endswith(";"):
        body += ";"
    return body + "\n" + content + closing


def generate_graph_termmap(graph, indentation):
    graph_value = graph[YARRRML_VALUE] if YARRRML_VALUE in graph else graph
    result = generate_rml_termmap(
        R2RML_GRAPH_MAP, R2RML_GRAPH_CLASS, graph_value, indentation
    )
    if YARRRML_TARGETS in graph:
        result = _append_term_map_property(
            result, indentation, RML_LOGICAL_TARGET,
            "<" + graph[YARRRML_TARGETS] + ">",
        )
    return result


def _format_term_map_value(term_map, text):
    if term_map == STAR_QUOTED:
        key = YARRRML_QUOTED if YARRRML_QUOTED in text else YARRRML_NON_ASSERTED
        return "<" + text[key] + "_0>"
    if term_map != R2RML_CONSTANT:
        return "\"" + text + "\""
    if text.startswith("http"):
        return "<" + text + ">"
    if ":" in text or "<" in text:
        return text
    return "\"" + text + "\""


def generate_cc_termmap(rml_property, rml_class, content, indentation, mapping_format=RML_URI):
    template = indentation[0:-1] + rml_property + " [\n" + indentation + "a " + rml_class + ";\n"
    if isinstance(content, dict) and 'value' in content:
        value_text = content.get('value', '')
        term_map, value_text = generate_rml_termmap_text(value_text, mapping_format)
        template += indentation + term_map + " " + _format_term_map_value(term_map, value_text) + ";\n"
    if isinstance(content[YARRRML_GATHER], str):
        term_map, text = generate_cc_termmap_text(content, mapping_format)
        if YARRRML_EMPTY in content:
            if content[YARRRML_EMPTY] == "\"true\"":
                template += indentation + RML_CC_EMPTY +" " + "true" + ";\n"
            elif content[YARRRML_EMPTY] == "\"false\"":
                template += indentation + RML_CC_EMPTY +" " + "false" + ";\n"
        template += indentation + RML_CC_GATHER + " ( [ " + term_map + " " + text + "; ] ) ;\n"
        if YARRRML_GATHER_AS in content and content[YARRRML_GATHER_AS] in YARRRML_GATHER_AS_OPTIONS:
            template += indentation + RML_CC_GATHER_AS + " rdf:" + content[YARRRML_GATHER_AS].capitalize() + ";\n"
    elif isinstance(content[YARRRML_GATHER], list):
        template += indentation + RML_CC_GATHER + " (\n"
        for gather_item in content[YARRRML_GATHER]:
            term_map, text = generate_cc_termmap_text(gather_item, mapping_format)
            if YARRRML_GATHER_AS in gather_item:
                template += indentation + "\t" + "[\n" + indentation + "\t\t" + RML_CC_GATHER + " ( [ " + term_map + " " + text + "; ] ) ;\n"
                template += indentation + "\t\t" + RML_CC_GATHER_AS + " rdf:" + gather_item[YARRRML_GATHER_AS].capitalize() + ";\n"
                template += indentation + "\t]\n"
            else:
                template += indentation + " [ " + term_map + " " + text + "; ] \n"

        template += indentation + ") ;\n"

        if YARRRML_GATHER_AS in content and content[YARRRML_GATHER_AS] in YARRRML_GATHER_AS_OPTIONS:
            template += indentation + RML_CC_GATHER_AS + " rdf:" + content[YARRRML_GATHER_AS].capitalize() + ";\n"
        if YARRRML_STRATEGY in content and content[YARRRML_STRATEGY] in ['append','cartesianProduct']:
            template += indentation + RML_CC_STRATEGY + " rml:" + content[YARRRML_STRATEGY] + ";\n"
    return template


## Generates a TermMap (subject, predicate, object) based on the property, class and the text
def generate_rml_termmap(rml_property, rml_class, text, indentation, mapping_format=RML_URI):
    template = indentation[0:-1] + rml_property + " [\n" + indentation + "a " + rml_class + ";\n" + indentation
    if isinstance(text, dict) and 'value' in text:
        text = text.get('value', '')
    if type(text) in basic_types:
        text = str(text)
    term_map, text = generate_rml_termmap_text(text, mapping_format)

    return (
        template + term_map + " " + _format_term_map_value(term_map, text)
        + ";\n" + indentation[:-1] + "];\n"
    )


def generate_rml_template(yarrrml_template: str) -> str:
    result = []
    i = 0
    n = len(yarrrml_template)

    while i < n:
        if i + 1 < n and yarrrml_template[i] == "$" and yarrrml_template[i + 1] == "(":
            i += 2
            depth = 1
            content = []
            while i < n and depth > 0:
                char = yarrrml_template[i]

                if char == "(":
                    depth += 1
                    content.append(char)
                elif char == ")":
                    depth -= 1
                    if depth > 0:
                        content.append(char)
                else:
                    content.append(char)

                i += 1
            if depth == 0:
                result.append("{")
                result.append("".join(content))
                result.append("}")
            else:
                result.append("$(")
                result.append("".join(content))
        else:
            result.append(yarrrml_template[i])
            i += 1

    return "".join(result)


