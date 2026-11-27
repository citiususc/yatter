import pytest
from rdflib import Graph, URIRef
from pathlib import Path
from ruamel.yaml import YAML

import yatter

from yatter.constants import (
    R2RML_OBJECT,
    R2RML_OBJECT_CLASS,
    R2RML_SUBJECT,
    R2RML_SUBJECT_CLASS,
    RML_URI,
    R2RML_COLUMN,
    R2RML_SQL_QUERY,
    RML_EXECUTION,
    RML_VALUE_MAP,
    RML_OLD_URI,
    RML_FILE_PATH_CLASS,
    RML_NAMESPACE,
    RML_OLD_NAMESPACE,
    R2RML_NAMESPACE,
)
from yatter.termmap import _term_for_format, generate_rml_termmap
from yatter.cli import main


@pytest.mark.parametrize(
    ("mapping_format", "property_name", "class_name", "value", "expected"),
    [
        (
            RML_URI,
            R2RML_SUBJECT,
            R2RML_SUBJECT_CLASS,
            "http://example.org/$(id)",
            '\trml:subjectMap [\n\t\ta rml:SubjectMap;\n'
            '\t\trml:template "http://example.org/{id}";\n\t];\n',
        ),
        (
            RML_URI,
            R2RML_OBJECT,
            R2RML_OBJECT_CLASS,
            "$(name)",
            '\trml:objectMap [\n\t\ta rml:ObjectMap;\n'
            '\t\trml:reference "name";\n\t];\n',
        ),
        (
            RML_OLD_URI,
            R2RML_SUBJECT,
            R2RML_SUBJECT_CLASS,
            "http://example.org/$(id)",
            '\trr:subjectMap [\n\t\ta rr:SubjectMap;\n'
            '\t\trr:template "http://example.org/{id}";\n\t];\n',
        ),
    ],
)
def test_termmap_format(mapping_format, property_name, class_name, value, expected):
    assert generate_rml_termmap(
        property_name, class_name, value, "\t\t", mapping_format
    ) == expected


@pytest.mark.parametrize(
    ("term", "expected", "old_expected"),
    [
        (R2RML_COLUMN, "rml:reference", "rr:column"),
        (RML_EXECUTION, "rml:functionExecution", "fnml:execution"),
        (RML_VALUE_MAP, "rml:inputValueMap", "fnml:valueMap"),
    ],
)
def test_core_terms_with_different_names(term, expected, old_expected):
    assert _term_for_format(term, RML_URI) == expected
    assert _term_for_format(term, RML_OLD_URI) == old_expected


def test_vocabulary_constants_are_full_iris():
    assert RML_FILE_PATH_CLASS == "http://w3id.org/rml/FilePath"
    assert R2RML_COLUMN == "http://www.w3.org/ns/r2rml#column"
    assert RML_EXECUTION == "http://semweb.mmlab.be/ns/fnml#execution"
    assert (RML_URI, RML_OLD_URI) == (RML_NAMESPACE, RML_OLD_NAMESPACE)
    assert R2RML_COLUMN.startswith(R2RML_NAMESPACE)


def test_core_rejects_r2rml_only_term():
    with pytest.raises(ValueError, match="No RML-Core term"):
        _term_for_format(R2RML_SQL_QUERY, RML_URI)


def test_unknown_format_is_rejected():
    with pytest.raises(ValueError, match="Unknown mapping format"):
        yatter.translate({}, mapping_format="unknown")

    with pytest.raises(ValueError, match="Unknown mapping format"):
        yatter.inverse_translate(Graph(), mapping_format="unknown")


@pytest.mark.parametrize(
    ("mapping_format", "case_path"),
    [
        (RML_NAMESPACE, "rml-core/YARRRML-CORE-TC-0001"),
        (RML_OLD_NAMESPACE, "rml-old/YARRRML-CORE_OLD-TC-0001"),
    ],
)
def test_uri_constants_select_translation_profiles(mapping_format, case_path):
    case = Path(__file__).parents[1] / case_path
    with (case / "mapping.yml").open() as stream:
        mapping = YAML(typ="safe", pure=True).load(stream)
    translated = yatter.translate(mapping, mapping_format)
    assert f"<{mapping_format}>" in translated
    if mapping_format == RML_URI:
        assert translated == yatter.translate(mapping)
        assert translated == (case / "mapping.ttl").read_text()
    graph = Graph().parse(data=translated, format="turtle")
    assert next(graph.triples((None, URIRef(mapping_format + "logicalSource"), None)), None)
    assert yatter.inverse_translate(graph, mapping_format)["mappings"]


def test_core_rejects_star_but_old_profile_still_accepts_it():
    path = Path(__file__).parents[1] / "rml-star/YARRRML-STAR-TC-0001/mapping.yml"
    with path.open() as stream:
        mapping = YAML(typ="safe", pure=True).load(stream)
    assert yatter.translate(mapping) is None
    assert yatter.translate(mapping, RML_OLD_URI) is not None


@pytest.mark.parametrize("profile", [None, "RML"])
def test_cli_core_profiles_match_snapshot(profile, tmp_path, monkeypatch):
    case = Path(__file__).parents[1] / "rml-core/YARRRML-CORE-TC-0001"
    output = tmp_path / "output.ttl"
    args = ["yatter", "-i", str(case / "mapping.yml"), "-o", str(output)]
    if profile:
        args += ["-f", profile]
    monkeypatch.setattr("sys.argv", args)
    assert main() == 0
    assert output.read_text() == (case / "mapping.ttl").read_text()


def test_cli_old_profile(tmp_path, monkeypatch):
    case = Path(__file__).parents[1] / "rml-old/YARRRML-CORE_OLD-TC-0001"
    output = tmp_path / "output.ttl"
    monkeypatch.setattr("sys.argv", [
        "yatter", "-i", str(case / "mapping.yml"), "-o", str(output), "-f", "RML-OLD"
    ])
    assert main() == 0
    assert (output.read_text()).find("http://semweb.mmlab.be/ns/rml#") >= 0


def test_cli_rejects_rml_core_alias(monkeypatch):
    monkeypatch.setattr("sys.argv", ["yatter", "-f", "RML-CORE"])
    with pytest.raises(SystemExit):
        main()
