"""Page parts for atropisomers/explain.html (Spec 4, axial chirality)."""

import html

from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

import build
from explain import cli, inchi, mark, picture, stereo_tail, warning
from molecules import ATROPISOMERS, UP, DOWN

# Dataset / unit-test molecules by their comparison-table title
DATA = {d["title"]: d for d in ATROPISOMERS}

# 2,2'-dibromo-6,6'-dichlorobiphenyl; SMILES atoms:
#   0 Cl, 1 C-Cl, 5 C-Br, 6 Br, 7 ipso | 8 ipso, 9 C-Cl, 10 Cl, 14 C-Br, 15 Br
#   axis 7-8, ortho positions 1, 5 (left ring) and 9, 14 (right ring)
BIARYL = "Clc1cccc(Br)c1-c1c(Cl)cccc1Br"
AXIS, ORTHO = (7, 8), (1, 5, 9, 14)
M_DRAWN = dict(smiles=BIARYL, wedges=[(7, 1, UP), (8, 9, DOWN)])
P_DRAWN = dict(smiles=BIARYL, wedges=[(7, 1, DOWN), (8, 9, UP)])

AXIS_COLOUR = (0.14, 0.34, 0.65)
ORTHO_COLOUR = (0.98, 0.83, 0.55)


def tail(mol, opts=None):
    s, _ = inchi(mol) if opts is None else inchi(mol, opts)
    return stereo_tail(s)


def highlighted(mol):
    """The biaryl with its axis (blue) and the four ortho positions (amber)."""
    m = Chem.MolFromMolBlock(build.from_smiles(dict(title="x", **mol)))
    Chem.ReapplyMolBlockWedging(m, allBondTypes=True)
    m = rdMolDraw2D.PrepareMolForDrawing(m, kekulize=True, addChiralHs=False, wedgeBonds=False)
    axis_bond = m.GetBondBetweenAtoms(*AXIS).GetIdx()
    d = rdMolDraw2D.MolDraw2DSVG(build.SVG_W, build.SVG_H)
    o = d.drawOptions()
    o.clearBackground = False
    o.maxFontSize = build.ATOM_FONT_MAX_PX
    d.DrawMolecule(
        m, highlightAtoms=list(AXIS + ORTHO), highlightBonds=[axis_bond],
        highlightAtomColors={**{a: AXIS_COLOUR for a in AXIS}, **{a: ORTHO_COLOUR for a in ORTHO}},
        highlightBondColors={axis_bond: AXIS_COLOUR})
    d.FinishDrawing()
    svg = d.GetDrawingText()
    return svg[svg.index("<svg"):]


def data_block(title):
    return build.molblock(DATA[title])


def data_picture(title):
    block = data_block(title)
    _, canon = inchi(block)
    return build.draw(block, canon, DATA[title].get("relayout", False))


# ---------------------------------------------------------------- sections

def hero():
    m, p = tail(M_DRAWN), tail(P_DRAWN)
    old_m, old_p = tail(M_DRAWN, []), tail(P_DRAWN, [])
    assert (m, p) == ("/t11-/m0/s1", "/t11-/m1/s1"), (m, p)
    assert old_m == old_p == "", (old_m, old_p)

    # Same isomer as the dataset's labelled (M) record: identical InChI
    dataset_m, _ = inchi(data_block("(M)-2,2'-dibromo-6,6'-dichlorobiphenyl"))
    assert dataset_m == inchi(M_DRAWN)[0], dataset_m

    full, _ = inchi(M_DRAWN)
    std, _ = inchi(M_DRAWN, [])
    return dict(hero_std=html.escape(std), hero_m=picture(M_DRAWN, numbers=False), hero_p=picture(P_DRAWN, numbers=False),
                hero_new_m=mark(m), hero_new_p=mark(p),
                hero_skeleton=html.escape(full[:full.index("/t")]))


def flow():
    one = dict(smiles=BIARYL, wedges=[(7, 1, UP)])
    flat = dict(smiles=BIARYL)
    assert tail(one) == tail(M_DRAWN)
    assert tail(flat) == "" and "Omitted undefined stereo" in warning(flat)

    _, canon = inchi(M_DRAWN)
    assert sorted(canon[a] for a in AXIS) == [11, 12], canon

    # Hindrance and dissymmetry, each changed in one place
    three = dict(smiles="Clc1ccccc1-c1c(Br)cccc1C", wedges=[(6, 1, UP), (7, 8, DOWN)])
    two = dict(smiles="Clc1ccccc1-c1c(Br)cccc1", wedges=[(6, 1, UP), (7, 8, DOWN)])
    twin = dict(smiles="Clc1cccc(Cl)c1-c1c(Cl)cccc1Br", wedges=[(7, 1, UP), (8, 9, DOWN)])
    assert tail(three) == "/t10-/m0/s1", tail(three)
    assert tail(two) == "" and tail(twin) == "", (tail(two), tail(twin))

    return dict(flow_draw=picture(M_DRAWN, numbers=False), flow_axis=highlighted(M_DRAWN),
                flow_numbered=picture(M_DRAWN), flow_one=picture(one, numbers=False),
                flow_flat=html.escape(warning(flat)),
                three_pic=picture(three, numbers=False), three_tail=mark(tail(three)),
                two_pic=picture(two, numbers=False),
                twin_pic=picture(twin, numbers=False))


