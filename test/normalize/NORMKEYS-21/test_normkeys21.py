from yatter.termmap import generate_rml_termmap_text
from yatter.constants import RML_URI


def test_rml_termmap_text_reference():
    term_map, value = generate_rml_termmap_text("$(name)", RML_URI)

    assert term_map == "rml:reference"
    assert value == "name"
