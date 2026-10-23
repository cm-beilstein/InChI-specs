"""What exists for one feature on the site, and what is missing.

Usage (from the repo root):
  python tools/audit.py <key>

  key  feature folder name, e.g. enhanced-stereo, inchi-versioning

Prints one line per document, 'ok' or 'MISSING', and exits 1 if anything
is missing. Checks files and config only; whether the content is current
is for the reader (see skills/inchi-feature-update).
"""

import json
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)


def main(key):
    site = json.load(open(os.path.join(TOOLS, "site.json")))
    giscus = json.load(open(os.path.join(TOOLS, "giscus.json")))
    spec = next((s for s in site["specs"] if s["key"] == key), None)
    folder = os.path.join(ROOT, key)
    has = lambda *p: os.path.exists(os.path.join(folder, *p))

    molecules = open(os.path.join(TOOLS, "molecules.py")).read()
    explain = open(os.path.join(TOOLS, "explain.py")).read()
    landing = open(os.path.join(ROOT, "index.html")).read()

    checks = [
        ("site.json entry", spec is not None),
        ("tracking: issue or PR", bool(spec and (spec["tracking"].get("issues")
                                                 or spec["tracking"].get("prs")))),
        ("general discussion", key in giscus.get("specDiscussions", {})),
        ("specification SPEC.md", has("SPEC.md")),
        ("explanation template", has("explain.template.html")),
        ("explanation module", f'"{key}":' in explain),
        ("explanation page", has("explain.html")),
        ("example table in molecules.py", re.search(rf'\("{key}", ""\)', molecules) is not None),
        ("examples page", has("examples", "index.html")),
        ("landing row", f'data-term="{key} · general"' in landing),
    ]

    for name, ok in checks:
        print(f"{'ok' if ok else 'MISSING':8} {name}")
    if spec:
        for side in ("old", "new"):
            if side in spec:
                run = spec[side]
                print(f"{'':8} {side}: {run['label']} {run['rev']} {' '.join(run['options'])}")
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
