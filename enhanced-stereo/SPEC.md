# Spec 1 — Enhanced Stereochemistry (V3000 ABS/OR/AND, tetrahedral centres)

| | |
|---|---|
| **Doc version** | 1.3 |
| **Date** | 2026-10-23 |
| **Status** | draft |
| **Author** | C. Müller |
| **Reviewers** | TBD (InChI Trust / project 2019-017-2-800 TG) |
| **Requirement prefix** | `ES-` |
| **Change history** | 0.1 (2026-07-09) — initial spec; verified against `dev`, incl. [BIOVIA]. 0.2 (2026-07-10) — consolidated: requirements/gates/deliverables/NFRs merged into one table (§4); ABNF grammar retained (§6). 0.3 (2026-07-10) — readability pass: added At-a-glance, split requirements from gates, tightened prose. 0.4 (2026-07-28) — ES-R11, ES-R14 and §5.E implemented on `feature/enh-stereo-hardening`; measurement of OR-only/AND-only output added two grammar-conformance gaps (ES-R17, ES-R18). 0.5 (2026-08-03) — full re-audit of `feature/enh-stereo-hardening` by reading + measuring: ES-R17 is implemented and gated (G7 half-satisfied); two defects the spec did not know about found, reproduced and fixed (ES-R19 V2000 crash, ES-R20 collection atom-remap off-by-two, commit `f4268f6`); test counts refreshed to 17 suites / 179 tests. 0.6 (2026-08-07) — **ES-R18 resolved and implemented.** [DECK] slide 10 settles the §3-vs-§6 contradiction explicitly ("/m0 and /m1 are only used in the context of absolute centers"; "In case that the structure only contains OR# and/or AND# centers /m# is obsolete a[n]d must not be used"), with worked examples on slides 11-12 showing no /m for OR/AND-only including the multi-group cases. Implemented per component (an ABS collection on a sibling component no longer keeps /m alive on an OR/AND-only one); G7 wired end-to-end and G9 ([BIOVIA] Appendix B) materialised from a file located in the wild. `dev` merged into `feature/enh-stereo-hardening`. Two further pre-existing defects recorded but not fixed (§5.I orphan /s groups, §5.J isotopic-only centres ignored). Test counts: 17 suites / 188 tests. 0.7 (2026-08-10) — **ES-R12 resolved and implemented**, the last open Must. A corpus of malformed collection files was assembled first (two real, from [rdkit/rdkit#8873]; six derived), which showed §5.H understated the defect: the corruption reaches `/t`, not only `/s`, so a malformed file could be given the InChI of a **different diastereomer**. Validation now runs in the reader (`StereoCollectionsAreMalformed`) and drops the collections rather than guessing; gated by G10. Two pre-existing tests moved with the behaviour and gained the `/s1` they used to drop. Spec requirement IDs, gate IDs and section references were removed from all source and test comments — the spec→code link is now by function name only. Test counts: 17 suites / 195 tests. 0.8 (2026-08-10) — **ES-R15 and ES-R13 done.** ES-R15 ported the `FIXTURES_DIR` CMake define from `atropisomers`; out-of-tree builds failed two suites before it and pass now. That unblocked ES-R13: the dormant G5 fixture was re-pinned by measurement — `/m` dropped from the 8 OR/AND-only records (§5.K as predicted), **all 35** `<InChI_new>` prefixes corrected to `1B/`, and four values found stale once the prefix noise cleared (18–20 shared one `<InChI>` across records whose standard strings differ; 26 carried a different molecule's formula in both columns). G5 is now wired over both columns, 70 assertions. Test counts: 17 suites / 196 tests. 0.9 (2026-08-10) — **ES-R16 closed by deletion, not implementation.** Investigating it showed the requirement rested on a false premise: `invert_parities` has no failure return, its non-zero paths mean "this collection list is empty", which is the ordinary case. Propagating the three results would have reported a no-op for nearly every real structure. `set_EnhancedStereo_t_m_layers` is now `void` and its three unread locals are gone. **Every requirement in this spec is now closed**, so what remains is the two pre-existing defects §5.I and §5.J, neither of which has a requirement ID yet. 1.0 (2026-10-08) — **multi-component audit** with seven pentan-2-ol/butan-2-ol structures (stereo-free spectators, one AND group per or over both alcohols). Found and fixed four defects that 0.9 marked ✅: §5 resolved-L `/s` merged equal components that were not adjacent, putting groups on the wrong component (ES-R21); resolved-M with `-AuxNone` the `/t`+`/m` normalisation read another component's aux, so a spectator changed `/m` (ES-R22); resolved-N an OR/AND group spanning components was silently split, colliding with independent groups (ES-R23, now diagnosed and dropped; the three inter-fragment tests that pinned the split moved with it); and the ungrouped-wedge `/m` rule was unstated (ES-R24, behaviour already correct once ES-R22 was fixed). §5.O found the same day and fixed (ES-R25): uniform multi-component `/s` now reduces to standard's single digit. §5.I fixed (ES-R26): re-derived by measurement first, it also reached `/m` (an ABS label on a CH₂ kept `/m` alive on an AND-only component) and `/t` (a CH₃ as a group's lowest atom skipped its sign normalisation: two InChIs for one racemate). Worked examples added (§8). An advisor review then found two collisions, measured and fixed (§5 resolved-P, ES-R24 restated, ES-R27): an ABS flip set `/m1` instead of toggling `/m`, and an ungrouped wedge beside an OR/AND group lost its configuration. Its three lower findings closed too: the ES-R23 spanning check moved from the reader's CTab union-find to InChI's own components after metal disconnection (a group over two Mg ligands was missed; a haptic group under `-MolecularInorganics` was falsely rejected); `?` centres under `-SUU` no longer block ES-R25; the stale §6 claim is gone. §5.Q (`-RecMet` crash, pre-existing) and §5.J (isotope-only centres) then fixed (ES-R28–ES-R30); chasing §5.Q exposed a meso defect, fixed too. **No open issue remains.** Test counts: 17 suites / 211 tests. 1.1 (2026-10-08) — **ES-R31 fixed on `feature/double-bond-ez`:** components equal in every standard layer were ordered by input order, and OR/AND parities were normalised only after the component sort, so swapping which of two equal components carries STEREL and which STERAC turned `/s2;3` into `/s3;2`. Normalisation now runs before the sort (`runichi4.c`) and the component's own `/s` (and grouped `/b`, Spec 3) string breaks ties before input order (`MakeEnhSortKey`, `CompEnhKey`). Gate: `test_EnhancedStereochemistry_component_order`. 1.2 (2026-10-09) — **ES-R32 fixed on `atropisomers` (`072d35c`), cherry-picked to `feature/enh-stereo-hardening` (`773c921`), `feature/allenes` (`f6fc3ef`) and `feature/double-bond-ez` (`546dd96`):** when collections existed but none named a stereo element (a label on a CH₃/CH₂, or an allene's terminal atom), `/s` was built from them and came out empty: the layer vanished (`/t3-,4-/m1`) or became bare separators (`/s;`). Every wedged centre is then ungrouped, hence absolute, and `/s1` is written, as in standard InChI. Gates: `test_EnhancedStereochemistry_only_orphan_collections_keep_s1`, `test_allenes.group_on_terminal_atom_is_ignored`. 1.3 (2026-10-23) — **ES-R33 fixed on `feature/enh-stereo-hardening` (`abab19a`)**, reported by John Mayfield in [#286]: an OR/AND group holding every centre of a meso component was emitted, so cyclohexane-1,4-diol gave three InChIs (`/t5-,6-`, `&1` ⇒ `/t5-,6-/s3`, `o1` ⇒ `/t5-,6-/s2`). Such a group is now ignored. A group on a subset of centres whose inversion is still a symmetry is not detected; recorded as open issue §5.S. Test counts: 19 suites / 228 tests (one disabled). |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

- ✅ **Works (end-to-end):** parse V3000 STEABS/STEREL#/STERAC# → `/t`+`/m` normalisation →
  grouped `/s1(…)2(…)3(…)` emission, incl. **all three** single-class reductions
  (`/s1`, `/s2`, `/s3`), the `/m`-only-with-ABS rule (per component) and multi-component.
  0.9 claimed every §6 MUST was met; the 1.0 multi-component audit disproved that (ES-R21–ES-R27),
  now fixed. Only stereocentres reach `/s` and `/m`; a component's absolute set (STEABS plus
  ungrouped wedges) flips as one and toggles `/m`. Malformed collections, including OR/AND groups spanning components, are diagnosed
  instead of laundered. Tested (G1–G11 pass).
- ❌ **Missing:** nothing required.
- ▶ **Next:** nothing open in §5. Worked examples: §8.

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
  edge tables; [DECK] slide 9 (`/s1(5,7)2(8,10)(9)3(4)(6)`) and slide 12. A chemist-oriented walkthrough is in §2.1.

**Input constraints (authoritative, [BIOVIA]):**
- A stereogenic centre belongs to **exactly one** stereochemical group. A structure may
  contain **at most one ABS collection** but **multiple OR# and AND# groups**. Centres not in
  any collection (no wedge) are unknown/undefined (`?`). A **wedged** centre in no collection is
  drawn with a definite configuration and is treated as absolute: with the STEABS members it
  forms the component's **absolute set**, which keeps `/m`, flips as one group, and stops a
  single OR/AND group beside it from reducing to bare `/s2`/`/s3` (ES-R24).
  Conflicting membership is malformed input — the reader must reject or diagnose it, not silently
  pick one.
- An OR or AND group **MUST NOT** span connected components: it would couple them (e.g. (R,R)
  and (S,S) of a salt pair), which the per-component `/s` cannot express. Such input is
  diagnosed and its collections dropped (ES-R23). An ABS collection may span components.
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
  did not number its atoms 1..n)*, and independent of output options such as `-AuxNone`
  ✅ *(held since ES-R22)*.
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

