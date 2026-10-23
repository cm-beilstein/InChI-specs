"""Is a feature documented: Doxygen comments in the code, and user docs?

Usage (from the repo root):
  python tools/doc_check.py <key> [--inchi ../InChI] [--option NAME ...]

Compares the feature's 'old' and 'new' revisions from tools/site.json:

1. Doxygen: every C function the change adds or modifies, and whether a
   '/** ... */' (or '/*! ... */') block sits right above its definition.
   New functions without one are MISSING; changed old functions without one
   are listed as 'legacy' (worth a comment, not a blocker).
2. User documentation: for each --option (as typed after '-', e.g.
   EnhancedStereochemistry), whether the 'new' revision mentions it in the
   command-line help, README.md, CHANGELOG, User Guide and API Reference.

Exits 1 if anything is MISSING. Reads git objects only; the InChI checkout
is not touched.
"""

import argparse
import json
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))

DEFINITION = re.compile(r"^(?!static\s+const|typedef|struct|enum|#)[A-Za-z_][\w\s\*]*?\b(\w+)\s*\(")

# Where users look for an option, in the InChI repo
USER_DOCS = [
    ("command-line help", "INCHI-1-SRC/INCHI_BASE/src/ichiparm.c", "inchi_ios_print_nodisplay"),
    ("README.md", "README.md", None),
    ("CHANGELOG", "INCHI-1-DOC/CHANGELOG.md", None),
    ("User Guide", "INCHI-1-DOC/UserGuide/InChI_UserGuide.md", None),
    ("API Reference", "INCHI-1-DOC/APIReference/InChI_API_Reference.md", None),
]


def git(inchi, *args):
    return subprocess.run(["git", "-C", inchi, *args], check=True, capture_output=True,
                          text=True).stdout


def show(inchi, rev, path):
    try:
        return git(inchi, "show", f"{rev}:{path}")
    except subprocess.CalledProcessError:
        return ""


def functions(source):
    """{name: (first line, last line, documented)} of top-level definitions
    (1-based lines; a definition ends at the next '}' in column 0)."""
    lines = source.splitlines()
    found = {}
    i = 0
    while i < len(lines):
        m = DEFINITION.match(lines[i])
        if not m or lines[i].rstrip().endswith(";"):
            i += 1
            continue

        # Must open a body before a ';' (else it is a prototype)
        j = i
        while j < len(lines) and "{" not in lines[j] and ";" not in lines[j]:
            j += 1
        if j >= len(lines) or ";" in lines[j].split("{")[0]:
            i += 1
            continue
        end = j
        while end < len(lines) and not lines[end].startswith("}"):
            end += 1

        # Doc block: the nearest non-blank line above ends a /** or /*! comment
        k = i - 1
        while k >= 0 and not lines[k].strip():
            k -= 1
        documented = False
        if k >= 0 and lines[k].strip().endswith("*/"):
            while k >= 0 and "/*" not in lines[k]:
                k -= 1
            documented = k >= 0 and re.search(r"/\*[*!]", lines[k]) is not None

        found[m.group(1)] = (i + 1, end + 1, documented)
        i = end + 1
    return found


def changed_lines(inchi, old, new, path):
    """Line numbers in 'new' touched by the diff old..new."""
    out = git(inchi, "diff", "-U0", old, new, "--", path)
    touched = set()
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", out, re.M):
        start, count = int(m.group(1)), int(m.group(2) or 1)
        touched.update(range(start, start + max(count, 1)))
    return touched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("key")
    ap.add_argument("--inchi", default=os.path.join(os.path.dirname(os.path.dirname(TOOLS)), "InChI"))
    ap.add_argument("--option", action="append", default=[])
    args = ap.parse_args()

    site = json.load(open(os.path.join(TOOLS, "site.json")))
    spec = next(s for s in site["specs"] if s["key"] == args.key)
    if "old" not in spec:
        sys.exit(f"{args.key}: no 'old' revision (proposal?), nothing to compare")
    old, new = spec["old"]["rev"], spec["new"]["rev"]
    missing = False

    print(f"Doxygen, functions added or changed {old}..{new}:")
    paths = git(args.inchi, "diff", "--name-only", old, new, "--",
                "INCHI-1-SRC/*.c", "INCHI-1-SRC/*.h").split()
    for path in paths:
        before = functions(show(args.inchi, old, path))
        after = functions(show(args.inchi, new, path))
        touched = changed_lines(args.inchi, old, new, path)
        for name, (first, last, documented) in sorted(after.items(), key=lambda f: f[1][0]):
            if not touched & set(range(first, last + 1)):
                continue
            new_function = name not in before
            status = "ok" if documented else "MISSING" if new_function else "legacy"
            missing |= status == "MISSING"
            print(f"  {status:8} {'new' if new_function else 'changed':8} {path}:{first} {name}")

    for option in args.option:
        print(f"User documentation of -{option} at {new}:")
        for label, path, marker in USER_DOCS:
            text = show(args.inchi, new, path)
            hits = [l for l in text.splitlines() if option in l and (marker is None or marker in l)]
            missing |= not hits
            print(f"  {'ok' if hits else 'MISSING':8} {label} ({path})")

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
