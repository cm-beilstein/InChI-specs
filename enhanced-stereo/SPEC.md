# Spec 1 — Enhanced Stereochemistry (V3000 ABS/OR/AND, tetrahedral centres)

| | |
|---|---|
| **Doc version** | 0.4 |
| **Date** | 2026-07-28 |
| **Status** | draft |
| **Author** | C. Müller |
| **Reviewers** | TBD (InChI Trust / project 2019-017-2-800 TG) |
| **Requirement prefix** | `ES-` |
| **Change history** | 0.1 (2026-07-09) — initial spec; verified against `dev`, incl. [BIOVIA]. 0.2 (2026-07-10) — consolidated: requirements/gates/deliverables/NFRs merged into one table (§4); ABNF grammar retained (§6). 0.3 (2026-07-10) — readability pass: added At-a-glance, split requirements from gates, tightened prose. 0.4 (2026-07-28) — ES-R11, ES-R14 and §5.E implemented on `feature/enh-stereo-hardening`; measurement of OR-only/AND-only output added two grammar-conformance gaps (ES-R17, ES-R18). |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

- ✅ **Works (end-to-end):** parse V3000 STEABS/STEREL#/STERAC# → `/t`+`/m` normalisation →
  grouped `/s1(…)2(…)3(…)` emission, incl. ABS-only reduction and multi-component.
  Tested (G1–G4, G6 pass).
- ❌ **Missing:** OR-only/AND-only reduction (ES-R17) and the `/m`-with-only-OR/AND rule
  (ES-R18) — both §6 MUSTs the code does not meet; one-group-per-centre enforcement
  (ES-R12); the dormant 35-molecule gate (ES-R13).
- ▶ **Next:** settle ES-R17/ES-R18 — the two open §6 conformance questions — then wire the
  dormant `enh_stereo_test_file_2.sdf` gate.

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
- *Determinism* — identical input ⇒ identical output, order-independent of input atom order.
- *Robustness* — malformed/empty/out-of-range collections MUST NOT crash and MUST degrade
  gracefully; the per-component `/s` substring dictionary MUST NOT drop components ✅ *(it is
  sized from the component count, so no cap exists; ES-R14)*.
- *Performance (SHOULD)* — `/s` construction SHOULD be ≤ O(n·log n) in centres ✅ *(orig→canon
  reverse map replaced the linear scans; §5 resolved-E)*.
- *Portability* — tests MUST resolve fixtures independent of build layout *(gap: §5.B)*.

## 3. Current implementation (branch `feature/enh-stereo-hardening`, verified by reading + running tests)

