"""Are the InChI strings in the workflow diagrams measured?

Usage (from the repo root):
  python tools/workflow_check.py [table ...]

The diagram sources tools/workflow/<table>.json are typed by hand. Every
full InChI, InChIKey and layer fragment (e.g. /t11-/m0/s1) in them must
also appear in the feature's measured pages: its examples SDF files or its
explanation page. Prints what is not found and exits 1, so tools/rebuild.py
fails instead of publishing a stale diagram.
"""

import glob
import html
import json
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
from molecules import SPEC_OF  # noqa: E402

INCHI = re.compile(r"InChI=1[A-Z]*/[^\s\"'<,]*")
KEY = re.compile(r"\b[A-Z]{14}-[A-Z]{10}-[A-Z]\b")
LAYERS = re.compile(r"(?:/[tbms][^\s\"',;<)·]*(?:\([^\s\"']*\))?)+")


def strings(text):
    """InChIs, InChIKeys and layer fragments (longer than '/m0') in 'text'."""
    found = INCHI.findall(text) + KEY.findall(text)
    rest = KEY.sub(" ", INCHI.sub(" ", text))
    return set(found + [s for s in LAYERS.findall(rest) if len(s) > 3])


def measured(key):
    """Text of the feature's measured pages: examples data and explanation."""
    text = "".join(open(f).read() for f in glob.glob(os.path.join(ROOT, key, "examples", "*.sdf")))
    path = os.path.join(ROOT, key, "explain.html")
    if os.path.exists(path):
        text += html.unescape(re.sub(r"<[^>]+>", "", open(path).read()))
    return text


def check(table):
    """Strings of tools/workflow/<table>.json not found in measured pages."""
    source = json.load(open(os.path.join(TOOLS, "workflow", table + ".json")))
    text = json.dumps(source, ensure_ascii=False)
    pages = measured(SPEC_OF[table][0])
    return sorted(s for s in strings(text) if s not in pages)


def main(tables):
    folder = os.path.join(TOOLS, "workflow")
    tables = tables or sorted(f[:-len(".json")] for f in os.listdir(folder) if f.endswith(".json"))
    bad = 0
    for table in tables:
        missing = check(table)
        bad += len(missing)
        for s in missing:
            print(f"{table}: not measured: {s}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
