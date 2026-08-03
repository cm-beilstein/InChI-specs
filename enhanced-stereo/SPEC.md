# Spec 1 — Enhanced Stereochemistry (V3000 ABS/OR/AND, tetrahedral centres)

| | |
|---|---|
| **Doc version** | 0.5 |
| **Date** | 2026-08-03 |
| **Status** | draft |
| **Author** | C. Müller |
| **Reviewers** | TBD (InChI Trust / project 2019-017-2-800 TG) |
| **Requirement prefix** | `ES-` |
| **Change history** | 0.1 (2026-07-09) — initial spec; verified against `dev`, incl. [BIOVIA]. 0.2 (2026-07-10) — consolidated: requirements/gates/deliverables/NFRs merged into one table (§4); ABNF grammar retained (§6). 0.3 (2026-07-10) — readability pass: added At-a-glance, split requirements from gates, tightened prose. 0.4 (2026-07-28) — ES-R11, ES-R14 and §5.E implemented on `feature/enh-stereo-hardening`; measurement of OR-only/AND-only output added two grammar-conformance gaps (ES-R17, ES-R18). 0.5 (2026-08-03) — full re-audit of `feature/enh-stereo-hardening` by reading + measuring: ES-R17 is implemented and gated (G7 half-satisfied); two defects the spec did not know about found, reproduced and fixed (ES-R19 V2000 crash, ES-R20 collection atom-remap off-by-two, commit `f4268f6`); test counts refreshed to 17 suites / 179 tests. |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

- ✅ **Works (end-to-end):** parse V3000 STEABS/STEREL#/STERAC# → `/t`+`/m` normalisation →
  grouped `/s1(…)2(…)3(…)` emission, incl. **all three** single-class reductions
  (`/s1`, `/s2`, `/s3`) and multi-component. Tested (G1–G4, G6, G8 pass; G7 half).
- ❌ **Missing:** the `/m`-with-only-OR/AND rule (ES-R18) — the last §6 MUST the code does not
  meet; one-group-per-centre enforcement (ES-R12); the dormant 35-molecule gate (ES-R13).
- ▶ **Next:** settle ES-R18 — the last open §6 conformance question — then ES-R12 (malformed
  input currently corrupts `/t` and `/s`, §5.H) and the dormant `enh_stereo_test_file_2.sdf` gate.

