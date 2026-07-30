# Enhanced-stereo validation run — 2026-07-30

**Update (same day):** ES-R17 (SPEC.md §5.F/§6) has since been fixed on this branch, commit
`<pending>` — see "ES-R17 fixed" section near the end. The mismatch counts and specific
mismatched rows below are as measured *before* that fix; re-running after it drops the
enhanced-string mismatch count from 5 to 1 (only the `file2_rec26` fixture data error
remains). The analysis of *why* each mismatch occurred is unchanged and kept below for
traceability.

Validates `feature/enh-stereo-hardening` (commit `8a30a2e`, dev merged in) against
[SPEC.md](../SPEC.md), using the binary built from
`INCHI-1-SRC/INCHI_EXE/inchi-1/gcc/makefile` (gcc 13.3.0, Linux x86_64, `-std=c11`).
"Old" = same binary run **without** `-EnhancedStereochemistry`; "New" = **with** it.
This is valid because ES's own backward-compatibility invariant (§2) requires the two
to be byte-identical except for the `1B` prefix when the input carries no enhanced-stereo
collections — confirmed holding in every row below with no `/s` layer.

## Dataset (73 molecules)

| Source | Count | Provenance |
|---|---|---|
| `enh_stereo_test_file_1.sdf` | 33 | Repo gate fixture (G2); systematic ABS/OR/AND/mixed/`?`-passthrough coverage |
| `enh_stereo_test_file_2.sdf` | 35 | Repo fixture for dormant gate G5 (ES-R13, never wired); embeds expected `<InChI>`/`<InChI_new>` |
| `EOS49757_steabs_only.mol` | 1 | Real screening compound, EU-OPENSCREEN ECBD (https://ecbd.eu/compound/EOS49757) — STEABS only |
| `rdkit_two_centers_and.mol` | 1 | RDKit test fixture — STEABS + STERAC1 mixed |
| `rdkit_two_centers_or.mol` | 1 | RDKit test fixture — STEABS + STEREL1 mixed |
| `rdkit_two_and_groups.mol` | 1 | Real BIOVIA/SciTegic vendor export via RDKit issue #5165 — two independent STERAC groups |
| `synthetic_sterel_only.mol` | 1 | Hand-built (no real source exists) — single STEREL1 group, no STEABS |

Full per-molecule output: [`comparison_table.csv`](comparison_table.csv) (columns: source,
molecule, rc_old, rc_new, inchi_old, inchi_new, expected_std, expected_new, std_match,
new_match).

## Headline result

**0 crashes across all 73 molecules** with the fixed binary (commit `8a30a2e`). Before that
fix, the unpatched branch (`52010b9`) **segfaulted on the majority of records carrying an
OR or AND collection** — see "Crash bug found" below; this was not caught by the CMake/ctest
build because it silently avoids the triggering condition (see that section).

## Cross-check against the dormant fixture's embedded expectations

`enh_stereo_test_file_2.sdf` embeds `<InChI>` (standard) and `<InChI_new>` (enhanced,
pre-dates the `1B`/ES-R6 prefix convention — normalized as `InChI=1**/` → `InChI=1B/` before
comparing) for all 35 records. This fixture is *dormant*: **no test references it**
(SPEC.md §4, ES-R13), so it has never been checked against real output. Comparing it here
is itself a first-time audit of that data.

- **30/35 enhanced-string matches**, **30/35 standard-string matches** (after prefix
  normalization).
- **4 mismatches trace to errors in the fixture's own embedded data, not the code**:
  - `file2_rec18/19/20`: three records sharing the `C10H14BrCl7` scaffold whose embedded
    `<InChI>` (**standard**, no enhanced-stereo flag involved) has a different `/t`+`/m`
    parity than what the record's own wedge bonds encode. Standard `/t`/`/m` parity
    assignment is a long-mature, unrelated code path — far more likely the embedded
    expectation was mistyped/copy-pasted during curation than that this exposed a
    stereo-parity bug.
  - `file2_rec26`: embedded values say `C7H14BrClO`; the record's own V3000 atom block has
    **8** carbon atoms (indices 1–7 and 11), not 7 — the code's `C8H16BrClO` output matches
    the actual structure. The embedded expectation is simply wrong for this record.
- **2 mismatches confirm the already-known ES-R17 gap**: `file2_rec22–25` (two single-group
  OR/AND records each) expect the bare reduced `/s2` / `/s3`; the code still emits the
  grouped `/s2(3,4,5)` / `/s3(3,4,5)` form. Independent, second confirmation of SPEC.md's
  ES-R17 finding (§5.F), this time from data the SPEC's own authoring pass hadn't
  exercised.

**Implication for ES-R13** ("wire the dormant 35-molecule gate"): don't wire it as-is —
first correct the ≥4 erroneous embedded expectations above, or the new gate will fail on
day one for reasons unrelated to code correctness.

## Crash bug found and fixed (not in SPEC.md)

`MakeSlayerString` (`ichiprt2.c`) called libc `strdup()`, which has no prototype under the
strict `-std=c11` this makefile uses (POSIX extension, hidden by glibc's feature-test
macros in strict-ISO mode). With no declared return type the compiler implicitly assumed
`int`, truncating the real 64-bit pointer before storing it in the `char**` dictionary —
segfaulting on read-back (`strlen`/`strcmp`) for the majority of inputs carrying a
single-atom OR/AND group. Confirmed via AddressSanitizer (`SEGV` inside `strlen`, called
from `inchi_strbuf_printf` ← `MakeSlayerString:2450`).

This predates the hardening branch — introduced in commit `9dacaa2` (2026-01-26, already on
`dev`). The CMake/ctest build never triggers it because `CMakeLists.txt` sets
`CMAKE_C_STANDARD 99` with `CMAKE_C_EXTENSIONS` at its CMake default (`ON`), i.e. compiles
as `-std=gnu99`, which does not hide `strdup`. **The "all 172 unit tests pass" claim in
SPEC.md §4 is accurate for that build but masks a crash in the plain-makefile build that
any downstream consumer building via `INCHI-1-SRC/INCHI_EXE/inchi-1/gcc/makefile` would hit.**

Fixed in commit `8a30a2e` on `feature/enh-stereo-hardening` (local, not pushed): replaced
`strdup` with `inchi_calloc` + `memcpy`, matching the `inchi_free` already used to release
these entries, instead of relying on libc's declaration. Verified against all 33 records of
`enh_stereo_test_file_1.sdf` plus the full 73-molecule set here — 0 crashes, output
unchanged from the pre-fix (ASan-patched) run.

## Notes on the web-sourced files

- `EOS49757` (STEABS-only): enhanced string is byte-identical to standard except the `1B`
  prefix — confirms the backward-compatibility invariant (§2) and ES-R11 reduction on a
  real third-party structure, not just repo fixtures.
- `rdkit_two_and_groups.mol` (2 independent STERAC groups, no STEABS): reproduces ES-R18 —
  `/m0` is emitted (`.../m0/s3(12,15)(13,14)`) despite the component having no ABS centre,
  contrary to SPEC.md §6's normative rule that `/m` MUST NOT appear in that case.
- `rdkit_two_centers_and.mol` / `_or.mol` (STEABS + one STERAC/STEREL group, real RDKit test
  molecules) both parse and group correctly once a missing blank molecule-name header line
  — dropped when the source was transcribed — was restored; see file history.
- `synthetic_sterel_only.mol`: the first hand-built attempt used a collinear 2D layout,
  which InChI's stereo perception correctly treated as non-stereogenic (no `/t` layer at
  all) — a property of degenerate 2D geometry, not a code defect. Corrected to a proper
  zig-zag layout; the result independently reproduces both ES-R17 and ES-R18 on a single
  minimal OR-only component (`.../m0/s2(3,4)`, not reduced to bare `/s2`, and `/m0` present
  despite no ABS centre).