| Stage | Location | State |
|-------|----------|-------|
| V3000 COLLECTION parse (STEABS/STEREL#/STERAC#, `ATOMS=()`, group #) | `mol_fmt3.c:647` `MolfileV3000ReadCollections`, dispatch `:695-729`, atoms `:738-780` | ✅ done; non-stereo collections skipped |
| Storage | `inpdef.h:396-404` `OAD_V3000.lists_steabs/sterel/sterac` | ✅ |
| Transfer molfile→`ORIG_ATOM_DATA.v3000` | `mol2atom.c:1646-1712`; component split `runichi3.c:359-395`; free `mol2atom.c:1421-1452` | ✅ |
| Option `-EnhancedStereochemistry` → `ip->bEnhancedStereo` | `ichiparm.c:273-275,2144` | ✅ |
| `1B` beta prefix | `ichiprt1.c:3119` `OutputINCHI_VersionAndKind`, `is_beta` set `:1713-1715`, `B` appended `:3132-3135` | ✅ |
| `/t`+`/m` sign-normalisation | `strutil.c` `set_EnhancedStereo_t_m_layers`, `invert_parities` (min-canon centre → `-`, whole-group flip; ABS toggles `nCompInv2Abs`; force `m0` when only OR/AND) | ✅ works, but the forced `m0` contradicts §6 → ES-R18 |
| Grouped `/s` emission | `ichiprt1.c:3496` `OutputINCHI_StereoLayer_EnhancedStereo` → `ichiprt2.c` `MakeSlayerString` → `MakeEnhStereoString` (type digit, canon-atom map, within-group + inter-group sort, parenthesised groups) | ✅ matches target ordering |
| ABS-only reduction to bare `/s1` | `ichiprt2.c` `MakeSlayerString` (per-sublayer lengths; ABS-only ⇒ bare type digit) | ✅ ES-R11 |
| Per-component `/s` substring dictionary | `ichiprt2.c` `MakeSlayerString` (sized from `num_components`; dense `n_entries` index) | ✅ ES-R14 — no cap, nothing droppable |
| orig→canon reverse map | `strutil.c` `make_orig_to_canon_map` / `lookup_canonical_atom_number`, used by `invert_parities` + `MakeEnhStereoString` | ✅ replaces the O(n²) scans |
| Multi-component `count*substr` + `;` (beyond single-molecule spec) | `ichiprt2.c` `MakeSlayerString` emit loop | ✅ present + tested (extension) |

Line numbers are omitted for the functions touched on this branch; they move. Grep the
function names.

Applies to **sp³ tetrahedral `/t` centres only**; E/Z, allene and atropisomer centres are
not grouped (see specs 2–4).

## 4. Requirements

Priority is MoSCoW. The core works end-to-end; the two open Must-haves (ES-R17, ES-R18) are
conformance gaps against §6 found by measuring OR-only/AND-only output, not missing features.
**Won't (this spec):** name-level `rac`/`rel` nomenclature and independent-centre superscripts ([ESR]/[BNF])
— IUPAC nomenclature recommendations, not InChI code.

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| ES-R1 | Parse STEABS/STEREL#/STERAC# `ATOMS=()` | Must | ✅ `mol_fmt3.c:647` |
| ES-R2 | Grouped `/s1(…)2(…)3(…)` emission | Must | ✅ `MakeEnhStereoString` / `MakeSlayerString` |
| ES-R3 | Within-/inter-group ordering | Must | ✅ `MakeEnhStereoString` (`qsort` on canon numbers) |
| ES-R4 | Sign normalisation + `/m` coupling to ABS | Must | ✅ `invert_parities` — but see ES-R18 |
| ES-R5 | Reductions (only-ABS ⇒ `/s1`, only-OR ⇒ `/s2`, only-AND ⇒ `/s3`) | Must | ✅ *partial* — ABS done (ES-R11); OR/AND not (→ ES-R17) |
| ES-R6 | `-EnhancedStereochemistry` + `1B` prefix | Must | ✅ `ichiparm.c:273` |
| ES-R7 | Multi-component `count*substring` / `;` composition | Should | ✅ `MakeSlayerString` emit loop |
| ES-R11 | Explicit-STEABS-only ⇒ bare `/s1` (== `SAbs`) | Should | ✅ done + gated (G6) |
| ES-R12 | Enforce one-group-per-centre / at-most-one-ABS; reject conflicts | Should | ❌ not implemented |
| ES-R13 | Wire `enh_stereo_test_file_2.sdf` gate (35 mol) | Should | ❌ dormant |
| ES-R14 | No component may be dropped from the `/s` substring dictionary | Should | ✅ done — dictionary sized from `num_components`; the fixed cap is gone |
| ES-R15 | Fixture-path robustness (`FIXTURES_DIR` CMake define) | Should | ❌ port from `atropisomers` *(§5.B)* |
| ES-R16 | Propagate `set_EnhancedStereo_t_m_layers` sub-call failures | Could | ❌ returns `0` always *(§5.D)* |
| ES-R17 | Single-OR ⇒ bare `/s2`, single-AND ⇒ bare `/s3` (§6 MUST) | Must | ❌ emits `/s2(…)` / `/s3(…)` *(§5.F)* |
| ES-R18 | No `/m` when a component has only OR/AND centres (§6 MUST) | Must | ❌ `m0` is forced instead *(§5.G)* |

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
- **G4** — `MakeSlayerString` → `/s1(1,2)2(6,7)(8)3(3)(4,5)`; plus ABS-only reduction, an
  over-reduction guard (ABS+AND stays grouped), no-component-dropped at 1/2/100/101/250
  components, and `count*substring` dedup. ✅ **passes**.
- **G5** — dormant 35-molecule `enh_stereo_test_file_2.sdf` (embedded `<InChI_new>`). ❌ *no gate wired* (ES-R13).
- **G6** — [STRING-ALG] "only ABS" edge table: explicit STEABS-only ⇒ bare `/s1`, whole string
  byte-identical to standard InChI apart from `1B`. ✅ **passes** (end-to-end, ES-R11).
- **G7** — [STRING-ALG] "only OR" / "only AND" edge tables ⇒ bare `/s2` / `/s3`, no `/m`.
  ❌ *fails* — measured output is `/m0/s2(3,4,…,10)` and `/m0/s3(3,4,…,10)`
  (ES-R17, ES-R18). No gate wired yet; wire it with the fix.

All 16 unit suites (172 tests) pass — `ctest` in `CMake_build/full_build` is green — and the
enhanced-stereo suites are clean under an ASAN Debug build. Out-of-tree build directories still
fail `test_enhancedStereo` and `test_ichimain` on fixture paths; see §5.B.

## 5. Open issues / risks

- **B. Fixture path fragility.** `test_EnhancedStereochemistry_test_file_1`
  (`test_enhancedStereo.cpp`) opens `../../../../../…/enh_stereo_test_file_1.sdf`; fails
  `ASSERT_TRUE(is_open())` unless run from one specific depth. It happens to resolve for the
  documented in-tree layout (`ctest` in `CMake_build/full_build` passes 16/16, because the test
  cwd is then five levels below the repo root), and breaks for any out-of-tree build directory.
  Logic is correct. Fix = CMake `FIXTURES_DIR` define (ES-R15).
- **D. Return value not propagated.** `set_EnhancedStereo_t_m_layers` returns its initial `0`
  regardless of the three `invert_parities` results (ES-R16).
- **F. OR-only / AND-only do not reduce (ES-R17).** Measured with the option on: a single
  STEREL1 collection over all centres yields `/s2(3,4,5,6,7,8,9,10)`, a single STERAC1 yields
  `/s3(3,4,5,6,7,8,9,10)`. §6 requires the bare `/s2` / `/s3`, matching `-SRel` / `-SRac`.
  The ABS-only reduction (ES-R11) deliberately did not touch this: for **multiple** OR or AND
  groups the grouping carries information the bare digit would lose, so the reduction must be
  conditional on a single group — that condition needs settling against [STRING-ALG] before
  implementation.
- **G. `/m` emitted for OR/AND-only components (ES-R18).** `set_EnhancedStereo_t_m_layers`
  forces `nCompInv2Abs = 1` (⇒ `m0`) when no ABS collection exists but OR/AND ones do, so
  measured output is `/m0/s2(…)`. §6 says `/m` MUST NOT appear when a component has only
  OR/AND centres, and `-SRel` / `-SRac` indeed emit no `/m`. Either the forced `m0` is a
  deliberate deviation and §6 is wrong, or §6 holds and the forcing must go — §3 marked this
  ✅ and §6 forbids it, so the two sections have been contradicting each other since 0.1.
  Resolve the intent first; do not "fix" one side blindly.

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
  `SAbs`); ⚠️ a single OR group **MUST** reduce to `/s2`; a single AND group to `/s3`
  *(ES-R17, §5.F)*.
- The lowest-numbered centre of each group **MUST** be normalised to `-` (whole-group sign
  flip; ABS groups additionally toggle `/m`).
- Multi-component output uses the existing `count*substring` / `;` composition (extension).

## 7. Assumptions & dependencies

- **A-1** Input is MDL V3000 with `STEABS`/`STERELn`/`STERACn` `ATOMS=()` collections; V2000
  has no ESR channel, so a V2000 file yields standard output (no `/s` grouping).
- **A-2** Each stereocentre belongs to **exactly one** collection ([BIOVIA]); the reader
  MUST reject/diagnose violations (ES-R12).
- **D-1** Depends on final **canonical ranks** (grouping/ordering use canonical atom numbers).
- **D-2** Depends on the existing `/t`+`/m` sp³ parity pipeline; enhanced grouping is layered
  on top, not a replacement.
- **D-3** Reuses the `is_beta` mechanism for the `1B` prefix.

[RFC 5234]: https://www.rfc-editor.org/rfc/rfc5234
