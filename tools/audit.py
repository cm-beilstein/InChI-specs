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
    spec_md = open(os.path.join(folder, "SPEC.md")).read() if has("SPEC.md") else ""
    datasets_md = (open(os.path.join(folder, "datasets", "DATASETS.md")).read()
                   if has("datasets", "DATASETS.md") else "")

    # Files in datasets/ that DATASETS.md does not mention by name
    unlisted = [f for f in sorted(os.listdir(os.path.join(folder, "datasets")))
                if f != "DATASETS.md" and f not in datasets_md] if has("datasets") else []
    explain = open(os.path.join(TOOLS, "explain.py")).read()
    landing = open(os.path.join(ROOT, "index.html")).read()
    readme = open(os.path.join(ROOT, "README.md")).read()

    checks = [
        ("site.json entry", spec is not None),
        ("tracking: issue or PR", bool(spec and (spec["tracking"].get("issues")
                                                 or spec["tracking"].get("prs")))),
        ("general discussion", key in giscus.get("specDiscussions", {})),
        ("specification SPEC.md", has("SPEC.md")),
        ("kick-off documents docs/<topic>/", bool(spec and spec.get("docs")) and
         os.path.isdir(os.path.join(ROOT, "docs", spec.get("docs", "-")))),
        ("readiness in SPEC.md header", "| **Readiness** |" in spec_md),
        ("datasets/DATASETS.md", bool(datasets_md)),
        ("every dataset file listed in DATASETS.md" + (f" ({', '.join(unlisted)})" if unlisted else ""),
         not unlisted),
        ("DATASETS.md linked from SPEC.md", "datasets/DATASETS.md" in spec_md),
        ("explanation template", has("explain.template.html")),
        ("explanation module", f'"{key}":' in explain),
        ("explanation page", has("explain.html")),
        ("explanation: 'How to use it' section",
         'id="use"' in (open(os.path.join(folder, "explain.template.html")).read()
                        if has("explain.template.html") else "")),
        ("example table in molecules.py", re.search(rf'\("{key}", ""\)', molecules) is not None),
        ("examples page", has("examples", "index.html")),
        ("landing row", f'data-term="{key} · general"' in landing),
        ("README row links the spec", f"| [{key}]({key}/SPEC.md) |" in readme),
    ]

    # A proposal has no new InChI yet, so nothing to compare old against
    proposed = bool(spec and spec["status"] == "proposed")
    not_applicable = {"example table in molecules.py", "examples page"} if proposed else set()
    checks = [(name, ok if name not in not_applicable else None) for name, ok in checks]

    for name, ok in checks:
        print(f"{'n/a' if ok is None else 'ok' if ok else 'MISSING':8} {name}")
    if spec:
        for side in ("old", "new"):
            if side in spec:
                run = spec[side]
                print(f"{'':8} {side}: {run['label']} {run['rev']} {' '.join(run['options'])}")
    return 0 if all(ok is not False for _, ok in checks) else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
