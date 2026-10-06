#!/usr/bin/env python3
"""Build the Hugo site twice and check the generated HTML.

Builds into $TMPDIR/agr-check/root (normal baseURL) and
$TMPDIR/agr-check/sub (GitHub Pages subpath /agrammon-website/), then runs
structural checks grouped by feature.

Usage:  python3 -I scripts/check_site.py [GROUP ...]   (no GROUP = all)
Exit status 0 when every selected check passes.
"""
import os
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get("TMPDIR") or "/tmp") / "agr-check"
SUB_BASE = "https://oposs.github.io/agrammon-website/"
SUBPATH = "/agrammon-website/"
LANGS = ("de", "en", "fr")
MOCKUPS = ("theme2", "theme3", "designs")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "source", "track", "wbr"}


# ── tiny DOM ────────────────────────────────────────────────────────────
class Node:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = {k: (v or "") for k, v in (attrs or [])}
        self.parent = parent
        self.children = []  # Node or str

    @property
    def classes(self):
        return self.attrs.get("class", "").split()

    def text(self):
        parts = [c if isinstance(c, str) else c.text() for c in self.children]
        return re.sub(r"\s+", " ", " ".join(parts)).strip()

    def find_all(self, tag=None, cls=None, attrs=None):
        found = []
        for c in self.children:
            if isinstance(c, str):
                continue
            if ((tag is None or c.tag == tag)
                    and (cls is None or cls in c.classes)
                    and all(c.attrs.get(k) == v for k, v in (attrs or {}).items())):
                found.append(c)
            found.extend(c.find_all(tag, cls, attrs))
        return found

    def find(self, tag=None, cls=None, attrs=None):
        hits = self.find_all(tag, cls, attrs)
        return hits[0] if hits else None


class _Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def parse(path):
    builder = _Builder()
    builder.feed(Path(path).read_text(encoding="utf-8"))
    return builder.root


# ── site helpers ────────────────────────────────────────────────────────
def page_file(site, href):
    """Built file for a site-internal href (with or without the subpath)."""
    path = unquote(href.split("#")[0].split("?")[0])
    if path.startswith(SUBPATH):
        path = "/" + path[len(SUBPATH):]
    target = site / path.lstrip("/")
    if path.endswith("/") or not target.suffix:
        target = target / "index.html"
    return target


def all_html(site):
    """Every real HTML page (no mockups, no alias redirects)."""
    for f in sorted(site.rglob("*.html")):
        if f.relative_to(site).parts[0] in MOCKUPS:
            continue
        if 'http-equiv="refresh"' in f.read_text(encoding="utf-8"):
            continue
        yield f


def content_pages(site):
    """(lang, url, file) for every index.html page of every language."""
    for f in all_html(site):
        parts = f.relative_to(site).parts
        if parts[0] in LANGS and f.name == "index.html":
            yield parts[0], "/" + "/".join(parts[:-1]) + "/", f


def uikit_markup(node):
    """True if node or a descendant carries a UIkit class or attribute."""
    for n in [node] + node.find_all():
        if any(c.startswith("uk-") for c in n.classes):
            return True
        if any(k.startswith("uk-") for k in n.attrs):
            return True
    return False


def title_of(doc):
    """Page title without the ' | Agrammon' suffix."""
    return doc.find("title").text().rsplit(" | ", 1)[0]


def build(dest, base_url=None):
    cmd = ["mise", "exec", "--", "hugo", "--cleanDestinationDir", "-d", str(dest)]
    if base_url:
        cmd += ["--baseURL", base_url]
    run = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    log = run.stdout + run.stderr
    if run.returncode != 0:
        sys.exit("hugo build failed:\n" + log)
    return log


# ── check registry ──────────────────────────────────────────────────────
CHECKS = []


def check(group):
    def register(fn):
        CHECKS.append((group, fn))
        return fn
    return register


class Ctx:
    pass


# ── baseline ────────────────────────────────────────────────────────────
@check("baseline")
def build_has_no_warnings(ctx):
    return [line for line in ctx.log.splitlines()
            if line.startswith(("WARN", "ERROR"))]