**Feature:** recognise MDL V3000 enhanced-stereo collections (STEABS / STEREL# / STERAC#) on
sp³ tetrahedral centres and encode them in an extended, grouped `/s` layer. · **Branch:** `dev`
· **Option:** `-EnhancedStereochemistry` · **Prefix:** `InChI=1B/…` · **Sources:** [STRING-ALG],
[DECK] slides 6–12, [BIOVIA] (authoritative ESR semantics), [BNF], [ESR].

---

## 1. Problem

Industrial structure files use MDL V3000 *enhanced stereochemical representation* (ESR) to
express partially-known stereochemistry: each stereocentre is tagged **abs** (absolute),
**or#** (one of two enantiomers — relative), or **and#** (both — racemic), with a group index
tying dependent centres together. Standard InChI ignores these collections and treats every
centre as absolute — so distinct substances (e.g. the cypermethrin family, [ESR]) collapse to
one identifier.

## 2. Target behaviour

From [STRING-ALG] and [DECK]. The normative encoding grammar is in §6; the behavioural rules:

- Parse V3000 `M V30 BEGIN COLLECTION` groups `MDLV30/STEABS`, `MDLV30/STEREL#`,
  `MDLV30/STERAC#` over `ATOMS=(n a1 a2 …)`.
- Emit an extended `/s` layer grouping the canonical atom numbers by type:
  `1`=ABS, `2`=OR, `3`=AND, e.g.

  ```
  InChI=1B/C10H20BrClINO2/c…/t4-,5-,6-,7+,8-,9-,10+/m0/s1(5,7)2(8,10)(9)3(4)(6)
  ```

- Rules (see [README](../README.md#common-encoding-conventions)): `/m` only with ABS;
  reductions to `SAbs`/`SRel`/`SRac` when a single class is present; within-group ascending
  order; groups ordered by smallest canonical atom; lowest centre in each group normalised
  to `-` (whole-group sign flip, ABS also toggles `/m`).
- Worked reference cases with expected strings: [STRING-ALG] "Only ABS / Only OR / Only AND"
  edge tables; [DECK] slide 9 (`/s1(5,7)2(8,10)(9)3(4)(6)`) and slide 12.

**Input constraints (authoritative, [BIOVIA]):**
- A stereogenic centre belongs to **exactly one** stereochemical group. A structure may
  contain **at most one ABS collection** but **multiple OR# and AND# groups**. Centres not in
  any collection (no wedge) are unknown/undefined (`?`). Conflicting membership is malformed
  input — the reader must reject or diagnose it, not silently pick one.
- Semantics: OR = "one stereoisomer, as-drawn *or* its epimer" (relative); AND = "as-drawn
  *and* its enantiomer" (racemic). Molfile keywords `STEABS` / `STERELn` / `STERACn` map to
  display labels `abs` / `orn` / `&n`. [BIOVIA] Appendix B is a full worked example V3000
  molfile (STEABS + STEREL1/2 + STERAC1/2) usable as an extra gate.

**Invariants (all MUST):**
- *Backward compatibility* — with `-EnhancedStereochemistry` off, output is byte-identical to
  standard InChI; with it on, an all-absolute structure MUST equal the standard string except
  the `1B` prefix ✅ *(held for explicit STEABS-only since ES-R11; gate G6)*.
- *Determinism* — identical input ⇒ identical output, order-independent of input atom order
  ✅ *(held since ES-R20; collection atom numbers were previously mis-remapped when the molfile
  did not number its atoms 1..n)*.
- *Robustness* — malformed/empty/out-of-range collections MUST NOT crash and MUST degrade
  gracefully; the per-component `/s` substring dictionary MUST NOT drop components ✅ *(it is
  sized from the component count, so no cap exists; ES-R14)*. Input without a V3000 collection
  block MUST NOT crash either ✅ *(ES-R19)*.
- *Performance (SHOULD)* — `/s` construction SHOULD be ≤ O(n·log n) in centres ✅ *(orig→canon
  reverse map replaced the linear scans; §5 resolved-E)*.
- *Portability* — tests MUST resolve fixtures independent of build layout *(gap: §5.B)*.

## 3. Current implementation (branch `feature/enh-stereo-hardening`, verified by reading + running tests)

| Stage | Location | State |
|-------|----------|-------|
| V3000 COLLECTION parse (STEABS/STEREL#/STERAC#, `ATOMS=()`, group #) | `mol_fmt3.c:647` `MolfileV3000ReadCollections`, dispatch `:695-729`, atoms `:738-782` | ✅ done; non-stereo collections skipped; atom-number remap fixed (ES-R20) |
| Storage | `inpdef.h:396-404` `OAD_V3000.lists_steabs/sterel/sterac` | ✅ |
| Transfer molfile→`ORIG_ATOM_DATA.v3000` | `mol2atom.c:1646-1712`; component split `runichi3.c:359-395`; free `mol2atom.c:1421-1452` | ✅ |
| Option `-EnhancedStereochemistry` → `ip->bEnhancedStereo` | `ichiparm.c:273-275,2144` | ✅ |
| `1B` beta prefix | `ichiprt1.c:3119` `OutputINCHI_VersionAndKind`, `is_beta` set `:1713-1715`, `B` appended `:3132-3135` | ✅ |
| `/t`+`/m` sign-normalisation | `strutil.c` `set_EnhancedStereo_t_m_layers`, `invert_parities` (min-canon centre → `-`, whole-group flip; ABS toggles `nCompInv2Abs`; force `m0` when only OR/AND) | ✅ works, but the forced `m0` contradicts §6 → ES-R18 |
| Grouped `/s` emission | `ichiprt1.c:3496` `OutputINCHI_StereoLayer_EnhancedStereo` → `ichiprt2.c` `MakeSlayerString` → `MakeEnhStereoString` (type digit, canon-atom map, within-group + inter-group sort, parenthesised groups) | ✅ matches target ordering |
| ABS-only reduction to bare `/s1` | `ichiprt2.c` `MakeSlayerString` (per-sublayer lengths; ABS-only ⇒ bare type digit) | ✅ ES-R11 |
| Single-OR / single-AND reduction to bare `/s2` / `/s3` | `ichiprt2.c` `MakeSlayerString` (guarded by `num_groups_used` from `MakeEnhStereoString`, so ≥2 groups stay grouped) | ✅ ES-R17 |
| `/s` emission guarded against absent V3000 data | `ichiprt1.c` `OutputINCHI_StereoLayer_EnhancedStereo` (`orig_inp_data->v3000` NULL ⇒ plain stereo-type digit) | ✅ ES-R19 |
| Per-component `/s` substring dictionary | `ichiprt2.c` `MakeSlayerString` (sized from `num_components`; dense `n_entries` index) | ✅ ES-R14 — no cap, nothing droppable |
| orig→canon reverse map | `strutil.c` `make_orig_to_canon_map` / `lookup_canonical_atom_number`, used by `invert_parities` + `MakeEnhStereoString` | ✅ replaces the O(n²) scans |
| Multi-component `count*substr` + `;` (beyond single-molecule spec) | `ichiprt2.c` `MakeSlayerString` emit loop | ✅ present + tested (extension) |

Line numbers are omitted for the functions touched on this branch; they move. Grep the
function names.

Applies to **sp³ tetrahedral `/t` centres only**; E/Z, allene and atropisomer centres are
not grouped (see specs 2–4).

## 4. Requirements

Priority is MoSCoW. The core works end-to-end; the one open Must-have (ES-R18) is a
conformance gap against §6 found by measuring OR-only/AND-only output, not a missing feature.
**Won't (this spec):** name-level `rac`/`rel` nomenclature and independent-centre superscripts ([ESR]/[BNF])
— IUPAC nomenclature recommendations, not InChI code.

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| ES-R1 | Parse STEABS/STEREL#/STERAC# `ATOMS=()` | Must | ✅ `mol_fmt3.c:647` (see ES-R20) |
| ES-R2 | Grouped `/s1(…)2(…)3(…)` emission | Must | ✅ `MakeEnhStereoString` / `MakeSlayerString` |
| ES-R3 | Within-/inter-group ordering | Must | ✅ `MakeEnhStereoString` (`qsort` on canon numbers) |
| ES-R4 | Sign normalisation + `/m` coupling to ABS | Must | ✅ `invert_parities` — but see ES-R18 |
| ES-R5 | Reductions (only-ABS ⇒ `/s1`, only-OR ⇒ `/s2`, only-AND ⇒ `/s3`) | Must | ✅ complete — ABS (ES-R11), single OR/AND (ES-R17) |
| ES-R6 | `-EnhancedStereochemistry` + `1B` prefix | Must | ✅ `ichiparm.c:273` |
| ES-R7 | Multi-component `count*substring` / `;` composition | Should | ✅ `MakeSlayerString` emit loop |
| ES-R11 | Explicit-STEABS-only ⇒ bare `/s1` (== `SAbs`) | Should | ✅ done + gated (G6) |
| ES-R12 | Enforce one-group-per-centre / at-most-one-ABS; reject conflicts | Must | ❌ not implemented — malformed input silently corrupts `/t` and `/s` *(§5.H; raised from Should)* |
| ES-R13 | Wire `enh_stereo_test_file_2.sdf` gate (35 mol) | Should | ❌ dormant |
| ES-R14 | No component may be dropped from the `/s` substring dictionary | Should | ✅ done — dictionary sized from `num_components`; the fixed cap is gone |
| ES-R15 | Fixture-path robustness (`FIXTURES_DIR` CMake define) | Should | ❌ port from `atropisomers` *(§5.B)* |
| ES-R16 | Propagate `set_EnhancedStereo_t_m_layers` sub-call failures | Could | ❌ returns `0` always *(§5.D)* |
| ES-R17 | Single-OR ⇒ bare `/s2`, single-AND ⇒ bare `/s3` (§6 MUST) | Must | ✅ done + gated (G7 partial, G4) — ≥2 groups stay grouped |
| ES-R18 | No `/m` when a component has only OR/AND centres (§6 MUST) | Must | ❌ `m0` is forced instead *(§5.G)* |
| ES-R19 | `-EnhancedStereochemistry` MUST NOT crash on input without V3000 collections | Must | ✅ done + gated (G8) — was a segfault *(§5, resolved-I)* |
| ES-R20 | Collection atom numbers MUST be remapped regardless of molfile atom numbering | Must | ✅ done + gated (G8) — was an off-by-two *(§5, resolved-J)* |

### Gates

Datasets live in the repo test tree; see [datasets/DATASETS.md](datasets/DATASETS.md) for
per-molecule detail.

- **G1** — 14 inline ABS/OR/AND cases in `test_enhancedStereo.cpp`. ✅ **14/14 pass**.
  `test_EnhancedStereochemistry_4_mols` had recorded the pre-ES-R11 `/s1(8,9,10,11);…` for a
  component whose single stereocentre is ABS; its expectation is now the reduced `/s1;…`.
- **G2** — 33-molecule `enh_stereo_test_file_1.sdf` (m0/m1 flips, `?` passthrough, reductions).
  ✅ **passes** (when fixture path resolves — §5.B).
- **G3** — `strutil` units (9): sign normalisation, `invert_parities`, canon lookups, and
  reverse-map/linear-scan equivalence (duplicates, invalid aux, NULL-map fallback, 5000 atoms).
  ✅ **9/9**.
- **G4** — `MakeSlayerString` → `/s1(1,2)2(6,7)(8)3(3)(4,5)`; plus ABS-only reduction,
  single-OR ⇒ `/s2` and single-AND ⇒ `/s3` (ES-R17), two over-reduction guards (ABS+AND stays
  grouped, multiple OR groups stay grouped), no-component-dropped at 1/2/100/101/250
  components, and `count*substring` dedup. ✅ **passes**.
- **G5** — dormant 35-molecule `enh_stereo_test_file_2.sdf` (embedded `<InChI_new>`). ❌ *no gate wired* (ES-R13).
- **G6** — [STRING-ALG] "only ABS" edge table: explicit STEABS-only ⇒ bare `/s1`, whole string
  byte-identical to standard InChI apart from `1B`. ✅ **passes** (end-to-end, ES-R11).
- **G7** — [STRING-ALG] "only OR" / "only AND" edge tables ⇒ bare `/s2` / `/s3`, no `/m`.
  ⚠️ **half passes** — the `/s` half now holds (ES-R17): a single STEREL1 over all centres
  measures `/s2`, a single STERAC1 `/s3`, byte-identical to `-SRel` / `-SRac` apart from the
  prefix **and** a spurious `/m0` (ES-R18). Unit-gated in G4; no end-to-end gate wired yet —
  wire it with the ES-R18 fix.
- **G8** — the two 0.5 defect regressions in `test_enhancedStereo.cpp`: an L-alanine **V2000**
  molfile with a stereocentre plus `-EnhancedStereochemistry` (ES-R19, segfaulted before) and
  the same V3000 structure with two STEREL groups presented twice, atoms numbered `1..18` and
  `101..118`, asserted to give one identical InChI (ES-R20). ✅ **passes**; both verified to
  fail without their fix.

All 17 unit suites (179 tests) pass — `ctest` in `CMake_build/full_build` is green — and the
enhanced-stereo suites are clean under an ASAN Debug build. Out-of-tree build directories still
fail `test_enhancedStereo` and `test_ichimain` on fixture paths; see §5.B.

## 5. Open issues / risks

- **B. Fixture path fragility.** `test_EnhancedStereochemistry_test_file_1`
  (`test_enhancedStereo.cpp`) opens `../../../../../…/enh_stereo_test_file_1.sdf`; fails
  `ASSERT_TRUE(is_open())` unless run from one specific depth. It happens to resolve for the
  documented in-tree layout (`ctest` in `CMake_build/full_build` passes 17/17, because the test
  cwd is then five levels below the repo root), and breaks for any out-of-tree build directory.
  Logic is correct. Fix = CMake `FIXTURES_DIR` define (ES-R15).
- **D. Return value not propagated.** `set_EnhancedStereo_t_m_layers` returns its initial `0`
  regardless of the three `invert_parities` results (ES-R16).
- **G. `/m` emitted for OR/AND-only components (ES-R18).** `set_EnhancedStereo_t_m_layers`
  forces `nCompInv2Abs = 1` (⇒ `m0`) when no ABS collection exists but OR/AND ones do, so
  measured output is `/m0/s2(…)`. §6 says `/m` MUST NOT appear when a component has only
  OR/AND centres, and `-SRel` / `-SRac` indeed emit no `/m`. Either the forced `m0` is a
  deliberate deviation and §6 is wrong, or §6 holds and the forcing must go — §3 marked this
  ✅ and §6 forbids it, so the two sections have been contradicting each other since 0.1.
  Resolve the intent first; do not "fix" one side blindly.
- **H. Missing ES-R12 validation corrupts output, it does not merely fail to diagnose.**
  Measured with the option on: putting atoms 1,2 in both `STEABS ATOMS=(8 1 2 3 4 5 12 13 14)`
  and `STERAC1 ATOMS=(2 1 2)` yields `/t3-,4-,5+,6+,7-,8+,9-,10+/m0/s1(3,4,5,6,7,8,9,10)3(9,10)`
  — the shared centres appear in **two** `/s` groups and their parities are flipped **twice**
  in `/t` (clean input gives `…9+,10-`). Two `STEABS` collections are likewise merged silently
  and then reduced to a bare `/s1`, erasing all trace of the malformed input. This is why
  ES-R12 is a Must from 0.5 on: the reader must reject/diagnose per [BIOVIA] before the
  normalisation pass runs.

**Resolved in 0.5** (kept for traceability):

- ~~**F. OR-only / AND-only do not reduce (ES-R17).**~~ A single STEREL1 collection over all
  centres emitted `/s2(3,4,…,10)` and a single STERAC1 `/s3(3,4,…,10)`, where §6 requires the
  bare `/s2` / `/s3`. Resolved as 0.4 predicted it had to be: the reduction is conditional on
  the component having exactly **one** OR (resp. AND) group — `MakeEnhStereoString` now reports
  the number of groups it actually emitted for the component, and `MakeSlayerString` reduces
  only at count 1, so multiple groups keep the grouping that carries the information. Measured
  end-to-end: single OR ⇒ `/s2`, single AND ⇒ `/s3`, two OR groups ⇒ `/s2(3,5,7,9,10)(4,6,8)`.
- ~~**I. Segfault on input without V3000 collections (ES-R19).**~~ `OutputINCHI_StereoLayer_EnhancedStereo`
  dereferenced `orig_inp_data->v3000` unguarded while emitting `/s`. That pointer is `NULL` for
  V2000 input and for V3000 without a collection block (`mol2atom.c` leaves it unset), so any
  such structure **with stereocentres** crashed the moment the option was on — e.g.
  `inchi-1 fixtures/naloxon.mol -EnhancedStereochemistry` → SIGSEGV at `ichiprt1.c:3619`.
  The pre-existing V2000 test missed it because its molecule has no stereo at all, so the `/s`
  branch was never reached. Fixed by guarding on `v3000` and falling back to the plain
  stereo-type digit; gated by G8. Commit `f4268f6`.
- ~~**J. Collection atom-number remap off-by-two (ES-R20).**~~ In `MolfileV3000ReadCollections`
  the loop mapping collection atom numbers onto the final atom order ran `for (k = 2; k < nnum; k++)`,
  but the atoms occupy `num_list[2 … nnum+1]` — so the **last two atoms of every collection**
  kept their raw molfile index. Invisible while a molfile numbers its atoms `1..n` (the map is
  then the identity), wrong for any other numbering: the same structure with atoms numbered
  `101..118` measured `/t…8-,9+,10-/m0/s2(7,9,10)(8)` against `/t…8+,9+,10-/m0/s2(3,5,7,9,10)(4,6,8)`
  for `1..18` — four centres silently dropped out of `/s` and one parity left unflipped in `/t`.
  Same substance, same stereochemistry, different InChI purely from input numbering, so this
  broke the §2 determinism invariant and ES-R1. Fixed to `k < nnum + 2`; gated by G8. Commit `f4268f6`.

**Resolved in 0.4** (kept for traceability):

- ~~**A. Silent group-count cap.**~~ The fixed `ENH_STEREO_DICT_SIZE=100` dictionary dropped
  the excess *and* shortened the `;`-list, so >100 distinct per-component `/s` substrings
  produced a wrong InChI rather than a truncated one. The dictionary is now sized from
  `num_components` — an exact upper bound, since each component contributes at most one
  distinct substring — so no cap exists and the constant is deleted from `mode.h` (ES-R14).
- ~~**C. Explicit-STEABS-only reduction unverified.**~~ Measured: `/t` and `/m` were already
  byte-identical to standard InChI, only `/s` differed. Reduction implemented and gated (G6).
- ~~**E. Efficiency.**~~ `make_orig_to_canon_map` / `lookup_canonical_atom_number` replaced the
  `get_canonical_atom_number` linear scans in `invert_parities` and `MakeEnhStereoString`
  (O(n²) → O(n)); the lookup falls back to the scan when no map is available, and duplicate
  original numbers still resolve to the lowest canonical number. The dictionary rewrite
  removed a second O(n²), the per-component slot searches.

## 6. Normative grammar (`/s` layer)

The extended stereo-type layer, in ABNF ([RFC 5234]); it is appended to the existing
`<stereo-layer>` after `/t` and `/m`.

```abnf
s-layer      = "/s" 1*s-group
s-group      = s-type 1*atom-group
s-type       = "1" / "2" / "3"          ; 1 = ABS, 2 = OR/relative, 3 = AND/racemic
atom-group   = "(" atom *("," atom) ")" ; canonical atom numbers, ascending within a group
atom         = 1*DIGIT                  ; canonical (final) atom rank
```

Rules (each **MUST** hold; ⚠️ marks a rule the code does not yet meet):
- Within an `atom-group`, atoms **MUST** be in ascending canonical order; `atom-group`s within
  an `s-type` **MUST** be ordered by their smallest atom.
- ⚠️ `/m` **MUST** be present iff at least one ABS centre exists; it **MUST NOT** appear when
  the component has only OR/AND centres *(ES-R18, §5.G)*.
- A component whose centres are all ABS **MUST** reduce to the standard `/s1` (identical to
  `SAbs`); a single OR group **MUST** reduce to `/s2`; a single AND group to `/s3` *(ES-R11,
  ES-R17)*. Two or more OR (resp. AND) groups **MUST NOT** be reduced — the grouping is
  information the bare digit would lose.
- The lowest-numbered centre of each group **MUST** be normalised to `-` (whole-group sign
  flip; ABS groups additionally toggle `/m`).
- Canonical atom numbers **MUST** be derived from the collection's molfile atom indexes through
  the final atom order, whatever those indexes are — output **MUST NOT** depend on the input
  numbering *(ES-R20)*.
- Multi-component output uses the existing `count*substring` / `;` composition (extension).

## 7. Assumptions & dependencies

- **A-1** Input is MDL V3000 with `STEABS`/`STERELn`/`STERACn` `ATOMS=()` collections; V2000
  has no ESR channel, so a V2000 file yields standard output (no `/s` grouping) ✅ *(held since
  ES-R19; it used to crash instead whenever the V2000 structure had stereocentres)*.
- **A-2** Each stereocentre belongs to **exactly one** collection ([BIOVIA]); the reader
  MUST reject/diagnose violations (ES-R12).
- **D-1** Depends on final **canonical ranks** (grouping/ordering use canonical atom numbers).
- **D-2** Depends on the existing `/t`+`/m` sp³ parity pipeline; enhanced grouping is layered
  on top, not a replacement.
- **D-3** Reuses the `is_beta` mechanism for the `1B` prefix.

[RFC 5234]: https://www.rfc-editor.org/rfc/rfc5234
