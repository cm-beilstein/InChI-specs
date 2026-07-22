# Allene dataset gates

No dedicated allene datasets exist in the repo test tree yet. The gates below are **seeded
from [DECK] slides 15–22** — the authoritative expected `1B` InChIs — and should be
materialised as a curated SDF (`allene_test_file_1.sdf`) plus a `test_allenes.cpp` harness.
The reference molecule throughout the deck is 1-bromo-1-fluoro-…-allene `C4H3BrClF`.

## A1 — Classic absolute axis (already works; needs an asserting test)

Expected (two enantiomers, [DECK] slide 17):
```
InChI=1S/C4H3BrClF/c1-3(6)2-4(5)7/h1H3/t2-/m0/s1
InChI=1S/C4H3BrClF/c1-3(6)2-4(5)7/h1H3/t2-/m1/s1
```
V3000 absolute molfile (slide 18, STEABS on the terminal); its InChI must equal the standard
form (proposal: "for abs axial enhanced stereochemistry use the standard InChI"):
```
  ACCLDraw07032617502D
 0  0  0     0  0            999 V3000
M  V30 BEGIN CTAB
M  V30 COUNTS 7 6 0 0 1
M  V30 BEGIN ATOM
M  V30 1 C 5.7812 -4.0938 0 0
M  V30 2 C 4.6005 -4.0938 0 0
M  V30 3 C 6.9621 -4.0938 0 0
M  V30 4 C 7.5524 -5.1163 0 0
M  V30 5 Cl 7.5524 -3.0712 0 0
M  V30 6 Br 4.0101 -5.1163 0 0
M  V30 7 F 4.0101 -3.0712 0 0
M  V30 END ATOM
M  V30 BEGIN BOND
M  V30 1 2 2 1
M  V30 2 2 1 3
M  V30 3 1 3 4
M  V30 4 1 3 5 CFG=1
M  V30 5 1 2 6 CFG=1
M  V30 6 1 2 7
M  V30 END BOND
M  V30 BEGIN COLLECTION
M  V30 MDLV30/STEABS ATOMS=(1 1)
M  V30 END COLLECTION
M  V30 END CTAB
M  END
```

## A3 — Single stereobond (currently unsupported; must become defined)

Per [ATROP]: a one-wedge allene that today yields the *stereo-free*
`InChI=1S/C3H2Br2/c4-2-1-3-5/h2-3H` must instead carry an axial `/t`. Seed with a `C4H3BrClF`
draw bearing a wedge on **one** terminal only; expected `…/t2-/m{0,1}/s1` for the two draws.

## A4 — Enhanced OR (`/s2`) — [DECK] slide 19

`MDLV30/STEREL1 ATOMS=(1 1)` (either CFG=3 or CFG=1 draw, both equivalent):
```
InChI=1S/C4H3BrClF/c1-3(6)2-4(5)7/h1H3/t2-/s2
```

## A5 — Enhanced AND (`/s3`) — [DECK] slide 20

`MDLV30/STERAC1 ATOMS=(1 1)`:
```
InChI=1S/C4H3BrClF/c1-3(6)2-4(5)7/h1H3/t2-/s3
```

## A6 — Combined allene + tetrahedral — [DECK] slide 22

`C5H5BrClFO`, allene central atom 2 + tetrahedral centre 3, three collection variants:
```
STEABS(1,6)          → InChI=1S/C5H5BrClFO/c1-3(9)4(7)2-5(6)8/h3,9H,1H3/t2-,3-/m1/s1
STEABS(6),STEREL1(1) → InChI=1S/C5H5BrClFO/c1-3(9)4(7)2-5(6)8/h3,9H,1H3/t2-,3-/m1/s1(3)2(2)
STEABS(1),STERAC1(6) → InChI=1S/C5H5BrClFO/c1-3(9)4(7)2-5(6)8/h3,9H,1H3/t2-,3-/m1/s1(2)3(3)
```
(Note the `1B` prefix applies once enhanced stereo is on; the deck shows `1S` on some slides
for the absolute-equivalent cases.)

## A-big — Complex multi-axis example — [DECK] slide 21

A `C24H21Cl6F3N6O3` hexaaryl example with mixed ABS/OR1/OR2/AND1/AND2 across six allene-like
arms; expected fragment `…/m0/s1(4),2(1,5),(3),3(2)(6)`. Use as a stress gate once A4–A6 pass.

## To materialise
- [ ] `allene_test_file_1.sdf` with the above records + expected `<InChI_new>` columns
- [ ] `test_allenes.cpp` asserting each, plus a Ra/Sa parity unit test and a rotamer-invariance
      test (drive two coordinate sets of one enantiomer → identical InChI)
