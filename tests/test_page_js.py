"""Run the converter tab's JavaScript outside OrcaSlicer.

Extracts the page from the plugin and runs tests/converter_harness.js under node.

    python3 tests/test_page_js.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def page_ids(page):
    """Every element id the markup actually defines."""
    return sorted(set(re.findall(r'id="([A-Za-z0-9_-]+)"', page)))


def missing_elements(page, js):
    """Ids the script looks up that the markup never defines.

    A null element write throws and aborts the whole inline script, so this is
    the failure the DOM stub exists to catch — and it has to come from the
    markup, or a stale stub would hide exactly the bug it guards.
    """
    looked_up = set(re.findall(r'\$\("#?([A-Za-z0-9_-]+)"\)', js))
    looked_up |= set(re.findall(r'getElementById\("([A-Za-z0-9_-]+)"\)', js))
    return sorted(looked_up - set(page_ids(page)))


def token_panel_starts_closed(page):
    """The token settings must be a <details> that does not start open.

    A credentials field sitting open reads as a requirement, and most of what this
    plugin does needs no token at all. The harness cannot check this after the
    fact, because delivering any state message legitimately opens the panel.
    """
    match = re.search(r'<details[^>]*id="tokenPanel"[^>]*>', page)
    return bool(match) and " open" not in match.group(0)


def extract_converter_page(source_path):
    """The converter tab, which is a plain (non-raw) string."""
    text = open(source_path, encoding="utf-8").read()
    match = re.search(r'^MAKERWORLD_PAGE = """(.*?)^"""$', text, re.S | re.M)
    if not match:
        raise SystemExit("could not find the MAKERWORLD_PAGE block in the plugin")
    page = match.group(1)
    start = page.index("<script>") + len("<script>")
    end = page.rindex("</script>")
    return page, page[start:end]


def main():
    if shutil.which("node") is None:
        print("node is not installed — skipping the page checks")
        return 0

    source = os.path.join(ROOT, "3mf-converter_any.py")
    page, js = extract_converter_page(source)

    work = tempfile.mkdtemp(prefix="3mfc-page-")
    try:
        js_path = os.path.join(work, "converter.js")
        with open(js_path, "w", encoding="utf-8") as fh:
            fh.write(js)
        ids_path = os.path.join(work, "converter-ids.json")
        with open(ids_path, "w", encoding="utf-8") as fh:
            json.dump(page_ids(page), fh)

        print("Converter tab markup")
        missing = missing_elements(page, js)
        checks = [
            ("the page has exactly one script block",
             page.count("<script>") == 1 and page.count("</script>") == 1),
            ("the $-helper tolerates both 'id' and '#id' spellings",
             'charAt(0) === "#"' in js),
            ("every showBanner call sets display, not just text",
             'banner.style.display = text ? "block" : "none"' in js),
            ("no nested template literals (a parse error in the webview)",
             not re.search(r"\$\{[^}]*`", js)),
            ("no optional-chaining method calls inside a template literal",
             not re.search(r"\$\{[^}]*\?\.\(", js)),
            ("the token itself is never sent back to the page",
             "token_set" in js and not re.search(r"message\.token\b(?!_set)", js)),
            ("the fallback names a menu item that exists",
             "Open Project" in js),
            ("the page asks for its state on load rather than waiting for a timer",
             'post({ type: "hello" })' in js),
            ("every element the script looks up is defined in the markup",
             not missing, str(missing)),
            ("the token settings sit behind a disclosure that starts closed",
             token_panel_starts_closed(page)),
            ("the token panel explains how to get a token",
             "How do I get a BambuCloud token?" in page
             and "F12" in page and "Cookies" in page
             and "copy its <b>Value</b>" in page
             and "Treat it like a password" in page),
            ("a local .3mf can be dropped or picked, not only typed",
             'id="drop"' in page and 'id="browse"' in page
             and 'id="file"' in page and 'type="file"' in page and '.3mf"' in page),
            ("the typed-path box is out of the flow, behind a fallback link",
             'id="pathRow"' in page and ' hidden' in
             re.search(r'<div[^>]*id="pathRow"[^>]*>', page).group(0)
             and 'id="showPath"' in page and 'id="convertPath"' in page),
        ]
        failed = 0
        for name, ok, *rest in checks:
            detail = rest[0] if rest and not ok else ""
            print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
                  + (f" — {detail}" if detail else ""))
            failed += 0 if ok else 1

        result = subprocess.run(["node", os.path.join(HERE, "converter_harness.js"),
                                 js_path, ids_path],
                                capture_output=True, text=True)
        print(result.stdout)
        if result.stderr.strip():
            print(result.stderr.strip())
        failed += 0 if result.returncode == 0 else 1
        return 1 if failed else 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
