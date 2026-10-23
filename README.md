# InChI Specifications

Specifications for new features and extensions of InChI, developed in
[IUPAC-InChI/InChI](https://github.com/IUPAC-InChI/InChI). Each spec states the **target
behaviour**, the **actual implementation state** (with function names as anchors), the
**dataset gates** that must pass, and what is done vs. missing. The first four cover the
stereochemistry work streams of IUPAC project
[2019-017-2-800](https://iupac.org/project/2019-017-2-800/) ("Enhanced recognition and
encoding of stereoconfiguration by InChI tools").

| # | Spec | Feature | Status | Ready | Branch |
|---|------|---------|--------|-------|--------|
| 1 | [enhanced-stereo](enhanced-stereo/SPEC.md) | V3000 ABS/OR/AND enhanced stereo for tetrahedral centres (grouped `/s` layer) | **Implemented** — v1.3; open: groups on a meso subset (§5.S) | ready | `atropisomers` (base: `feature/enh-stereo-hardening`) |
| 2 | [allenes](allenes/SPEC.md) | Axial chirality of allenes/cumulenes + single-stereobond + enhanced OR/AND | **Implemented** — v0.6; open: cumulene length, slide-21 molecule, pseudo-asymmetric axis | open points | `atropisomers` (from `feature/allenes`) |
| 3 | [double-bond-ez](double-bond-ez/SPEC.md) | Enhanced OR/AND for C=C double bonds (grouped `/b` layer) | **Implemented** — v0.5; open: reading grouped `/b` back, fixed-H/isotopic `/b` | open points | `atropisomers` (from `feature/double-bond-ez`) |
| 4 | [atropisomers](atropisomers/SPEC.md) | Axial chirality about a hindered single bond | **Implemented** — v0.6 (detection, `/t`+`/m`); open: reparse round-trip, C–N/N–N axes | open points | `atropisomers` |
| 5 | [impossible-ring-stereo](impossible-ring-stereo/SPEC.md) | Warn on physically impossible ring stereo (in/out bridgeheads, trans fusion) | **Proposed** — v0.1, [IUPAC-InChI/InChI#287](https://github.com/IUPAC-InChI/InChI/issues/287); open: ring-size limits, warning text | open points | — |
| 6 | [inchi-versioning](inchi-versioning/SPEC.md) | Version prefix `1S`/`1B`/`1N` + subversion `B` (Molecular Inorganics), InChIKey flags `SA`…`NB` | **Implemented** — v0.1 (#280); open: combining letters, metalloids, lookup table | open points | `dev` |

`#` is the spec number and the landing row (`#f<n>`). Specs 1–4 run under one option,
`-EnhancedStereochemistry`, with prefix `InChI=1B/`; branch `atropisomers` contains all of them.

## Layout

```
index.html                 landing page (generated)
<key>/SPEC.md              specification, for developers
<key>/explain.html         explanation for chemists (generated from explain.template.html)
<key>/examples/            old vs. new InChI per molecule (generated)
<key>/workflow.html        how the new InChI is built, step by step (optional)
<key>/datasets/            molecules the spec, tests and pages use; DATASETS.md lists them
docs/<topic>/              kick-off documents (issue attachments, decks, papers)
tools/                     generators and helpers, below
skills/                    Claude Code skills for this workflow, below
```

## Site

[InChI Specifications](https://cm-beilstein.github.io/InChI-specs/), served from `main` by
GitHub Pages. One row per feature (`tools/site.json`, in order) with these columns:

| Column | Content | Source |
|---|---|---|
| Ready | is the information sufficient to implement? ready / open points / not ready | Readiness row in the SPEC.md header, confirmed by a person |
| Done | Must/Should requirements and gates met | ✅ markers in the SPEC.md requirement table and Gates section |
| For chemists | explanation page | `<key>/explain.html` |
| Examples | old vs. new InChI (and InChIKey) per molecule | `<key>/examples/` |
| Technical | specification, workflow, datasets, kick-off documents | `SPEC.md`, `workflow.html`, `datasets/DATASETS.md`, `docs/<topic>/` |
| GitHub | branch, issues and pull requests in IUPAC-InChI/InChI | `tracking` in `tools/site.json` |
| Discussion | the feature's general discussion | `specDiscussions` in `tools/giscus.json` |

Molecule IDs are global over all specs (1–129 at present) and never renumbered: issue
comments refer to them. New molecules get the next free number. `#m13` links to molecule 13.

### Tools

| Command | Does |
|---|---|
| `python tools/rebuild.py` | builds the InChI revisions named in `site.json` (cached in `~/.cache/inchi-specs/`), regenerates explanation, examples and landing pages |
| `python tools/audit.py <key>` | lists every document of a feature as ok or MISSING |
| `python tools/new_discussion.py <key>` | creates the feature's general discussion once |

Python with RDKit ≥ 2024 (e.g. `~/.venvs/inchi-specs`), an InChI clone at `../InChI`, `gh`
logged in. `rebuild.py` only fetches and adds temporary worktrees in the clone; it leaves
the checked-out branch alone.

### Comments

Every molecule and every explanation section has a **Comment** button that opens its own
[giscus](https://giscus.app) thread, stored in this repo's Discussions, titled e.g.
`enhanced-stereo · molecule 13` or `enhanced-stereo · explain · meso`. Commenting needs a
GitHub account. Each feature also has a general discussion (`<key> · general`), linked from
every page and opened by the landing page's Comment buttons. Configuration:
`tools/giscus.json` (category Announcements: only giscus opens threads, everyone replies).

## Skills

Two [Claude Code](https://claude.com/claude-code) skills in `skills/` run this workflow;
link them into `~/.claude/skills/` to use them:

- **inchi-feature-check** — takes an issue/PR/feature through kick-off documents,
  readiness, datasets, unit tests, code, spec, site entry with discussion, examples and
  explanation, and creates what is missing.
- **inchi-feature-update** — after a code change, finds every affected document (including
  sibling specs) and updates it from measurements.

## Source documents

Kick-off documents live in `docs/<topic>/`, one folder per topic. Stereochemistry
(specs 1–4), in [`docs/stereochemistry/`](docs/stereochemistry/):

- [`docs/stereochemistry/2026-07-22 Enhanced stereochemistry V00.pptx`](docs/stereochemistry/2026-07-22%20Enhanced%20stereochemistry%20V00.pptx)
  — the current consolidated deck; authoritative for the proposed InChI-string encodings of all
  four features. Referenced below as **[DECK]** with slide numbers.
- [`docs/stereochemistry/Enhanced stereochemistry InChI string creation.docx`](docs/stereochemistry/Enhanced%20stereochemistry%20InChI%20string%20creation.docx)
  — the tetrahedral grouped-`/s` algorithm with worked examples and expected strings. **[STRING-ALG]**
- [`docs/stereochemistry/Enhanced Stereoc.docx`](docs/stereochemistry/Enhanced%20Stereoc.docx) — ESR concepts + nomenclature (Yerin, 2023). **[ESR]**
- [`docs/stereochemistry/Inchi New Stereoisomer Layer Issues YQ.docx`](docs/stereochemistry/Inchi%20New%20Stereoisomer%20Layer%20Issues%20YQ.docx)
  — BNF for the revised stereo layer + the atropisomer-in-`/t` parsing-ambiguity analysis. **[BNF]**
- [`docs/stereochemistry/IUPAC prject - Enhanced recognition and encoding of stereoconfiguration by InChI tools.docx`](docs/stereochemistry/IUPAC%20prject%20-%20Enhanced%20recognition%20and%20encoding%20of%20stereoconfiguration%20by%20InChI%20tools.docx)
  — project charter/scope. **[CHARTER]**
- [`docs/stereochemistry/biovia-enhanced-stereochemical-representation-white-paper.pdf`](docs/stereochemistry/biovia-enhanced-stereochemical-representation-white-paper.pdf)
  — third-party BIOVIA ESR reference; **the authoritative source for ESR semantics** (ABS/OR/AND
  definitions, STEABS/STERELn/STERACn, display labels `abs`/`orn`/`&n`, the "one group per
  centre" rule, an Appendix-B example V3000 molfile). Referenced as **[BIOVIA]**.
- [`docs/stereochemistry/InChI encoding of atropisomers.docx`](docs/stereochemistry/InChI%20encoding%20of%20atropisomers.docx)
  — atropisomer recognition + encoding proposal (Yerin). **[ATROP]**
- `2018-06-09-AJM_Atropisomerism_GM_website.pdf` — academic literature-review deck (Metrano,
  Princeton, 2018): atropisomer fundamentals, scaffold taxonomy, descriptors (CIP `aR`/`aS` vs
  helical `M`/`P`), rotational barriers. **Background only** — no InChI encoding content, **not
  vendored**. Referenced as **[ATROP-BG]**.

Impossible ring stereo (spec 5), in [`docs/impossible-ring-stereo/`](docs/impossible-ring-stereo/):

- [`docs/impossible-ring-stereo/issue-287.md`](docs/impossible-ring-stereo/issue-287.md) — snapshot of
  [IUPAC-InChI/InChI#287](https://github.com/IUPAC-InChI/InChI/issues/287) with its comments: problem,
  example molfile, proposed detection rules.

Versioning (spec 6), in [`docs/inchi-versioning/`](docs/inchi-versioning/):

- [`docs/inchi-versioning/InChITrust-Chicago InChI Meeting - Versioning.pdf`](docs/inchi-versioning/InChITrust-Chicago%20InChI%20Meeting%20-%20Versioning.pdf)
  — InChI Trust meeting slides on version prefixes and InChIKey flags, attached to
  [IUPAC-InChI/InChI#285](https://github.com/IUPAC-InChI/InChI/issues/285).

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
