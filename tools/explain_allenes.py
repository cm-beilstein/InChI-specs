"""Page parts for allenes/explain.html (Spec 2, axial chirality of allenes)."""

import html

from explain import cli, inchi, mark, picture, stereo_tail, warning

UP, DOWN = 1, 3

# 1-bromo-1-fluoro-3-chlorobuta-1,2-diene ([DECK] slide 18):
#   0 F, 1 C (end), 2 Br, 3 C (centre), 4 C (end), 5 CH3, 6 Cl
DECK = "FC(Br)=C=C(C)Cl"
TWO = [(1, 2, UP), (4, 6, DOWN)]
MIRROR = [(1, 2, DOWN), (4, 6, UP)]
CENTRE = 3


def deck(wedges=TWO, coll=(), **kw):
    return dict(smiles=DECK, wedges=wedges, coll=list(coll), **kw)


# But-3-en-2-ol with an allene: CH3-C*H(OH)-CH=C=CH-Cl
#   1 = stereocentre, 4 = allene centre
COMBO = "C[C@H](O)C=C=CCl"

OR, AND = "or", "and"

# (title, molecule, what it means, expected enhanced tail, vials)
CASES = [
    ("Two wedges", deck(),
     "Both ends wedged. The axis is defined; standard InChI already handles this.",
     "/t2-/m0/s1", None),
    ("Mirror image", deck(MIRROR),
     "Both wedges reversed: the other enantiomer. Only /m changes.",
     "/t2-/m1/s1", None),
    ("Same molecule, rotated", deck(rotate=1.0),
     "A rotated drawing of case 1 gives the same InChI.",
     "/t2-/m0/s1", None),
    ("One wedge (new)", deck([(4, 6, UP)]),
     "Only the Cl end is wedged; the Br/F end lies flat in the paper. IUPAC accepts this; "
     "standard InChI does not.",
     "/t2-/m1/s1", None),
    ("One wedge at the other end", deck([(1, 0, UP)]),
     "Only the F end is wedged.",
     "/t2-/m1/s1", None),
    ("or1 on the central carbon", deck(coll=[("STEREL1", [CENTRE])]),
     "One enantiomer, unknown which.",
     "/t2-/s2", OR),
    ("&1 on the central carbon", deck(coll=[("STERAC1", [CENTRE])]),
     "The racemate: both enantiomers, 1:1.",
     "/t2-/s3", AND),
    ("&1 with one wedge", deck([(4, 6, UP)], [("STERAC1", [CENTRE])]),
     "Labels work on a one-wedge drawing too.",
     "/t2-/s3", AND),
    ("Allene &1, stereocentre abs",
     dict(smiles=COMBO, wedges=[(5, 6, UP)], coll=[("STEABS", [1]), ("STERAC1", [4])]),
     "The centre is known; the axis is racemic. The axis is canonical atom 2, the centre 5.",
     "/t2-,5-/m0/s1(5)3(2)", None),
    ("Allene or1, stereocentre abs",
     dict(smiles=COMBO, wedges=[(5, 6, UP)], coll=[("STEABS", [1]), ("STEREL1", [4])]),
     "The centre is known; the axis is one configuration, unknown which.",
     "/t2-,5-/m0/s1(5)2(2)", None),
    ("Two axes, or1 and or2",
     dict(smiles="ClC=C=CCC=C=CCl", wedges=[(1, 0, UP), (3, 4, DOWN), (5, 4, UP), (7, 8, DOWN)],
          coll=[("STEREL1", [2]), ("STEREL2", [6])]),
     "Two independent axes, each unknown on its own.",
     "/t4-,5-/s2(4)(5)", None),
]

# Inputs that give no axis, or whose label is not used:
#   (title, molecule, why, expected enhanced tail, warning expected?)
IGNORED = [
    ("Both ends flat", deck([]),
     "No wedge: the handedness is not drawn. The axis is left out.", "", True),
    ("Two wedges at one end", deck([(1, 0, UP), (1, 2, UP)]),
     "Both substituents of the same end point up: the drawing contradicts itself. Left out.",
     "", True),
    ("Label on an end carbon", deck(coll=[("STERAC1", [1])]),
     "&1 names an end carbon, not the central one. The label is ignored; the wedges count "
     "as absolute.", "/t2-/m0/s1", False),
    ("Symmetric end", dict(smiles="CC(C)=C=CCl", wedges=[(1, 0, UP), (4, 5, DOWN)]),
     "One end carries two methyls. The molecule equals its mirror image: no axis.", "", False),
    ("Three double bonds (butatriene)", dict(smiles="ClC=C=C=CCl"),
     "An even number of cumulated carbons: the ends are coplanar. This is E/Z, written in /b.",
     "/b4-3+", False),
    ("Four double bonds (pentatetraene)",
     dict(smiles="ClC=C=C=C=CCl", wedges=[(1, 0, UP), (5, 6, DOWN)]),
     "Axially chiral like an allene, but longer than InChI supports. No stereo is written.",
     "", False),
]


