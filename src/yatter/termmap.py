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

def generate_cc_termmap_text(text, mapping_format=RML_URI):
    from .mapping import prefixes
    term_map = get_termmap_type(text[YARRRML_GATHER], mapping_format)
    text = text[YARRRML_GATHER]
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
        text = f'"{text}"'
    elif term_map == R2RML_CONSTANT and text == "a":
        text = RDF_TYPE
    return term_map, text

def generate_rml_termmap_text(text, mapping_format=RML_URI):
    from .mapping import prefixes
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
    return term_map, text

def generate_cc_termmap(rml_property, rml_class, content, indentation, mapping_format=RML_URI):
    template = indentation[0:-1] + rml_property + " [\n" + indentation + "a " + rml_class + ";\n"
    if isinstance(content, dict) and 'value' in content:
        value_text = content.get('value', '')
        term_map, value_text = generate_rml_termmap_text(value_text, mapping_format)
        if term_map == STAR_QUOTED:
            if 'quoted' in value_text:
                template +=indentation + term_map + " <" + value_text[YARRRML_QUOTED] + "_0>;\n"
            else:
                template +=indentation +  term_map + " <" + value_text[YARRRML_NON_ASSERTED] + "_0>;\n"
        elif term_map != "rr:constant":
            template +=indentation +  term_map + " \"" + value_text + "\";\n"
        else:
            if value_text.startswith("http"):
                template +=indentation +  term_map + " <" + value_text + ">;\n"
            else:
                if ":" in value_text or "<" in value_text:
                    template +=indentation +  term_map + " " + value_text + ";\n"
                else:
                    template +=indentation +  term_map + " \"" + value_text + "\";\n"
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
    term_map, text = generate_rml_termmap_text(text, mapping_format)

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


