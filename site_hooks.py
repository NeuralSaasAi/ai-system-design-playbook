"""MkDocs hooks that let the same markdown work on GitHub and on the website.
Nothing in the case studies needs to change for the site. This file:
1. Builds the navigation from the README catalog table, grouped by each case study's `category`,
   so there's no second list to maintain.
2. Rewrites links to non-page files (code, LICENSE, CITATION.cff) to their GitHub URLs, and links
   to the AI Engineering Playbook on GitHub to its website.
3. Lets markdown inside <details> render on the site, as it does on GitHub.
4. Adds a level / industry / status / last-reviewed line under each case study's title, from its
   front matter, with a visible "Draft" label for drafts.
5. Uses the home template for the root README.
6. Uses each case study's last_reviewed date as its sitemap <lastmod>. Other pages use the date
   of their last git commit.
7. Builds a unique meta description for every page.
8. Writes robots.txt, a web app manifest, and llms.txt (a plain index for AI assistants and search).
"""
from __future__ import annotations

import datetime as dt
import json
import posixpath
import re
import subprocess
from pathlib import Path

import yaml

REPO = "https://github.com/NeuralSaasAi/ai-system-design-playbook"
ENGINEERING_REPO = "https://github.com/NeuralSaasAi/ai-engineering-playbook"
ENGINEERING_SITE = "https://ai-engineering.neuralsaasai.com"
ROOT = Path(__file__).resolve().parent

# A catalog row: | 1 | [Title](case-studies/01-x.md) | Industry | Problem | Patterns | Status |
CATALOG_ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*\[([^\]]+)\]\((case-studies/[^)\s]+\.md)\)\s*\|(.*)$", re.M)
LINK_TARGET = re.compile(r"\]\(([^)\s]+)\)")  # the (...) part of any markdown link or image
H1 = re.compile(r"^#\s+(.+?)\s*$", re.M)
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
ENGINEERING_LINK = re.compile(re.escape(ENGINEERING_REPO) + r"(?:/(?:blob|tree)/main/([^)\s#]*))?(#[^)\s]*)?(?=[)\s])")

# What a visitor sees as the page name for the "Case studies" level of the breadcrumb.
CASE_STUDIES_LABEL = "Case studies"

_CATALOG: list[dict] = []  # one dict per case study, in README order
_NAV = {}  # the site navigation, kept for llms.txt


def _front_matter(path: Path) -> dict:
    m = FRONT_MATTER.match(path.read_text(encoding="utf-8"))
    return yaml.safe_load(m.group(1)) if m else {}


def _as_date(value) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _read_catalog() -> list[dict]:
    """Case studies in README catalog order, with their front matter and catalog columns."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    entries = []
    for number, title, src, rest in CATALOG_ROW.findall(readme):
        cells = [c.strip() for c in rest.split("|")]
        meta = _front_matter(ROOT / src)
        entries.append(
            {
                "number": int(number),
                "src": src,
                "title": meta.get("title") or title,
                "meta": meta,
                "problem": cells[1] if len(cells) > 1 else "",
            }
        )
    return entries


def _plain(text: str) -> str:
    """Strip markdown links, emphasis and code marks from a short string."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[*`_]", "", text).strip()


def _truncate(text: str, limit: int = 160) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


