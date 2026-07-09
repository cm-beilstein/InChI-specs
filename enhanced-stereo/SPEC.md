# Spec 1 — Enhanced Stereochemistry (V3000 ABS/OR/AND, tetrahedral centres)

| | |
|---|---|
| **Doc version** | 0.1 |
| **Date** | 2026-07-09 |
| **Status** | draft |
| **Author** | C. Müller |
| **Reviewers** | TBD (InChI Trust / project 2019-017-2-800 TG) |
| **Requirement prefix** | `ES-` |
| **Change history** | 0.1 (2026-07-09) — initial spec; verified against `dev`, incl. [BIOVIA] |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

- **Feature:** recognise MDL V3000 enhanced-stereo collections (STEABS / STEREL# / STERAC#)
  on sp³ tetrahedral centres and encode them in an extended, grouped InChI `/s` layer.
- **Branch:** `dev` (implemented) · **Option:** `-EnhancedStereochemistry` · **Prefix:** `InChI=1B/…`
- **Status:** **Mostly implemented end-to-end.** Parse → transfer → `/t`+`/m` normalisation →
  grouped `/s` emission all present and tested. Remaining work is edge-case completion,
  robustness, and closing dataset gaps — enumerated in §6.
- **Sources:** [STRING-ALG], [DECK] slides 6–12, [BIOVIA] (authoritative ESR semantics), [BNF], [ESR].

---

## 1. Problem

Industrial structure files use MDL V3000 *enhanced stereochemical representation* (ESR) to
express mixtures / partially-known stereochemistry: each stereocentre is tagged **abs**
(absolute), **or#** (one of two enantiomers — relative), or **and#** (both enantiomers —
racemic), with a group index tying dependent centres together. Standard InChI ignores these
collections and treats every centre as absolute, so distinct substances (e.g. the
cypermethrin family, [ESR]) collapse to one identifier.

## 2. Target behaviour

From [STRING-ALG] and [DECK]:

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

## 4. Dataset gates

Datasets live in the repo test tree; see [datasets/DATASETS.md](datasets/DATASETS.md) for
per-molecule detail.

| Gate | Dataset | Assertion | Observed status |
|------|---------|-----------|-----------------|
| G1 Unit/integration cases | inline molblocks in `test_enhancedStereo.cpp` (13 cases) | exact `szInChI` for single-mol ABS/OR/AND, empty/invalid collections, multi-component dedup, differing-AND | ✅ **13/13 pass** |
| G2 Reference dataset | `fixtures/enh_stereo_test_file_1.sdf` (33 molecules) via `test_EnhancedStereochemistry_test_file_1`, expected in `list_expected_inchis[33]` | all 33 emitted InChIs match | ✅ **passes** (only when fixture path resolves — see §6.B) |
| G3 `strutil` units | `test_strutil_enhancedStereo.cpp` (4) | `set_EnhancedStereo_t_m_layers`, `invert_parities`, canon lookups | ✅ **4/4 pass** |
| G4 `/s` emitter unit | `test_ichiprt1_enhancedStereo.cpp` (1) | `MakeSlayerString` → `/s1(1,2)2(6,7)(8)3(3)(4,5)` | ✅ **passes** |
| G5 Second dataset | `fixtures/enh_stereo_test_file_2.sdf` (35 molecules, **embedded** `<InChI>`/`<InChI_new>`/`<Isomer>` columns) | emitted `/s` InChI == embedded `<InChI_new>` | ❌ **no gate exists** — dataset unused by any test |
| G6 [STRING-ALG] edge tables | "Only ABS / Only OR / Only AND" worked examples | explicit STEABS-only ⇒ bare `/sX` reduction | ⚠️ **untested** (see §6.C) |

## 5. Deliverables checklist

**Done**
- [x] Parse STEABS / STEREL# / STERAC# collections with group numbers and atom lists
- [x] Store + transfer + component-split + free enhanced-stereo lists
- [x] `-EnhancedStereochemistry` CLI option and `1B` beta prefix
- [x] Grouped `/s1(…)2(…)3(…)` emission with correct type digits and parenthesisation
- [x] Within-group ascending sort; inter-group ordering by smallest canonical atom
- [x] Sign normalisation (lowest centre → `-`, whole-group flip)
- [x] `/m` coupled to ABS only; forced `m0` when only OR/AND present
- [x] Reductions: only-OR ⇒ `/s2`, only-AND ⇒ `/s3`, `?` undefined centres preserved
- [x] Multi-component multipliers/dedup (`2*1(…)`, `;`)
- [x] Unit + integration + 33-molecule dataset gates (G1–G4)

**Missing / to complete**
- [ ] **G5:** wire `enh_stereo_test_file_2.sdf` into a test asserting emitted InChI ==
      embedded `<InChI_new>` (35-molecule validation gate currently dormant)
- [ ] **G6 / §6.C:** define + test explicit-STEABS-only reduction to bare `/s1`
      (identical to `SAbs`) — [STRING-ALG] requires molfile-type independence
