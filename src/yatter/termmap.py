from .constants import *


## return the type of TermMap based on the input text
def get_termmap_type(text, mapping_format):
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


## Generates a TermMap (subject, predicate, object) based on the property, class and the text
def generate_rml_termmap(rml_property, rml_class, text, indentation, mapping_format=RML_URI):
    from .mapping import prefixes
    template = indentation[0:-1] + rml_property + " [\n" + indentation + "a " + rml_class + ";\n" + indentation
    if isinstance(text, dict) and 'value' in text:
        text = text.get('value', '')
    term_map = get_termmap_type(text, mapping_format)
    if term_map == R2RML_TEMPLATE:
        text = generate_rml_template(text)
        text = text.replace('"', r'\"')
        if ":" in text:
            text_prefix_split = text.split(":")
            if text_prefix_split[0] in prefixes:
                text = prefixes[text_prefix_split[0]] + text_prefix_split[1]
    elif term_map == RML_REFERENCE or term_map == R2RML_COLUMN:
        text = text.replace("$(", "").replace(")", "")
        text = text.replace('"', r'\"')
    elif term_map == R2RML_CONSTANT and text == "a":
        text = RDF_TYPE

    if term_map == STAR_QUOTED:
        if 'quoted' in text:
            template += term_map + " <" + text[YARRRML_QUOTED] + "_0>;\n" + indentation[0:-1] + "];\n"
        else:
            template += term_map + " <" + text[YARRRML_NON_ASSERTED] + "_0>;\n" + indentation[0:-1] + "];\n"
    elif term_map != "rr:constant":
        template += term_map + " \"" + text + "\";\n"+indentation[0:-1]+"];\n"
    else:
        if text.startswith("http"):
            template += term_map + " <" + text + ">;\n" + indentation[0:-1] + "];\n"
        else:
            if ":" in text or "<" in text:
                template += term_map + " " + text + ";\n"+indentation[0:-1]+"];\n"
            else:
                template += term_map + " \"" + text + "\";\n" + indentation[0:-1] + "];\n"

    return template


def generate_rml_template(yarrrml_template):
    references = 0
    for i in range(len(yarrrml_template)):
        if yarrrml_template[i]=="$" and yarrrml_template[i+1]=="(":
            references = references + 1
    yarrrml_template = yarrrml_template.replace("$(", "{")
    yarrrml_template = "}".join(yarrrml_template.rsplit(")", references))
    return yarrrml_template