@check("baseline")
def language_homes_exist(ctx):
    return [f"missing /{lang}/" for lang in LANGS
            if not (ctx.root / lang / "index.html").exists()]


# ── foundation (Task 2) ─────────────────────────────────────────────────
@check("foundation")
def no_google_fonts(ctx):
    errs = []
    files = list(all_html(ctx.root)) + [
        f for f in ctx.root.rglob("*.css")
        if f.relative_to(ctx.root).parts[0] not in MOCKUPS]
    for f in files:
        if re.search(r"fonts\.(googleapis|gstatic)\.com", f.read_text(encoding="utf-8")):
            errs.append(f"{f.relative_to(ctx.root)} references Google Fonts")
    return errs


@check("foundation")
def single_fingerprinted_stylesheet(ctx):
    errs = []
    for site in (ctx.root, ctx.sub):
        for f in all_html(site):
            links = [n for n in parse(f).find_all("link")
                     if n.attrs.get("rel") == "stylesheet"]
            rel = f.relative_to(site)
            if len(links) != 1:
                errs.append(f"{site.name}/{rel}: {len(links)} stylesheets")
                continue
            href = links[0].attrs.get("href", "")
            if (not re.search(r"/css/site(\.min)?\.[0-9a-f]{64}\.css$", href)
                    or not page_file(site, href).exists()):
                errs.append(f"{site.name}/{rel}: bad stylesheet {href}")
    return errs


@check("foundation")
def fonts_self_hosted_and_resolve(ctx):
    errs = []
    for site in (ctx.root, ctx.sub):
        css = sorted(site.glob("css/site.*.css"))
        if not css:
            errs.append(f"{site.name}: no css/site.*.css")
            continue
        urls = re.findall(r"url\(([^)]+)\)", css[0].read_text(encoding="utf-8"))
        fonts = [u.strip("'\"") for u in urls if ".woff2" in u]
        if len(fonts) != 18:
            errs.append(f"{site.name}: {len(fonts)} woff2 urls, want 18")
        for u in fonts:
            if u.startswith(("http:", "https:", "/")):
                errs.append(f"{site.name}: font url not relative: {u}")
            elif not (css[0].parent / u).resolve().exists():
                errs.append(f"{site.name}: font missing: {u}")
    return errs


@check("foundation")
def no_uikit_sass_or_dark_mode_assets(ctx):
    errs = []
    for f in all_html(ctx.root):
        text = f.read_text(encoding="utf-8")
        for needle in ("uikit", "theme.js", "localStorage"):
            if needle in text:
                errs.append(f"{f.relative_to(ctx.root)} contains {needle!r}")
    for path in ("assets/uikit", "assets/scss", "assets/js/theme.js"):
        if (ROOT / path).exists():
            errs.append(f"{path} still exists")
    if "sass" in (ROOT / "mise.toml").read_text(encoding="utf-8"):
        errs.append("mise.toml still pins sass")
    return errs


# ── main ────────────────────────────────────────────────────────────────
def main(argv):
    wanted = set(argv)
    unknown = wanted - {group for group, _ in CHECKS}
    if unknown:
        known = sorted({group for group, _ in CHECKS})
        sys.exit(f"unknown group(s) {sorted(unknown)}; known: {known}")
    ctx = Ctx()
    ctx.root, ctx.sub = OUT / "root", OUT / "sub"
    ctx.log = build(ctx.root)
    build(ctx.sub, SUB_BASE)
    failing = 0
    for group, fn in CHECKS:
        if wanted and group not in wanted:
            continue
        errors = fn(ctx)
        print(f"{'FAIL' if errors else 'ok  '} {group}:{fn.__name__}")
        for err in errors[:20]:
            print(f"       {err}")
        if len(errors) > 20:
            print(f"       ... {len(errors) - 20} more")
        failing += bool(errors)
    print(f"\n{failing} failing check(s)" if failing else "\nall checks passed")
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