- [ ] **§6.A:** guard `ENH_STEREO_DICT_SIZE=100` overflow (currently silent truncation)
- [ ] **§6.D:** propagate `set_EnhancedStereo_t_m_layers` sub-call failures (return always `0`)
- [ ] Fixture-path robustness (§6.B) — port the `FIXTURES_DIR` CMake fix from `atropisomers`
- [ ] Enforce the [BIOVIA] "one group per centre" rule — reject/diagnose a centre appearing
      in more than one collection, and more than one ABS collection (currently unchecked)
- [ ] Documentation of the `/s` grammar in the InChI technical manual

## 6. Open issues / risks

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
- **F. Nomenclature scope out of band.** [ESR]/[BNF] discuss name-level `rac`/`rel` and
  independent-centre superscripts; these are IUPAC nomenclature recommendations, not InChI
  code, and are out of scope for this spec.

## 7. Normative grammar (`/s` layer)

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

## 8. Assumptions & dependencies

- **A-1** Input is MDL V3000 with `STEABS`/`STERELn`/`STERACn` `ATOMS=()` collections; V2000
  has no ESR channel, so a V2000 file yields standard output (no `/s` grouping).
- **A-2** Each stereocentre belongs to **exactly one** collection ([BIOVIA]); the reader
  MUST reject/diagnose violations (see §6, `ES-R12`).
- **D-1** Depends on final **canonical ranks** (grouping/ordering use canonical atom numbers).
- **D-2** Depends on the existing `/t`+`/m` sp³ parity pipeline; enhanced grouping is layered
  on top, not a replacement.
- **D-3** Reuses the `is_beta` mechanism for the `1B` prefix.

## 9. Non-functional requirements

- **ES-N1 (backward compatibility, MUST):** with `-EnhancedStereochemistry` off, output is
  byte-identical to standard InChI. With it on, an all-absolute structure MUST equal the
  standard string except the `1B` prefix. *(gap: §6.C — currently untested/possibly divergent.)*
- **ES-N2 (determinism, MUST):** identical input ⇒ identical output; order-independent of
  input atom order.
- **ES-N3 (robustness, MUST):** malformed/empty/out-of-range collections MUST NOT crash and
  MUST degrade gracefully (covered by G1 cases). The `ENH_STEREO_DICT_SIZE=100` cap MUST
  raise an overflow diagnostic rather than silently truncate *(gap: §6.A)*.
- **ES-N4 (performance, SHOULD):** `/s` construction SHOULD be ≤ O(n·log n) in centres; the
  current O(n²) canonical-number scans are acceptable for typical inputs but SHOULD be
  addressed for large structures *(§6.E)*.
- **ES-N5 (portability, MUST):** builds and passes on the InChI-supported toolchains; tests
  MUST resolve fixtures independent of build layout *(§6.B)*.

## 10. Requirement traceability

| ID | Requirement | Priority | Gate | Source | Code / status |
|----|-------------|----------|------|--------|---------------|
| ES-R1 | Parse STEABS/STEREL#/STERAC# `ATOMS=()` | Must | G1,G2 | [BIOVIA], [DECK] | `mol_fmt3.c:647` ✅ |
| ES-R2 | Grouped `/s1(…)2(…)3(…)` emission | Must | G1,G4 | [STRING-ALG] | `ichiprt2.c:2213/2327` ✅ |
| ES-R3 | Within-/inter-group ordering | Must | G1,G4 | [STRING-ALG] | `ichiprt2.c:2268-2275` ✅ |
| ES-R4 | Sign normalisation + `/m` coupling to ABS | Must | G1,G2 | [STRING-ALG] | `strutil.c:4968-5089` ✅ |
| ES-R5 | Reductions (only-ABS/OR/AND) | Must | G2 | [DECK] s10 | partial — explicit-STEABS-only untested (ES-R11) |
| ES-R6 | `-EnhancedStereochemistry` + `1B` | Must | G1 | [DECK] | `ichiparm.c:273` ✅ |
| ES-R7 | Multi-component composition | Should | G1 | [DECK] s9 | `ichiprt2.c:2415` ✅ |
| ES-R11 | Explicit-STEABS-only ⇒ bare `/s1` | Should | G6 | [STRING-ALG] | untested ❌ |
| ES-R12 | Enforce one-group-per-centre | Should | — (new) | [BIOVIA] | not implemented ❌ |
| ES-R13 | Wire `enh_stereo_test_file_2.sdf` gate | Should | G5 | dataset | dormant ❌ |

**Prioritisation (MoSCoW) of open items:** Must — none outstanding (core works). Should —
ES-R11, ES-R12, ES-R13, ES-N3 overflow guard, ES-N5 fixture-path. Could — ES-N4 O(n²),
return-propagation (§6.D). Won't (this spec) — name-level nomenclature (§6.F).

[RFC 5234]: https://www.rfc-editor.org/rfc/rfc5234
