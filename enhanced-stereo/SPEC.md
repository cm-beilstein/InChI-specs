# Spec 1 — Enhanced Stereochemistry (V3000 ABS/OR/AND, tetrahedral centres)

| | |
|---|---|
| **Doc version** | 0.2 |
| **Date** | 2026-07-10 |
| **Status** | draft |
| **Author** | C. Müller |
| **Reviewers** | TBD (InChI Trust / project 2019-017-2-800 TG) |
| **Requirement prefix** | `ES-` |
| **Change history** | 0.1 (2026-07-09) — initial spec; verified against `dev`, incl. [BIOVIA]. 0.2 (2026-07-10) — consolidated: requirements/gates/deliverables/NFRs merged into one table (§4); ABNF grammar retained (§6). 0.3 (2026-07-10) — readability pass: added At-a-glance, split requirements from gates, tightened prose. |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

- ✅ **Works (end-to-end):** parse V3000 STEABS/STEREL#/STERAC# → `/t`+`/m` normalisation →
  grouped `/s1(…)2(…)3(…)` emission, incl. reductions and multi-component. Tested (G1–G4 pass).
- ❌ **Missing:** explicit-STEABS-only reduction (ES-R11), one-group-per-centre enforcement
  (ES-R12), the dormant 35-molecule gate (ES-R13), and a group-count overflow guard.
- ▶ **Next:** wire the dormant `enh_stereo_test_file_2.sdf` gate and settle the STEABS-only
  reduction — the two open correctness questions.

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
  the `1B` prefix *(gap: §5.C)*.
- *Determinism* — identical input ⇒ identical output, order-independent of input atom order.
- *Robustness* — malformed/empty/out-of-range collections MUST NOT crash and MUST degrade
  gracefully; the `ENH_STEREO_DICT_SIZE=100` cap MUST raise an overflow diagnostic rather than
  silently truncate *(gap: §5.A)*.
- *Performance (SHOULD)* — `/s` construction SHOULD be ≤ O(n·log n) in centres; current O(n²)
  canonical scans are acceptable for typical inputs *(§5.E)*.
- *Portability* — tests MUST resolve fixtures independent of build layout *(gap: §5.B)*.

## 3. Current implementation (branch `dev`, verified by reading + running tests)

| Stage | Location | State |
|-------|----------|-------|
| V3000 COLLECTION parse (STEABS/STEREL#/STERAC#, `ATOMS=()`, group #) | `mol_fmt3.c:647` `MolfileV3000ReadCollections`, dispatch `:695-729`, atoms `:738-780` | ✅ done; non-stereo collections skipped |
| Storage | `inpdef.h:396-404` `OAD_V3000.lists_steabs/sterel/sterac` | ✅ |
| Transfer molfile→`ORIG_ATOM_DATA.v3000` | `mol2atom.c:1646-1712`; component split `runichi3.c:359-395`; free `mol2atom.c:1421-1452` | ✅ |
| Option `-EnhancedStereochemistry` → `ip->bEnhancedStereo` | `ichiparm.c:273-275,2144` | ✅ |
| `1B` beta prefix | `ichiprt1.c:3119` `OutputINCHI_VersionAndKind`, `is_beta` set `:1713-1715`, `B` appended `:3132-3135` | ✅ |
| `/t`+`/m` sign-normalisation | `strutil.c:5053` `set_EnhancedStereo_t_m_layers`, `:4968` `invert_parities` (min-canon centre → `-`, whole-group flip; ABS toggles `nCompInv2Abs`; force `m0` when only OR/AND `:5085-5089`) | ✅ |
| Grouped `/s` emission | `ichiprt1.c:3496` `OutputINCHI_StereoLayer_EnhancedStereo` → `ichiprt2.c:2327` `MakeSlayerString` → `:2213` `MakeEnhStereoString` (type digit, canon-atom map, within-group + inter-group sort, parenthesised groups) | ✅ matches target ordering |
| Multi-component `count*substr` + `;` (beyond single-molecule spec) | `ichiprt2.c:2415-2430` | ✅ present + tested (extension) |

Applies to **sp³ tetrahedral `/t` centres only**; E/Z, allene and atropisomer centres are
not grouped (see specs 2–4).

## 4. Requirements

Priority is MoSCoW; all Must-haves are already met (core works end-to-end). **Won't (this
spec):** name-level `rac`/`rel` nomenclature and independent-centre superscripts ([ESR]/[BNF])
— IUPAC nomenclature recommendations, not InChI code.

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| ES-R1 | Parse STEABS/STEREL#/STERAC# `ATOMS=()` | Must | ✅ `mol_fmt3.c:647` |
| ES-R2 | Grouped `/s1(…)2(…)3(…)` emission | Must | ✅ `ichiprt2.c:2213/2327` |
| ES-R3 | Within-/inter-group ordering | Must | ✅ `ichiprt2.c:2268-2275` |
| ES-R4 | Sign normalisation + `/m` coupling to ABS | Must | ✅ `strutil.c:4968-5089` |
| ES-R5 | Reductions (only-ABS ⇒ `/s1`, only-OR ⇒ `/s2`, only-AND ⇒ `/s3`) | Must | ✅ *partial* — explicit-STEABS-only untested (→ ES-R11) |
| ES-R6 | `-EnhancedStereochemistry` + `1B` prefix | Must | ✅ `ichiparm.c:273` |
| ES-R7 | Multi-component `count*substring` / `;` composition | Should | ✅ `ichiprt2.c:2415` |
| ES-R11 | Explicit-STEABS-only ⇒ bare `/s1` (== `SAbs`) | Should | ❌ untested *(§5.C)* |
| ES-R12 | Enforce one-group-per-centre / at-most-one-ABS; reject conflicts | Should | ❌ not implemented |
| ES-R13 | Wire `enh_stereo_test_file_2.sdf` gate (35 mol) | Should | ❌ dormant |
| ES-R14 | Overflow diagnostic for `ENH_STEREO_DICT_SIZE=100` cap | Should | ❌ silent truncation *(§5.A)* |
| ES-R15 | Fixture-path robustness (`FIXTURES_DIR` CMake define) | Should | ❌ port from `atropisomers` *(§5.B)* |
| ES-R16 | Propagate `set_EnhancedStereo_t_m_layers` sub-call failures | Could | ❌ returns `0` always *(§5.D)* |

