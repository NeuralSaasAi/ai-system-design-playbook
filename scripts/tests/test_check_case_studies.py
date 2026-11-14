"""Tests for scripts/check_case_studies.py. Each rule has a passing and a failing case."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import check_case_studies as cc  # noqa: E402

SECTIONS = cc.REQUIRED_SECTIONS

FRONT = """---
title: Customer support agent
level: advanced
status: {status}
category: Conversational and support
last_reviewed: 2026-11-14
---
"""


def build(status: str = "reviewed", *, drop: str | None = None, swap: bool = False,
          details: bool = True, extra: str = "", numbers: str = "Cost = tokens x price.",
          words: int = 0) -> str:
    """Build a valid case study, then let a test break one thing."""
    parts = [FRONT.format(status=status), "# Customer support agent\n"]
    names = list(SECTIONS)
    if swap:
        names[2], names[3] = names[3], names[2]
    for name in names:
        if name == drop:
            continue
        parts.append(f"## {name}\n")
        if name == "At a glance":
            parts.append("| Problem | Scale |\n|---|---|\n| Support | 500K tickets |\n")
            continue
        parts.append("This section explains the idea in plain words. It is short on purpose.\n")
        if name == "Numbers":
            parts.append(numbers + "\n")
        if name == "Architecture":
            parts.append("```mermaid\nflowchart TD\n  A --> B\n```\n")
        if name == "One request, end to end":
            parts.append("```mermaid\nsequenceDiagram\n  A->>B: hi\n```\n")
        if name == "Interview mode":
            if details:
                parts.append("<details>\n<summary>Answer</summary>\n\nUse a queue.\n\n</details>\n")
            else:
                parts.append("Answer: use a queue.\n")
    if extra:
        parts.append(extra + "\n")
    if words:
        parts.append(("word " * words) + "\n")
    return "\n".join(parts)


def write_repo(tmp_path: Path, files: dict[str, str], readme: str | None = None) -> Path:
    for name, text in files.items():
        p = tmp_path / "case-studies" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    if readme is not None:
        (tmp_path / "README.md").write_text(readme, encoding="utf-8")
    return tmp_path


def messages(root: Path) -> list[str]:
    return [p.message for p in cc.check_repo(root)]


def readme_for(status_emoji: str, name: str = "01-support.md") -> str:
    return (
        "# Playbook\n\n| # | Case study | Status |\n|---|---|---|\n"
        f"| 1 | [Support](case-studies/{name}) | {status_emoji} |\n"
    )


# ---------- passing case ----------

def test_valid_case_study_passes(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": build(words=2600)}, readme_for("✅"))
    assert messages(root) == []


def test_draft_has_no_minimum_length(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": build("draft")}, readme_for("🚧"))
    assert messages(root) == []


# ---------- front matter ----------

def test_missing_front_matter(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": "# Title\n"}, readme_for("📝"))
    assert any("front matter" in m for m in messages(root))


@pytest.mark.parametrize("field", ["title", "level", "status", "category", "last_reviewed"])
def test_missing_front_matter_field(tmp_path, field):
    text = "\n".join(
        line for line in build("draft").splitlines() if not line.startswith(f"{field}:")
    )
    root = write_repo(tmp_path, {"01-support.md": text}, readme_for("🚧"))
    assert any(f"`{field}`" in m for m in messages(root))


def test_bad_level(tmp_path):
    text = build("draft").replace("level: advanced", "level: expert")
    root = write_repo(tmp_path, {"01-support.md": text}, readme_for("🚧"))
    assert any("level must be" in m for m in messages(root))


def test_bad_status(tmp_path):
    text = build("draft").replace("status: draft", "status: done")
    root = write_repo(tmp_path, {"01-support.md": text}, readme_for("🚧"))
    assert any("status must be" in m for m in messages(root))


def test_bad_date(tmp_path):
    text = build("draft").replace("2026-11-14", "14/11/2026")
    root = write_repo(tmp_path, {"01-support.md": text}, readme_for("🚧"))
    assert any("YYYY-MM-DD" in m for m in messages(root))


# ---------- sections ----------

def test_missing_section(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": build("draft", drop="Scaling from 1x to 100x")},
                      readme_for("🚧"))
    assert any("missing section `## Scaling from 1x to 100x`" in m for m in messages(root))


def test_sections_out_of_order(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": build("draft", swap=True)}, readme_for("🚧"))
    assert any("out of order" in m for m in messages(root))


def test_section_must_open_with_plain_words(tmp_path):
    text = build("draft").replace(
        "## Requirements\n\nThis section explains the idea in plain words. It is short on purpose.\n",
        "## Requirements\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
    )
    assert "| a | b |" in text
    root = write_repo(tmp_path, {"01-support.md": text}, readme_for("🚧"))
    assert any("Requirements" in m and "plain" in m for m in messages(root))


def test_interview_answers_need_details(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": build("draft", details=False)}, readme_for("🚧"))
    assert any("<details>" in m for m in messages(root))


def test_numbers_section_needs_a_formula(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": build("draft", numbers="Some numbers.")},
                      readme_for("🚧"))
    assert any("formula" in m for m in messages(root))


def test_planned_status_skips_content_rules(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": FRONT.format(status="planned") + "# T\n"},
                      readme_for("📝"))
    assert messages(root) == []


# ---------- length and diagrams ----------

def test_reviewed_case_study_too_short(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": build("reviewed")}, readme_for("✅"))
    assert any("at least" in m and "words" in m for m in messages(root))


def test_case_study_too_long(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": build("draft", words=8000)}, readme_for("🚧"))
    assert any("split" in m for m in messages(root))


def test_reviewed_needs_two_diagrams(tmp_path):
    text = build(words=2600).replace("```mermaid\nsequenceDiagram\n  A->>B: hi\n```\n", "")
    root = write_repo(tmp_path, {"01-support.md": text}, readme_for("✅"))
    assert any("mermaid" in m for m in messages(root))


# ---------- style ----------

@pytest.mark.parametrize("word", ["robust", "leverage", "delve", "landscape", "revolutionary",
                                  "game-changing", "pivotal", "foster"])
def test_banned_words(tmp_path, word):
    root = write_repo(tmp_path, {"01-support.md": build("draft", extra=f"This is a {word} idea.")},
                      readme_for("🚧"))
    assert any(word in m for m in messages(root))


def test_banned_word_inside_code_is_allowed(tmp_path):
    extra = "```python\nrobust = True\n```"
    root = write_repo(tmp_path, {"01-support.md": build("draft", extra=extra)}, readme_for("🚧"))
    assert messages(root) == []


def test_site_only_syntax(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": build("draft", extra="!!! note\n    hi")},
                      readme_for("🚧"))
    assert any("site-only syntax" in m for m in messages(root))


# ---------- links ----------

def test_broken_relative_link(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": build("draft", extra="See [x](missing.md).")},
                      readme_for("🚧"))
    assert any("broken relative link" in m for m in messages(root))


def test_valid_relative_link(tmp_path):
    files = {"01-support.md": build("draft", extra="See [other](02-other.md)."),
             "02-other.md": FRONT.format(status="planned") + "# T\n"}
    readme = readme_for("🚧") + "| 2 | [Other](case-studies/02-other.md) | 📝 |\n"
    root = write_repo(tmp_path, files, readme)
    assert messages(root) == []


def test_missing_anchor(tmp_path):
    files = {"01-support.md": build("draft", extra="See [x](02-other.md#nope)."),
             "02-other.md": FRONT.format(status="planned") + "# T\n"}
    readme = readme_for("🚧") + "| 2 | [Other](case-studies/02-other.md) | 📝 |\n"
    root = write_repo(tmp_path, files, readme)
    assert any("heading anchor" in m for m in messages(root))


# ---------- catalog ----------

def test_case_study_missing_from_readme(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": build("draft")}, "# Playbook\n")
    assert any("not listed in README" in m for m in messages(root))


def test_catalog_status_mismatch(tmp_path):
    root = write_repo(tmp_path, {"01-support.md": build("draft")}, readme_for("✅"))
    assert any("status" in m and "README" in m for m in messages(root))


def test_template_passes_checker():
    root = Path(__file__).resolve().parent.parent.parent
    template = root / "templates" / "case-study-template.md"
    if not template.exists():
        pytest.skip("template not written yet")
    text = template.read_text(encoding="utf-8")
    assert [p.message for p in cc.check_case_study(Path("template.md"), text, strict_length=False)] == []
