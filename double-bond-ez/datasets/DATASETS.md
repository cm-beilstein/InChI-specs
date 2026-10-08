# Double-bond E/Z dataset gates

Gates seeded from [DECK] slides 25–30, materialised as inline molblocks in
`INCHI-1-TEST/tests/test_unit/test_doubleBondEZ.cpp`. The reference molecule is `C2BrCl2F`
(BrClC=CClF) throughout. With `-EnhancedStereochemistry` every InChI carries the `1B` prefix.

## Z1 — Classic absolute (works today; needs asserting test) — slide 25
```
InChI=1B/C2BrCl2F/c3-1(4)2(5)6/b2-1+
```
V3000 with `MDLV30/STEBABS BONDS=(1 3)` must reduce to this standard `/b`.

## Z2 — Unknown / either (works today; no `/b`) — slide 26
Crossed ("double-either", V2 bond code `2 3`) and wavy ("single-either", `1 4`) draws:
```
InChI=1B/C2BrCl2F/c3-1(4)2(5)6
```

## Z3 — Enhanced OR (`/b2(…)`) — slide 27
`MDLV30/STEBREL1 BONDS=(1 3)`:
```
InChI=1B/C2BrCl2F/c3-1(4)2(5)6/b2(2-1-)
```
Rule: each bond = higher canonical atom, `-`, lower atom, parity; the lowest bond of a group
reads `-` (whole-group flip), the others keep their relative parity.

## Z4 — Enhanced AND (`/b3(…)`) — slide 28
`MDLV30/STEBRAC1 BONDS=(1 3)`:
```
InChI=1B/C2BrCl2F/c3-1(4)2(5)6/b3(2-1-)
```

## Z5 — Multi-group stress case — slide 29
`C18H19Br2Cl4F3N2O2`, one STEBREL1 (bonds=2), STEBRAC1 (bonds 16,20), STEBRAC2 (bond 26).
Expected `/b` fragment (as transcribed from the slide):
```
/b12-5+,2(16-14-),3(1(15-10-)(17-11-),2(18-13-))
```
In the adopted grammar (user decision 2026-10-08, Spec 3 §6) this reads
`/b12-5+,2(16-14-),3(15-10-,17-11-)(18-13-)`: one block per group, no group indices. Not
materialised — the slide's molfile is not available; the layouts are gated with a two-bond
molecule F(Br)C=C(Cl)-CH2-C(Cl)=C(I)F instead (`Z5_multiple_groups`).

## Z6 — Combined double bond + tetrahedral — slide 30
`C4H5BrClFO`, double bond 3–4 + tetrahedral centre 2:
```
STEBABS bond + abs centre       → InChI=1B/C4H5BrClFO/c1-2(8)3(5)4(6)7/h2,8H,1H3/b4-3-/t2-/m1/s1
STEBREL2 bond + abs centre      → InChI=1B/C4H5BrClFO/c1-2(8)3(5)4(6)7/h2,8H,1H3/b2(4-3-)/t2-/m1/s1
STEBABS bond + STERAC1 centre   → InChI=1B/C4H5BrClFO/c1-2(8)3(5)4(6)7/h2,8H,1H3/b4-3-/t2-/s3
```
Confirms: double bonds group in `/b`, sp³ centres group in `/t`+`/s`, independently, in one
InChI. All three reproduced exactly (`Z6_bond_plus_tetrahedral`).

## Materialised
- [x] `test_doubleBondEZ.cpp`: Z1–Z4, Z6, multi-group layouts, relative geometry in a group,
      non-stereo bond ignored, renumbering invariance, malformed collections
- [ ] Z5 with the slide-29 molecule (needs its molfile)
- [ ] Round-trip parse of grouped `/b` (InChI→structure out of scope, Spec 3 §5)
