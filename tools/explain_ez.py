"""Page parts for double-bond-ez/explain.html (Spec 3, E/Z with OR/AND)."""

import html
import re

import build
from explain import ENH, EXE, inchi, isomer, label_chip, mark, molblock, picture, run_cli, stereo_tail

# Sorbic acid, CH3-C5H=C4H-C3H=C2H-C1OOH. Double bonds in SMILES order:
#   db 0 = C4=C5 (canonical 3-2), db 1 = C2=C3 (canonical 5-4)
# Keys name the geometry as (2x,4y): "ZE" = (2Z,4E)
SORBIC = {
    "EE": "C/C=C/C=C/C(=O)O",
    "ZE": "C/C=C/C=C\\C(=O)O",
    "ZZ": "C/C=C\\C=C/C(=O)O",
    "EZ": "C/C=C\\C=C\\C(=O)O",
}
SORBIC_NAME = {k: f"(2{k[0]},4{k[1]})" for k in SORBIC}
C45, C23 = ("db", 0), ("db", 1)

# Butenedioic acid: fumaric (E) and maleic (Z); db 1 is the C=C
FUMARIC, MALEIC = "OC(=O)/C=C/C(=O)O", "OC(=O)/C=C\\C(=O)O"
BUTENE = "C/C=C/C"
CC = ("db", 1)

AND, OR, ONE = "and", "or", "one"

# The eight labellings of the (2E,4E) drawing, with what the sample holds:
#   (label C2=C3, label C4=C5, collections, isomers, mixture?, meaning, expected /b)
LABELLINGS = [
    ("abs", "abs", [("STEBABS", [C23, C45])], ["EE"], ONE,
     "Pure (2E,4E). Both bonds known.", "/b3-2+,5-4+"),
    ("or1", "or1", [("STEBREL1", [C23, C45])], ["EE", "ZZ"], OR,
     "One isomer, unknown which. Known: both bonds have the same geometry.", "/b2(3-2-,5-4-)"),
    ("&1", "&1", [("STEBRAC1", [C23, C45])], ["EE", "ZZ"], AND,
     "A mixture of both. Each molecule has two equal geometries.", "/b3(3-2-,5-4-)"),
    ("&1", "abs", [("STEBABS", [C45]), ("STEBRAC1", [C23])], ["EE", "ZE"], AND,
     "C4=C5 is known (E); C2=C3 is an E/Z mixture.", "/b3-2+,3(5-4-)"),
    ("or1", "abs", [("STEBABS", [C45]), ("STEBREL1", [C23])], ["EE", "ZE"], OR,
     "C4=C5 is known (E); C2=C3 is one geometry, unknown which.", "/b3-2+,2(5-4-)"),
    ("or1", "or2", [("STEBREL1", [C23]), ("STEBREL2", [C45])], ["EE", "ZZ", "ZE", "EZ"], OR,
     "Any one of the four isomers. Each bond unknown on its own.", "/b2(3-2-)(5-4-)"),
    ("&1", "&2", [("STEBRAC1", [C23]), ("STEBRAC2", [C45])], ["EE", "ZZ", "ZE", "EZ"], AND,
     "All four isomers. Each bond a mixture on its own.", "/b3(3-2-)(5-4-)"),
    ("none", "&1", [("STEBRAC1", [C45])], ["EE", "EZ"], AND,
     "C2=C3 is known (E, no label); C4=C5 is an E/Z mixture.", "/b5-4+,3(3-2-)"),
]


# ------------------------------------------------------------ helpers

def sorbic(key, coll=(), either=()):
    return dict(smiles=SORBIC[key], coll=list(coll), either=list(either))


def tail(mol, opts=ENH):
    return stereo_tail(inchi(mol, opts)[0])


def warn(mol):
    """Text of the first warning, both log formats:
      'Warning (text) structure #1.'  and  'Warning: (text) inp structure #1.'"""
    _, log = run_cli(EXE, molblock(mol), ENH)
    line = next((l for l in log if l.startswith("Warning")), "")
    m = re.search(r"\((.*)\)", line)
    return m.group(1) if m else ""


B_GROUP = re.compile(r"(^|,)([23])((?:\([^)]*\))+)")
B_CLASS = {"2": "or", "3": "and"}


def mark_b(layer):
    """Colour the grouped classes of a /b layer: '/b3-2+,3(5-4-)' -> and '3(5-4-)'."""
    body = layer[2:]
    body = B_GROUP.sub(lambda m: f'{m.group(1)}<span class="c-{B_CLASS[m.group(2)]}">'
                                 f'{m.group(2)}{m.group(3)}</span>', body)
    return f'<span class="layer">/b{body}</span>'


def mark_ez(s):
    """mark() for every layer, with /b coloured by class."""
    out = []
    for layer in re.findall(r"/[a-z][^/]*", html.escape(s)):
        out.append(mark_b(layer) if layer.startswith("/b") else mark(layer))
    return "".join(out)


