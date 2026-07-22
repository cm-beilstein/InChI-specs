# Spec 2 — Allenes (axial chirality of cumulated double bonds)

| | |
|---|---|
| **Doc version** | 0.2 |
| **Date** | 2026-07-10 |
| **Status** | draft |
| **Author** | C. Müller |
| **Reviewers** | TBD (InChI Trust / project 2019-017-2-800 TG) |
| **Requirement prefix** | `AL-` |
| **Change history** | 0.1 (2026-07-09) — initial spec; verified against `dev`. 0.2 (2026-07-10) — consolidated: merged normative MUSTs into §2, requirements/gates/NFRs into one table (§4). 0.3 (2026-07-10) — readability pass: added At-a-glance, split requirements from gates, tightened prose. |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

- ✅ **Works:** classic allene & odd-cumulene axial chirality — geometric parity, `/t` emission,
  `/m` enantiomer inversion, isotopic/0D paths. Mature.
- ❌ **Missing:** single-stereobond recognition; enhanced OR/AND grouping on the axis; any
  dedicated unit tests.
- ▶ **Next:** add an allene test suite (**AL-R7**) — the working classic path is currently
  untested, which blocks release.

**Feature:** recognise and encode the axial chirality of allenes (`X=C=C=Y`) and odd cumulenes,
plus two enhancement asks — (a) accept a **single** stereobond, and (b) support **enhanced
OR/AND** mixtures on the allene axis. · **Branch:** `dev` · **Sources:** [DECK] slides 13–22,
[ATROP] (allene analogy), [CHARTER] ("support of longer allenes").

---

## 1. Problem

An allene (`abC=C=Ccd`) is axially chiral — its two ends sit in perpendicular planes, so the
axis carries a handedness. InChI already models this. **Two gaps remain** ([DECK]):

1. **Single stereobond.** IUPAC accepts an allene drawn with a wedge on only *one* terminal.
   Per [ATROP], InChI does **not** recognise these today (e.g. `InChI=1S/C3H2Br2/c4-2-1-3-5/h2-3H`
   for what should be a chiral draw).
2. **Enhanced OR/AND.** The ESR "or"/"and" mixture concept extends to allene axes — a
   pure-but-unknown axis (`/s2`) or a racemic axis (`/s3`), grouped like tetrahedral centres.

## 2. Target behaviour & normative rules

