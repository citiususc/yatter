import pytest
from rdflib import Graph
from pathlib import Path
from ruamel.yaml import YAML

import yatter

from yatter.constants import (
    R2RML_OBJECT,
    R2RML_OBJECT_CLASS,
    R2RML_SUBJECT,
    R2RML_SUBJECT_CLASS,
    RML_CORE_URI,
    RML_URI,
)
from yatter.termmap import generate_rml_termmap
from yatter.cli import main


@pytest.mark.parametrize(
    ("mapping_format", "property_name", "class_name", "value", "expected"),
    [
        (
            RML_CORE_URI,
            R2RML_SUBJECT,
            R2RML_SUBJECT_CLASS,
            "http://example.org/$(id)",
            '\trml:subjectMap [\n\t\ta rml:SubjectMap;\n'
            '\t\trml:template "http://example.org/{id}";\n\t];\n',
        ),
        (
            RML_CORE_URI,
            R2RML_OBJECT,
            R2RML_OBJECT_CLASS,
            "$(name)",
            '\trml:objectMap [\n\t\ta rml:ObjectMap;\n'
            '\t\trml:reference "name";\n\t];\n',
        ),
        (
            RML_URI,
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


def test_unknown_format_is_rejected():
    with pytest.raises(ValueError, match="Unknown mapping format"):
        yatter.translate({}, mapping_format="unknown")

    with pytest.raises(ValueError, match="Unknown mapping format"):
        yatter.inverse_translate(Graph(), mapping_format="unknown")


def test_core_rejects_star_but_old_profile_still_accepts_it():
    path = Path(__file__).parents[1] / "rml-star/YARRRML-STAR-TC-0001/mapping.yml"
    with path.open() as stream:
        mapping = YAML(typ="safe", pure=True).load(stream)
    assert yatter.translate(mapping) is None
    assert yatter.translate(mapping, RML_URI) is not None


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
