#!/usr/bin/env python3
"""Check that case studies follow the house format.

Rules (see STYLE.md and templates/case-study-template.md):

Every markdown file in the repo:
  - uses no site-generator-only syntax (MkDocs `!!!` admonitions, Jekyll `{: }` attributes, Liquid `{% %}`)
  - links to other files in this repo with relative paths (and heading anchors) that exist

Every file in case-studies/:
  - starts with front matter: title, level, status, category, industry, last_reviewed
  - targets a different industry or problem from every other case study (front matter `industry`
    values are unique, and so are the values in the README catalog's Industry column)
  - is listed in the README catalog with a matching status emoji
  Unless its status is `planned`, it also:
  - has the 17 template sections as `## ` headings, in order
  - has `### Words used in this case study`, `### Layers and tools` and `### Build order` inside `## Architecture`
  - opens each section with plain sentences (not a table, list, code block or sub-heading)
  - shows a formula in `Numbers`
  - puts interview answers inside <details> blocks
  - avoids the banned words listed in STYLE.md (code is not checked)
  - stays within the word limits (code and front matter are not counted)
  - has at least two mermaid diagrams when the status is `reviewed`

Standard library only, so it runs anywhere with Python 3.10+.
Usage: python3 scripts/check_case_studies.py [ROOT]
"""

from __future__ import annotations