### Gates

Datasets live in the repo test tree; see [datasets/DATASETS.md](datasets/DATASETS.md) for
per-molecule detail.

- **G1** — 13 inline ABS/OR/AND cases in `test_enhancedStereo.cpp`. ✅ **13/13 pass**.
- **G2** — 33-molecule `enh_stereo_test_file_1.sdf` (m0/m1 flips, `?` passthrough, reductions).
  ✅ **passes** (when fixture path resolves — §5.B).
- **G3** — `strutil` units (4): sign normalisation, `invert_parities`, canon lookups. ✅ **4/4**.
- **G4** — `MakeSlayerString` → `/s1(1,2)2(6,7)(8)3(3)(4,5)`. ✅ **passes**.
- **G5** — dormant 35-molecule `enh_stereo_test_file_2.sdf` (embedded `<InChI_new>`). ❌ *no gate wired* (ES-R13).
- **G6** — [STRING-ALG] "only ABS/OR/AND" edge tables: explicit STEABS-only ⇒ bare `/s1`. ⚠️ *untested* (ES-R11).

## 5. Open issues / risks

- **A. Silent group-count cap.** `MakeSlayerString` uses a fixed dictionary
  `ENH_STEREO_DICT_SIZE=100` (`mode.h:639`); >100 distinct per-component `/s` substrings are
  dropped with no overflow flag (`ichiprt2.c:2404-2410`).
- **B. Fixture path fragility.** `test_EnhancedStereochemistry_test_file_1`
  (`test_enhancedStereo.cpp:1123`) opens `../../../../../…/enh_stereo_test_file_1.sdf`; fails
  `ASSERT_TRUE(is_open())` unless run from one specific depth. Logic is correct (verified by
  running from a resolvable cwd — G2 passes). Fix = CMake `FIXTURES_DIR` define.
- **C. Explicit-STEABS-only reduction unverified.** With the option on, output is always
  `1B` and an explicit STEABS-only collection would emit `/s1(…)` with parens; [STRING-ALG]
  says a pure-absolute structure must reduce to the bare standard form. In shipped tests this
  only occurs via molfiles with *no* collection block (fall back to standard path); the
  literal explicit-STEABS-only case is untested.
- **D. Return value not propagated.** `set_EnhancedStereo_t_m_layers` returns its initial `0`
  regardless of the three `invert_parities` results (`strutil.c:5057,5081-5091`).
- **E. Efficiency.** `get_canonical_atom_number` is a linear scan called inside loops →
  O(n²) in `invert_parities`/`MakeEnhStereoString`; correctness fine, slow on large inputs.

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

Rules (each **MUST** hold):
- Within an `atom-group`, atoms **MUST** be in ascending canonical order; `atom-group`s within
  an `s-type` **MUST** be ordered by their smallest atom.
- `/m` **MUST** be present iff at least one ABS centre exists; it **MUST NOT** appear when the
  component has only OR/AND centres.
- A component whose centres are all ABS **MUST** reduce to the standard `/s1` (identical to
  `SAbs`); a single OR group **MUST** reduce to `/s2`; a single AND group to `/s3`.
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