def sample(keys, how, svgs, names):
    """One solid vial for a mixture, dashed vials for 'one of these'."""
    if how == OR:
        vials = '<span class="joiner">or</span>'.join(
            f'<figure class="vial vial-or">{svgs[k]}<figcaption>{names[k]}</figcaption></figure>'
            for k in keys)
        return f'<div class="vials">{vials}</div>'

    figs = '<span class="joiner">+</span>'.join(
        f'<figure>{svgs[k]}<figcaption>{names[k]}</figcaption></figure>' for k in keys)
    return f'<div class="vials"><div class="vial vial-and">{figs}</div></div>'


# ------------------------------------------------------------ parts

def hero():
    """Fumaric acid with three labels; standard InChI cannot tell them apart."""
    rows = []
    for name, word, want in (("STEBABS", "abs", "/b2-1+"),
                             ("STEBREL1", "or", "/b2(2-1-)"),
                             ("STEBRAC1", "and", "/b3(2-1-)")):
        got = tail(dict(smiles=FUMARIC, coll=[(name, [CC])]))
        assert got == want, (name, got)
        rows.append(f'<li><span class="chip c-{word}">{word}</span>'
                    f'<code class="inchi">{mark_ez(got)}</code></li>')
    std = tail(dict(smiles=FUMARIC), [])
    assert std == "/b2-1+", std
    return dict(hero_pic=picture(FUMARIC, numbers=False), hero_list="".join(rows),
                hero_std=html.escape(std))


def basics():
    """Fumaric vs maleic acid: & on either drawing is one mixture."""
    svgs = {"E": isomer(FUMARIC), "Z": isomer(MALEIC)}
    names = {"E": "fumaric acid (E)", "Z": "maleic acid (Z)"}
    fum = tail(dict(smiles=FUMARIC, coll=[("STEBRAC1", [CC])]))
    mal = tail(dict(smiles=MALEIC, coll=[("STEBRAC1", [CC])]))
    assert fum == mal == "/b3(2-1-)", (fum, mal)
    std_f, std_m = tail(dict(smiles=FUMARIC), []), tail(dict(smiles=MALEIC), [])
    assert (std_f, std_m) == ("/b2-1+", "/b2-1-"), (std_f, std_m)
    return dict(vial_or=sample(["E", "Z"], OR, svgs, names),
                vial_and=sample(["E", "Z"], AND, svgs, names),
                fum_pic=picture(dict(smiles=FUMARIC, coll=[("STEBRAC1", [CC])]), numbers=False),
                mal_pic=picture(dict(smiles=MALEIC, coll=[("STEBRAC1", [CC])]), numbers=False),
                fummal_tail=mark_ez(fum), std_fum=html.escape(std_f), std_mal=html.escape(std_m))


def flow():
    """Running example: sorbic acid, C4=C5 abs, C2=C3 &1; drawn (2E,4E), then (2Z,4E)."""
    coll = [("STEBABS", [C45]), ("STEBRAC1", [C23])]
    ee, ze = sorbic("EE", coll), sorbic("ZE", coll)
    full = inchi(ee)[0]
    assert stereo_tail(full) == tail(ze) == "/b3-2+,3(5-4-)", full

    # The signs as drawn are the standard InChI's: /b3-2+,5-4+ for (2E,4E)
    assert tail(sorbic("EE"), []) == "/b3-2+,5-4+"
    assert tail(sorbic("ZE"), []) == "/b3-2+,5-4-"
    return dict(flow_draw=picture(ee, numbers=False), flow_numbered=picture(ee),
                flow_other=picture(ze, numbers=False), flow_result=mark_ez(stereo_tail(full)),
                flow_skeleton=html.escape(full[:full.index("/b")]))


def rules():
    """Example strings quoted in the rules, all measured."""
    order = tail(sorbic("EE", [("STEBRAC1", [C45]), ("STEBREL1", [C23])]))
    assert order == "/b2(5-4-),3(3-2-)", order
    same = tail(sorbic("EE", [("STEBRAC1", [C23, C45])]))
    diff = tail(sorbic("ZE", [("STEBRAC1", [C23, C45])]))
    assert (same, diff) == ("/b3(3-2-,5-4-)", "/b3(3-2-,5-4+)"), (same, diff)
    assert tail(sorbic("ZZ", [("STEBRAC1", [C23, C45])])) == same
    assert tail(sorbic("EZ", [("STEBRAC1", [C23, C45])])) == diff
    return dict(rule_order=mark_ez(order), rule_same=mark_ez(same), rule_diff=mark_ez(diff))


