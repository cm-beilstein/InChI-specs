# Double-bond E/Z dataset gates

No double-bond stereo tests exist in the repo. Gates seeded from [DECK] slides 25–30. The
reference molecule is `C2BrCl2F` (1-bromo-2,2-dichloro-1-fluoroethene-like) throughout.
Materialise as `double_bond_ez_test_file_1.sdf` + `test_doubleBondEZ.cpp`.

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

## Z3 — Enhanced OR (`/b2(…)`) — slide 27  (NOT IMPLEMENTED)
`MDLV30/STEBREL1 BONDS=(1 3)`:
```
InChI=1B/C2BrCl2F/c3-1(4)2(5)6/b2(2-1-)
```
Rule: each bond = canonical atom pair, **higher number first**, both signed `-`.

## Z4 — Enhanced AND (`/b3(…)`) — slide 28  (NOT IMPLEMENTED)
`MDLV30/STEBRAC1 BONDS=(1 3)`:
```
InChI=1B/C2BrCl2F/c3-1(4)2(5)6/b3(2-1-)
```

## Z5 — Multi-group stress case — slide 29  (NOT IMPLEMENTED)
`C18H19Br2Cl4F3N2O2`, one STEBREL1 (bonds=2), STEBRAC1 (bonds 16,20), STEBRAC2 (bond 26).
Expected `/b` fragment (as transcribed from the slide):
```
/b12-5+,2(16-14-),3(1(15-10-)(17-11-),2(18-13-))
```
i.e. absolute `12-5+`, then OR block `2(…)`, then AND block `3(…)` with nested group indices.
(Transcribed from slide text — re-verify atom numbers against the molfile when building.)

## Z6 — Combined double bond + tetrahedral — slide 30  (NOT IMPLEMENTED)
`C4H5BrClFO`, double bond 3–4 + tetrahedral centre 2:
```
STEABS bond + abs centre        → InChI=1S/C4H5BrClFO/c1-2(8)3(5)4(6)7/h2,8H,1H3/b4-3-/t2-/m1/s1
STEBREL2 bond + abs centre      → InChI=1S/C4H5BrClFO/c1-2(8)3(5)4(6)7/h2,8H,1H3/b2(4-3-)/t2-/m1/s1
STEBABS bond + STERAC1 centre   → InChI=1S/C4H5BrClFO/c1-2(8)3(5)4(6)7/h2,8H,1H3/b4-3-/t2-/s3
```
Confirms: double bonds group in `/b`, sp³ centres group in `/t`+`/s`, independently, in one
InChI. (`1B` prefix applies with enhanced stereo on.)

## To materialise
- [ ] `double_bond_ez_test_file_1.sdf` with records above + expected `<InChI_new>` columns
- [ ] `test_doubleBondEZ.cpp` asserting each; include Z1/Z2 regression for the classic path
- [ ] A round-trip test: parse an emitted `/b2(…)`/`/b3(…)` and reproduce it
