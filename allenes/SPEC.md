# Spec 2 — Allenes (axial chirality of cumulated double bonds)

| | |
|---|---|
| **Doc version** | 0.1 |
| **Date** | 2026-07-09 |
| **Status** | draft |
| **Author** | C. Müller |
| **Reviewers** | TBD (InChI Trust / project 2019-017-2-800 TG) |
| **Requirement prefix** | `AL-` |
| **Change history** | 0.1 (2026-07-09) — initial spec; verified against `dev` |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

- **Feature:** recognise and encode the axial chirality of allenes (`X=C=C=Y`) and odd
  cumulenes, including the two enhancement asks: (a) accept a **single** stereobond, and
  (b) support **enhanced OR/AND** mixtures on the allene axis.
- **Branch:** `dev`
- **Status:** **Classic allene axial chirality is complete and mature.** Single-stereobond
  recognition and enhanced OR/AND grouping are **not done**.
- **Sources:** [DECK] slides 13–22, [ATROP] (allene analogy), [CHARTER] ("support of longer
  allenes").

---

## 1. Problem

An allene `abC=C=Ccd` is axially chiral: the two end substituent planes are perpendicular,
so the axis carries a handedness. InChI already models this. Two gaps remain per [DECK]:

1. **Single stereobond.** IUPAC recommendations accept an allene drawn with a wedge on only
   *one* terminal. [ATROP] notes InChI currently does **not** recognise such single-stereobond
   allenes (e.g. `InChI=1S/C3H2Br2/c4-2-1-3-5/h2-3H` for what should be a chiral draw).
2. **Enhanced OR/AND.** The ESR "or"/"and" mixture concept extends to allene axes — a pure
   but unknown axial configuration (`/s2`) or a racemic axis (`/s3`), grouped like tetrahedral
   centres.

## 2. Target behaviour

From [DECK] slides 15–22:

- The allene axis is encoded on the **central `sp` carbon** in the `/t` layer, exactly as
  today: `InChI=1B/C4H3BrClF/c1-3(6)2-4(5)7/h1H3/t2-/m1/s1` (slide 15).
- **Absolute axis** (pure known): identical to the standard InChI — "in case of *abs axial
  enhanced stereochemistry* use the standard InChI representation" (slide 18).
- **Pure-but-unknown (OR):** `…/t2-/s2` — analogous to tetrahedral OR#; multiple OR axes
  ordered ascending, grouped `2(…)` when combined with other classes (slide 19).
- **Racemic (AND):** `…/t2-/s3` — analogous to tetrahedral AND# (slide 20).
- **Combined allene + tetrahedral:** follow the tetrahedral-centre grouping, the allene's
  central atom participating as an ordinary `/t` centre, e.g.
  `…/t2-,3-/m1/s1(3)2(2)` (slide 22).
- **Single stereobond:** a wedge at one terminal (other end flat) must define the axis, per
  IUPAC — currently unrecognised (slide 15 states only up/up and down/down are handled).

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

## 4. Dataset gates

There are **no dedicated allene unit tests** — coverage today is only end-to-end regression
via the bundled `INCHI_API/bin/Linux/InChI_TestSet_ext.sdf` (`Allene`, `Allene1`,
`D4h-allene`, `cumulenes-c.#001..#006`), which assert nothing about `/t`/`/s`. See
[datasets/DATASETS.md](datasets/DATASETS.md) for the gate molecules seeded from [DECK].

| Gate | Content | Status |
|------|---------|--------|
| A1 Classic axial parity | Ra/Sa allene pair → `/t2-/m0` vs `/t2-/m1` (slide 17) | ⚠️ behaviour present; **no unit test asserting it** |
| A2 Rotamer invariance | two draws of one enantiomer → identical InChI | ⚠️ no test |
| A3 Single stereobond | one-wedge allene → defined `/t` (currently `?`/absent) | ❌ **fails / unsupported** |
| A4 Enhanced OR | `MDLV30/STEREL1 ATOMS=(central)` → `…/t2-/s2` (slide 19) | ❌ not implemented |
| A5 Enhanced AND | `MDLV30/STERAC1 ATOMS=(central)` → `…/t2-/s3` (slide 20) | ❌ not implemented |
| A6 Combined allene+tetrahedral | slide 22 examples → `…/t2-,3-/m1/s1(3)2(2)` | ❌ not implemented |

## 5. Deliverables checklist

**Done**
- [x] Allene/odd-cumulene detection (element + valence + chain-length rules)
- [x] Geometric axial parity (triple product), numbering-invariant, with `MIN_DOT_PROD` cut
- [x] Encoding on central atom in `/t`; enantiomer `/m` inversion
- [x] 0D, isotopic, and cumulene-canonicalisation paths
- [x] Historical FClC=C=CFCl parity bug fixed (`ichister.c:4412`)

**Missing / to do**
- [ ] **Single-stereobond recognition** (A3): make a lone terminal wedge define the axis, per
      IUPAC — adjust the geometry/threshold logic; add fixtures for one-wedge Ra/Sa
- [ ] **Enhanced OR (`/s2`) on allene axes** (A4) — allow `STEREL#` collection to reference
      the allene's terminal/central atom; group it in the `/s` layer
- [ ] **Enhanced AND (`/s3`) on allene axes** (A5)
- [ ] **Combined allene + tetrahedral grouping** (A6) — reuse the tetrahedral `/t`+`/s` path
- [ ] **Dedicated allene test suite** (A1–A2): assert `/t`, `/m`, rotamer invariance,
      round-trip reparse — none exist today
- [ ] Build a curated allene dataset with expected `1B` InChIs (from [DECK] slides 15–22) and
      wire it as a gate
- [ ] Decide/encode longer cumulenes beyond `MAX_CUMULENE_LEN=2` if in scope ([CHARTER]
      "longer allenes") — currently capped (`ichister.c:3352` "short chains for now")

## 6. Open issues / risks

- **Single-bond threshold interplay.** Lowering the effective threshold for one wedge risks
  false positives on decorative wedges; needs the same "ignore decorative stereobonds"
  discipline [ATROP] raises for atropisomers.
- **Enhanced-on-`/t` reuse.** Grouping allenes into `/s` is low-risk *because* the allene is
  already a `/t` centre — but the STEREL/STERAC parser (`mol_fmt3.c:695`) currently only
  meaningfully groups tetrahedral centres; it must tolerate an allene central/terminal atom
  as a group member and the `/t`+`/m` normaliser (`strutil.c:5053`) must handle it.
- **Cumulene length.** `MAX_CUMULENE_LEN=2` and a hard loop cap of 20
  (`ichister.c:4874`) bound support; confirm the project's intended maximum.

## 7. Normative encoding

Allenes reuse the **tetrahedral encoding**, not a new layer: the axial parity is emitted as a
`/t` entry on the **central `sp` atom**, and enhanced OR/AND grouping reuses the `/s` grammar
of [Spec 1 §7](../enhanced-stereo/SPEC.md#7-normative-grammar-s-layer). Requirements (each **MUST**):
- An allene/odd-cumulene axis with defined geometry **MUST** contribute exactly one `/t` entry
  on its central atom; an even cumulene / plain double bond **MUST NOT**.
- Absolute axial configuration **MUST** produce output identical to standard InChI (no `1B`
  divergence for the pure-absolute case).
- Enhanced OR/AND **MUST** place the central atom in an `/s2`/`/s3` group per Spec 1 rules.
- A geometrically undefined axis (`|triple_prod| < MIN_DOT_PROD`) **MUST** render as `?`
  (undefined), never as a guessed parity.

## 8. Assumptions & dependencies

- **A-1** Handedness comes from 2D wedge codes or 3D coordinates via `half_stereo_bond_parity`.
- **A-2** "Single stereobond" support (AL-R3) assumes IUPAC accepts a one-wedge allene as
  configuration-defining; confirm against the recommendation before implementing.
- **D-1** Depends on the allene parity primitives (`half_stereo_bond_parity`,
  `triple_prod_char`) — reuse verbatim; **no new vector maths** (also an atropisomer dep).
- **D-2** Enhanced OR/AND depends on Spec 1's `/s` grouping (`ES-R2..R5`) and on the STEREL/
  STERAC parser tolerating an allene central/terminal atom as a group member.

## 9. Non-functional requirements

- **AL-N1 (numbering invariance, MUST):** axial parity is computed via a triple product and
  MUST be independent of input atom order (already true — `triple_prod_char`).
- **AL-N2 (backward compatibility, MUST):** classic allene InChIs MUST NOT change; enhancement
  work is additive.
- **AL-N3 (no false positives, MUST):** a lone decorative wedge MUST NOT fabricate an axis;
  single-stereobond support (AL-R3) MUST preserve this (`MIN_DOT_PROD` discipline).
- **AL-N4 (rotamer invariance, MUST):** two conformers of one enantiomer MUST yield identical
  InChI (gate A2).

## 10. Requirement traceability

| ID | Requirement | Priority | Gate | Source | Status |
|----|-------------|----------|------|--------|--------|
| AL-R1 | Classic allene/odd-cumulene detection + parity | Must | A1 | existing | `ichister.c:3116-3583` ✅ |
| AL-R2 | Emit on central atom in `/t`; `/m` inversion | Must | A1 | [DECK] s15 | `ichimak2.c:451-546` ✅ |
| AL-R3 | Single-stereobond recognition | Should | A3 | [ATROP], IUPAC | ❌ not done |
| AL-R4 | Enhanced OR (`/s2`) on allene axis | Should | A4 | [DECK] s19 | ❌ not done |
| AL-R5 | Enhanced AND (`/s3`) on allene axis | Should | A5 | [DECK] s20 | ❌ not done |
| AL-R6 | Combined allene + tetrahedral grouping | Should | A6 | [DECK] s22 | ❌ not done |
| AL-R7 | Dedicated allene test suite (parity, rotamer, round-trip) | Must | A1,A2 | — | ❌ none exist |
| AL-R8 | Cumulene length beyond 2 (if in scope) | Could | — | [CHARTER] | capped ❌ |

**Prioritisation (MoSCoW):** Must — AL-R7 (tests for the *already-working* classic path are a
release blocker: behaviour is untested). Should — AL-R3..R6 (the enhancement asks). Could —
AL-R8. Won't (this spec) — spiranes/other axial classes.
