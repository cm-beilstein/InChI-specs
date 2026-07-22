# Atropisomer dataset gates

Canonical dataset lives in the repo test tree:
`INCHI-1-TEST/tests/test_unit/fixtures/atropisomers_test_file_1_v2.sdf` (and `_orig.sdf`).
Driven by `INCHI-1-TEST/tests/test_unit/test_atropisomers.cpp` (branch `atropisomers`).

## Labelled recall/negative set (Sub-project A — passing)

Referenced by molecule index in the design/tests:
- **mol 1–4** — canonical biaryl atropisomers → axis must be a candidate.
- **mol 12** — bridged biaryl, axis inside an **8-membered** ring → candidate (ring filter is
  `≤6` only; ≥7 rings remain candidates).
- **mol 13** — Caryophyllene, macrocyclic → stereo stays classical; must not change output.
- **mol 14** — biaryl (also the `test_dummy_14` end-to-end molecule).
- **mol 43** — `C14H26`, **fully acyclic** → central `C1–C2` axis is a candidate (proves no
  "must touch a ring" rule).
- **mol 44** — aryl `N,N`-dimethylamide (non-biaryl): `C3–C7` aryl–carbonyl axis → candidate;
  the symmetric amide `C7–N8` must be **pruned** in B (dissymmetry); flat/no-wedge → `?`.
- **Negative:** plain benzene / any ≤6-ring single bond → **not** flagged.

Gates T1–T5 (detection recall, negative guards, determinism/order-independence, parity unit,
string neutrality) pass on this set today. See [SPEC.md](../SPEC.md) §4.

## Encoding gate ([ATROP] §3 — Sub-project B, not yet met)

Reference biaryl `C12H6Br2Cl2`. Current (no axial layer):
```
InChI=1S/C12H6Br2Cl2/c13-7-3-1-5-9(15)11(7)12-8(14)4-2-6-10(12)16/h1-6H
```
Target with axial configuration (single, lower-numbered axis atom = 11):
```
InChI=1B/C12H6Br2Cl2/c13-7-3-1-5-9(15)11(7)12-8(14)4-2-6-10(12)16/h1-6H/t11-/m0/s1   (one isomer)
InChI=1B/C12H6Br2Cl2/c13-7-3-1-5-9(15)11(7)12-8(14)4-2-6-10(12)16/h1-6H/t11-/m1/s1   (enantiomer)
```
([ATROP] shows `1S`; with the beta/enhanced mechanism the prefix is `1B`.)

## Sub-project B invariant gates (to build)
- [ ] **Enantiomer pair (T6):** Ra and Sa of one skeleton → identical connectivity + `/t`,
      **opposite** `/m`.
- [ ] **Rotamer invariance:** two conformers (different torsion, incl. ~44° 3D) of the *same*
      enantiomer → **identical** InChI.
- [ ] **Round-trip:** parsing an emitted atropisomer InChI reproduces it.
- [ ] **Dissymmetry pruning:** mol 44 amide `C7–N8` dropped; mol 43 isopropyl branch bonds
      dropped; only genuine axes retained.
- [ ] **Single stereobond:** one-wedge biaryl draw defines the axis (shared with allenes).

## Notes
- The `_v2.sdf` fixture is opened via the `FIXTURES_DIR` CMake define (fixed on this branch);
  do not reintroduce the fixed `../../../../../` relative path.
- The 37 MB `2018-06-09-AJM_Atropisomerism_GM_website.pdf` is background (not machine-readable
  here); [ATROP] `.docx` is the authoritative recognition/encoding source.