import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REQUIRED_SECTIONS = [
    "At a glance",
    "The scenario",
    "Requirements",
    "Numbers",
    "Choosing the shape",
    "Architecture",
    "One request, end to end",
    "Deep dives",
    "Scaling from 1x to 100x",
    "Failure modes and safety",
    "Measuring quality",
    "Cost",
    "Trade-offs we made",
    "What teams get wrong",
    "Interview mode",
    "Concepts used",
    "Further reading",
]
# Sub-sections (`### `) that every non-planned `## Architecture` must contain.
# They make each case study usable by a reader with little AI background:
# plain-words glossary, the layers with tool categories, and a build order.
REQUIRED_ARCHITECTURE_SUBSECTIONS = [
    "Words used in this case study",
    "Layers and tools",
    "Build order",
]
# These sections may start with a table (the at-a-glance summary row).
MAY_START_WITH_TABLE = {"At a glance"}
LEVELS = {"intermediate", "advanced"}
STATUSES = {"planned": "📝", "draft": "🚧", "reviewed": "✅"}
MIN_WORDS_REVIEWED = 2500
MAX_WORDS = 11000
MIN_DIAGRAMS_REVIEWED = 2
BANNED_WORDS = [
    "robust", "leverage", "leverages", "leveraged", "leveraging", "delve", "delves",
    "landscape", "revolutionary", "game-changing", "game changer", "pivotal", "foster",
]
BANNED = re.compile(r"\b(" + "|".join(re.escape(w) for w in BANNED_WORDS) + r")\b", re.I)
SKIP_DIRS = {".git", ".venv", "node_modules", ".pytest_cache", ".ruff_cache", "fixtures"}
SKIP_FILES = {"IMPLEMENTATION_TRACKER.md", "LICENSE"}
FORBIDDEN_SYNTAX = [
    (re.compile(r"^\s*!!!\s+\w+", re.M), "MkDocs admonition (`!!! note`); use a GitHub alert (`> [!NOTE]`)"),
    (re.compile(r"\{:\s*[.#][^}]*\}"), "Jekyll/kramdown attribute (`{: .class}`)"),
    (re.compile(r"\{%.*?%\}"), "Liquid tag (`{% ... %}`)"),
]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^(```|~~~).*?^\1\s*$", re.M | re.S)
INLINE_CODE = re.compile(r"`[^`\n]+`")
# A line that starts a table, code fence, heading, quote, HTML tag, or list item is not prose.
NOT_PROSE = re.compile(r"^\s*(\||```|~~~|#|>|<|[-*+]\s|\d+[.)]\s)")


@dataclass
class Problem:
    path: Path
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def strip_fences(text: str) -> str:
    return FENCE.sub("", text)


def strip_code(text: str) -> str:
    return INLINE_CODE.sub("", strip_fences(text))


def split_front_matter(text: str) -> tuple[dict[str, str] | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip("\"'")
    return meta, text[end + 5:]


def github_slug(heading: str) -> str:
    slug = heading.strip().lower()
    slug = re.sub(r"[^\w\- ]", "", slug)
    return slug.replace(" ", "-")


def heading_slugs(text: str) -> set[str]:
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    for match in re.finditer(r"^#{1,6}\s+(.+?)\s*#*\s*$", strip_fences(text), re.M):
        base = github_slug(match.group(1))
        n = counts.get(base, 0)
        slugs.add(base if n == 0 else f"{base}-{n}")
        counts[base] = n + 1
    return slugs


def iter_markdown(root: Path):
    for path in sorted(root.rglob("*.md")):
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in rel_parts[:-1]) or path.name in SKIP_FILES:
            continue
        yield path


def check_links(path: Path, text: str, slug_cache: dict[Path, set[str]]) -> list[Problem]:
    problems: list[Problem] = []
    for target in LINK.findall(strip_code(text)):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
            continue  # external; lychee checks these
        file_part, _, anchor = target.partition("#")
        dest = path if not file_part else (path.parent / file_part).resolve()
        if file_part and not dest.exists():
            problems.append(Problem(path, f"broken relative link: {target}"))
            continue
        if file_part.startswith("/"):
            problems.append(Problem(path, f"absolute path link: {target}; use a relative path"))
        if anchor and dest.suffix == ".md":
            if dest not in slug_cache:
                slug_cache[dest] = heading_slugs(dest.read_text(encoding="utf-8"))
            if anchor.lower() not in slug_cache[dest]:
                problems.append(Problem(path, f"missing heading anchor: {target}"))
    return problems


def sections_of(body: str) -> list[tuple[str, str]]:
    """Return (heading, content) for each `## ` section outside code fences."""
    clean = strip_fences_keep_positions(body)
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", clean, re.M))
    result = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        result.append((m.group(1), body[m.end():end]))
    return result


def strip_fences_keep_positions(text: str) -> str:
    """Blank out fenced code with spaces so heading offsets still match the original text."""
    return FENCE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def check_front_matter(path: Path, text: str) -> tuple[dict[str, str] | None, str, list[Problem]]:
    meta, body = split_front_matter(text)
    if meta is None:
        return None, text, [Problem(path, "missing YAML front matter (title, level, status, category, industry, last_reviewed)")]
    problems: list[Problem] = []
    for key in ("title", "level", "status", "category", "industry", "last_reviewed"):
        if not meta.get(key):
            problems.append(Problem(path, f"front matter is missing `{key}`"))
    if meta.get("level") and meta["level"] not in LEVELS:
        problems.append(Problem(path, f"level must be one of {sorted(LEVELS)}, got `{meta['level']}`"))
    if meta.get("status") and meta["status"] not in STATUSES:
        problems.append(Problem(path, f"status must be one of {sorted(STATUSES)}, got `{meta['status']}`"))
    if meta.get("last_reviewed"):
        try:
            reviewed = dt.date.fromisoformat(meta["last_reviewed"])
            if reviewed > dt.date.today() + dt.timedelta(days=1):
                problems.append(Problem(path, "last_reviewed is in the future"))
        except ValueError:
            problems.append(Problem(path, "last_reviewed must be YYYY-MM-DD"))
    return meta, body, problems


def check_case_study(path: Path, text: str, strict_length: bool = True) -> list[Problem]:
    meta, body, problems = check_front_matter(path, text)
    if meta is None:
        return problems
    status = meta.get("status", "")
    if status == "planned":
        return problems

    sections = sections_of(body)
    headings = [h for h, _ in sections]
    positions = []
    for name in REQUIRED_SECTIONS:
        if name not in headings:
            problems.append(Problem(path, f"missing section `## {name}`"))
        else:
            positions.append(headings.index(name))
    if positions != sorted(positions):
        problems.append(Problem(path, "sections are out of order (see templates/case-study-template.md)"))

    content = dict(sections)
    for name in REQUIRED_SECTIONS:
        if name in MAY_START_WITH_TABLE or name not in content:
            continue
        first = next((ln for ln in content[name].splitlines() if ln.strip()), "")
        if not first or NOT_PROSE.match(first):
            problems.append(Problem(path, f"`{name}` must open with plain sentences before any table, list or code"))

    if "Architecture" in content:
        subs = re.findall(r"^###\s+(.+?)\s*$", strip_fences_keep_positions(content["Architecture"]), re.M)
        for needed in REQUIRED_ARCHITECTURE_SUBSECTIONS:
            if needed not in subs:
                problems.append(Problem(path, f"`## Architecture` is missing the sub-section `### {needed}`"))

    if "Numbers" in content and "=" not in strip_fences_keep_positions(content["Numbers"]) \
            and "=" not in content["Numbers"]:
        problems.append(Problem(path, "`Numbers` must show at least one formula (with `=`)"))
    if "Interview mode" in content and "<details>" not in content["Interview mode"]:
        problems.append(Problem(path, "`Interview mode` answers must be inside <details> blocks"))

    for word in sorted({m.group(1).lower() for m in BANNED.finditer(strip_code(body))}):
        problems.append(Problem(path, f"banned word `{word}` (see STYLE.md)"))

    words = len(re.findall(r"\b\w+\b", strip_code(body)))
    if words > MAX_WORDS:
        problems.append(Problem(path, f"{words} words; split case studies longer than {MAX_WORDS} words"))
    if status == "reviewed" and strict_length:
        if words < MIN_WORDS_REVIEWED:
            problems.append(Problem(path, f"{words} words; a reviewed case study needs at least {MIN_WORDS_REVIEWED} words"))
        diagrams = len(re.findall(r"^```mermaid\s*$", body, re.M))
        if diagrams < MIN_DIAGRAMS_REVIEWED:
            problems.append(Problem(path, f"{diagrams} mermaid diagram(s); a reviewed case study needs at least {MIN_DIAGRAMS_REVIEWED}"))
    return problems


def check_catalog(root: Path, studies: list[tuple[Path, str]]) -> list[Problem]:
    if not studies:
        return []
    readme = root / "README.md"
    if not readme.exists():
        return [Problem(Path("README.md"), "README.md is missing, so the catalog cannot be checked")]
    lines = readme.read_text(encoding="utf-8").splitlines()
    problems: list[Problem] = []
    for path, status in studies:
        needle = f"case-studies/{path.name}"
        row = next((ln for ln in lines if needle in ln), None)
        if row is None:
            problems.append(Problem(Path("README.md"), f"{needle} is not listed in README catalog"))
        elif status in STATUSES and STATUSES[status] not in row:
            problems.append(Problem(Path("README.md"),
                                    f"README catalog row for {path.name} must show status {STATUSES[status]} ({status})"))
    return problems


def _duplicates(pairs: list[tuple[str, str]]) -> list[tuple[str, list[str]]]:
    """pairs of (industry, where). Return industries that appear more than once."""
    seen: dict[str, list[str]] = {}
    label: dict[str, str] = {}
    for industry, where in pairs:
        key = industry.strip().lower()
        if not key:
            continue
        seen.setdefault(key, []).append(where)
        label.setdefault(key, industry.strip())
    return [(label[k], v) for k, v in seen.items() if len(v) > 1]


def check_industries(root: Path, file_industries: list[tuple[str, str]]) -> list[Problem]:
    """Every case study must target a different industry or problem."""
    problems: list[Problem] = []
    for industry, where in _duplicates(file_industries):
        problems.append(Problem(Path("case-studies"),
                                f"industry `{industry}` is used by {', '.join(where)}; each case study must target a different industry or problem"))
    readme = root / "README.md"
    if readme.exists():
        column = None
        rows: list[tuple[str, str]] = []
        for line in readme.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|"):
                column = None
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if any(c.lower() == "industry" for c in cells):
                column = next(i for i, c in enumerate(cells) if c.lower() == "industry")
                continue
            if column is not None and cells and cells[0].isdigit() and len(cells) > column:
                rows.append((cells[column], f"catalog row {cells[0]}"))
        for industry, where in _duplicates(rows):
            problems.append(Problem(Path("README.md"),
                                    f"industry `{industry}` appears in {', '.join(where)}; each case study must target a different industry or problem"))
    return problems


def check_repo(root: Path) -> list[Problem]:
    root = root.resolve()
    problems: list[Problem] = []
    slug_cache: dict[Path, set[str]] = {}
    studies: list[tuple[Path, str]] = []
    file_industries: list[tuple[str, str]] = []
    for path in iter_markdown(root):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root)
        for pattern, label in FORBIDDEN_SYNTAX:
            if pattern.search(strip_code(text)):
                problems.append(Problem(rel, f"site-only syntax found: {label}"))
        problems += [Problem(rel, p.message) for p in check_links(path, text, slug_cache)]
        if len(rel.parts) == 2 and rel.parts[0] == "case-studies":
            problems += [Problem(rel, p.message) for p in check_case_study(path, text)]
            meta, _ = split_front_matter(text)
            studies.append((rel, (meta or {}).get("status", "")))
            file_industries.append(((meta or {}).get("industry", ""), rel.name))
    problems += check_catalog(root, studies)
    problems += check_industries(root, file_industries)
    return problems


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    problems = check_repo(root)
    for problem in problems:
        print(problem)
    count = len(list((root / "case-studies").glob("*.md"))) if (root / "case-studies").exists() else 0
    if problems:
        print(f"\n{len(problems)} problem(s) found.")
        return 1
    print(f"OK: {count} case studies checked, no problems found.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
