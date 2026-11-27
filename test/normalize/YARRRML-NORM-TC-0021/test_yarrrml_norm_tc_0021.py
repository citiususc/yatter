from yatter.termmap import generate_rml_termmap_text
from yatter.constants import RML_OLD_URI, RML_REFERENCE


def test_yarrrml_norm_tc_0021():
    term_map, value = generate_rml_termmap_text("$(name)", RML_OLD_URI)

    assert term_map == RML_REFERENCE
    assert value == "name"
