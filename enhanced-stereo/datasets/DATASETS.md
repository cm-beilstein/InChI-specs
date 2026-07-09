# Enhanced-stereo dataset gates

Canonical datasets live in the InChI repo test tree (not duplicated here to avoid drift).
Paths are relative to the repo root `INCHI-1-TEST/tests/test_unit/`.

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

## Reference molfile from [BIOVIA] Appendix B (materialisable gate)

The BIOVIA white paper Appendix B contains a complete 29-atom V3000 molfile mixing all group
types in one structure:
```
M V30 MDLV30/STEABS  ATOMS=(1 17)
M V30 MDLV30/STEREL2 ATOMS=(2 6 7)
M V30 MDLV30/STEREL1 ATOMS=(2 22 23)
M V30 MDLV30/STERAC2 ATOMS=(1 2)
M V30 MDLV30/STERAC1 ATOMS=(1 21)
```
Full molblock is in the extracted `pdf_biovia.txt` (Appendix B). Materialise it as a gate,
compute its expected `1B` InChI once, and pin it — a good independent cross-check of the
grouping/ordering logic against a third-party authority.

## Build & run

```bash
cmake -S <repo> -B <build> -DCMAKE_BUILD_TYPE=Release
cmake --build <build> --target test_enhancedStereo test_strutil_enhancedStereo test_ichiprt1_enhancedStereo -j"$(nproc)"
# from a path where the fixture resolves:
<build>/INCHI-1-TEST/tests/test_unit/test_enhancedStereo
```