# (title in molecules.py, caption, expected tail, note)
GALLERY = [
    ("3D input (projection), 44° torsion", "3D coordinates, torsion +44°",
     "/t11-/m1/s1", "No wedges needed: the 3D geometry fixes the axis. +44° is P."),
    ("3D input (projection), -44° torsion", "3D coordinates, torsion −44°",
     "/t11-/m0/s1", "The mirror image, M."),
    ("(M)-BINOL", "(M)-BINOL", "/t19-/m0/s1",
     "Fused rings count as ortho substituents: each naphthyl end has two."),
    ("(P)-BINOL", "(P)-BINOL", "/t19-/m1/s1", "Its enantiomer: only /m changes."),
    ("lignan, biaryl bridged into an 8-ring (M)", "Lignan, axis inside an 8-membered ring",
     "/t15?,16?,19-/m0/s1",
     "An 8-ring holds the biaryl twisted, so the two bridge positions suffice. "
     "The two CH centres (15, 16) are not wedged in this file, so they read ?."),
    ("edge: acyclic C14H26 axis", "No ring at all",
     "/t13-/m1/s1", "Axes need not involve aromatic rings: four branched groups hinder this C–C bond."),
    ("aryl N,N-dimethylamide, aryl-carbonyl axis", "Aryl–carbonyl axis of an amide",
     "/t11-/m1/s1", "The C=O carbon is a flat, three-connected end like an aryl carbon."),
    ("(M)-6,6'-dinitrodiphenic acid", "(M)-6,6'-dinitrodiphenic acid, a classic",
     "/t11-/m0/s1", "The first resolved atropisomer (Christie and Kenner, 1922)."),
]


def gallery():
    rows = []
    for title, caption, expected, note in GALLERY:
        block = data_block(title)
        new, _ = inchi(block)
        old, _ = inchi(block, [])
        assert stereo_tail(new) == expected, (title, new)
        rows.append(f"""
<article class="case">
  <div class="case-head">{html.escape(caption)}</div>
  <div class="case-body">
    <div class="case-pic">{data_picture(title)}</div>
    <div class="case-text">
      <p>{html.escape(note)}</p>
      <dl class="strings">
        <dt>New InChI</dt><dd class="inchi">{mark(stereo_tail(new))}</dd>
        <dt>Standard InChI</dt><dd class="inchi muted">{html.escape(stereo_tail(old)) or "no stereo layer"}</dd>
      </dl>
    </div>
  </div>
</article>""")
    return dict(gallery="".join(rows))


def enhanced():
    """or / & labels on the axis; the label must name the lower-numbered axis atom."""
    and_ = dict(M_DRAWN, coll=[("STERAC1", [7])])
    or_ = dict(M_DRAWN, coll=[("STEREL1", [7])])
    or_high = dict(M_DRAWN, coll=[("STEREL1", [8])])
    assert tail(and_) == "/t11-/s3" and tail(or_) == "/t11-/s2", (tail(and_), tail(or_))
    assert tail(or_high) == tail(M_DRAWN), tail(or_high)
    assert inchi(or_high)[1][8] == 12  # the text names carbon 12
    return dict(and_pic=picture(and_), and_tail=mark(tail(and_)), or_tail=mark(tail(or_)),
                or_high_pic=picture(or_high), or_high_tail=mark(tail(or_high)))


# (title in molecules.py, caption, why)
NOT_DETECTED = [
    ("edge: both wedges on one side (degenerate)", "Both wedges on one side",
     "The drawing contradicts itself; the axis counts as undefined and is left out."),
    ("edge: bare bridged biaryl, 7-ring (fast ring flip)", "Biaryl bridged into a 7-ring, no other substituent",
     "Only two ortho positions are substituted, and the ring flips quickly at room temperature."),
    ("edge: 3,3'-bipyridine, too little hindrance", "3,3'-Bipyridine",
     "No ortho substituent: the rings rotate freely."),
    ("edge: C-N axis (out of scope, v1 carbon only)", "Aryl–N axis (N-aryl indole)",
     "Version 1 covers carbon–carbon axes only. C–N, N–N and C–O axes come later."),
    ("edge: N-N axis (M)", "N–N axis (2,2'-diethyl-1,1'-biindole)", "Same: not carbon–carbon."),
    ("edge: overcrowded alkene (Z,M)", "Overcrowded alkene",
     "The twist is around a C=C bond, which InChI already records as E/Z in /b. No single-bond axis."),
]


def not_detected():
    rows = []
    for title, caption, why in NOT_DETECTED:
        new, _ = inchi(data_block(title))
        old, _ = inchi(data_block(title), [])
        assert stereo_tail(new) == stereo_tail(old), (title, new)
        shown = stereo_tail(new)
        rows.append(f"""
<figure class="miss">
  <div class="case-pic">{data_picture(title)}</div>
  <figcaption><b>{html.escape(caption)}</b><br>{html.escape(why)}<br>
  {f'<code class="inchi">{mark(shown)}</code>' if shown else '<span class="muted">No axis in the InChI.</span>'}</figcaption>
</figure>""")
    return dict(missed="".join(rows))


def usage():
    """How to use it: the biaryl drawn (M), with and without the option."""
    with_option = cli(M_DRAWN, ["-EnhancedStereochemistry"], "biaryl.mol")
    without = cli(M_DRAWN, [], "biaryl.mol")
    assert "/t" in with_option and "/m" in with_option, with_option
    assert "/t" not in without, without
    return dict(use_cli=with_option, use_std=without)


def parts():
    return dict(**usage(), **hero(), **flow(), **gallery(), **enhanced(), **not_detected())
