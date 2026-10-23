# InChI Specifications

Specifications for new features and extensions of InChI, developed in
[IUPAC-InChI/InChI](https://github.com/IUPAC-InChI/InChI). Each spec states the **target
behaviour**, the **actual implementation state** (with function names as anchors), the
**dataset gates** that must pass, and what is done vs. missing. The first four cover the
stereochemistry work streams of IUPAC project
[2019-017-2-800](https://iupac.org/project/2019-017-2-800/) ("Enhanced recognition and
encoding of stereoconfiguration by InChI tools").

| # | Spec | Feature | Status | Branch |
|---|------|---------|--------|--------|
| 1 | [enhanced-stereo](enhanced-stereo/SPEC.md) | V3000 ABS/OR/AND enhanced stereo for tetrahedral centres (grouped `/s` layer) | **Implemented** — v1.3; open: groups on a meso subset (§5.S) | `atropisomers` (base: `feature/enh-stereo-hardening`) |
| 2 | [allenes](allenes/SPEC.md) | Axial chirality of allenes/cumulenes + single-stereobond + enhanced OR/AND | **Implemented** — v0.6; open: cumulene length, slide-21 molecule, pseudo-asymmetric axis | `atropisomers` (from `feature/allenes`) |
| 3 | [double-bond-ez](double-bond-ez/SPEC.md) | Enhanced OR/AND for C=C double bonds (grouped `/b` layer) | **Implemented** — v0.5; open: reading grouped `/b` back, fixed-H/isotopic `/b` | `atropisomers` (from `feature/double-bond-ez`) |
| 4 | [atropisomers](atropisomers/SPEC.md) | Axial chirality about a hindered single bond | **Implemented** — v0.6 (detection, `/t`+`/m`); open: reparse round-trip, C–N/N–N axes | `atropisomers` |
| 5 | [explanation](impossible-ring-stereo/explain.html) | Detect physically impossible ring stereo (in/out bridgeheads, trans fusion) | **Proposed** — [IUPAC-InChI/InChI#287](https://github.com/IUPAC-InChI/InChI/issues/287), to be discussed | — |

The four implemented ones run under one option, `-EnhancedStereochemistry`, with prefix `InChI=1B/`. Branch
`atropisomers` contains all of them.

## Site

[InChI Specifications](https://cm-beilstein.github.io/InChI-specs/) — per spec, four documents,
plus its branch, issues and pull requests in IUPAC-InChI/InChI (`TRACKING` in `tools/build.py`):

| File | For | Built by |
|---|---|---|
| `<spec>/SPEC.md` | developers: requirements, gates, open issues | hand |
| `<spec>/explain.html` | chemists: what the labels mean, how they reach the InChI | `tools/explain.py` from `explain.template.html` |
| `<spec>/examples/` | old vs. new InChI per molecule (`index.html`, `<table>.sdf`, `svg/`) | `tools/build.py` from `tools/molecules.py` |
| `<spec>/workflow.html` | chemists: the new InChI built step by step | [archify](https://github.com/tt-a1i/archify) from `tools/workflow/<table>.json` |

Molecule IDs are global over all specs (1–115 at present) and never renumbered: issue
comments refer to them. New molecules get the next free number. `#m13` links to molecule 13.

Rebuild (RDKit needed; `../InChI` checked out on `atropisomers`):

```
INCHI_OLD=/path/dev/inchi-1 INCHI_NEW=/path/atropisomers/inchi-1 python tools/build.py
INCHI_NEW=/path/atropisomers/inchi-1 python tools/explain.py
```

### Comments

Every molecule and every explain section has a **Comment** button that opens its own
[giscus](https://giscus.app) thread, stored in this repo's Discussions, titled e.g.
`enhanced-stereo · molecule 13` or `enhanced-stereo · explain · meso`. Commenting needs a
GitHub account. Setup: Discussions on, giscus app installed, a discussion category for the
threads (here: Announcements, so only giscus opens threads; everyone can reply); then fill
`tools/giscus.json` (`repo`, `repoId`, `category`, `categoryId`, shown on https://giscus.app)
and rebuild. With `repo` empty the pages have no buttons.

Each spec also has a general discussion (`<spec> · general`, numbers in
`specDiscussions` of `tools/giscus.json`), linked from every page and opened in place by
the landing page's Comment buttons.

## Source documents

Authored project documents are vendored in [`docs/`](docs/):

- [`docs/2026-07-22 Enhanced stereochemistry V00.pptx`](docs/2026-07-22%20Enhanced%20stereochemistry%20V00.pptx)
  — the current consolidated deck; authoritative for the proposed InChI-string encodings of all
  four features. Referenced below as **[DECK]** with slide numbers.
- [`docs/Enhanced stereochemistry InChI string creation.docx`](docs/Enhanced%20stereochemistry%20InChI%20string%20creation.docx)
  — the tetrahedral grouped-`/s` algorithm with worked examples and expected strings. **[STRING-ALG]**
- [`docs/Enhanced Stereoc.docx`](docs/Enhanced%20Stereoc.docx) — ESR concepts + nomenclature (Yerin, 2023). **[ESR]**
- [`docs/Inchi New Stereoisomer Layer Issues YQ.docx`](docs/Inchi%20New%20Stereoisomer%20Layer%20Issues%20YQ.docx)
  — BNF for the revised stereo layer + the atropisomer-in-`/t` parsing-ambiguity analysis. **[BNF]**
- [`docs/IUPAC prject - Enhanced recognition and encoding of stereoconfiguration by InChI tools.docx`](docs/IUPAC%20prject%20-%20Enhanced%20recognition%20and%20encoding%20of%20stereoconfiguration%20by%20InChI%20tools.docx)
  — project charter/scope. **[CHARTER]**
- [`docs/biovia-enhanced-stereochemical-representation-white-paper.pdf`](docs/biovia-enhanced-stereochemical-representation-white-paper.pdf)
  — third-party BIOVIA ESR reference; **the authoritative source for ESR semantics** (ABS/OR/AND
  definitions, STEABS/STERELn/STERACn, display labels `abs`/`orn`/`&n`, the "one group per
  centre" rule, an Appendix-B example V3000 molfile). Referenced as **[BIOVIA]**.
- [`docs/InChI encoding of atropisomers.docx`](docs/InChI%20encoding%20of%20atropisomers.docx)
  — atropisomer recognition + encoding proposal (Yerin). **[ATROP]**
- `2018-06-09-AJM_Atropisomerism_GM_website.pdf` — academic literature-review deck (Metrano,
  Princeton, 2018): atropisomer fundamentals, scaffold taxonomy, descriptors (CIP `aR`/`aS` vs
  helical `M`/`P`), rotational barriers. **Background only** — no InChI encoding content, **not
  vendored**. Referenced as **[ATROP-BG]**.

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