From [DECK] slides 15–22. Allenes reuse the **tetrahedral encoding** — no new layer: the axial
parity is emitted as a `/t` entry on the central `sp` atom, and enhanced OR/AND grouping reuses
the `/s` grammar of [Spec 1 §6](../enhanced-stereo/SPEC.md#6-normative-grammar-s-layer). The
rules below are normative (each **MUST**).

- **`/t` on the central atom.** An allene/odd-cumulene axis with defined geometry **MUST**
  contribute exactly one `/t` entry on its central `sp` atom; an even cumulene / plain double
  bond **MUST NOT**. Example: `InChI=1B/C4H3BrClF/c1-3(6)2-4(5)7/h1H3/t2-/m1/s1` (slide 15).
- **Absolute axis (pure known).** Output **MUST** be identical to standard InChI — "in case of
  *abs axial enhanced stereochemistry* use the standard InChI representation" (slide 18); no
  `1B` divergence for the pure-absolute case.
- **Pure-but-unknown (OR).** `…/t2-/s2`, analogous to tetrahedral OR#; multiple OR axes ordered
  ascending, grouped `2(…)` when combined with other classes (slide 19). The central atom
  **MUST** be placed in an `/s2` group per Spec 1 rules.
- **Racemic (AND).** `…/t2-/s3`, analogous to tetrahedral AND# (slide 20); central atom in an
  `/s3` group.
- **Combined allene + tetrahedral.** Follow the tetrahedral-centre grouping, the allene's
  central atom participating as an ordinary `/t` centre, e.g. `…/t2-,3-/m1/s1(3)2(2)` (slide 22).
- **Single stereobond.** A wedge at one terminal (other end flat) **MUST** define the axis, per
  IUPAC — currently unrecognised (slide 15 states only up/up and down/down are handled).
- **Undefined geometry.** An axis with `|triple_prod| < MIN_DOT_PROD` **MUST** render as `?`
  (undefined), never a guessed parity.

**Invariants (all MUST, mostly already met — see §3):**
- *Numbering invariance* — axial parity computed via triple product, independent of input atom
  order (met: `triple_prod_char`).
- *Backward compatibility* — classic allene InChIs MUST NOT change; enhancement is additive.
- *No false positives* — a lone decorative wedge MUST NOT fabricate an axis; single-stereobond
  support (AL-R3) MUST preserve this via the `MIN_DOT_PROD` discipline.
- *Rotamer invariance* — two conformers of one enantiomer MUST yield identical InChI (gate A2).

## 3. Current implementation (branch `dev`)

Constants: `extr_ct.h:242` `MAX_CUMULENE_LEN=2`, `:249` `BOND_CHAIN_LEN`, `:250`
`IS_ALLENE_CHAIN` (odd chain ⇒ axial centre on middle atom), `:288` `MIN_DOT_PROD=50`.

| Capability | Location | State |
|-----------|----------|-------|
| Terminal/middle atom eligibility | `ichister.c:1615` `bCanAtomBeMiddleAllene`, `:1705` `bCanAtomBeTerminalAllene` (C/Si/Ge, neutral, non-radical) | ✅ |
| Chain walking + accept filter | `ichister.c:3116-3358` (`chain_length<=MAX_CUMULENE_LEN`, one stereo bond, no alt bonds) | ✅ |
| Half-bond geometry → `z_dir` (incl. wedge→z) | `ichister.c:2121` `half_stereo_bond_parity` (`:2280-2330` wedge/z) | ✅ |
| Axial parity via triple product | `ichister.c:3575-3577` (odd chain → `triple_prod_char` `:1218`; even → dot product); threshold `:3579-3583` | ✅ numbering-invariant |
| Emit on central atom in `/t` | `ichimak2.c:451` `Copy2StereoBondOrAllene`, insertion `:516-546`; driver `:566` | ✅ |
| Enantiomer inversion (`/m`) | `ichicans.c:2063-2114` (`if (cumulene_len % 2)` invert smaller-numbered atom) | ✅ |
| Cumulene canonical ranking | `ichicans.c:871-960`, `1181-1253` | ✅ |
| 0D (molfile parity) + isotopic paths | `ichister.c:3534-3539` `FixSb0DParities`, `save_a_stereo_bond` `:3595-3662` | ✅ |
| Historical FClC=C=CFCl parity bug | fixed `ichister.c:4412` | ✅ |

**Single stereobond:** there is *no explicit reject* — well-definedness is purely the
`|triple_prod| >= MIN_DOT_PROD` threshold (`ichister.c:3579`). With both terminals flat the
axis lies in-plane ⇒ triple product ≈ 0 ⇒ `AB_PARITY_UNDF` (correct). A single wedge tilts
one `z_dir`; whether that clears `MIN_DOT_PROD` is borderline, which is why the practical
recipe is "wedges at both ends". Supporting a lone terminal wedge is a change to the geometry
interpretation / threshold logic in `set_stereo_bonds_parity` / `half_stereo_bond_parity`,
**not** removal of a guard.

**Enhanced OR/AND:** no per-group OR#/AND# machinery exists anywhere (see spec 1 §3 — it is
tetrahedral-only). Because the allene is injected as an ordinary `/t` centre
(`ichimak2.c:543-544`), it already rides along in the legacy whole-molecule `/s2`/`/s3`
(`INCHI_FLAG_REL/RAC_STEREO`, `ichimak2.c:1226-1230`). True per-axis grouping would reuse the
tetrahedral `/t`+`/s` grouping path (spec 1), keyed on the allene's central atom.