def _git_date(path: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            cwd=ROOT, capture_output=True, text=True, timeout=10, check=False,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return out or None


def on_config(config, **kwargs):
    _CATALOG[:] = _read_catalog()
    groups: dict[str, list] = {}
    for entry in _CATALOG:  # categories appear in the order the README first lists them
        category = entry["meta"].get("category", "Other")
        groups.setdefault(category, []).append({entry["title"]: entry["src"]})
    config["nav"] = [
        {"Home": "README.md"},
        {"Design method": "DESIGN-METHOD.md"},
        {CASE_STUDIES_LABEL: [{category: items} for category, items in groups.items()]},
        {"Why this exists": "WHY-THIS-EXISTS.md"},
        {
            "About": [
                {"Contributing": "CONTRIBUTING.md"},
                {"Style guide": "STYLE.md"},
                {"Code of conduct": "CODE_OF_CONDUCT.md"},
            ]
        },
    ]
    return config


def _rewrite_links(markdown: str, page_src: str, docs_dir: Path, files) -> str:
    """Point links at files that aren't pages to GitHub, and Part 1 links to its website."""

    def engineering(m: re.Match) -> str:
        path, anchor = m.group(1) or "", m.group(2) or ""
        if path.endswith("README.md"):
            path = path[: -len("README.md")]
        elif path.endswith(".md"):
            path = path[: -len(".md")] + "/"
        return f"{ENGINEERING_SITE}/{path}{anchor}"

    markdown = ENGINEERING_LINK.sub(engineering, markdown)
    page_dir = posixpath.dirname(page_src)

    def repl(m: re.Match) -> str:
        target = m.group(1)
        if re.match(r"^[a-z][a-z0-9+.-]*:|^#", target, re.I):
            return m.group(0)
        path, _, anchor = target.partition("#")
        rel = posixpath.normpath(posixpath.join(page_dir, path))
        full = docs_dir / rel
        page_file = files.get_file_from_path(rel) if path.endswith(".md") else None
        if page_file is not None and not page_file.inclusion.is_excluded():
            return m.group(0)  # a page on the site: MkDocs handles it
        if full.exists():
            kind = "tree" if full.is_dir() else "blob"
            url = f"{REPO}/{kind}/main/{rel}" + (f"#{anchor}" if anchor else "")
            return f"]({url})"
        return m.group(0)

    return LINK_TARGET.sub(repl, markdown)


def _first_paragraph(markdown: str) -> str:
    """First plain paragraph after the title, for pages that have no front matter."""
    body = FRONT_MATTER.sub("", markdown)
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block or block[0] in "#>|`-<[!" or block[0].isdigit():
            continue
        return _truncate(_plain(" ".join(block.split())))
    return ""


def _meta_line(meta: dict) -> str:
    level = str(meta.get("level", ""))
    status = str(meta.get("status", ""))
    reviewed = _as_date(meta.get("last_reviewed"))
    parts = []
    if level:
        parts.append(f'<span class="pb-pill level level-{level}">{level.title()}</span>')
    if meta.get("industry"):
        parts.append(f'<span class="pb-industry">{meta["industry"]}</span>')
    if status == "draft":
        parts.append('<span class="pb-pill status status-draft" title="This case study is still being reviewed">Draft</span>')
    elif status:
        parts.append(f'<span class="pb-pill status status-{status}">{status.title()}</span>')
    if reviewed:
        parts.append(f"Last reviewed {reviewed:%-d %B %Y}")
    return '<p class="note-meta">' + " · ".join(parts) + "</p>"


def on_page_markdown(markdown, page, config, files, **kwargs):
    src = page.file.src_uri
    docs_dir = Path(config["docs_dir"])
    entry = next((e for e in _CATALOG if e["src"] == src), None)

    if src == "README.md":
        page.meta["template"] = "home.html"
        page.meta["hide"] = ["navigation", "toc"]
        page.meta.setdefault("description", config["site_description"])
        dates = [d for e in _CATALOG if (d := _as_date(e["meta"].get("last_reviewed")))]
        if dates:
            page.update_date = max(dates).isoformat()
    elif entry:
        meta = entry["meta"]
        page.meta["number"] = entry["number"]
        page.meta["problem"] = entry["problem"]
        problem = _plain(entry["problem"]).rstrip(".")
        page.meta["description"] = (
            f"{problem}. AI system design case study: architecture, scale, cost, failure modes "
            "and a 45-minute interview plan."
        )
        if reviewed := _as_date(meta.get("last_reviewed")):
            page.update_date = reviewed.isoformat()  # sitemap <lastmod>
    else:
        # Pages without front matter use their own H1 for <title>
        if h1 := H1.search(markdown):
            page.meta.setdefault("title", _plain(h1.group(1)))
        page.meta.setdefault("description", _first_paragraph(markdown))
        if date := _git_date(Path(page.file.abs_src_path)):
            page.update_date = date

    markdown = _rewrite_links(markdown, src, docs_dir, files)
    markdown = re.sub(r"<details>", '<details markdown="1">', markdown)
    if entry:
        markdown = H1.sub(lambda m: f"{m.group(0)}\n\n{_meta_line(entry['meta'])}\n", markdown, count=1)
    return markdown


def on_nav(nav, config, files, **kwargs):
    _NAV["nav"] = nav
    return nav


def on_post_build(config, **kwargs):
    site_dir = Path(config["site_dir"])
    site_url = (config.get("site_url") or "").rstrip("/")
    robots = "User-agent: *\nAllow: /\n"
    if site_url:
        robots += f"Sitemap: {site_url}/sitemap.xml\n"
    (site_dir / "robots.txt").write_text(robots, encoding="utf-8")

    manifest = {
        "name": config["site_name"],
        "short_name": "AI System Design",
        "description": config["site_description"],
        "start_url": "./",
        "display": "standalone",
        "background_color": "#080A09",
        "theme_color": "#0B6E7A",
        "icons": [
            {"src": "assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "assets/logo-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }
    (site_dir / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    lines = [f"# {config['site_name']}", "", f"> {config['site_description'].strip()}", ""]
    lines += [
        "Free, open learning resource by NeuralSaas AI. Content CC BY-SA 4.0.",
        f"Source: {REPO}",
        f"Part 1, the concepts these case studies assume: {ENGINEERING_SITE}/",
    ]
    by_src = {e["src"]: e for e in _CATALOG}
    current = None
    for page in _NAV["nav"].pages:  # navigation order
        entry = by_src.get(page.file.src_uri)
        if entry:
            section = f"{CASE_STUDIES_LABEL}: {entry['meta'].get('category', 'Other')}"
        elif page.is_homepage or page.file.src_uri in ("DESIGN-METHOD.md", "WHY-THIS-EXISTS.md"):
            section = "Start"
        else:
            section = "About"
        if section != current:
            lines += ["", f"## {section}", ""]
            current = section
        name = page.meta.get("title") or page.title
        detail = f": {_plain(entry['problem'])}" if entry else ""
        lines.append(f"- [{name}]({page.canonical_url}){detail}")
    (site_dir / "llms.txt").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
