"""Build enhanced-stereo/explain.html: how an enhanced-stereo InChI is made,
for chemists, from enhanced-stereo/explain.template.html.

Usage (from the repo root; RDKit >= 2024 needed):
  INCHI_NEW=/path/to/atropisomers/inchi-1 python tools/explain.py

Molfile, InChI and drawing helpers come from the sibling checkout
../InChI-enh-Stereo (tools/build.py).

Every InChI on the page is measured here, never typed in. Standard
strings come from the same binary without -EnhancedStereochemistry.
"""

import html
import os
import re
import string
import sys

from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

SPECS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(SPECS), "InChI-enh-Stereo", "tools"))

import build  # noqa: E402
from build import from_smiles, run_inchi, run_cli, draw

# Drawings show "&1" as structure editors do, not the comparison table's "and1"
build.COLL_LABEL["RAC"] = "&"

EXE = os.environ.get("INCHI_NEW", "")
ENH = ["-EnhancedStereochemistry"]
ISO_W, ISO_H = 200, 150

# 3-chlorobutan-2-ol, CH3-C2H(OH)-C3H(Cl)-CH3; SMILES atoms 1 = C2, 3 = C3
ISOMERS = {
    "RR": "C[C@@H](O)[C@@H](C)Cl",
    "SS": "C[C@H](O)[C@H](C)Cl",
    "RS": "C[C@@H](O)[C@H](C)Cl",
    "SR": "C[C@H](O)[C@@H](C)Cl",
}
ISO_NAME = {"RR": "(2R,3R)", "SS": "(2S,3S)", "RS": "(2R,3S)", "SR": "(2S,3R)"}

# The eight labellings of the (2R,3R) drawing, with what the sample holds:
#   (labels C2, labels C3, CXSMILES suffix, isomers, mixture?, meaning)
AND, OR, ONE = "and", "or", "one"
LABELLINGS = [
    ("abs", "abs", "|a:1,3|", ["RR"], ONE,
     "Pure (2R,3R). Both centres known."),
    ("or1", "or1", "|o1:1,3|", ["RR", "SS"], OR,
     "One enantiomer, unknown which. The relative configuration is known."),
    ("&1", "&1", "|&1:1,3|", ["RR", "SS"], AND,
     "The racemate: both enantiomers, 1:1."),
    ("abs", "&1", "|a:1,&1:3|", ["RR", "RS"], AND,
     "C2 is known (R); C3 is a mixture of both epimers."),
    ("abs", "or1", "|a:1,o1:3|", ["RR", "RS"], OR,
     "C2 is known (R); C3 is one configuration, unknown which."),
    ("or1", "or2", "|o1:1,o2:3|", ["RR", "SS", "RS", "SR"], OR,
     "Any one of the four stereoisomers. Each centre unknown on its own."),
    ("&1", "&2", "|&1:1,&2:3|", ["RR", "SS", "RS", "SR"], AND,
     "All four stereoisomers. Each centre racemic on its own."),
    ("&1", "none", "|&1:1|", ["RR", "SR"], AND,
     "C3 is known (R, wedged, no label); C2 is racemic."),
]


# ------------------------------------------------------------ measurement

def inchi(smiles, opts=ENH):
    block = from_smiles(dict(smiles=smiles, title="x"))
    return run_inchi(EXE, block, opts)


def warning(smiles):
    block = from_smiles(dict(smiles=smiles, title="x"))
    _, log = run_cli(EXE, block, ENH)
    return next((l.split(" structure")[0] for l in log if l.startswith("Warning")), "")


def stereo_tail(s):
    """'/t3-,4-/m1/s1' from a full InChI; '' when it has no /t."""
    return s[s.index("/t"):] if "/t" in s else ""


# ---------------------------------------------------------------- drawing

def picture(smiles, numbers=True):
    """Molecule with its collection labels; canonical numbers optional."""
    block = from_smiles(dict(smiles=smiles, title="x"))
    _, canon = run_inchi(EXE, block, ENH)
    return draw(block, canon if numbers else {})


def isomer(smiles):
    """Small unlabelled stereoisomer with R/S annotations."""
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
    """Colour the layers of a stereo tail: /t ink, /m abs blue, /s by class."""
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


# ------------------------------------------------------------------ parts

def sample(keys, how, iso_svgs):
    """What is in the bottle: one vial holding a mixture, or several
    dashed vials of which the sample is one."""
    if how == OR:
        vials = '<span class="joiner">or</span>'.join(
            f'<figure class="vial vial-or">{iso_svgs[k]}<figcaption>{ISO_NAME[k]}</figcaption></figure>'
            for k in keys)
        return f'<div class="vials">{vials}</div>'

    figs = '<span class="joiner">+</span>'.join(
        f'<figure>{iso_svgs[k]}<figcaption>{ISO_NAME[k]}</figcaption></figure>' for k in keys)
    return f'<div class="vials"><div class="vial vial-and">{figs}</div></div>'


