"""Build <spec>/explain.html: how an enhanced InChI is made, for chemists.

Usage (from the repo root; RDKit >= 2024 needed):
  INCHI_NEW=/path/to/atropisomers/inchi-1 python tools/explain.py [spec ...]

  spec: enhanced-stereo, allenes, double-bond-ez, atropisomers (default: all)

Each spec has a module tools/explain_<name>.py whose parts() returns the
$fields of <spec>/explain.template.html; tools/explain.css is inlined as
$style. Molfile, InChI and drawing helpers come from tools/build.py.

Every InChI on a page is measured here, never typed in. Standard strings
come from the same binary without -EnhancedStereochemistry.
"""

import html
import importlib
import os
import re
import string
import sys

from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

TOOLS = os.path.dirname(os.path.abspath(__file__))
SPECS = os.path.dirname(TOOLS)

import build  # noqa: E402
from build import REPO_URL, from_smiles, run_inchi, run_cli, draw  # noqa: E402,F401
from comments import snippet, spec_link  # noqa: E402

# Drawings show "&1" as structure editors do, not the comparison table's "and1"
build.COLL_LABEL["RAC"] = "&"

EXE = os.environ.get("INCHI_NEW", "")
ENH = ["-EnhancedStereochemistry"]
ISO_W, ISO_H = 200, 150

# spec folder -> generator module
SPEC_MODULES = {
    "enhanced-stereo": "explain_enhanced",
    "allenes": "explain_allenes",
    "double-bond-ez": "explain_ez",
    "atropisomers": "explain_atropisomers",
}


# ------------------------------------------------------------ measurement

def molblock(mol):
    """V3000 molblock from a molblock, a (CX)SMILES, or a build.py entry
    dict (smiles + wedges/either/coll/rotate, see molecules.py)."""
    if isinstance(mol, dict):
        return from_smiles(dict(title="x", **mol))
    if "M  END" in mol:
        return mol
    return from_smiles(dict(smiles=mol, title="x"))


def inchi(mol, opts=ENH):
    """(InChI, {0-based input atom: canonical number})."""
    return run_inchi(EXE, molblock(mol), opts)


def warning(mol):
    """First warning line of the enhanced run, '' when none."""
    _, log = run_cli(EXE, molblock(mol), ENH)
    return next((l.split(" structure")[0] for l in log if l.startswith("Warning")), "")


def stereo_tail(s):
    """'/t3-,4-/m1/s1' from a full InChI: everything from the first stereo
    layer (/b or /t) on; '' when there is none."""
    m = re.search(r"/[bt]", s)
    return s[m.start():] if m else ""


# ---------------------------------------------------------------- drawing

def picture(mol, numbers=True):
    """Molecule with its collection labels; canonical numbers optional."""
    block = molblock(mol)
    _, canon = run_inchi(EXE, block, ENH)
    return draw(block, canon if numbers else {})


def isomer(smiles):
    """Small unlabelled stereoisomer with CIP annotations (R/S, E/Z)."""
    mol = Chem.MolFromSmiles(smiles)
    rdDepictor.SetPreferCoordGen(True)
    rdDepictor.Compute2DCoords(mol)
    d = rdMolDraw2D.MolDraw2DSVG(ISO_W, ISO_H)
    o = d.drawOptions()
    o.addStereoAnnotation = True
    o.clearBackground = False
    o.annotationFontScale = 0.9
    rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
    d.FinishDrawing()
    svg = d.GetDrawingText()
    return svg[svg.index("<svg"):]


# ------------------------------------------------------------ InChI markup

S_GROUP = re.compile(r"([123])((?:\([\d,]+\))*)")
CLASS = {"1": "abs", "2": "or", "3": "and"}


def mark_s(s):
    """Colour each /s class with its groups: '1(4)3(3)' -> abs '1(4)', and '3(3)'."""
    return S_GROUP.sub(lambda m: f'<span class="c-{CLASS[m.group(1)]}">{m.group(0)}</span>', s)


def mark(tail):
    """Colour the layers of a stereo tail: /b and /t ink, /m abs blue, /s by class."""
    out = []
    for layer in re.findall(r"/[a-z][^/]*", tail):
        body = html.escape(layer)
        if layer.startswith("/m"):
            body = f'<span class="c-abs">{body}</span>'
        elif layer.startswith("/s"):
            body = "/s" + mark_s(html.escape(layer[2:]))
        out.append(f'<span class="layer">{body}</span>')
    return "".join(out)


def label_chip(label):
    kind = {"a": "abs", "o": "or", "&": "and", "n": "none"}[label[0]]
    return f'<span class="chip c-{kind}">{html.escape(label)}</span>'


# ------------------------------------------------------------------- page

def render(spec, parts):
    """Fill <spec>/explain.template.html and write <spec>/explain.html."""
    folder = os.path.join(SPECS, spec)
    template = string.Template(open(os.path.join(folder, "explain.template.html")).read())
    style = open(os.path.join(TOOLS, "explain.css")).read()
    page = template.substitute(parts, style=style, spec_url=f"{REPO_URL}/{spec}/SPEC.md")
    if spec_link(spec):
        page = page.replace("</footer>", f'<p>General discussion of this extension: '
                            f'<a href="{spec_link(spec)}">on GitHub</a>.</p>\n</footer>')
    page = page.replace("</body>", snippet(spec) + "</body>")
    open(os.path.join(folder, "explain.html"), "w").write(page)


def main(specs):
    assert EXE, "set INCHI_NEW to an inchi-1 built from branch 'atropisomers'"
    for spec in specs or SPEC_MODULES:
        render(spec, importlib.import_module(SPEC_MODULES[spec]).parts())
        print("wrote", os.path.join(spec, "explain.html"))


if __name__ == "__main__":
    main(sys.argv[1:])