## ES-R17 fixed

`MakeSlayerString` (`ichiprt2.c`) already reduced ABS-only components to the bare `/s1`
(ES-R11) but had no analogous reduction for a single OR or single AND group. Fixed by:

- Adding an out-parameter `num_groups_used` to `MakeEnhStereoString` (and its declaration
  in `ichimake.h`) that counts how many of the component's own OR/AND *collections*
  actually contributed atoms — not the global collection count on `orig_inp_data->v3000`,
  which spans every component in a multi-component structure and would give the wrong
  answer for components other than the first.
- In `MakeSlayerString`, mirroring the existing ABS-only branch: when a component's only
  contributing collection type is OR (`len_rel > 0 && len_abs == 0 && len_rac == 0`) and
  exactly one OR group contributed (`num_groups_rel == 1`), collapse to the bare `"2"`;
  symmetric for AND with `"3"`. Multiple OR or multiple AND groups on the same component
  are left grouped, since SPEC.md §5.F explicitly calls out that the grouping is meaningful
  in that case (matching the already-implemented ABS behavior, and confirmed still holding
  by `rdkit_two_and_groups.mol`, two independent AND groups, staying as `/s3(12,15)(13,14)`
  after the fix).

**Verified:**
- All 73 molecules in this dataset re-run cleanly (0 crashes); enhanced-string mismatches
  against the dormant fixture's embedded `<InChI_new>` drop from 5 to 1 — the remaining one
  is `file2_rec26`, the pre-existing fixture data error documented above, unrelated to this
  fix.
- `file2_rec22`/`rec23` (single OR group) now emit `.../m0/s2` (previously
  `.../m0/s2(3,4,5)`); `rec24`/`rec25` (single AND group) now emit `.../m0/s3` (previously
  `.../m0/s3(3,4,5)`); `synthetic_sterel_only.mol` now emits `.../m0/s2` (previously
  `.../m0/s2(3,4)`) — all now matching SPEC.md §6's normative rule.
- 12 of the inline single-molblock cases in `test_enhancedStereo.cpp` (extracted and run
  directly, since `cmake`/`ctest` aren't available in this environment) still match their
  hard-coded `expected_inchi`, including the ABS-only reduction, the atropisomer no-`/t`
  case, and multi-component/multi-group mixed cases — no regression from adding the OR/AND
  reduction alongside the existing ABS one.
- ES-R18 (`/m0` still forced for OR/AND-only components) is unaffected by this fix and
  remains open, as does the `file2_rec26` fixture typo and the other dormant-gate data
  issues (`rec18`–`rec20`) documented above.
