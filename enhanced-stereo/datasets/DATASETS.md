# Enhanced-stereo dataset gates

Canonical datasets live in the InChI repo test tree; copies are kept in this directory
(alongside independently-sourced molfiles) so validation runs here don't depend on the
repo checkout layout. Paths below are relative to the repo root
`INCHI-1-TEST/tests/test_unit/` unless noted otherwise.

## 2026-07-30 validation run

See [VALIDATION_RESULTS.md](VALIDATION_RESULTS.md) for the full writeup (73-molecule
old-vs-new comparison, a crash bug found + fixed, and an audit of the dormant G5 fixture's
embedded expectations) and [comparison_table.csv](comparison_table.csv) for the raw
per-molecule table. Files added to this directory for that run:

- `enh_stereo_test_file_1.sdf`, `enh_stereo_test_file_2.sdf` — copies of the repo fixtures
  below, used directly (not duplicated logic, just co-located for the run).
- `EOS49757_steabs_only.mol` — real screening compound (EU-OPENSCREEN ECBD), STEABS-only.
- `rdkit_two_centers_and.mol`, `rdkit_two_centers_or.mol` — real RDKit test fixtures,
  STEABS + one STERAC/STEREL group each.
- `rdkit_two_and_groups.mol` — real BIOVIA/SciTegic vendor export (via RDKit issue #5165),
  two independent STERAC groups, no STEABS.
- `synthetic_sterel_only.mol` — hand-built, single STEREL1 group, no STEABS. Kept as the
  smallest OR-only case; the "no real STEREL-only file could be found publicly" caveat that
  motivated it no longer holds, see the 2026-08-07 additions below.

## 2026-08-07 additions (ES-R18 verification, third-party sources)

Collected while implementing ES-R18 (no `/m` for OR/AND-only components). All were fetched
from public repositories and re-measured against this build; provenance URLs are given so the
originals can be re-fetched. The five ABS-free files are the independent evidence for ES-R18 —
each is byte-identical to its `-SRel` / `-SRac` counterpart apart from the version prefix
(except `indigo_rel_and_rac.mol`, which carries two classes and so keeps its grouping).

| File | Source | Collections | Enhanced output |
|------|--------|-------------|-----------------|
| `indigo_sterel_only.mol` | [epam/Indigo] `data/molecules/stereo/enhanced_stereo2.mol` | `STEREL1(3)` | `/t8-/s2`, == `-SRel` |
| `indigo_rel_and_rac.mol` | [epam/Indigo] `data/molecules/stereo/enhanced_stereo3.mol` | `STEREL1(3)` + `STERAC1(4)` | `/t7-,9-/s2(9)3(7)` |
| `ketcher_or_enantiomer.mol` | [epam/ketcher] `ketcher-autotests/tests/test-data/Molfiles-V3000/or-enantiomer.mol` | `STEREL1(5)` | `/t4-/s2`, == `-SRel` |
| `openchemlib_cyclosporin_rac.mol` | [cheminfo/openchemlib-utils] `benchmark/data/cyclosporin.mol` | `STERAC1` over **12** atoms | `/t40-,41+,…,52-/s3`, == `-SRac` |
| `cdpkit_chembl_sterel_only.mol` | [molinfo-vienna/CDPKit] `Data/Testing/ChEMBLStandardizerTestData.sdf` (the one record carrying a collection) | `STEREL1(1,2)` | `/t13-,15-/s2`, == `-SRel` |
| `indigo_stereogroups_abs_rac.mol` | [epam/lifescience] `rst/indigo/release-notes/1.1.x/data/stereogroups.mol` | `STEABS` + `STERAC1` + `STERAC2` | `/t10-,11-,12-/m1/s1(11)3(10)(12)` |
| `biovia_white_paper_fig22.mol` | [mn-am/corina-classic-python] `python/MDL_white_paper_fig22.v3000.sdf` | all five types | see **gate G9** below |

Why these matter beyond ES-R18:
- `openchemlib_cyclosporin_rac.mol` is a real drug with **12 stereocentres in one AND group**,
  reducing to the bare `/s3` — the ES-R17 reduction at a scale nothing else here reaches.
- `indigo_rel_and_rac.mol` is the only real file with **two classes and no ABS**.
- `ketcher_or_enantiomer.mol`, `indigo_sterel_only.mol` and `cdpkit_chembl_sterel_only.mol` are
  three independent **real** STEREL-only files.
- Sanity contrast: `epam/Indigo` `api/tests/integration/tests/formats/molecules/non_atrop.mol`
  puts `STEREL1` on a non-stereogenic atom and correctly yields no `/t` and no `/s` at all
  (not persisted; noted because it bounds the orphan-`/s`-group defect, see SPEC §5).

Extraction notes (both are upstream transcription artefacts, not InChI bugs):
- `biovia_white_paper_fig22.mol` — the upstream file terminates with `M END` (one space)
  instead of `M  END`, which InChI rejects with `Error 64 (no InChI; Unknown error)`. Corrected
  here, and the trailing SDF `$$$$` dropped so the `.mol` extension is honest.
- `cdpkit_chembl_sterel_only.mol` — extracted from a multi-record SDF; the record's empty title
  line must be preserved or the 4-line molfile header is short and the counts line is
  misparsed (`Fatal Error 3 ... Cannot interpret counts line`).

[epam/Indigo]: https://github.com/epam/Indigo
[epam/ketcher]: https://github.com/epam/ketcher
[epam/lifescience]: https://github.com/epam/lifescience
[cheminfo/openchemlib-utils]: https://github.com/cheminfo/openchemlib-utils
[molinfo-vienna/CDPKit]: https://github.com/molinfo-vienna/CDPKit
[mn-am/corina-classic-python]: https://github.com/mn-am/corina-classic-python

## Active gates

### `fixtures/enh_stereo_test_file_1.sdf` — 33 molecules (**gate G2**)
- Driven by `test_enhancedStereo.cpp::test_EnhancedStereochemistry_test_file_1`.
- Expected InChIs are hard-coded in the test (`list_expected_inchis[33]`, ~`:1158-1192`),
  **not** embedded in the SDF. 24 of the 33 records carry a `BEGIN COLLECTION` block; the
  first has none (pure-standard ⇒ `/s1`).
- Systematically exercises: `m0`/`m1` flips, `?` undefined-centre passthrough, and the
  `/s1`,`/s2`,`/s3` reductions. Representative expected values:
  - only-OR: `…/t4-/m0/s2(4)`
  - only-AND: `…/s3(4,5)`
  - mixed ABS+OR+AND: `…/m0/s1(4)2(5)3(6)`
- **Run tip:** the test opens the file with a fixed relative path; run the binary from a cwd
  where `../../../../../INCHI-1-TEST/…` resolves, or apply the `FIXTURES_DIR` CMake fix.

### Inline molblocks in `test_enhancedStereo.cpp` (**gate G1**, 13 cases)
Key expected strings (option `-EnhancedStereochemistry`):
- `test_EnhancedStereochemistry_1`:
  `InChI=1B/C10H14BrCl7/…/t3-,4-,5+,6-,7-,8-,9+,10-/m0/s1(3,5)2(4)(6,8)3(7,9)(10)`
- `test_EnhancedStereochemistry_2_atropisomer`: `InChI=1B/C12H6Br2Cl2/…` — **no `/t`/`/s`
  layer** (confirms non-tetrahedral enhanced stereo is not yet emitted; ties to spec 4).
- multi-component: `2C10H14BrCl7 → …/m00/s2*1(3,5)2(4)(6,8)3(7,9)(10)`.

### Unit gates
- `test_strutil_enhancedStereo.cpp` (**G3**, 4 tests) — `set_EnhancedStereo_t_m_layers`,
  `invert_parities`, `get_canonical_atom_number`, `get_parity_idx_from_canonical_atom_number`.
- `test_ichiprt1_enhancedStereo.cpp` (**G4**, 1 test) — asserts `MakeSlayerString` →
  `/s1(1,2)2(6,7)(8)3(3)(4,5)`.

## Dormant gate to activate

### `fixtures/enh_stereo_test_file_2.sdf` — 35 molecules (**gate G5, not yet wired**)
- Unlike file_1, this SDF **embeds** the expected values as data columns:
  `>  <InChI>` (standard), `>  <InChI_new>` (enhanced), `>  <Isomer>`.
- No test references it. **Deliverable:** add a test that, for each record, runs
  `-EnhancedStereochemistry` and asserts the emitted string equals the `<InChI_new>` column
  (and the plain run equals `<InChI>`). This turns 35 curated molecules into a live gate.

## Reference molfile from [BIOVIA] Appendix B — **gate G9, wired**

The BIOVIA white paper Appendix B contains a complete 29-atom V3000 molfile mixing all group
types in one structure:
```
M V30 MDLV30/STEABS  ATOMS=(1 17)
M V30 MDLV30/STEREL2 ATOMS=(2 6 7)
M V30 MDLV30/STEREL1 ATOMS=(2 22 23)
M V30 MDLV30/STERAC2 ATOMS=(1 2)
M V30 MDLV30/STERAC1 ATOMS=(1 21)
```
This is no longer a to-do. The same molfile was located in the wild as
`MDL_white_paper_fig22.v3000.sdf` ([mn-am/corina-classic-python], fig. 22 of the white paper) —
29 atoms, 32 bonds, collection block matching the listing above line for line. It is persisted
here as `biovia_white_paper_fig22.mol` and pinned as a gate:

- Driven by `test_enhancedStereo.cpp::test_EnhancedStereochemistry_biovia_appendix_b`
  (molblock inline, so it does not depend on the fragile fixture path — ES-R15).
- Measured and pinned:
  ```
  InChI=1B/C24H34N2O3/…/t13-,14-,15-,17-,18-,21-,23+/m1/s1(15)2(13,14)(21,23)3(17)(18)
  ```
- What it independently cross-checks against a third-party authority, in one structure:
  ABS `(15)` from `STEABS(17)`; two OR groups `(13,14)` and `(21,23)`; two AND groups `(17)`
  and `(18)`; `/m1` **present** because an ABS collection exists (ES-R18 negative control);
  neither the two OR nor the two AND groups reduced (ES-R17 over-reduction guard); and every
  one of the five groups with its lowest-numbered centre normalised to `-`.
- See the extraction note above: the upstream `M END` must be corrected to `M  END`.

## Build & run

```bash
cmake -S <repo> -B <build> -DCMAKE_BUILD_TYPE=Release
cmake --build <build> --target test_enhancedStereo test_strutil_enhancedStereo test_ichiprt1_enhancedStereo -j"$(nproc)"
# from a path where the fixture resolves:
<build>/INCHI-1-TEST/tests/test_unit/test_enhancedStereo
```
