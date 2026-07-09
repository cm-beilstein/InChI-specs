# InChI Enhanced Stereochemistry — Specifications

Four specifications covering the stereochemistry work streams of IUPAC project
[2019-017-2-800](https://iupac.org/project/2019-017-2-800/) ("Enhanced recognition and
encoding of stereoconfiguration by InChI tools"). Each spec states the **target behaviour**
from the project documents, the **actual implementation state** in this repository (with
`file:line` anchors), the **dataset gates** that must pass, and a **deliverables checklist**
of what is done vs. missing.

| # | Spec | Feature | Status | Branch |
|---|------|---------|--------|--------|
| 1 | [enhanced-stereo](enhanced-stereo/SPEC.md) | V3000 ABS/OR/AND enhanced stereo for tetrahedral centres (grouped `/s` layer) | **Mostly implemented** — needs completion/verification | `dev` |
| 2 | [allenes](allenes/SPEC.md) | Axial chirality of allenes/cumulenes + single-stereobond + enhanced OR/AND | Classic done; single-bond & enhanced **not done** | `dev` |
| 3 | [double-bond-ez](double-bond-ez/SPEC.md) | Enhanced OR/AND for C=C double bonds (grouped `/b` layer) | Classic `/b` done; enhanced **not done at all** | `dev` |
| 4 | [atropisomers](atropisomers/SPEC.md) | Axial chirality about a hindered single bond | **Partly implemented** (detection + parity); emission not done | `atropisomers` |

## Source documents

Authored project documents (not in this repo) live in the user's `Downloads`:

- `enh stereo/2026-07-22 Enhanced stereochemistry V00.pptx` — the current consolidated deck
  (presented 2026-06-25); authoritative for the proposed InChI-string encodings of all four
  features. Referenced below as **[DECK]** with slide numbers.
- `enh stereo/Enhanced stereochemistry InChI string creation.docx` — the tetrahedral
  grouped-`/s` algorithm with worked examples and expected strings. **[STRING-ALG]**
- `enh stereo/Enhanced Stereoc.docx` — ESR concepts + nomenclature (Yerin, 2023). **[ESR]**
- `enh stereo/Inchi New Stereoisomer Layer Issues YQ.docx` — BNF for the revised stereo
  layer + the atropisomer-in-`/t` parsing-ambiguity analysis. **[BNF]**
- `enh stereo/IUPAC prject - …docx` — project charter/scope. **[CHARTER]**
- `enh stereo/biovia-enhanced-stereochemical-representation-white-paper.pdf` — third-party
  BIOVIA ESR reference; **the authoritative source for ESR semantics** (ABS/OR/AND
  definitions, STEABS/STERELn/STERACn, display labels `abs`/`orn`/`&n`, the "one group per
  centre" rule, an Appendix-B example V3000 molfile). Referenced as **[BIOVIA]**.
- `atropisomers/InChI encoding of atropisomers.docx` — atropisomer recognition +
  encoding proposal (Yerin). **[ATROP]**
- `atropisomers/2018-06-09-AJM_Atropisomerism_GM_website.pdf` — academic literature-review
  deck (Metrano, Princeton, 2018): atropisomer fundamentals, scaffold taxonomy, descriptors
  (CIP `aR`/`aS` vs helical `M`/`P`), rotational barriers. **Background only** — no InChI
  encoding content. Referenced as **[ATROP-BG]**.

## Common encoding conventions (from [DECK]/[STRING-ALG])

- **Version prefix `1B`** — enhanced-stereo output is flagged *beta/experimental*
  (`InChI=1B/…`) via the existing `is_beta` mechanism.
- **`/s` stereo-type digits:** `1` = absolute (ABS/STEABS), `2` = relative/OR (STEREL#),
  `3` = racemic/AND (STERAC#). Grouped form: `/s1(a,b)2(c,d)(e)3(f)`.
- **`/m` only accompanies absolute centres.** If a component has only OR and/or AND centres,
  `/m` is omitted.
- **Reductions:** a component with only ABS ⇒ identical to standard `SAbs`; only one OR
  group ⇒ identical to `SRel` (`/s2`); only one AND group ⇒ identical to `SRac` (`/s3`).
- **Sign normalisation:** the lowest-numbered centre in each group is normalised to `-`;
  if flipping is needed the whole group's signs flip (and for ABS groups `/m` toggles).

## Requirement conventions (normative)

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHOULD**, **SHOULD NOT**,
**MAY**, and **OPTIONAL** in these specifications are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) / [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174),
and **only when in UPPERCASE**. Lowercase "must"/"should" in prose is explanatory, not normative.

- **Requirement IDs** are per-spec prefixed and stable: `ES-` enhanced stereo, `AL-` allenes,
  `EZ-` double-bond E/Z, `AT-` atropisomers (e.g. `ES-R3`). Each spec's §Traceability maps
  `requirement → gate → source → code`.
- **Gate IDs** (`G#`/`A#`/`Z#`/`T#`) are the verifiable acceptance criteria: a named dataset
  + expected result + observed pass/fail.
- **Prioritisation** uses MoSCoW: **Must** (blocks the feature), **Should** (needed for a
  complete release), **Could** (desirable/deferrable), **Won't** (explicitly out of scope).

## Document control

Each `SPEC.md` opens with a control block: **version · date · status · author · reviewers ·
change history**. Status values: `draft` → `in review` → `approved` → `superseded`. Bump the
version and append a change-history row on every material edit. These specs are `v0.1 (draft)`
as of 2026-07-09.

## Glossary

| Term | Meaning |
|------|---------|
| **ESR** | Enhanced Stereochemical Representation (MDL/BIOVIA V3000 ABS/OR/AND groups). |
| **ABS / OR / AND** | Absolute / relative (one-of-two) / racemic (both) stereo-group types; molfile `STEABS`/`STERELn`/`STERACn`; labels `abs`/`orn`/`&n`. |
| **`/t` layer** | Tetrahedral (and allene-central, atropisomer-axis) parity list: `atom±`. |
| **`/m` layer** | Enantiomer/mirror flag (`m0`/`m1`); accompanies **absolute** centres only. |
| **`/s` layer** | Stereo-type/grouping layer; `1`/`2`/`3` = ABS/OR/AND, grouped `/s1(…)2(…)3(…)`. |
| **`/b` layer** | Double-bond (cis/trans, E/Z) parity layer; proposed grouped form `/b2(2-1-)`. |
| **parity** | InChI canonical odd/even handedness (`AB_PARITY_ODD`/`EVEN`/`UNDF`), **not** CIP R/S. |
| **axial chirality** | Handedness of an axis (allene, atropisomer bond) rather than a point centre. |
| **dissymmetry** | The substituent inequivalence at each end that makes an axis genuinely stereogenic. |
| **cumulene** | Chain of consecutive double bonds `=C=C=…`; odd-length → axial centre on the middle atom. |
| **canonical rank / number** | InChI's invariant atom ordering; the basis for all layer atom numbers. |
| **candidate axis** | A bond passing the topological predicate before dissymmetry pruning (atropisomers). |
| **1B** | Beta/experimental InChI version prefix used for all enhanced-stereo output. |

## How gate status was determined

Enhanced-stereo (dev) and atropisomer (branch) test suites were **built and run** in this
session; gate results below are observed, not inferred. A recurring caveat: several
dataset-driven tests open their fixture via a fixed `../../../../../` relative path that
only resolves at one build depth (`ASSERT_TRUE(is_open())` fails otherwise). This is an
environmental test-harness bug, **not** a logic failure — it is called out per spec and has
a known fix (a CMake `FIXTURES_DIR` compile definition, already applied on the
`atropisomers` branch).