def tail_or_none(s):
    t = stereo_tail(s)
    return html.escape(t) if t else '<span class="muted">no stereo</span>'


def vials(how):
    """The two enantiomers: one solid vial (mixture) or two dashed (one of them)."""
    a = picture(deck(), numbers=False)
    b = picture(deck(MIRROR), numbers=False)
    if how == OR:
        return ('<div class="vials"><figure class="vial vial-or">' + a + '</figure>'
                '<span class="joiner">or</span><figure class="vial vial-or">' + b + '</figure></div>')
    return ('<div class="vials"><div class="vial vial-and"><figure>' + a + '</figure>'
            '<span class="joiner">+</span><figure>' + b + '</figure></div></div>')


def case(n, title, mol, meaning, expected, extra=""):
    old, _ = inchi(mol, [])
    new, _ = inchi(mol)
    assert stereo_tail(new) == expected, (title, new)
    same = stereo_tail(old) == stereo_tail(new)
    note = "" if same else '<span class="note">differs</span>'
    return f"""
<article class="case">
  <div class="case-head"><span class="case-n">{n}</span>{html.escape(title)}</div>
  <div class="case-body">
    <div class="case-pic">{picture(mol, numbers=False)}</div>
    <div class="case-text">
      <p>{html.escape(meaning)}</p>
      {extra}
      <dl class="strings">
        <dt>New InChI</dt><dd class="inchi">{mark(stereo_tail(new)) or '<span class="muted">no stereo</span>'}</dd>
        <dt>Standard InChI</dt><dd class="inchi muted">{tail_or_none(old)} {note}</dd>
      </dl>
    </div>
  </div>
</article>"""


def gallery():
    vial_html = {OR: vials(OR), AND: vials(AND)}
    return "".join(case(n, t, m, w, e, vial_html.get(v, ""))
                   for n, (t, m, w, e, v) in enumerate(CASES, 1))


def ignored():
    out = []
    for n, (title, mol, why, expected, warns) in enumerate(IGNORED, 1):
        msg = warning(mol)
        assert bool(msg) == warns, (title, msg)
        # "Warning (Omitted undefined stereo)" -> "InChI warns: omitted undefined stereo"
        text = msg.removeprefix("Warning").strip(" :()")
        extra = f'<div class="dropped">InChI warns: {html.escape(text)}</div>' if msg else ""
        out.append(case(n, title, mol, why, expected, extra))
    return "".join(out)


def flow():
    """Running example: the deck allene, both ends wedged, then labelled."""
    full, canon = inchi(deck())
    mirror, _ = inchi(deck(MIRROR))
    one, _ = inchi(deck([(4, 6, UP)]))
    labelled, _ = inchi(deck(coll=[("STERAC1", [CENTRE])]))
    assert stereo_tail(full) == "/t2-/m0/s1", full
    assert stereo_tail(mirror) == "/t2-/m1/s1", mirror
    assert stereo_tail(one) == "/t2-/m1/s1", one
    assert stereo_tail(labelled) == "/t2-/s3", labelled
    assert canon[CENTRE] == 2, canon
    return dict(
        flow_draw=picture(deck(), numbers=False),
        flow_one=picture(deck([(4, 6, UP)]), numbers=False),
        flow_numbered=picture(deck()),
        flow_label=picture(deck(coll=[("STERAC1", [CENTRE])]), numbers=False),
        flow_skeleton=html.escape(full[:full.index("/t")]),
        flow_result=mark(stereo_tail(full)),
        flow_mirror=mark(stereo_tail(mirror)),
        flow_labelled=mark(stereo_tail(labelled)),
    )


def hero():
    """Old vs new for the deck allene: what changes."""
    rows = []
    for label, mol in (("two wedges", deck()),
                       ("one wedge", deck([(4, 6, UP)])),
                       ("or1", deck(coll=[("STEREL1", [CENTRE])])),
                       ("&1", deck(coll=[("STERAC1", [CENTRE])]))):
        old, _ = inchi(mol, [])
        new, _ = inchi(mol)
        rows.append(f'<tr><th scope="row">{label}</th><td class="inchi muted">{tail_or_none(old)}</td>'
                    f'<td class="inchi">{mark(stereo_tail(new))}</td></tr>')
    return dict(hero_pic=picture(deck(), numbers=False), hero_rows="".join(rows))


def usage():
    """How to use it: the deck allene, racemic axis (label on the central atom)."""
    racemic = deck(coll=[("STERAC1", [CENTRE])])
    with_option = cli(racemic, ["-EnhancedStereochemistry"], "allene.mol")
    without = cli(racemic, [], "allene.mol")
    assert "/s3" in with_option, with_option
    return dict(use_cli=with_option, use_std=without)


def parts():
    return dict(**usage(), **hero(), **flow(), gallery=gallery(), ignored=ignored(),
                vials_or=vials(OR), vials_and=vials(AND))
