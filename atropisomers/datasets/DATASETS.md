# Atropisomer dataset gates

Canonical dataset lives in the repo test tree:
`INCHI-1-TEST/tests/test_unit/fixtures/atropisomers_test_file_1_v2.sdf` (and `_orig.sdf`).
Driven by `INCHI-1-TEST/tests/test_unit/test_atropisomers.cpp` (branch `atropisomers`).

## Labelled recall/negative set (Sub-project A — passing)

Every record carries `ID`, `Isomer` (`<skeleton>-M|P|0`), `IUPAC Name` and `Comment` data
fields; the `Isomer` label is the oracle for the B gates (M → `/m0`, P → `/m1`, 0 → no layer).

Referenced by molecule index in the design/tests:
- **mol 1–4** — canonical biaryl atropisomers → axis must be a candidate.
- **mol 12** — bridged biaryl, axis inside an **8-membered** ring → candidate (ring filter is
  `≤6` only; ≥7 rings remain candidates).
- **mol 13** — Caryophyllene, macrocyclic → stereo stays classical; must not change output.
- **mol 14** — biaryl (also the `test_dummy_14` end-to-end molecule).
- **mol 43** — `C14H26`, **fully acyclic** → central `C1–C2` axis is a candidate (proves no
  "must touch a ring" rule).
- **mol 44** — aryl `N,N`-dimethylamide (non-biaryl): `C3–C7` aryl–carbonyl axis → candidate
  and emitted (`/t11-/m1/s1`, the drawing has a wedge); the amide `C7–N8` is C–N (out of v1
  scope) and symmetric anyway.
- **Negative:** plain benzene / any ≤6-ring single bond → **not** flagged.

Gates T1–T5 (detection recall, negative guards, determinism/order-independence, parity unit,
string neutrality) pass on this set today. See [SPEC.md](../SPEC.md) §4.

## Encoding gate ([ATROP] §3 — Sub-project B, met)

Reference biaryl `C12H6Br2Cl2`. Standard InChI (option off):
```
InChI=1S/C12H6Br2Cl2/c13-7-3-1-5-9(15)11(7)12-8(14)4-2-6-10(12)16/h1-6H
```
With `-Atropisomers` (single, lower-numbered axis atom = 11; dataset mols 7 and 36):
```
InChI=1B/C12H6Br2Cl2/c13-7-3-1-5-9(15)11(7)12-8(14)4-2-6-10(12)16/h1-6H/t11-/m0/s1   (one isomer)
InChI=1B/C12H6Br2Cl2/c13-7-3-1-5-9(15)11(7)12-8(14)4-2-6-10(12)16/h1-6H/t11-/m1/s1   (enantiomer)
```
([ATROP] shows `1S`; with the beta/enhanced mechanism the prefix is `1B`.)

## Sub-project B invariant gates (`test_atropisomers`, 33/33)
- [x] **Enantiomer pair (T6):** `gate_t6_enantiomer_flips_m` — wedges mirrored → `/m0` ↔ `/m1`.
      Whole dataset: skeleton 1 (mols 1–6, 39, 40), 2 (7–14, 36–38), 3 (17–21, 41, 42),
      4 (22–26) — every `M` → `/m0`, every `P` → `/m1`, 2D and 3D alike.
- [x] **Rotamer invariance:** `gate_t6_rotamers_one_inchi` — generated 3D
      2,2'-dibromo-6,6'-dichlorobiphenyl at 44°, 90°, 120° → one InChI; −44° → the enantiomer.
      Mols 7–14 (eight drawings of 2-M) → one InChI.
- [ ] **Round-trip:** reparse of the emitted InChI — open (InChI→structure engine).
- [x] **Dissymmetry pruning:** `dissymmetry_symmetric_end_pruned` (2,6-dichloro end);
      mol 43 isopropyl branch bonds dropped, central `C13–C14` kept (`/t13-/m1/s1`).
- [x] **Hindrance:** `unhindered_axis_not_emitted` — mols 34/35 (3,3'-bipyridine, wedge drawn)
      get no layer; the file's own comment ("not sure, we can demand more substituents") agrees.
- [x] **Single stereobond:** `single_wedge_defines_axis`; `flat_axis_is_omitted` (no wedge →
      omitted + "Omitted undefined stereo" warning).
- [x] **Backward compatibility:** `standard_output_unchanged`; CLI diff of
      `InChI_TestSet_ext.sdf` (2188) and all fixtures, no option and `-EnhancedStereochemistry`
      — zero differences.

## Dataset records that stay without an axial layer (by design)
- **mols 15/16** (`2-0`): both wedges on the same side of the axis → degenerate geometry →
  undefined → omitted (warning).
- **mols 27/28/33/45** C–N, **29/30** N–N axes: deferred (AT-R11). Mol 45 keeps its sp³ `/t12-`.
- **mols 31/32**: no atropisomer; unchanged.
- **mols 46–49** (`Z,M` …): overcrowded alkene — the chirality axis is the C=C bond in a fused
  system, no single-bond candidate; only `/b24-23±` emitted.
- **mol 22–26** (`8aM/P`): axis `/t19-` plus two undefined sp³ ring-fusion centres now shown as
  `15?,16?` (standard InChI rule once a defined element exists).

## Notes
- The `_v2.sdf` fixture is opened via the `FIXTURES_DIR` CMake define (fixed on this branch);
  do not reintroduce the fixed `../../../../../` relative path.
- The 37 MB `2018-06-09-AJM_Atropisomerism_GM_website.pdf` is background (not machine-readable
  here); [ATROP] `.docx` is the authoritative recognition/encoding source.
