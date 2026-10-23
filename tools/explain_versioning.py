"""Page parts for inchi-versioning/explain.html (IUPAC-InChI/InChI#285, PR #280).

Every string is measured with the spec's 'new' binary (INCHI_NEW) and, for
the before/after rows, its 'old' binary (INCHI_OLD, set by rebuild.py).
"""

import html

from build import inchi_key, run_cli
from explain import cli, EXE, OLD_EXE, molblock, picture, run_inchi

ETHANOL = "CCO"
NACL = "[Na+].[Cl-]"
CISPLATIN = "[NH3]->[Pt](<-[NH3])(Cl)Cl"
MIXTURE = "CCO.[Na+].[Cl-]"
BETA = ["-EnhancedStereochemistry"]
NONSTD = ["-FixedH"]
LEGACY = ["-LegacyMetalHandling"]


def measure(exe, mol, opts=()):
    """(InChI, InChIKey) of one run."""
    block = molblock(mol)
    return run_inchi(exe, block, list(opts))[0], inchi_key(exe, block, list(opts))[len("InChIKey="):]


def prefix(s):
    """'InChI=1BB/C2H6O/...' -> '1BB'"""
    return s[len("InChI="):s.index("/")]


def code(s):
    return f'<span class="inchi">{html.escape(s)}</span>'


def key_html(key):
    """Key with its two version letters (positions 24, 25) in bold."""
    return code(key[:23]) + f"<b>{html.escape(key[23:25])}</b>" + code(key[25:])


def grid():
    """The six prefix / flag combinations, each measured."""
    rows = [("standard", "", ETHANOL, [], "1S", "SA"),
            ("standard", "B", None, None, "1SB", "SB"),
            ("beta", "", ETHANOL, BETA, "1B", "BA"),
            ("beta", "B", NACL, [], "1BB", "BB"),
            ("non-standard", "", ETHANOL, NONSTD, "1N", "NA"),
            ("non-standard", "B", NACL, NONSTD, "1NB", "NB")]
    out = []
    for cls, sub, mol, opts, want, flags in rows:
        if mol is None:
            example = '<span class="muted">not made in this release (Molecular Inorganics is beta)</span>'
        else:
            s, k = measure(EXE, mol, opts)
            assert prefix(s) == want and k[23:25] == flags, (want, s, k)
            what = "ethanol" if mol == ETHANOL else "NaCl"
            how = " ".join(opts) or "default options"
            example = f"{what}, <code>{html.escape(how)}</code>: {code(s)}"
        mi = "Molecular Inorganics" if sub else "base InChI 1"
        out.append(f"<tr><td><code>InChI={want}/</code></td><td>{cls}</td><td>{mi}</td>"
                   f"<td><code>…{flags}-…</code></td><td>{example}</td></tr>")
    return "\n".join(out)


def before_after(mol, opts=()):
    old, old_key = measure(OLD_EXE, mol, opts)
    new, new_key = measure(EXE, mol, opts)
    return old, old_key, new, new_key


def metals():
    old, old_key, new, new_key = before_after(CISPLATIN)
    assert old == "InChI=1S/2ClH.2H3N.Pt/h2*1H;2*1H3;/q;;;;+2/p-2", old
    assert new == "InChI=1BB/Cl2H6N2Pt/c1-5(2,3)4/h3-4H3", new
    assert (old_key, new_key) == ("LXZZYRPGZAFOLE-UHFFFAOYSA-L", "NKTISDOLGLLLMZ-UHFFFAOYBB-N")

    n_old, n_old_key, n_new, n_new_key = before_after(NACL)
    assert n_old.split("/", 1)[1] == n_new.split("/", 1)[1], (n_old, n_new)
    assert prefix(n_old) == "1S" and prefix(n_new) == "1BB"
    assert n_old_key[:23] == n_new_key[:23] and n_new_key[23:25] == "BB", n_new_key

    mix, mix_key = measure(EXE, MIXTURE)
    assert mix.startswith("InChI=1BB/C2H6O.ClH.Na/"), mix

    eth, eth_key = measure(EXE, ETHANOL)
    assert eth == "InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3" and eth_key.endswith("SA-N"), eth

    return dict(cis_pic=picture(CISPLATIN, numbers=False),
                cis_old=code(old), cis_old_key=key_html(old_key),
                cis_new=code(new), cis_new_key=key_html(new_key),
                nacl_pic=picture(NACL, numbers=False),
                nacl_old=code(n_old), nacl_old_key=key_html(n_old_key),
                nacl_new=code(n_new), nacl_new_key=key_html(n_new_key),
                mix=code(mix), eth=code(eth), eth_key=key_html(eth_key))


def metalloids():
    rows = []
    for el, n, flagged in (("Sb", 3, True), ("As", 3, False), ("Ge", 4, False), ("Te", 4, False)):
        s, _ = measure(EXE, f"Cl[{el}]" + "(Cl)" * (n - 2) + "Cl")
        assert prefix(s) == ("1BB" if flagged else "1S"), s
        rows.append(f"<tr><td>{el}Cl{n}</td><td>{'yes' if flagged else 'no'}</td><td>{code(s)}</td></tr>")
    return dict(metalloid_rows="\n".join(rows))


def nonstandard():
    old, _ = measure(OLD_EXE, ETHANOL, NONSTD)
    new, _ = measure(EXE, ETHANOL, NONSTD)
    assert (prefix(old), prefix(new)) == ("1", "1N"), (old, new)

    legacy, legacy_key = measure(EXE, CISPLATIN, LEGACY)
    assert legacy == "InChI=1N/2ClH.2H3N.Pt/h2*1H;2*1H3;/q;;;;+2/p-2", legacy
    return dict(fixedh_old=code(old), fixedh_new=code(new),
                legacy=code(legacy), legacy_key=key_html(legacy_key))


def old_reader():
    """What 1.07-era software makes of a new string: InChI2InChI in the old binary."""
    new, _ = measure(EXE, CISPLATIN)
    out, log = run_cli(OLD_EXE, new, ["-InChI2InChI"])
    read = next(line for line in out if line.startswith("InChI="))
    assert read == "InChI=1/" + new.split("/", 1)[1], read
    assert not any(line.startswith("Error") for line in log), log
    return dict(reader_in=code(new), reader_out=code(read))


def usage():
    """How to use it: no option needed; -LegacyMetalHandling for the old rules."""
    default = cli(NACL, [], "nacl.mol")
    legacy = cli(NACL, LEGACY, "nacl.mol")
    assert "InChI=1BB/" in default and "BB-" in default, default
    assert "InChI=1N/" in legacy and "NA-" in legacy, legacy
    return dict(use_cli=default, use_legacy=legacy)


def parts():
    assert OLD_EXE, "INCHI_OLD must name the old binary; run tools/rebuild.py"
    return dict(**usage(), grid_rows=grid(), **metals(), **metalloids(), **nonstandard(), **old_reader())