### 2.1 Chemistry primer — what the labels mean, by example

**The molecule.** 3-Chlorobutan-2-ol, CH₃–C²H(OH)–C³H(Cl)–CH₃, has two stereocentres and
therefore four stereoisomers: the enantiomer pair **(2R,3R)/(2S,3S)** and the enantiomer pair
**(2R,3S)/(2S,3R)**. The two pairs are diastereomers of each other. Its InChI skeleton is

```
InChI=1B/C4H9ClO/c1-3(5)4(2)6/h3-4,6H,1-2H3
```

where canonical atom **3 is C3 (the C–Cl carbon)** and **4 is C2 (the C–OH carbon)**.

**Reading the stereo layers.**
- **`/t`** gives each centre's parity, i.e. the **relative** configuration. `/t3-,4-` covers the
  (2R,3R)/(2S,3S) pair; `/t3-,4+` covers the other pair.
- **`/m`** picks one enantiomer of that pair: `/m1` here means (2R,3R) and `/m0` means (2S,3S). It
  is written only when something in the component is known absolutely.
- **`/s`** says what is known: `1` = absolute (ABS), `2` = relative (OR, "one of the two, unknown
  which"), `3` = racemic (AND, "both, as a mixture"). A bare digit applies to every centre; `3(3)`
  applies class 3 to canonical atom 3.

**One drawing, eight labellings.** All rows below use the drawing of (2R,3R), with both wedges up.
In a structure editor the labels appear as `abs`, `or1`, `&1`. Every string was measured. The last
column shows that standard InChI, which treats every wedge as absolute, cannot tell these
substances apart.

| # | labels on C2 / C3 | what the sample is | enhanced InChI (after the skeleton) | standard InChI |
|---|---|---|---|---|
| 1 | none, or `abs` on both | (2R,3R) | `/t3-,4-/m1/s1` | same |
| 2 | `or1` on both | (2R,3R) **or** (2S,3S): one enantiomer, unknown which | `/t3-,4-/s2` | `/t3-,4-/m1/s1` |
| 3 | `&1` on both | (2R,3R) **and** (2S,3S): the racemate | `/t3-,4-/s3` | `/t3-,4-/m1/s1` |
| 4 | `abs` / `&1` | (2R,3R) **and** (2R,3S): C2 known, mixture of C3 epimers | `/t3-,4-/m1/s1(4)3(3)` | `/t3-,4-/m1/s1` |
| 5 | `abs` / `or1` | (2R,3R) **or** (2R,3S): C2 known, C3 unknown | `/t3-,4-/m1/s1(4)2(3)` | `/t3-,4-/m1/s1` |
| 6 | `or1` / `or2` | any **one** of the four stereoisomers, unknown which | `/t3-,4-/s2(3)(4)` | `/t3-,4-/m1/s1` |
| 7 | `&1` / `&2` | **all four** stereoisomers: each centre racemic on its own | `/t3-,4-/s3(3)(4)` | `/t3-,4-/m1/s1` |
| 8 | `&1` / none (C3 wedged, unlabelled) | (2R,3R) **and** (2S,3R): C3 known, C2 racemic | `/t3-,4-/m1/s3(4)` | `/t3-,4-/m1/s1` |

**What to notice.**
- **Same sample, same InChI.** Drawing the other member of a group gives an identical string: the
  (2S,3S) drawing in rows 2 and 3, the (2R,3S) drawing in rows 4 and 5, any of the four drawings
  in rows 6 and 7, the (2S,3R) drawing in row 8. Each group is normalised so that its lowest
  canonical centre reads `-` (§6), so the drawing chosen does not matter.
- **Different samples, different InChIs.** Rows 2 and 3 share `/t` and differ only in `/s2` vs
  `/s3`: "one unknown enantiomer" is a different substance from "the racemate". With row 2's
  labels, the (2R,3S) drawing gives `/t3-,4+/s2`, because it is the other diastereomer pair.
- **`/m` only with something absolute.** Rows 2, 3, 6 and 7 have no absolute centre, so there is
  no `/m`. Rows 4, 5 and 8 keep `/m` for their absolute centre. In row 8 that centre is C3, which is
  wedged but in no collection; an unlabelled wedge counts as absolute (ES-R24). With row 4's
  labels, the (2S,3S) drawing gives `/m0`: a different sample.
- **Bare digit or groups.** One class covering every centre in a single group gives a bare digit
  (rows 1–3). Several groups (rows 6 and 7) or mixed classes (rows 4, 5 and 8) list the atoms.

**More than one molecule.** `/t`, `/m` and `/s` each have one `;`-separated slot per component.
(R)-Pentan-2-ol mixed with racemic butan-2-ol, the pentanol wedged and unlabelled and the
butanol `&1`, gives `/t5-;4-/m1./s;3`. Read slot by slot:
- pentanol: `5-`, `1` in `/m`, nothing in `/s`, so it is absolute;
- butanol: `4-`, `.` in `/m`, `3` in `/s`, so it is racemic.

Adding water adds an empty slot (`/m1../s;3;`) and changes nothing else. A single `&1` group
across **both** alcohols would say "(R,R) and (S,S) pairs", a link between two separate molecules
that per-molecule slots cannot express. Such input is rejected with a warning (ES-R23). §8 has the
full set of multi-component, meso and isotope examples.

## 3. Current implementation (branch `feature/enh-stereo-hardening`, `dev` merged in; verified by reading + running tests)

| Stage | Location | State |
|-------|----------|-------|
| V3000 COLLECTION parse (STEABS/STEREL#/STERAC#, `ATOMS=()`, group #) | `mol_fmt3.c` `MolfileV3000ReadCollections`, atoms via `MolfileV3000ReadStereoCollection` + `get_actual_atom_number` | ✅ done; non-stereo collections skipped; atom-number remap fixed (ES-R20) |
| Input validation of the collection block | `mol_fmt3.c` `StereoCollectionsAreMalformed`, called once from `MolfileV3000ReadCollections` after the block is read | ✅ ES-R12 — five checks; on any hit it names the violation via `AddErrorMessage` and `NumLists_Free`s all three lists |
| OR/AND group spanning components (ES-R23) | `runichi3.c` `CheckStereoGroupComponents` → `StereoGroupSpansComponents`, at the end of `PreprocessOneStructure` (and before its `-MolecularInorganics` early return), on `at[].component`; only with `-EnhancedStereochemistry` | ✅ warning via `WarningMessage`; `DropStereoCollections` on the original, disconnected and reconnected copies |
| Storage | `inpdef.h:396-404` `OAD_V3000.lists_steabs/sterel/sterac` | ✅ |
| Transfer molfile→`ORIG_ATOM_DATA.v3000` | `mol2atom.c:1646-1712`; component split `runichi3.c:359-395`; free `mol2atom.c:1421-1452` | ✅ |
| Option `-EnhancedStereochemistry` → `ip->bEnhancedStereo` | `ichiparm.c:273-275,2144` | ✅ |
| `1B` beta prefix | `ichiprt1.c:3119` `OutputINCHI_VersionAndKind`, `is_beta` set `:1713-1715`, `B` appended `:3132-3135` | ✅ |
| `/t`+`/m` sign-normalisation | `strutil.c` `set_EnhancedStereo_t_m_layers`, `invert_parities` (min-canon centre → `-`, whole-group flip; ABS toggles `nCompInv2Abs`); called from `OutputINChI1` with the component's own aux | ✅ ES-R22 |
| `/m` suppressed for OR/AND-only components (ES-R18) | `strutil.c` `set_EnhancedStereo_t_m_layers` zeroes `nCompInv2Abs` (⇒ `str_StereoAbsInv` emits the `.` placeholder), membership tested per component by `component_has_collection_atom`, stereocentres only (`lookup_stereo_centre`); `ichiprt1.c` `bHasAbsStereoComponent` drops the whole `/m` segment when no component keeps an ABS reference | ✅ ES-R18 — [DECK] slide 10 |
| Grouped `/s` emission | `ichiprt1.c:3496` `OutputINCHI_StereoLayer_EnhancedStereo` → `ichiprt2.c` `MakeSlayerString` → `MakeEnhStereoString` (type digit, canon-atom map, within-group + inter-group sort, parenthesised groups) | ✅ matches target ordering |
| ABS-only reduction to bare `/s1` | `ichiprt2.c` `MakeSlayerString` (per-sublayer lengths; ABS-only ⇒ bare type digit) | ✅ ES-R11 |
| Single-OR / single-AND reduction to bare `/s2` / `/s3` | `ichiprt2.c` `MakeSlayerString` (guarded by `num_groups_used` from `MakeEnhStereoString`, so ≥2 groups stay grouped) | ✅ ES-R17 |
| `/s` emission guarded against absent V3000 data | `ichiprt1.c` `OutputINCHI_StereoLayer_EnhancedStereo` (`orig_inp_data->v3000` NULL ⇒ plain stereo-type digit) | ✅ ES-R19 |
| Per-component `/s` substrings | `ichiprt2.c` `MakeSlayerString` (one slot per component, in component order) | ✅ ES-R14, ES-R21 |
| orig→canon reverse map | `strutil.c` `make_orig_to_canon_map` / `lookup_canonical_atom_number`, used by `invert_parities` + `MakeEnhStereoString` | ✅ replaces the O(n²) scans |
| Groups that invert a meso component ignored (ES-R33) | `ichimak2.c` keeps standard InChI's meso decision in `INChI_Stereo.bMeso` (never changed afterwards, unlike `nCompInv2Abs`); `strutil.c` `enh_group_is_noop`, skipped by `invert_parities`, `component_has_collection_atom`, `absolute_centres` and `ichiprt2.c` `MakeEnhStereoString` | 🟡 whole component only (§5.S) |
| Multi-component `count*substr` + `;` (beyond single-molecule spec) | `ichiprt2.c` `MakeSlayerString` emit loop — folds only consecutive equal non-empty substrings | ✅ ES-R21 |

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
(§5 resolved-D). 1.0 added and closed ES-R21–ES-R26 (multi-component audit and §5.I). What
remains open is §5.J, which carries no requirement ID yet.
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
| ES-R21 | Multi-component `/s` MUST be positional: one `;` slot per component, `n*` only over consecutive equal components, empty slots never folded | Must | ✅ done + gated (G11) *(§5, resolved-L)* |
| ES-R22 | Output MUST NOT depend on `-AuxNone` | Must | ✅ done + gated (G11) *(§5, resolved-M)* |
| ES-R23 | An OR/AND group spanning InChI components (after salt and metal disconnection) MUST be diagnosed and the collections dropped | Must | ✅ done + gated (G11) *(§5, resolved-N)* |
| ES-R24 | A wedged centre in no collection is absolute: it joins STEABS in the component's absolute set, keeps `/m`, and blocks the single OR/AND reduction | Must | ✅ done + gated (G11) — held only for components without OR/AND until resolved-P |
| ES-R25 | When every component with sp3 centres reduces to the same bare digit and the rest have no defined centre outside a collection (`?` centres do not count), `/s` MUST be that single digit (== `SAbs`/`SRel`/`SRac`) | Must | ✅ done + gated (G11) *(§5, resolved-O)* |
| ES-R26 | Only stereocentres of the component's `/t` reach `/s` and the `/m` membership test | Must | ✅ done + gated (G11) *(§5, resolved-I)* |
| ES-R27 | Flipping the absolute set MUST toggle `/m`, not set it | Must | ✅ done + gated (G11) *(§5, resolved-P)* |
| ES-R28 | `-EnhancedStereochemistry -RecMet` MUST NOT read through missing input data | Must | ✅ done + gated (G11) *(§5, resolved-Q)* |
| ES-R29 | A meso component with OR/AND stereocentres MUST keep its `/s` | Must | ✅ done + gated (G11) *(§5, resolved-Q)* |
| ES-R30 | Collections apply to the isotopic stereo layer as to the main one; its `/s` is printed when its classes differ from the main layer's | Must | ✅ done + gated (G11) *(§5, resolved-J)* |
| ES-R32 | When no collection names a stereo element but wedged centres exist, `/s` MUST be `1` (all centres ungrouped, hence absolute; == standard InChI) | Must | ✅ done + gated (G11) *(§5, resolved-R)* |
| ES-R33 | An OR/AND group whose inversion is a symmetry of the component carries no information and MUST be ignored (its centres are ungrouped) | Must | 🟡 partial + gated (G11) — whole-meso case done *(§5, resolved-T)*; subset case open *(§5.S)* |

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

- **G11** — the 1.0 multi-component audit, in `test_enhancedStereo.cpp`:
  `..._s_layer_is_positional` (ES-R21: `/s;3;`, `/s;3;;`, `/s3;;;`, `/s2*3;;`),
  `..._independent_of_aux_none` (ES-R22: same string with and without `-AuxNone`),
  `..._group_spanning_components_is_not_used` (ES-R23: STERAC1/STEREL1 over two components ⇒
  warning + standard string with `1B`; ABS over two components accepted) and
  `..._ungrouped_wedge_keeps_m` (ES-R24: `/m1.` vs `/m0.` for the two enantiomers of the ungrouped
  component), and `..._uniform_class_reduces_to_standard` (ES-R25: all-ABS, all-ABS + Na⁺/OH⁻,
  one OR group per component, one AND group per component + Na⁺/OH⁻ — each byte-identical to
  standard / `-SRel` / `-SRac` apart from the prefix), and `..._non_stereocentres_are_ignored`
  (ES-R26: ABS on a CH₂ of the ungrouped pentanol, on a CH₂ of the AND-only butanol, on OH⁻, and
  AND groups naming a CH₃ beside their centre, incl. two wedge combinations that need the group's
  sign flip). ✅ **passes**; all but ES-R24's verified to fail
  without their fix. Unit level: `test_ichiprt2` `MakeEnhStereoString_skips_non_stereocentres`.
  `..._absolute_set_flips_as_one` (ES-R24, ES-R27) asserts substance identity rather than digits:
  for 3-chlorobutan-2-ol under ABS-C2 + AND-C3, AND-C2 + ungrouped C3, and OR-C2 + ungrouped C3,
  the two wedge sets of one substance give one InChI and the two substances differ; verified to
  fail in all three before the fix. `..._group_spanning_disconnected_metal_is_not_used` and
  `..._haptic_group_follows_inchi_components` (ES-R23 on InChI components: Mg complex rejected;
  haptic complex kept under `-MolecularInorganics` as `/t5-,6-/s3`, rejected without it), and
  `..._unknown_centres_do_not_block_reduction` (ES-R25 under `-SUU`: equals `-SUU` / `-SUU -SRac`).
  `..._reconnected_metal_layer` (ES-R28: `-RecMet`, one AND group per Mg ligand, no crash and `/r`
  carries `/s3`), `..._meso_component_keeps_s` (ES-R29: butane-2,3-diol, meso and chiral drawings
  equal; all-ABS meso stays standard), `..._meso_group_is_dropped` (ES-R33: cyclohexane-1,4-diol
  with no group, AND, OR all `/t5-,6-`; butane-2,3-diol with one AND group over both centres:
  meso drawing `/t3-,4+`, chiral drawing keeps `/t3-,4-/s3`; verified to fail before the fix), `..._isotopic_only_centre` (ES-R30: propan-2-ol-1-¹³C equals
  `-SRel` / `-SRac` / standard) and `..._isotopic_layer_states_its_classes` (ES-R30: OR vs AND on
  an isotope-only centre beside a main-layer centre differ). The three
  `..._inter_enhstereo_grps` tests, which pinned the lossy split, now expect the ES-R23 warning.
  Source structures: `H:\docs\inchi\molecules_enh_stereo\molecules` (7 molfiles + README).

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

Standard output is untouched by 1.0: with the option off (also with `-RecMet`, `-SUU`, `-SRel`)
the InChI and AuxInfo lines are byte-identical to the 0.9 base `4f94b95` — 404 runs over 101
files (test fixtures, these datasets, `datasets/multi_component/`).

All 19 unit suites (228 tests, one disabled: §5.S) pass — `ctest` is green in a fresh out-of-tree build; the
`test_enhancedStereo` suite is now 40 tests, `test_ichiprt2` 25 and `test_mol_fmt` 18. Backward compatibility was re-verified for 0.6 by
building the tree with and without the ES-R18 change and diffing standard (option-off) output
over 84 structures: byte-identical. Out-of-tree build directories still fail
`test_enhancedStereo` and `test_ichimain` on fixture paths — fixed in 0.8, see §5 resolved-B.

> **Build note.** `cmake --build` links the CLI as `bin/inchi-1d`; a stale `bin/inchi-1` from an
> earlier build may sit alongside it and will silently serve outdated measurements. Check the
> binary's mtime before trusting a hand-run comparison.

## 5. Open issues / risks

- **S. A group on a subset of centres whose inversion is a symmetry is still emitted (ES-R33).**
  In O[C@H]1CC[C@H](OCC[C@H](N)C)CC1 the side-chain centre makes the molecule chiral; ring
  centres 9 and 10 only fix cis/trans. Inverting both keeps cis/trans, so a group on them says
  nothing, yet `&1:1,4` gives `/t8-,9-,10-/m1/s3(9,10)` and `o1:1,4` gives `/m1/s2(9,10)`
  instead of `/m1/s1`. Standard InChI only tests whether inverting *all* centres is a symmetry
  (meso); a subset needs an automorphism search, or re-canonicalising a copy with the group
  inverted. Both are canonicalisation-internal and were judged too risky for now. No cheap
  criterion is sound: "every centre has two equivalent neighbours" fails for
  meso-pentane-2,3,4-triol, where inverting C3 alone gives another diastereomer. Pinned as
  `DISABLED_test_EnhancedStereochemistry_meso_subset_group_is_dropped`.

**Resolved in 1.3** (kept for traceability):

- ~~**T. Group inverting a whole meso component was emitted (ES-R33).**~~ Reported in [#286].
  Cyclohexane-1,4-diol measured `/t5-,6-` without a group, `/t5-,6-/s3` with `&1:1,4` and
  `/t5-,6-/s2` with `o1:1,4`: three InChIs for one achiral compound. When one group holds every
  defined centre of a meso component, inverting it mirrors the component, which gives the same
  structure, so the group is ignored. Meso-ness is taken from standard InChI (`nNumberInv` /
  `t_parityInv` equal `nNumber` / `t_parity`) and kept in `INChI_Stereo.bMeso`, because the
  enhanced-stereo code later overwrites `nCompInv2Abs` and flips parities; a late comparison
  would mistake a flipped chiral component for meso. Per-centre groups on a meso component
  (ES-R29) are unaffected: inverting one centre turns meso into chiral.

**Resolved in 1.2** (kept for traceability):

- ~~**R. `/s` lost when no collection named a stereo element (ES-R32).**~~ Found on the
  old-vs-new comparison page: an allene with an AND group on a terminal atom gave `/t2-/m0`,
  no `/s`. The same held for a tetrahedral centre with any label only on a CH₂ or CH₃. As soon
  as the input carries collections, `/s` is built from them (`MakeSlayerString`); here every
  group resolved to nothing, so every slot was empty and the layer vanished (two components:
  `/s;`). The wedged centres are ungrouped, hence absolute, so the output must equal standard
  InChI's `/s1`. Now an all-empty `/s` beside ungrouped centres is written `1`. Not changed: an
  empty slot beside a non-empty one still means "absolute" (`/s;3`, §8.1).

**Resolved in 1.0** (kept for traceability):

- ~~**Q. `-RecMet` crash, and meso components lost `/s` (ES-R28, ES-R29).**~~ With a disconnected
  metal and `-RecMet`, the AuxInfo-only pass for the reconnected structure calls `OutputINChI1`
  with `orig_inp_data = NULL`, and `set_EnhancedStereo_t_m_layers` read through it (valgrind:
  invalid read at `0x68`, segfault; present at the 0.9 base `4f94b95`; natively it ran on stack
  garbage). Now an early return; the INChI pass before it already normalised the same components.
  The garbage had hidden a second defect, single-molecule as well: the `/s` segment followed
  standard InChI's decision, which gives a **meso** component neither `/m` nor `/s`. Butane-2,3-diol
  with one OR (AND) group per centre measured `/t3-,4-` for the meso drawing and `/t3-,4-/s2(3)(4)`
  (`/s3(3)(4)`) for the chiral one — one substance, two InChIs, one of them with no `/s` at all.
  The enhanced main layer now prints `/s` when a component has OR/AND stereocentres
  (`bHasRelRacComponent`); all-ABS meso is untouched and stays standard.
- ~~**J. Isotope-only stereocentres were ignored (ES-R30).**~~ The enhanced pipeline only touched
  `Stereo`, never `StereoIsotopic`. Propan-2-ol-1-¹³C with an OR group measured `/i1+1/t3-/m0/s1` or
  `/m1/s1` by wedge, against `-SRel`'s `/i1+1/t3-/s2`. Fixed through an **isotopic view** of each
  component (`isotopic_stereo_view`: shallow INChI/INChI_Aux copies with `Stereo := StereoIsotopic`
  and the isotopic canonical order), so the existing normalisation, `/m` rule and `MakeSlayerString`
  run on the isotopic layer unchanged. Measuring a mixed molecule (3-chloro-2-methylbutane-¹³C:
  C3 a main-layer centre, C2 isotope-only) found one more gap: standard InChI omits the isotopic
  `/s` when its digit equals the main layer's, so OR and AND on C2 both gave `/i1+1/t4-,5-`. The
  isotopic `/s` is now printed when its **enhanced** classes differ from the main layer's
  (`bIsoSlayerDiffers`): `/s2(4)3(5)` vs `/s3(4)(5)`. Structures with isotopes but no isotope-only
  centre are unchanged (compared against the previous build).

- ~~**P. Absolute centres did not flip as one (ES-R24, ES-R27).**~~ Found by advisor review,
  then measured on 3-chlorobutan-2-ol.
  (1) `invert_parities` *set* `nCompInv2Abs = -1` on an ABS flip instead of toggling it. The
  flip only happens when a lower centre is OR/AND or ungrouped, and then both mirror images
  flipped and both got `/m1`: ABS-C2 + AND-C3, wedges down/up and up/down — different substances —
  both `/t3-,4-/m1/s1(4)3(3)`. Pre-existing since the first implementation.
  (2) An ungrouped wedge counted as absolute only in a component without OR/AND. Beside a single
  OR or AND group, the reduction emitted bare `/s2`/`/s3` and `/m` was zeroed, so all four wedge
  sets of OR-C2 + ungrouped C3 gave `/t3-,4-/s2`: two substances, one InChI.
  Now `absolute_centres` collects STEABS stereocentres plus defined (`+`/`-`) centres in no
  collection; that set is normalised as one group and toggles `/m`; `/m` survives iff it is
  non-empty; and `MakeSlayerString` keeps a single OR/AND group grouped beside an ungrouped wedge.
  No pinned output changed (G1–G10 green unmodified).

- ~~**I. `/s` emitted classes for atoms that are not stereocentres (ES-R26).**~~
  `MakeEnhStereoString` admitted a collection atom on the sole test that it maps into the
  component, so a group could name an atom absent from `/t`, or a component whose `/t` is empty.
  Re-derived by measurement before fixing, as resolved-D advised. Confirmed: `3(1,3)` for `3(3)`
  when an AND group names a CH₃ beside its centre; a bare `1` for a component whose only
  centre is ungrouped, from ABS on one of its CH₂; a `1` on water or OH⁻; the two pinned sightings
  (`…;1(6)3(7,8)` on an empty-`/t` C₈H₁₈, `1(7)3(8,9)` with 7 not in `/t8-,9+`). **Wider than
  recorded:** `component_has_collection_atom` shared the test, so ABS on a CH₂ of an AND-only
  component kept `/m` alive (`/m10/s;1(3)3(4)` for `/m1./s;3`), and it reached `/t`:
  `invert_parities` normalised each group by its lowest canonical atom, centre or not; a CH₃ there
  has no parity, so the group's sign flip was skipped. 3-chlorobutan-2-ol with AND on C2 measured
  `/t3-,4+` when the group also listed the CH₃ and `/t3-,4-` when it did not — one racemate, two
  InChIs, in two of the four wedge combinations. All three paths now go through
  `lookup_stereo_centre`, which also requires the atom in the component's `/t`. A component
  without stereo data admits nothing.

- ~~**O. Uniform multi-component `/s` differed from standard (ES-R25).**~~ Two all-ABS components
  emitted `/s2*1` (`/s2*1;;` with spectators) where standard InChI has `/s1`, breaking the §2
  backward-compatibility invariant beyond one component (G6 covered one). OR/AND likewise:
  `/s2*2`, `/s2*3;;` against `-SRel`/`-SRac`'s `/s2`, `/s3`. `MakeSlayerString` now emits the
  single digit when every component with sp3 centres reduces to the same bare digit and the rest
  have none. A stereo component without a collection (ungrouped wedge) blocks the reduction, so
  `/s;3` stays positional. Sound only because ES-R23 keeps OR/AND groups inside one component.

- ~~**L. `/s` merged non-adjacent components (ES-R21).**~~ `MakeSlayerString` collected the
  per-component substrings in a dictionary that merged equal strings from any position, then
  printed them first-seen. Pentanol + racemic butanol + water gave `/s2*;3` (water racemic)
  for `/s;3;`. Every existing multi-component test had its equal components adjacent. Now one
  slot per component; only consecutive equal non-empty substrings fold, as in `/t` and `/q`.
- ~~**M. `-AuxNone` corrupted `/t` and `/m` (ES-R22).**~~ `OutputINChI1` assigns `pINChI_Aux`
  only when AuxInfo is output, so with `-AuxNone` `set_EnhancedStereo_t_m_layers` received the
  aux of the last component an earlier loop saw. Membership and sign flips ran against the wrong
  component; stereo-free spectators changed `/m` (`/m10..` where none is due) because they
  changed which component that was. Now passed `is->pINChI_Aux[jj]`.
- ~~**N. OR/AND groups spanning components were split silently (ES-R23).**~~ One STERAC1 over two
  alcohols, the same with one wedge flipped, and two independent STERAC groups all gave
  `/t5-;4-/s2*3`. Each component was normalised and reduced on its own, losing the coupling.
  First fixed in the reader with a union-find over the CTab bonds. Advisor review showed that is
  not InChI's component split, and both ways were measured: Mg bis(butan-2-olate) with STERAC1 over
  both ligands passed (Mg is disconnected later) and two different substances shared
  `/t2*4-;/s3`; and a haptically bound ligand that `-MolecularInorganics` keeps in the metal's
  component was falsely rejected. The check now runs after preprocessing on InChI's own
  component numbers (`runichi3.c` `StereoGroupSpansComponents`), only with
  `-EnhancedStereochemistry`, and drops the collections from every copy of the structure.
  Remaining ceilings: every collection atom counts, not only stereocentres (they are not known
  yet at that point); and with `-RecMet` a group inside one reconnected component but across
  disconnected ones is rejected for both layers.

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

Rules (each **MUST** hold; as of 1.0 the code meets all of them, gated by G1–G11):
- An `atom` **MUST** be a stereocentre of the component's `/t`; collection atoms that are not
  are ignored *(ES-R26)*.
- Within an `atom-group`, atoms **MUST** be in ascending canonical order; `atom-group`s within
  an `s-type` **MUST** be ordered by their smallest atom.
- `/m` **MUST** be present iff the component's absolute set — its ABS collection members plus
  its wedged centres in no collection — is non-empty (ES-R24); it
  **MUST NOT** appear when the component has only OR/AND centres, and in a multi-component
  structure this is decided **per component** — the `.` placeholder is used for the components
  that carry no ABS reference, and the segment is omitted entirely when none do
  *(ES-R18, [DECK] slide 10, §5 resolved-G)*. The criterion is membership of a **stereocentre**
  of the component's `/t`, the same test `/s` applies *(ES-R26)*. A spectator without stereo gets
  `.` and never changes another component's digit (ES-R22).
- A component whose centres are all ABS **MUST** reduce to the standard `/s1` (identical to
  `SAbs`); a single OR group **MUST** reduce to `/s2`; a single AND group to `/s3` *(ES-R11,
  ES-R17)* — unless the component also has wedged centres in no collection, which keeps the
  group explicit, e.g. `/m1/s2(4)` *(ES-R24)*. Two or more OR (resp. AND) groups **MUST NOT** be reduced — the grouping is
  information the bare digit would lose.
- The lowest-numbered centre of each group **MUST** be normalised to `-` (whole-group sign
  flip). The absolute set counts as one group, and its flip **MUST** toggle `/m` *(ES-R27)*.
- Canonical atom numbers **MUST** be derived from the collection's molfile atom indexes through
  the final atom order, whatever those indexes are — output **MUST NOT** depend on the input
  numbering *(ES-R20)*.
- Multi-component output uses the existing `count*substring` / `;` composition (extension):
  positional, one `;` slot per component, `n*` only over **consecutive** equal components,
  empty slots never folded — e.g. `/t5-;4-;;` pairs with `/s;3;;` *(ES-R21)*. If every
  component with sp3 centres reduces to the same bare digit and the rest have none, `/s` is that
  single digit, as in standard InChI — `/s3`, not `/s2*3;;` *(ES-R25)*.

## 7. Assumptions & dependencies

- **A-1** Input is MDL V3000 with `STEABS`/`STERELn`/`STERACn` `ATOMS=()` collections; V2000
  has no ESR channel, so a V2000 file yields standard output (no `/s` grouping) ✅ *(held since
  ES-R19; it used to crash instead whenever the V2000 structure had stereocentres)*.
- **A-2** Each stereocentre belongs to **exactly one** collection ([BIOVIA]); the reader MUST
  reject/diagnose violations. An OR/AND group lies within one **InChI** component — after salt
  and metal disconnection, with haptic ligands kept only under `-MolecularInorganics` ✅ *(held
  since ES-R12 / ES-R23; diagnosed and the collections dropped, so the enhanced layer degrades to
  standard output rather than encoding a guess. Ceilings: §5 resolved-N)*.
- **D-1** Depends on final **canonical ranks** (grouping/ordering use canonical atom numbers).
- **A-3** Applies to sp³ centres of the non-isotopic and the isotopic `/t` layer alike; a centre
  stereogenic only through isotopic substitution is grouped in the isotopic layer *(ES-R30)*.
- **D-2** Depends on the existing `/t`+`/m` sp³ parity pipeline; enhanced grouping is layered
  on top, not a replacement.
- **D-3** Reuses the `is_beta` mechanism for the `1B` prefix.

## 8. Worked examples (multi-component)

Measured on `feature/enh-stereo-hardening` with `-EnhancedStereochemistry`; each string is
identical with and without `-AuxNone` (ES-R22). Gated by G11; the molfiles are in
[datasets/multi_component/](datasets/multi_component/).

**Structures.** Butan-2-ol (molfile atoms 1–5, centre **2**) and pentan-2-ol (atoms 6–11,
centre **7**), each wedged, as two components. InChI orders them pentanol first (`C5H12O`), then
butanol (`C4H10O`), then any spectator: water (atom 12), or Na⁺ (12) and OH⁻ (13). Canonical
centres are pentanol 5, butanol 4. Everything up to `/t` is fixed per spectator set:

```
none   InChI=1B/C5H12O.C4H10O/c1-3-4-5(2)6;1-3-4(2)5/h5-6H,3-4H2,1-2H3;4-5H,3H2,1-2H3
water  InChI=1B/C5H12O.C4H10O.H2O/c1-3-4-5(2)6;1-3-4(2)5;/h5-6H,3-4H2,1-2H3;4-5H,3H2,1-2H3;1H2
Na/OH  InChI=1B/C5H12O.C4H10O.Na.H2O/c1-3-4-5(2)6;1-3-4(2)5;;/h5-6H,3-4H2,1-2H3;4-5H,3H2,1-2H3;;1H2/q;;+1;/p-1
```

Below, only the part from `/t` on is shown.

### 8.1 Positional `/s` — one slot per component (ES-R21)

| collections | spectators | `/t…` | wrong (pre-1.0) |
|---|---|---|---|
| `STERAC1 (1 2)` (butanol) | none | `/t5-;4-/m1./s;3` | — |
| `STERAC1 (1 2)` (butanol) | water | `/t5-;4-;/m1../s;3;` | `/s2*;3` (reads: water racemic) |
| `STERAC1 (1 2)` (butanol) | Na/OH | `/t5-;4-;;/m1.../s;3;;` | `/s3*;3` (reads: OH⁻ racemic) |
| `STERAC1 (1 7)` (pentanol) | none | `/t5-;4-/m.0/s3;` | `/m10` with `-AuxNone` |

Each `/s` slot lines up with the `/t` slot of the same component. `n*` folds consecutive equal
non-empty slots only; an empty slot is always written out (`;;`), as in `/t` and `/q`.

### 8.2 `/m` — absolute reference per component (ES-R18, ES-R22, ES-R24)

| collections | `/t…` | why |
|---|---|---|
| `STERAC1 (1 2)`, pentanol wedge up | `/t5-;4-/m1./s;3` | ungrouped wedged pentanol keeps its digit; AND-only butanol gets `.` |
| `STERAC1 (1 2)`, pentanol wedge down | `/t5-;4-/m0./s;3` | the other enantiomer of the pentanol stays distinct |
| `STERAC1 (1 2)` + `STERAC2 (1 7)`, Na/OH | `/t5-;4-;;/s3` | no absolute reference anywhere: no `/m` segment; spectators do not revive it |

### 8.2b Absolute set — mirror images must differ (ES-R24, ES-R27)

3-chlorobutan-2-ol (§8.5), wedges written C2/C3 (up = `CFG=1`, down = `CFG=3`). An AND or OR group
on one centre makes its two epimers one substance.

| collections | wedges → `/t…` | pre-fix |
|---|---|---|
| `STEABS (1 2)` + `STERAC1 (1 3)` | up/up, up/down → `/t3-,4-/m1/s1(4)3(3)`; down/down, down/up → `/t3-,4-/m0/s1(4)3(3)` | down/up gave `/m1`: mirror of up/down, same InChI |
| `STEREL1 (1 2)`, C3 ungrouped | up/up, down/up → `/t3-,4-/m1/s2(4)`; down/down, up/down → `/t3-,4-/m0/s2(4)` | all four `/t3-,4-/s2` |
| `STERAC1 (1 2)`, C3 ungrouped | same split with `/s3(4)` | all four `/t3-,4-/s3` |

### 8.3 Uniform class ⇒ standard single digit (ES-R25)

| collections | spectators | `/t…` | equals |
|---|---|---|---|
| `STEABS (2 2 7)` | none | `/t5-;4-/m10/s1` | standard InChI |
| `STEABS (2 2 7)` | Na/OH | `/t5-;4-;;/m10../s1` | standard InChI |
| `STEREL1 (1 2)` + `STEREL2 (1 7)` | none | `/t5-;4-/s2` | `-SRel` |
| `STERAC1 (1 2)` + `STERAC2 (1 7)` | Na/OH | `/t5-;4-;;/s3` | `-SRac` |

Pre-1.0 these were `/s2*1`, `/s2*1;;`, `/s2*2`, `/s2*3;;`. Not reduced when a component with
stereocentres has no collection: `/s;3` stays positional.

### 8.4 OR/AND group spanning components (ES-R23)

| collections | result |
|---|---|
| `STERAC1 (2 2 7)` or `STEREL1 (2 2 7)` | warning `V3000 collections: STERAC1 spans more than one component`; collections dropped; `/t5-;4-/m10/s1` (standard InChI with `1B`) |
| `STEABS (2 2 7)` | accepted (§8.3) |

Components are InChI's, not the drawing's. Mg bis(butan-2-olate), drawn as one molecule with
`STERAC1` over both ligand centres: Mg is disconnected, the group spans the two butan-2-olates, so
the same warning and standard output with `1B` — `/t2*4-;/m10./s1` or `/m11./s1` by wedges. Pre-fix
both wedge sets gave `/t2*4-;/s3`. Conversely, a ligand bound haptically to Pt stays in Pt's
component under `-MolecularInorganics`, so a `STERAC1` over a centre on it and one on another Pt
ligand is kept: `/t5-,6-/s3`.

Pre-1.0, one AND group over both, the same with the pentanol wedge flipped, and two independent
AND groups all gave `/t5-;4-/s2*3`: three different mixtures, one identifier.

### 8.4b Meso and isotope-only centres (ES-R29, ES-R30, ES-R33)

| structure, collections | `-EnhancedStereochemistry` | pre-fix |
|---|---|---|
| butane-2,3-diol, `STERAC1 (1 2)` + `STERAC2 (1 3)`, chiral or meso drawing | `/t3-,4-/s3(3)(4)` both | meso: `/t3-,4-` (no `/s`) |
| butane-2,3-diol meso, `STEABS (2 2 3)` | `/t3-,4+` (as standard) | same |
| butane-2,3-diol, `STERAC1 (2 2 3)`, meso drawing | `/t3-,4+` (as standard) | `/t3-,4+/s3` |
| butane-2,3-diol, `STERAC1 (2 2 3)`, chiral drawing | `/t3-,4-/s3` (racemate, kept) | same |
| cyclohexane-1,4-diol, `STERAC1 (2 2 5)` / `STEREL1 (2 2 5)` | `/t5-,6-` (as standard) | `/t5-,6-/s3` / `/t5-,6-/s2` |
| O[C@H]1CC[C@H](OCC[C@H](N)C)CC1, `STERAC1` on ring centres | `/t8-,9-,10-/m1/s3(9,10)` — open, §5.S; should be `/m1/s1` | same |
| propan-2-ol-1-¹³C, `STEREL1 (1 2)`, either wedge | `/i1+1/t3-/s2` (== `-SRel`) | `/m0/s1` or `/m1/s1` |
| propan-2-ol-1-¹³C, `STERAC1 (1 2)` | `/i1+1/t3-/s3` (== `-SRac`) | `/m0/s1` |
| 3-chloro-2-methylbutane-¹³C, AND on C3 + OR on C2 | `/t5-/s3/i1+1/t4-,5-/s2(4)3(5)` | `/t5-/s3/i1+1/t4-,5-` |
| same, AND on C3 + AND on C2 | `/t5-/s3/i1+1/t4-,5-/s3(4)(5)` | `/t5-/s3/i1+1/t4-,5-` |
| Mg bis(butan-2-olate), one AND group per ligand, `-RecMet` | `…/t2*4-;/s3/r…/t7-,8-/s3(7)(8)` | crash under valgrind; `/r` without `/s` |

### 8.5 Collection atoms that are not stereocentres (ES-R26)

| collections | `/t…` | wrong (pre-1.0) |
|---|---|---|
| `STERAC1 (1 2)` + `STEABS (1 9)` (CH₂ of pentanol) | `/t5-;4-/m1./s;3` | `/s1;3` |
| `STERAC1 (1 2)` + `STEABS (1 4)` (CH₂ of butanol) | `/t5-;4-/m1./s;3` | `/m10/s;1(3)3(4)` |
| `STERAC1 (1 2)` + `STEABS (1 12)` (water O) | `/t5-;4-;/m1../s;3;` | `/s;3;1` |
| `STERAC1 (1 4)` only (CH₂ of butanol), both centres wedged *(ES-R32)* | `/t5-;4-/m10/s1` | `/s;` (pre-1.2) |

A label that names no stereocentre at all leaves standard InChI's `/s1` *(ES-R32)*:
3-chlorobutan-2-ol, both wedged, `STERAC1 (1 1)` (a CH₃) gives `…/t3-,4-/m1/s1`, not `…/m1`.

Single component, 3-chlorobutan-2-ol (C2–OH, C3–Cl, both wedged up): `STEABS (1 2)` +
`STERAC1 (2 3 4)`, where atom 4 is the CH₃ next to C3:

```
InChI=1B/C4H9ClO/c1-3(5)4(2)6/h3-4,6H,1-2H3/t3-,4-/m1/s1(4)3(3)
```

Pre-1.0: `…/s1(4)3(1,3)`, naming canonical atom 1 (a CH₃) as racemic.

The same molecule with `STEABS (1 3)` and the AND group on C2 plus its CH₃, `STERAC1 (2 1 2)`,
C2 wedged up and C3 down — the CH₃ must not stop the group's sign normalisation:

```
InChI=1B/C4H9ClO/c1-3(5)4(2)6/h3-4,6H,1-2H3/t3-,4-/m0/s1(3)3(4)
```

Pre-1.0: `…/t3-,4+/m0/s1(3)3(4)`, while `STERAC1 (1 2)` without the CH₃ gave `/t3-,4-`.

[RFC 5234]: https://www.rfc-editor.org/rfc/rfc5234
[rdkit/rdkit#8873]: https://github.com/rdkit/rdkit/issues/8873
[rdkit/rdkit#6050]: https://github.com/rdkit/rdkit/issues/6050
[#286]: https://github.com/IUPAC-InChI/InChI/issues/286
