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

## 2026-08-10 additions (ES-R12 validation corpus)

`malformed/` — eight molfiles violating the [BIOVIA] one-group-per-centre / at-most-one-ABS
constraints: two real (attachments to `rdkit/rdkit#8873`), six derived from
`rdkit_two_centers_or.mol` by editing only the collection block. All eight measure "0 errors"
today. See [malformed/MALFORMED.md](malformed/MALFORMED.md) for per-file measurements, what
RDKit and Indigo do with the same input, and the correction to SPEC §5.H — the corruption
reaches `/t`, not just `/s`.

## 2026-08-10 — `enh_stereo_test_file_2.sdf` re-pinned (ES-R13)

The repo copy of the 35-molecule G5 fixture was re-pinned from measurement and the gate wired;
the copy in this directory is the **pre-repin** version and is kept as the historical record of
the hand-authored expectations. The repo also keeps one beside the fixture as
`enh_stereo_test_file_2.sdf.bak`, where it doubles as the negative control for the new G5 loop
(run against it, the loop reports 40 failures — exactly the 40 lines re-pinning changed).
Three classes of staleness: `/m` on the 8 OR/AND-only records, version prefixes on **all 35**,
and four wrong values. See SPEC §5 resolved-K.

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

## 2026-10-08 additions (1.0 multi-component audit, gate G11)

`multi_component/` — the structures behind SPEC §8. Each string there is measured on
`feature/enh-stereo-hardening`; G11 holds the same molecules inline.

| file | what it exercises | SPEC |
|------|-------------------|------|
| `01`–`07_*.mol` | pentan-2-ol + butan-2-ol, AND groups, Na⁺/OH⁻ or water spectators (third-party report) | §8.1–8.4, ES-R21–R25 |
| `chlorobutanol_abs_and_mirror.mol` | ABS-C2 + AND-C3, wedges down/up: the mirror image that collided | §8.2b, ES-R27 |
| `chlorobutanol_or_ungrouped.mol` | OR-C2, C3 wedged in no collection | §8.2b, ES-R24 |
| `mg_bis_butanolate_and_spanning.mol` | AND over two ligands of Mg: spans after metal disconnection | §8.4, ES-R23 |
| `mg_bis_butanolate_and_per_ligand.mol` | one AND group per ligand; with `-RecMet` | §8.4b, ES-R28 |
| `pt_haptic_and_spanning.mol` | AND over a haptic and an O-bound ligand of Pt | §8.4, ES-R23 |
| `butanediol_meso_and_per_centre.mol` | meso drawing, one AND group per centre | §8.4b, ES-R29 |
| `propanol_13C_or.mol` | centre stereogenic only through ¹³C, OR | §8.4b, ES-R30 |
| `chloromethylbutane_13C_and_or.mol` | AND on a main-layer centre, OR on an isotope-only one | §8.4b, ES-R30 |

## 2026-10-23 additions (1.3 meso groups, ES-R33)

`meso/` — the meso case John Mayfield raised in
[IUPAC-InChI/InChI#286](https://github.com/IUPAC-InChI/InChI/issues/286). Measured on
`atropisomers` 09043c1 (contains the ES-R33 fix).

| file | what it exercises | SPEC |
|------|-------------------|------|
| `meso/mol_file_2c.mol` | trans-cyclohexane-1,4-diol drawn in Indigo, one `STERAC1` over both centres (johnmay case 2c): `/t5-,6-` with `-EnhancedStereochemistry`, same as standard (`/t5-,6-/s3` before the fix) | §5 resolved-T, §8.4b, ES-R33 |

The other meso cases (2d, 2f, 2g and butane-2,3-diol) are inline molblocks in
`test_enhancedStereo.cpp` (`..._meso_group_is_dropped`, `DISABLED_..._meso_subset_group_is_dropped`)
and molecules 108–115 of the examples page.

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