def gallery():
    svgs = {k: isomer(s) for k, s in SORBIC.items()}
    std = tail(sorbic("EE"), [])
    rows = []
    for n, (c23, c45, coll, keys, how, meaning, want) in enumerate(LABELLINGS, 1):
        mol = sorbic("EE", coll)
        got = tail(mol)
        assert got == want, (n, got)
        note = "" if got == std else '<span class="note">cannot tell this sample apart</span>'
        rows.append(f"""
<article class="case">
  <div class="case-head"><span class="case-n">{n}</span>
    C2=C3 {label_chip(c23)} C4=C5 {label_chip(c45)}</div>
  <div class="case-body">
    <div class="case-pic">{picture(mol, numbers=False)}</div>
    <div class="case-text">
      <p>{html.escape(meaning)}</p>
      {sample(keys, how, svgs, SORBIC_NAME)}
      <dl class="strings">
        <dt>Enhanced InChI</dt><dd class="inchi">{mark_ez(got)}</dd>
        <dt>Standard InChI</dt><dd class="inchi muted">{html.escape(std)} {note}</dd>
      </dl>
    </div>
  </div>
</article>""")
    return dict(gallery="".join(rows))


def centres():
    """(R,E)-pent-3-en-2-ol: bond and centre groups are independent."""
    smiles = "C[C@@H](O)/C=C/C"
    cases = [
        ("&1", "abs", smiles + " |a:1|", [("STEBRAC1", [("db", 0)])], "/b3(4-3-)/t5-/m1/s1"),
        ("none", "&1", smiles + " |&1:1|", [], "/b4-3+/t5-/s3"),
        ("&2", "&1", smiles + " |&1:1|", [("STEBRAC2", [("db", 0)])], "/b3(4-3-)/t5-/s3"),
    ]
    rows = []
    for bond, centre, s, coll, want in cases:
        got = tail(dict(smiles=s, coll=coll))
        assert got == want, (bond, centre, got)
        rows.append(f"<tr><td>{label_chip(bond)}</td><td>{label_chip(centre)}</td>"
                    f'<td class="inchi">{mark_ez(got)}</td></tr>')
    std = tail(dict(smiles=smiles), [])
    assert std == "/b4-3+/t5-/m1/s1", std
    return dict(centre_pic=picture(dict(smiles=smiles + " |a:1|", coll=[("STEBRAC1", [("db", 0)])])),
                centre_rows="".join(rows), centre_std=html.escape(std))


def multi():
    """E/Z-mixed fumaric acid + (E)-but-2-ene + water: one slot each."""
    mol = dict(smiles=f"{FUMARIC}.{BUTENE}.O", coll=[("STEBRAC1", [CC])])
    got = tail(mol)
    assert got == "/b3(2-1-);4-3+;", got

    # db 1 = fumaric C=C, db 3 = butene C=C (db 0, 2 are C=O)
    span = dict(smiles=f"{FUMARIC}.{BUTENE}", coll=[("STEBRAC1", [("db", 1), ("db", 3)])])
    span_got, span_std = tail(span), tail(span, [])
    assert span_got == span_std == "/b2-1+;4-3+", span_got
    span_warn = warn(span)
    assert "spans more than one component" in span_warn, span_warn
    return dict(multi_pic=picture(mol), multi_tail=mark_ez(got),
                span_pic=picture(span, numbers=False), span_warn=html.escape(span_warn),
                span_tail=html.escape(span_got))


def ignored():
    """Crossed bond, label on a single bond, bond in two collections."""
    crossed = sorbic("EE", [("STEBRAC1", [C23])], either=[1])
    crossed_got = tail(crossed)
    assert crossed_got == tail(sorbic("EE", either=[1]), []) == "/b3-2+,5-4?", crossed_got

    single = sorbic("EE", [("STEBRAC1", [("bond", 3)])])  # 1-based bond 3: C3-C4
    assert tail(single) == "/b3-2+,5-4+"

    twice = sorbic("EE", [("STEBRAC1", [C23, C45]), ("STEBREL1", [C23])])
    twice_warn = warn(twice)
    assert "more than one stereo collection" in twice_warn, twice_warn
    assert tail(twice) == "/b3-2+,5-4+"
    return dict(crossed_tail=mark_ez(crossed_got), single_pic=picture(single),
                twice_warn=html.escape(twice_warn))


def retinal():
    """All-trans retinal, one & and one or bond: reading a real string."""
    mol = dict(smiles="CC1=C(C(C)(C)CCC1)/C=C/C(C)=C/C=C/C(C)=C/C=O",
               coll=[("STEBRAC1", [("db", 2)]), ("STEBREL1", [("db", 4)])])
    got = tail(mol)
    assert got == "/b9-6+,12-11+,2(17-13-),3(16-8-)", got

    # Wider canvas than build.py's 320x240, or the numbers are unreadable
    size = build.SVG_W, build.SVG_H
    build.SVG_W, build.SVG_H = 720, 300
    try:
        pic = picture(mol)
    finally:
        build.SVG_W, build.SVG_H = size
    return dict(retinal_pic=pic, retinal_tail=mark_ez(got))


def parts():
    return dict(**hero(), **basics(), **flow(), **rules(), **gallery(), **centres(),
                **multi(), **ignored(), **retinal())
