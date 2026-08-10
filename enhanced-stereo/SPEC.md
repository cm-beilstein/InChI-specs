# Spec 1 — Enhanced Stereochemistry (V3000 ABS/OR/AND, tetrahedral centres)

| | |
|---|---|
| **Doc version** | 0.9 |
| **Date** | 2026-08-10 |
| **Status** | draft |
| **Author** | C. Müller |
| **Reviewers** | TBD (InChI Trust / project 2019-017-2-800 TG) |
| **Requirement prefix** | `ES-` |
| **Change history** | 0.1 (2026-07-09) — initial spec; verified against `dev`, incl. [BIOVIA]. 0.2 (2026-07-10) — consolidated: requirements/gates/deliverables/NFRs merged into one table (§4); ABNF grammar retained (§6). 0.3 (2026-07-10) — readability pass: added At-a-glance, split requirements from gates, tightened prose. 0.4 (2026-07-28) — ES-R11, ES-R14 and §5.E implemented on `feature/enh-stereo-hardening`; measurement of OR-only/AND-only output added two grammar-conformance gaps (ES-R17, ES-R18). 0.5 (2026-08-03) — full re-audit of `feature/enh-stereo-hardening` by reading + measuring: ES-R17 is implemented and gated (G7 half-satisfied); two defects the spec did not know about found, reproduced and fixed (ES-R19 V2000 crash, ES-R20 collection atom-remap off-by-two, commit `f4268f6`); test counts refreshed to 17 suites / 179 tests. 0.6 (2026-08-07) — **ES-R18 resolved and implemented.** [DECK] slide 10 settles the §3-vs-§6 contradiction explicitly ("/m0 and /m1 are only used in the context of absolute centers"; "In case that the structure only contains OR# and/or AND# centers /m# is obsolete a[n]d must not be used"), with worked examples on slides 11-12 showing no /m for OR/AND-only including the multi-group cases. Implemented per component (an ABS collection on a sibling component no longer keeps /m alive on an OR/AND-only one); G7 wired end-to-end and G9 ([BIOVIA] Appendix B) materialised from a file located in the wild. `dev` merged into `feature/enh-stereo-hardening`. Two further pre-existing defects recorded but not fixed (§5.I orphan /s groups, §5.J isotopic-only centres ignored). Test counts: 17 suites / 188 tests. 0.7 (2026-08-10) — **ES-R12 resolved and implemented**, the last open Must. A corpus of malformed collection files was assembled first (two real, from [rdkit/rdkit#8873]; six derived), which showed §5.H understated the defect: the corruption reaches `/t`, not only `/s`, so a malformed file could be given the InChI of a **different diastereomer**. Validation now runs in the reader (`StereoCollectionsAreMalformed`) and drops the collections rather than guessing; gated by G10. Two pre-existing tests moved with the behaviour and gained the `/s1` they used to drop. Spec requirement IDs, gate IDs and section references were removed from all source and test comments — the spec→code link is now by function name only. Test counts: 17 suites / 195 tests. 0.8 (2026-08-10) — **ES-R15 and ES-R13 done.** ES-R15 ported the `FIXTURES_DIR` CMake define from `atropisomers`; out-of-tree builds failed two suites before it and pass now. That unblocked ES-R13: the dormant G5 fixture was re-pinned by measurement — `/m` dropped from the 8 OR/AND-only records (§5.K as predicted), **all 35** `<InChI_new>` prefixes corrected to `1B/`, and four values found stale once the prefix noise cleared (18–20 shared one `<InChI>` across records whose standard strings differ; 26 carried a different molecule's formula in both columns). G5 is now wired over both columns, 70 assertions. Test counts: 17 suites / 196 tests. 0.9 (2026-08-10) — **ES-R16 closed by deletion, not implementation.** Investigating it showed the requirement rested on a false premise: `invert_parities` has no failure return, its non-zero paths mean "this collection list is empty", which is the ordinary case. Propagating the three results would have reported a no-op for nearly every real structure. `set_EnhancedStereo_t_m_layers` is now `void` and its three unread locals are gone. **Every requirement in this spec is now closed**, so what remains is the two pre-existing defects §5.I and §5.J, neither of which has a requirement ID yet. |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

- ✅ **Works (end-to-end):** parse V3000 STEABS/STEREL#/STERAC# → `/t`+`/m` normalisation →
  grouped `/s1(…)2(…)3(…)` emission, incl. **all three** single-class reductions
  (`/s1`, `/s2`, `/s3`), the `/m`-only-with-ABS rule (per component) and multi-component.
  **Every §6 MUST is now met**, and malformed collections are diagnosed instead of laundered.
  Tested (G1–G4, G6–G10 pass).
- ❌ **Missing:** nothing. Every requirement is closed as of 0.9.
- ▶ **Next:** the two pre-existing defects found in 0.6 and still unfixed — §5.I (orphan `/s`
  groups for atoms that are not stereocentres) and §5.J (isotopic-only centres ignored). Both are
  correctness gaps in what `/s` admits, and §5.I shares its root cause with ES-R2/ES-R12.

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
- *No laundering* — a collection block that violates the input constraints below MUST be
  diagnosed, and MUST NOT be turned into a valid-looking `/s` or into a `/t` that names a
  different stereoisomer ✅ *(held since ES-R12)*.
- *Robustness* — malformed/empty/out-of-range collections MUST NOT crash and MUST degrade
  gracefully; the per-component `/s` substring dictionary MUST NOT drop components ✅ *(it is
  sized from the component count, so no cap exists; ES-R14)*. Input without a V3000 collection
  block MUST NOT crash either ✅ *(ES-R19)*.
- *Performance (SHOULD)* — `/s` construction SHOULD be ≤ O(n·log n) in centres ✅ *(orig→canon
  reverse map replaced the linear scans; §5 resolved-E)*.
- *`/m` only with ABS* — a component with only OR/AND centres MUST NOT carry `/m` ✅ *(held
  since ES-R18; per component, and the segment disappears when no component has ABS)*.
- *Portability* — tests MUST resolve fixtures independent of build layout ✅ *(held since ES-R15;
  out-of-tree builds failed `test_enhancedStereo` and `test_ichimain` before it)*.

## 3. Current implementation (branch `feature/enh-stereo-hardening`, `dev` merged in; verified by reading + running tests)

| Stage | Location | State |
|-------|----------|-------|
| V3000 COLLECTION parse (STEABS/STEREL#/STERAC#, `ATOMS=()`, group #) | `mol_fmt3.c` `MolfileV3000ReadCollections`, atoms via `MolfileV3000ReadStereoCollection` + `get_actual_atom_number` | ✅ done; non-stereo collections skipped; atom-number remap fixed (ES-R20) |
| Input validation of the collection block | `mol_fmt3.c` `StereoCollectionsAreMalformed`, called once from `MolfileV3000ReadCollections` after the block is read | ✅ ES-R12 — five checks; on any hit it names the violation via `AddErrorMessage` and `NumLists_Free`s all three lists |
| Storage | `inpdef.h:396-404` `OAD_V3000.lists_steabs/sterel/sterac` | ✅ |
| Transfer molfile→`ORIG_ATOM_DATA.v3000` | `mol2atom.c:1646-1712`; component split `runichi3.c:359-395`; free `mol2atom.c:1421-1452` | ✅ |
| Option `-EnhancedStereochemistry` → `ip->bEnhancedStereo` | `ichiparm.c:273-275,2144` | ✅ |
| `1B` beta prefix | `ichiprt1.c:3119` `OutputINCHI_VersionAndKind`, `is_beta` set `:1713-1715`, `B` appended `:3132-3135` | ✅ |
| `/t`+`/m` sign-normalisation | `strutil.c` `set_EnhancedStereo_t_m_layers`, `invert_parities` (min-canon centre → `-`, whole-group flip; ABS toggles `nCompInv2Abs`) | ✅ |
| `/m` suppressed for OR/AND-only components (ES-R18) | `strutil.c` `set_EnhancedStereo_t_m_layers` zeroes `nCompInv2Abs` (⇒ `str_StereoAbsInv` emits the `.` placeholder), membership tested per component by `component_has_collection_atom`; `ichiprt1.c` `bHasAbsStereoComponent` drops the whole `/m` segment when no component keeps an ABS reference | ✅ ES-R18 — [DECK] slide 10 |
| Grouped `/s` emission | `ichiprt1.c:3496` `OutputINCHI_StereoLayer_EnhancedStereo` → `ichiprt2.c` `MakeSlayerString` → `MakeEnhStereoString` (type digit, canon-atom map, within-group + inter-group sort, parenthesised groups) | ✅ matches target ordering |
| ABS-only reduction to bare `/s1` | `ichiprt2.c` `MakeSlayerString` (per-sublayer lengths; ABS-only ⇒ bare type digit) | ✅ ES-R11 |
| Single-OR / single-AND reduction to bare `/s2` / `/s3` | `ichiprt2.c` `MakeSlayerString` (guarded by `num_groups_used` from `MakeEnhStereoString`, so ≥2 groups stay grouped) | ✅ ES-R17 |
| `/s` emission guarded against absent V3000 data | `ichiprt1.c` `OutputINCHI_StereoLayer_EnhancedStereo` (`orig_inp_data->v3000` NULL ⇒ plain stereo-type digit) | ✅ ES-R19 |
| Per-component `/s` substring dictionary | `ichiprt2.c` `MakeSlayerString` (sized from `num_components`; dense `n_entries` index) | ✅ ES-R14 — no cap, nothing droppable |
| orig→canon reverse map | `strutil.c` `make_orig_to_canon_map` / `lookup_canonical_atom_number`, used by `invert_parities` + `MakeEnhStereoString` | ✅ replaces the O(n²) scans |
| Multi-component `count*substr` + `;` (beyond single-molecule spec) | `ichiprt2.c` `MakeSlayerString` emit loop | ✅ present + tested (extension) |

Line numbers are omitted for the functions touched on this branch; they move. Grep the
function names — **as of 0.7 that is the only spec↔code link.** Requirement IDs, gate IDs and
section references were removed from all source and test comments, so the code no longer points
back here; keep the function names in this table current, because nothing else does.

Applies to **sp³ tetrahedral `/t` centres only**; E/Z, allene and atropisomer centres are
not grouped (see specs 2–4).

## 4. Requirements

Priority is MoSCoW. **As of 0.9 every requirement in this table is closed.** ES-R12 took the last
Must in 0.7 (malformed collections are diagnosed rather than laundered, §5 resolved-H); ES-R13 and
ES-R15 took the last Shoulds in 0.8 (§5 resolved-K, resolved-B); and ES-R16, the last Could, was
**withdrawn** in 0.9 rather than implemented, because it asked for something that does not exist
(§5 resolved-D). What remains open is the two pre-existing defects §5.I and §5.J, which carry no
requirement IDs yet.
**Won't (this spec):** name-level `rac`/`rel` nomenclature and independent-centre superscripts ([ESR]/[BNF])
— IUPAC nomenclature recommendations, not InChI code.

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| ES-R1 | Parse STEABS/STEREL#/STERAC# `ATOMS=()` | Must | ✅ `mol_fmt3.c:647` (see ES-R20) |
| ES-R2 | Grouped `/s1(…)2(…)3(…)` emission | Must | ✅ `MakeEnhStereoString` / `MakeSlayerString` |
| ES-R3 | Within-/inter-group ordering | Must | ✅ `MakeEnhStereoString` (`qsort` on canon numbers) |
| ES-R4 | Sign normalisation + `/m` coupling to ABS | Must | ✅ `invert_parities` + ES-R18 |
| ES-R5 | Reductions (only-ABS ⇒ `/s1`, only-OR ⇒ `/s2`, only-AND ⇒ `/s3`) | Must | ✅ complete — ABS (ES-R11), single OR/AND (ES-R17) |
| ES-R6 | `-EnhancedStereochemistry` + `1B` prefix | Must | ✅ `ichiparm.c:273` |
| ES-R7 | Multi-component `count*substring` / `;` composition | Should | ✅ `MakeSlayerString` emit loop |
| ES-R11 | Explicit-STEABS-only ⇒ bare `/s1` (== `SAbs`) | Should | ✅ done + gated (G6) |
| ES-R12 | Enforce one-group-per-centre / at-most-one-ABS; reject conflicts | Must | ✅ done + gated (G10) — diagnosed in the reader, collections dropped *(§5, resolved-H)* |
| ES-R13 | Wire `enh_stereo_test_file_2.sdf` gate (35 mol) | Should | ✅ done + gated (G5) — fixture re-pinned by measurement first *(§5, resolved-K)* |
| ES-R14 | No component may be dropped from the `/s` substring dictionary | Should | ✅ done — dictionary sized from `num_components`; the fixed cap is gone |
| ES-R15 | Fixture-path robustness (`FIXTURES_DIR` CMake define) | Should | ✅ done — ported from `atropisomers` *(§5, resolved-B)* |
| ES-R16 | Propagate `set_EnhancedStereo_t_m_layers` sub-call failures | Could | ⊘ **withdrawn** — there are no failures to propagate; the return value was deleted instead *(§5, resolved-D)* |
| ES-R17 | Single-OR ⇒ bare `/s2`, single-AND ⇒ bare `/s3` (§6 MUST) | Must | ✅ done + gated (G4, G7, G9) — ≥2 groups stay grouped; confirmed by [DECK] slides 10, 12 |
| ES-R18 | No `/m` when a component has only OR/AND centres (§6 MUST) | Must | ✅ done + gated (G7 end-to-end, G9 negative control) — [DECK] slide 10 is explicit *(§5, resolved-G)* |
| ES-R19 | `-EnhancedStereochemistry` MUST NOT crash on input without V3000 collections | Must | ✅ done + gated (G8) — was a segfault *(§5, resolved-I)* |
| ES-R20 | Collection atom numbers MUST be remapped regardless of molfile atom numbering | Must | ✅ done + gated (G8) — was an off-by-two *(§5, resolved-J)* |

### Gates

Datasets live in the repo test tree; see [datasets/DATASETS.md](datasets/DATASETS.md) for
per-molecule detail.

- **G1** — 14 inline ABS/OR/AND cases in `test_enhancedStereo.cpp`. ✅ **14/14 pass**.
  `test_EnhancedStereochemistry_4_mols` had recorded the pre-ES-R11 `/s1(8,9,10,11);…` for a
  component whose single stereocentre is ABS; its expectation is now the reduced `/s1;…`.
- **G2** — 33-molecule `enh_stereo_test_file_1.sdf` (m0/m1 flips, `?` passthrough, reductions).
  ✅ **passes** (fixture path no longer layout-dependent — ES-R15).
- **G3** — `strutil` units (9): sign normalisation, `invert_parities`, canon lookups, and
  reverse-map/linear-scan equivalence (duplicates, invalid aux, NULL-map fallback, 5000 atoms).
  ✅ **9/9**.
- **G4** — `MakeSlayerString` → `/s1(1,2)2(6,7)(8)3(3)(4,5)`; plus ABS-only reduction,
  single-OR ⇒ `/s2` and single-AND ⇒ `/s3` (ES-R17), two over-reduction guards (ABS+AND stays
  grouped, multiple OR groups stay grouped), no-component-dropped at 1/2/100/101/250
  components, and `count*substring` dedup. ✅ **passes**.
- **G5** — 35-molecule `enh_stereo_test_file_2.sdf`. ✅ **passes**, wired as
  `test_enhancedStereo.cpp::test_EnhancedStereochemistry_test_file_2`. Both embedded columns are
  checked, `<InChI>` with the option off and `<InChI_new>` with it on — 70 assertions, so every
  record doubles as a backward-compatibility case. The expectations are **read from the SDF**
  rather than transcribed into the test as G2 does, since this file already carries them and a
  second copy would drift. Two hazards the loop handles explicitly: every record opens with an
  **empty title line**, so trimming leading whitespace after the `$$$$` split (what the G2 loop
  does) shifts the 4-line header up and misparses the counts line; and a missing tag would read
  as an empty expectation and pass vacuously, so the record count and both tags are asserted
  first. Verified to fail: run against the pre-repin copy kept beside it as
  `enh_stereo_test_file_2.sdf.bak`, it reports 40 failures — exactly the 40 lines re-pinning
  changed.
- **G6** — [STRING-ALG] "only ABS" edge table: explicit STEABS-only ⇒ bare `/s1`, whole string
  byte-identical to standard InChI apart from `1B`. ✅ **passes** (end-to-end, ES-R11).
- **G7** — [STRING-ALG] "only OR" / "only AND" edge tables ⇒ bare `/s2` / `/s3`, no `/m`.
  ✅ **passes**, end-to-end gate now wired as
  `test_enhancedStereo.cpp::test_EnhancedStereochemistry_or_and_only_omit_m_layer`: a single
  STEREL1 over all centres measures `/s2`, a single STERAC1 `/s3`, and each is byte-identical
  to `-SRel` / `-SRac` apart from the version prefix — asserted as whole-string equality, not
  just on the `/s` substring. Two further ES-R18 gates accompany it:
  `..._m_layer_is_per_component` (ABS + OR-only siblings ⇒ `/m.1/s2;1`; both OR/AND-only ⇒ no
  `/m` at all) and `..._or_only_omits_m_with_mobile_h` (the Fixed-H path, == `-SRel -FixedH`).
  All three verified to fail with the fix reverted.
- **G9** — [BIOVIA] Appendix B / [DECK]-era MDL white-paper fig. 22, the 29-atom molfile mixing
  all five collection types. ✅ **passes** —
  `test_enhancedStereo.cpp::test_EnhancedStereochemistry_biovia_appendix_b`, molblock inline so
  it did not inherit the then-unfixed path fragility (ES-R15). Pinned to
  `…/t13-,14-,15-,17-,18-,21-,23+/m1/s1(15)2(13,14)(21,23)3(17)(18)`, which in one structure
  cross-checks against a third-party authority: ABS `(15)`, two OR groups, two AND groups,
  `/m1` **present** (ES-R18 negative control), neither the OR nor the AND pair reduced
  (ES-R17 over-reduction guard), and every group's lowest centre normalised to `-`.
  Dataset: `datasets/biovia_white_paper_fig22.mol` (upstream `M END` corrected to `M  END`).
- **G8** — the two 0.5 defect regressions in `test_enhancedStereo.cpp`: an L-alanine **V2000**
  molfile with a stereocentre plus `-EnhancedStereochemistry` (ES-R19, segfaulted before) and
  the same V3000 structure with two STEREL groups presented twice, atoms numbered `1..18` and
  `101..118`, asserted to give one identical InChI (ES-R20). ✅ **passes**; both verified to
  fail without their fix.

- **G10** — the ES-R12 malformed-input corpus, `datasets/malformed/` (eight molfiles, two of them
  real: the attachments to [rdkit/rdkit#8873], reported from a live R-group-enumeration pipeline).
  ✅ **passes**, wired at two levels. Reader: `test_mol_fmt.cpp`
  `test_malformed_collections_*` — six cases (atom in two collections, second STEABS, atom twice
  in one collection, unresolvable atom index, repeated group number, plus a **well-formed
  over-rejection guard**), each asserting the named diagnostic, that all three collection lists
  are emptied, and that the structure itself still parses. End-to-end:
  `test_enhancedStereo.cpp::test_EnhancedStereochemistry_malformed_collections_are_not_used` —
  four cases, each asserting `inchi_Ret_WARNING`, the diagnostic reaching the caller through
  `szMessage`, and a string byte-identical to the standard InChI apart from the `1B` prefix.
  Three of the four were verified to fail with the fix reverted, producing exactly the strings
  recorded in `datasets/malformed/MALFORMED.md`; the second-STEABS case is **not** detectable
  end-to-end, because the laundered output coincides with the degraded one — only the diagnostic
  separates them, which is why the reader test carries it.

All 17 unit suites (195 tests) pass — `ctest` in `CMake_build/full_build` is green; the
`test_enhancedStereo` suite is now 22 tests and `test_mol_fmt` 18. Backward compatibility was re-verified for 0.6 by
building the tree with and without the ES-R18 change and diffing standard (option-off) output
over 84 structures: byte-identical. Out-of-tree build directories still fail
`test_enhancedStereo` and `test_ichimain` on fixture paths — fixed in 0.8, see §5 resolved-B.

> **Build note.** `cmake --build` links the CLI as `bin/inchi-1d`; a stale `bin/inchi-1` from an
> earlier build may sit alongside it and will silently serve outdated measurements. Check the
> binary's mtime before trusting a hand-run comparison.

## 5. Open issues / risks

- **I. `/s` emits classes for atoms that are not stereocentres.** `MakeEnhStereoString` admits a
  collection atom on the sole test that it maps into the component (`lookup_canonical_atom_number
  != -1`); it never requires the atom to be a stereocentre. So a group can be emitted for an
  atom absent from `/t`, and even for a component with an **empty** `/t`. Three sightings, all
  pre-existing: `test_EnhancedStereochemistry_4_mols` pins `/s1(7)` where canon 7 is not in that
  component's `/t8-,9+`; the pinned `2C10H14BrCl7.C8H18` expectation carries `…;1(6)3(7,8)` for a
  component whose `/t` is empty; and a minimal two-component case (propane bearing
  `STEABS ATOMS=(1 8)` on a CH₂) measures `/t3-,4-;/s2;1` — the stereo-free component reported as
  class 1 via the ABS-only reduction. ES-R18 deliberately keys `/m` on the *same* membership test
  so `/m` and `/s` cannot disagree; fixing the root cause belongs with ES-R12/ES-R2. Contrast
  `epam/Indigo` `non_atrop.mol`, where a `STEREL1` on a non-stereogenic atom in a structure with
  **no** stereocentres at all is correctly ignored (no `/t`, no `/s`) — so the defect needs the
  structure to have stereo somewhere.
- **J. Isotopic-only stereocentres are ignored entirely.** For a centre that is stereogenic only
  through isotopic substitution (CH₃ vs CD₃), `-EnhancedStereochemistry` reproduces standard
  InChI — `/i1D3/t3-/m1/s1`, collection ignored, no `/s2`, `/m1` retained — where `-SRel` gives
  `/i1D3/t3-/s2`. Cause: `set_EnhancedStereo_t_m_layers` returns early on
  `nNumberOfStereoCenters <= 0`, which counts the **non-isotopic** centres only. Arguably outside
  the "sp³ tetrahedral `/t` centres only" scope in §3, but a `/t` does exist here, so §3 should
  say so explicitly rather than leave it implied.

**Resolved in 0.9** (kept for traceability):

- ~~**D. Return value not propagated.**~~ True as stated — `ret` was set to `0` and returned
  untouched while `ret_abs`/`ret_rac`/`ret_rel` were assigned and never read — but the remedy the
  requirement implies would have been a **bug**. `invert_parities` has no failure return: its two
  non-zero paths are `list_atoms == NULL` and `nof_lists == 0`, both the ordinary case, since a
  structure with no AND groups has `n_sterac == 0`. It returns `0` only after doing work, and
  `set_EnhancedStereo_t_m_layers` follows the same convention, returning `1` for not-V3000, NULL
  inputs, no stereocentres and no aux atoms — every one a no-op. These are did-I-do-anything
  codes, not error codes, so OR-ing the three together would have reported a no-op for nearly
  every real structure: almost none carry all three collection types (`biovia_white_paper_fig22.mol`
  is the rare file that does). Nor is there anything to report — the one allocation,
  `make_orig_to_canon_map`, is *allowed* to fail, because `lookup_canonical_atom_number` falls
  back to the linear scan, so exhaustion degrades to slow rather than wrong.

  The sole caller already ignored the result, so the function is now `void` and the three dead
  locals are gone. The one test touching it asserted only `ret == 0`, which said nothing about
  whether the parities were normalised; it now pins the resulting `t_parity` array and
  `nCompInv2Abs`, measured rather than derived, and verified to fail (5 assertions) with the
  function body neutered.

  **The lesson for the remaining entries:** this requirement was written from reading the
  function in isolation. §5.I and §5.J should be re-derived by measurement before anyone
  implements them.

**Resolved in 0.8** (kept for traceability):

- ~~**B. Fixture path fragility.**~~ `test_enhancedStereo` and `test_ichimain` opened their
  fixtures through a relative path counted in five `../` hops, so they resolved only when the
  binary was launched exactly five levels below the repo root — true for the documented in-tree
  layout, false for any out-of-tree build directory, where both suites failed on
  `ASSERT_TRUE(is_open())` / `fopen` with nothing wrong in the test logic. CMake now passes
  `FIXTURES_DIR` as an absolute compile definition (ported from `atropisomers`), each file
  keeping the old literal behind an `#ifndef` fallback. Measured both ways with a build directory
  configured outside the tree: 2 suites failed before, 17/17 pass after; in-tree unaffected.
  *Not fixed, and out of ES-R15's scope:* `test_ichimain` **writes** into the fixture directory
  (`output.txt`, `mkstemp` templates). Now that the path always resolves, out-of-tree runs write
  into the source tree where they previously just failed. Nothing is left behind after a run, but
  the tests are not hermetic.

- ~~**K. The dormant G5 fixture disagrees with ES-R18 and is the stale side.**~~ Confirmed, and
  it was staler than 0.6 knew. Re-pinned from measurement, never by hand, in three passes:
  1. **`/m` on the 8 OR/AND-only records** (22–25, 32–35, identified from their molblocks as the
     records with no `STEABS`) — dropped, exactly as this entry predicted.
  2. **Version prefixes.** Not just the two records 0.6 noticed: **no record at all** carried
     `1B/` in `<InChI_new>` (31 said `1S/`, 4 said `1/`), and record 23 said `1/` in `<InChI>`.
     Corrected to `1B/` and `1S/` after confirming the binary emits exactly those for all 35
     records in both modes.
  3. **Four stale values**, only visible once the prefix noise was gone. Records 18–20 shared one
     `<InChI>` expectation across three records whose standard strings are *not* all the same
     (18 and 19 agree; 20 does not). Record 26 carried `C7H14BrClO` in **both** columns while its
     own molblock — 11 heavy atoms — is `C8H16BrClO`; the molblock is the correct side.

  40 `InChI=` lines changed in total, no molblock, tag, record count or line count touched. The
  hand-authored original is kept beside it as `enh_stereo_test_file_2.sdf.bak`, which then served
  as the negative control proving the new G5 loop actually asserts something.

**Resolved in 0.7** (kept for traceability):

- ~~**H. Missing ES-R12 validation corrupts output, it does not merely fail to diagnose.**~~
  A corpus of malformed collection files was assembled before touching the code
  (`datasets/malformed/`, with per-file measurements and the reference-implementation
  comparison in `MALFORMED.md`). It disproved this entry's own closing claim.
  **0.6 said the corruption is confined to `/s`. It is not.** Two cases change `/t`:
  a `STEREL1` group split over two lines is read as two groups and each runs its own
  whole-group sign flip, giving `/t4-,5-,6-` against the well-formed `6+`; and the real
  two-`STEABS` file from [rdkit/rdkit#8873] measured `/t7-,8-` where standard InChI gives
  `/t7-,8+` for the very same file — the enhanced string named a **different diastereomer**,
  breaking the §2 backward-compatibility invariant outright. 0.6 reasoned from a single
  overlapping-pair example in which the two flips happened to cancel; that is not the general
  case. A third case, an atom repeated inside one collection, emitted `/s2(4,4,6)` — not
  ascending, so **not conformant to the §6 grammar either**, which makes ES-R12 an output
  correctness requirement and not only an input-hygiene one.

  Resolved by validating in the reader rather than repairing: `StereoCollectionsAreMalformed`
  runs once after the collection block is read and rejects a second STEABS collection, a
  STEREL/STERAC group number naming two collections, an atom in two collections, an atom
  listed twice in one collection, and an atom the CTab does not have. On any hit it names the
  violation and frees all three collection lists, so the enhanced path takes the ES-R19 route —
  the same as a structure with no collection block. **Diagnose, do not guess:** on merging
  vs. renumbering same-id groups even RDKit has no settled answer
  ([rdkit/rdkit#6050], and the #8873 discussion: *"since we don't have a context, I don't think
  we can assume merging will always be the right answer"*), so InChI must not invent one.
  Gated by G10. Three consequences worth recording:
  - **Standard InChI strings are unchanged** — the option-off path never used the collections.
    Only the API return moves `inchi_Ret_OKAY` → `inchi_Ret_WARNING`, and it does so whether the
    option is on or off, since the collection block is parsed either way.
  - **Two existing tests moved with the behaviour.** `..._3_empty_collection_info` and
    `..._3_wrong_atoms_in_collection` now expect the warning, and their string gains the `/s1`
    it used to drop — the new value is byte-identical to standard InChI apart from the prefix,
    so §2 now holds where it previously did not.
  - **One regression in usefulness.** `ATOMS=(3 4 5)` promises three atoms and lists two; the
    third slot is garbage and trips the unknown-atom check. It used to produce the correct
    `/s1(5)2(4,6)` by luck and now warns and drops the collection. Consistent with the policy,
    but it is a file that worked and now does not.

  What this does **not** fix: §5.I. Validation checks collection membership for consistency,
  never stereocentre-hood, so a group can still be emitted for an atom absent from `/t`.
  Same root cause, still open.

**Resolved in 0.6** (kept for traceability):

- ~~**G. `/m` emitted for OR/AND-only components (ES-R18).**~~ `set_EnhancedStereo_t_m_layers`
  forced `nCompInv2Abs = 1` (⇒ `m0`) when no ABS collection existed but OR/AND ones did, so
  measured output was `/m0/s2(…)`. §3 marked this ✅ while §6 forbade it, and the two sections had
  contradicted each other since 0.1. **[DECK] slide 10 settles it in favour of §6**, in terms that
  leave no room: "*/m0 and /m1 are only used in the context of absolute centers*" and "*In case
  that the structure only contains OR# and/or AND# centers /m# is obsolete a[n]d must not be
  used*" — with worked examples on slides 11–12 showing no `/m` for OR/AND-only including the
  multi-group cases, which also independently confirms ES-R17's reduce-only-at-one-group reading.
  Two things the fix had to get right beyond deleting the forcing: (i) `/m` **segment** presence
  is decided by `CompINChILayers` *before* the normalisation pass runs, and the same `bRelRac`
  value gates `/s`, so zeroing `nCompInv2Abs` early would have destroyed the `/s` layer too —
  hence the separate `bHasAbsStereoComponent` gate in the enhanced-only output function; (ii) the
  collection lists are structure-wide, so the test must be **per component** or an ABS collection
  on one component keeps `/m` alive on an OR/AND-only sibling (measured `/m11/s2;1`, now
  `/m.1/s2;1`). Gated by G7 end-to-end plus G9 as the negative control.

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

Rules (each **MUST** hold; as of 0.6 the code meets all of them):
- Within an `atom-group`, atoms **MUST** be in ascending canonical order; `atom-group`s within
  an `s-type` **MUST** be ordered by their smallest atom.
- `/m` **MUST** be present iff the component has at least one ABS collection member; it
  **MUST NOT** appear when the component has only OR/AND centres, and in a multi-component
  structure this is decided **per component** — the `.` placeholder is used for the components
  that carry no ABS reference, and the segment is omitted entirely when none do
  *(ES-R18, [DECK] slide 10, §5 resolved-G)*. Note the criterion is collection **membership**,
  matching what `/s` itself admits, not stereocentre-hood — see §5.I.
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
  MUST reject/diagnose violations ✅ *(held since ES-R12; diagnosed and the collections dropped,
  so the enhanced layer degrades to standard output rather than encoding a guess)*.
- **D-1** Depends on final **canonical ranks** (grouping/ordering use canonical atom numbers).
- **A-3** Applies to centres present in the **non-isotopic** `/t` layer. Centres that are
  stereogenic only through isotopic substitution are currently ignored by the grouping *(§5.J)*.
- **D-2** Depends on the existing `/t`+`/m` sp³ parity pipeline; enhanced grouping is layered
  on top, not a replacement.
- **D-3** Reuses the `is_beta` mechanism for the `1B` prefix.

[RFC 5234]: https://www.rfc-editor.org/rfc/rfc5234
[rdkit/rdkit#8873]: https://github.com/rdkit/rdkit/issues/8873
[rdkit/rdkit#6050]: https://github.com/rdkit/rdkit/issues/6050
