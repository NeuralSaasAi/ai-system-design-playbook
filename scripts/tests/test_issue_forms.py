"""Make sure every GitHub issue form parses and has what GitHub needs."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

FORMS_DIR = Path(__file__).resolve().parent.parent.parent / ".github" / "ISSUE_TEMPLATE"
FORMS = sorted(p for p in FORMS_DIR.glob("*.yml") if p.name != "config.yml")
VALID_TYPES = {"markdown", "textarea", "input", "dropdown", "checkboxes"}


def test_forms_exist():
    names = {p.name for p in FORMS}
    assert {"propose-case-study.yml", "content-fix.yml", "broken-link.yml"} <= names


@pytest.mark.parametrize("path", FORMS, ids=lambda p: p.name)
def test_form_is_valid(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    for key in ("name", "description", "body"):
        assert data.get(key), f"{path.name}: missing `{key}`"
    assert data.get("labels"), f"{path.name}: needs at least one label"
    ids = []
    for item in data["body"]:
        assert item["type"] in VALID_TYPES, f"{path.name}: bad type {item['type']}"
        if item["type"] != "markdown":
            assert item.get("id"), f"{path.name}: every field needs an id"
            ids.append(item["id"])
            assert item["attributes"].get("label") or item["type"] == "checkboxes"
        if item["type"] == "dropdown":
            assert item["attributes"]["options"], f"{path.name}: dropdown has no options"
    assert len(ids) == len(set(ids)), f"{path.name}: duplicate field ids"
    assert any(i.get("validations", {}).get("required") for i in data["body"]), \
        f"{path.name}: at least one field must be required"


def test_config_disables_blank_issues():
    data = yaml.safe_load((FORMS_DIR / "config.yml").read_text(encoding="utf-8"))
    assert data["blank_issues_enabled"] is False
    for link in data.get("contact_links", []):
        assert {"name", "url", "about"} <= set(link)