def gallery(iso_svgs):
    rows = []
    for n, (c2, c3, labels, keys, how, meaning) in enumerate(LABELLINGS, 1):
        smiles = ISOMERS["RR"] + " " + labels
        enh, _ = inchi(smiles)
        std, _ = inchi(ISOMERS["RR"], [])
        same = stereo_tail(enh) == stereo_tail(std)
        rows.append(f"""
<article class="case">
  <div class="case-head"><span class="case-n">{n}</span>
    C2 {label_chip(c2)} C3 {label_chip(c3)}</div>
  <div class="case-body">
    <div class="case-pic">{picture(smiles, numbers=False)}</div>
    <div class="case-text">
      <p>{html.escape(meaning)}</p>
      {sample(keys, how, iso_svgs)}
      <dl class="strings">
        <dt>Enhanced InChI</dt><dd class="inchi">{mark(stereo_tail(enh))}</dd>
        <dt>Standard InChI</dt><dd class="inchi muted">{html.escape(stereo_tail(std))}
          {"" if same else '<span class="note">cannot tell this sample apart</span>'}</dd>
      </dl>
    </div>
  </div>
</article>""")
    return "".join(rows)


def flow():
    """Running example: abs on C2, &1 on C3, drawn (2R,3R); then (2R,3S)."""
    labels = " |a:1,&1:3|"
    rr, rs = ISOMERS["RR"] + labels, ISOMERS["RS"] + labels
    enh_rr, _ = inchi(rr)
    enh_rs, _ = inchi(rs)
    assert stereo_tail(enh_rr) == stereo_tail(enh_rs) == "/t3-,4-/m1/s1(4)3(3)", enh_rr
    return dict(flow_draw=picture(rr, numbers=False), flow_numbered=picture(rr),
                flow_other=picture(rs, numbers=False), flow_result=mark(stereo_tail(enh_rr)),
                flow_skeleton=html.escape(enh_rr[:enh_rr.index("/t")]))


def multi():
    """(R)-pentan-2-ol + racemic butan-2-ol + water: one slot per molecule."""
    smiles = "C[C@@H](O)CCC.C[C@H](O)CC.O |&1:7|"
    enh, _ = inchi(smiles)
    tail = stereo_tail(enh)
    assert tail == "/t5-;4-;/m1../s;3;", tail

    span = "C[C@@H](O)CCC.C[C@H](O)CC |&1:1,7|"
    span_enh, _ = inchi(span)
    span_std, _ = inchi(span, [])
    assert stereo_tail(span_enh) == stereo_tail(span_std)
    return dict(multi_pic=picture(smiles), multi_tail=mark(tail),
                span_pic=picture(span, numbers=False), span_warn=html.escape(warning(span)),
                span_tail=html.escape(stereo_tail(span_enh)))


def ignored():
    """An &1 label on a CH3 next to C3 is not a stereocentre: dropped."""
    smiles = ISOMERS["RR"] + " |&1:0,3,a:1|"
    enh, _ = inchi(smiles)
    assert stereo_tail(enh) == "/t3-,4-/m1/s1(4)3(3)", enh
    return dict(ch3_pic=picture(smiles), ch3_tail=mark(stereo_tail(enh)))


def biovia():
    """The BIOVIA white paper example: every class, several groups."""
    path = os.path.join(SPECS, "enhanced-stereo", "datasets", "biovia_white_paper_fig22.mol")
    block = open(path).read()
    enh, canon = run_inchi(EXE, block, ENH)
    tail = stereo_tail(enh)
    groups = []
    s = tail[tail.index("/s") + 2:]
    for digit, atoms in S_GROUP.findall(s):
        for g in re.findall(r"\(([\d,]+)\)", atoms):
            groups.append(f'<tr><td>{mark_s(digit + "(" + g + ")")}</td>'
                          f'<td>{ {"1": "absolute", "2": "or: one of two, unknown which", "3": "and: mixture of both"}[digit]}</td>'
                          f'<td>{g.replace(",", ", ")}</td></tr>')
    return dict(biovia_pic=draw(block, canon), biovia_tail=mark(tail), biovia_rows="".join(groups))


# ------------------------------------------------------------------- page

def build():
    assert EXE, "set INCHI_NEW to an inchi-1 built from branch 'atropisomers'"
    iso_svgs = {k: isomer(s) for k, s in ISOMERS.items()}
    parts = dict(gallery=gallery(iso_svgs), **flow(), **multi(), **ignored(), **biovia())

    # Hero: the three labellings that standard InChI cannot separate
    hero = []
    for labels, word in (("|a:1,3|", "abs"), ("|o1:1,3|", "or"), ("|&1:1,3|", "and")):
        enh, _ = inchi(ISOMERS["RR"] + " " + labels)
        hero.append(f'<li><span class="chip c-{word}">{word}</span>'
                    f'<code class="inchi">{mark(stereo_tail(enh))}</code></li>')
    std, _ = inchi(ISOMERS["RR"], [])
    parts.update(hero_pic=picture(ISOMERS["RR"], numbers=False), hero_list="".join(hero),
                 hero_std=html.escape(stereo_tail(std)))

    spec = os.path.join(SPECS, "enhanced-stereo")
    template = string.Template(open(os.path.join(spec, "explain.template.html")).read())
    open(os.path.join(spec, "explain.html"), "w").write(template.substitute(parts))


if __name__ == "__main__":
    build()