## 4. Requirements

Priority is MoSCoW. **Won't (this spec):** spiranes and other axial-chirality classes.

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| AL-R1 | Classic allene/odd-cumulene detection + parity | Must | ✅ `ichister.c:3116-3583` (behaviour only — no test) |
| AL-R2 | Emit on central atom in `/t`; `/m` inversion | Must | ✅ `ichimak2.c:451-546` |
| AL-R7 | Dedicated allene test suite (parity, rotamer, round-trip) | Must | ❌ **release blocker** — classic path is untested |
| AL-R3 | Single-stereobond recognition (shared: atropisomers AT-R9) | Should | ❌ adjust geometry/threshold logic |
| AL-R4 | Enhanced OR (`/s2`) on allene axis | Should | ❌ |
| AL-R5 | Enhanced AND (`/s3`) on allene axis | Should | ❌ |
| AL-R6 | Combined allene + tetrahedral grouping (reuse `/t`+`/s`) | Should | ❌ |
| AL-R8 | Cumulene length beyond `MAX_CUMULENE_LEN=2` (if in scope) | Could | ❌ capped (`ichister.c:3352` "short chains for now") |

### Gates

No dedicated allene unit tests exist today — coverage is only end-to-end regression via the
bundled `InChI_TestSet_ext.sdf` (`Allene`, `D4h-allene`, `cumulenes-c.#001..#006`), which
assert nothing about `/t`/`/s`. Gate molecules seeded from [DECK] are in
[datasets/DATASETS.md](datasets/DATASETS.md).

- **A1** — classic Ra/Sa pair → `/t2-/m0` vs `/t2-/m1` (slide 17). ⚠️ behaviour present, *no test*.
- **A2** — rotamer invariance: two draws of one enantiomer → identical InChI. ⚠️ *no test*.
- **A3** — single stereobond: one-wedge allene → defined `/t`. ❌ currently `?`/absent.
- **A4** — enhanced OR: `STEREL1 ATOMS=(central)` → `…/t2-/s2` (slide 19). ❌
- **A5** — enhanced AND: `STERAC1 ATOMS=(central)` → `…/t2-/s3` (slide 20). ❌
- **A6** — combined allene+tetrahedral → `…/t2-,3-/m1/s1(3)2(2)` (slide 22). ❌

## 5. Open issues / risks

- **Single-bond threshold interplay.** Lowering the effective threshold for one wedge risks
  false positives on decorative wedges; needs the same "ignore decorative stereobonds"
  discipline [ATROP] raises for atropisomers.
- **Enhanced-on-`/t` reuse.** Grouping allenes into `/s` is low-risk *because* the allene is
  already a `/t` centre — but the STEREL/STERAC parser (`mol_fmt3.c:695`) currently only
  meaningfully groups tetrahedral centres; it must tolerate an allene central/terminal atom
  as a group member and the `/t`+`/m` normaliser (`strutil.c:5053`) must handle it.
- **Cumulene length.** `MAX_CUMULENE_LEN=2` and a hard loop cap of 20
  (`ichister.c:4874`) bound support; confirm the project's intended maximum.

## 6. Assumptions & dependencies

- **A-1** Handedness comes from 2D wedge codes or 3D coordinates via `half_stereo_bond_parity`.
- **A-2** "Single stereobond" support (AL-R3) assumes IUPAC accepts a one-wedge allene as
  configuration-defining; confirm against the recommendation before implementing.
- **D-1** Depends on the allene parity primitives (`half_stereo_bond_parity`,
  `triple_prod_char`) — reuse verbatim; **no new vector maths** (also an atropisomer dep).
- **D-2** Enhanced OR/AND depends on Spec 1's `/s` grouping (`ES-R2..R5`) and on the STEREL/
  STERAC parser tolerating an allene central/terminal atom as a group member.
