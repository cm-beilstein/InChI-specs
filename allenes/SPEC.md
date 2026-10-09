# Spec 2 — Allenes (axial chirality of cumulated double bonds)

| | |
|---|---|
| **Doc version** | 0.5 |
| **Date** | 2026-10-09 |
| **Status** | draft |
| **Author** | C. Müller |
| **Reviewers** | TBD (InChI Trust / project 2019-017-2-800 TG) |
| **Requirement prefix** | `AL-` |
| **Change history** | 0.1 (2026-07-09) — initial spec; verified against `dev`. 0.2 (2026-07-10) — consolidated: merged normative MUSTs into §2, requirements/gates/NFRs into one table (§4). 0.3 (2026-07-10) — readability pass: added At-a-glance, split requirements from gates, tightened prose. 0.4 (2026-10-08) — implemented on `feature/allenes` (from `feature/enh-stereo-hardening`): AL-R3 single stereobond (under `-EnhancedStereochemistry` only), AL-R7 test suite `test_allenes` (gates A1–A6). AL-R4–R6 measured to work without code change. Fixed: A1 STEABS names the *central* atom; `1B` prefix whenever the option is on; undefined axis is omitted, not `?`; collection membership keys on the central atom; line references replaced by function names. 0.5 (2026-10-09) — `-EnhancedStereochemistry` is now the only switch (`-Atropisomers` removed, Spec 4 0.5). A group on a terminal atom lost `/s` (`/t2-/m0`): fixed with Spec 1 ES-R32 (`072d35c`), gated by `group_on_terminal_atom_is_ignored`. |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

- ✅ **Works:** classic allene & odd-cumulene axial chirality — geometric parity, `/t` emission,
  `/m` enantiomer inversion, isotopic/0D paths; single stereobond (enhanced only); enhanced
  OR/AND grouping on the axis; test suite `test_allenes` (A1–A6).
- ❌ **Missing:** AL-R8 (cumulenes beyond `MAX_CUMULENE_LEN`), the A-big stress gate.
- ▶ **Next:** nothing blocking; AL-R8 only if the TG wants longer cumulenes.

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
- **Absolute axis (pure known).** Output **MUST** be identical to standard InChI apart from the
  `1B` prefix — "in case of *abs axial enhanced stereochemistry* use the standard InChI
  representation" (slide 18).
- **Group membership.** A STEABS/STEREL/STERAC collection names the axis by its **central**
  atom (as the deck does). A terminal atom is not a stereocentre and is ignored like any other
  non-centre ([Spec 1](../enhanced-stereo/SPEC.md) ES-R26); the axis then counts as ungrouped.
- **Pure-but-unknown (OR).** `…/t2-/s2`, analogous to tetrahedral OR#; multiple OR axes ordered
  ascending, grouped `2(…)` when combined with other classes (slide 19). The central atom
  **MUST** be placed in an `/s2` group per Spec 1 rules.
- **Racemic (AND).** `…/t2-/s3`, analogous to tetrahedral AND# (slide 20); central atom in an
  `/s3` group.
- **Combined allene + tetrahedral.** Follow the tetrahedral-centre grouping, the allene's
  central atom participating as an ordinary `/t` centre, e.g. `…/t2-,3-/m1/s1(3)2(2)` (slide 22).
- **Single stereobond.** With `-EnhancedStereochemistry`, a wedge at one terminal (other end
  flat) **MUST** define the axis, per IUPAC: the flat end lies in the drawing plane, the wedged
  end perpendicular to it. Standard InChI **MUST** stay unchanged (no axis), per the
  backward-compatibility invariant.
- **Undefined geometry.** An axis with `|triple_prod| < MIN_DOT_PROD` **MUST NOT** get a
  defined parity; it is rendered `?` or omitted by InChI's usual undefined-stereo rules
  (omitted when it is the only stereo element).

**Invariants (all MUST, mostly already met — see §3):**
- *Numbering invariance* — axial parity computed via triple product, independent of input atom
  order (met: `triple_prod_char`).
- *Backward compatibility* — classic allene InChIs MUST NOT change; enhancement is additive.
- *No false positives* — a lone decorative wedge MUST NOT fabricate an axis; single-stereobond
  support (AL-R3) MUST preserve this via the `MIN_DOT_PROD` discipline.
- *Rotamer invariance* — two conformers of one enantiomer MUST yield identical InChI (gate A2).

## 3. Current implementation (branch `feature/allenes`)

Constants (`extr_ct.h`): `MAX_CUMULENE_LEN=2`, `BOND_CHAIN_LEN`, `IS_ALLENE_CHAIN` (odd chain ⇒
axial centre on middle atom), `MIN_DOT_PROD=50`. References are by function name; line numbers
rot.

| Capability | Location | State |
|-----------|----------|-------|
| Terminal/middle atom eligibility | `ichister.c` `bCanAtomBeMiddleAllene`, `bCanAtomBeTerminalAllene` (C/Si/Ge, neutral, non-radical) | ✅ |
| Chain walking + accept filter | `ichister.c` `set_stereo_bonds_parity` (`chain_length<=MAX_CUMULENE_LEN`, one stereo bond, no alt bonds) | ✅ |
| Half-bond geometry → `z_dir` (incl. wedge→z) | `ichister.c` `half_stereo_bond_parity` | ✅ |
| Axial parity via triple product | `set_stereo_bonds_parity` (odd chain → `triple_prod_char`; even → dot product; `MIN_DOT_PROD` threshold) | ✅ numbering-invariant |
| Single stereobond | `ichister.c` `allene_one_wedge_z`, enabled by `PES_BIT_ALLENE_ONE_WEDGE` ← `TG_FLAG_ALLENE_ONE_WEDGE` ← `-EnhancedStereochemistry` | ✅ enhanced only |
| Emit on central atom in `/t` | `ichimak2.c` `Copy2StereoBondOrAllene` | ✅ |
| Enantiomer inversion (`/m`) | `ichicans.c` (`if (cumulene_len % 2)` invert smaller-numbered atom) | ✅ |
| Enhanced OR/AND on the axis | Spec 1 path unchanged (`strutil.c` `lookup_stereo_centre`, `invert_parities`, `absolute_centres`); the central atom is an ordinary `/t` centre | ✅ no code change |
| 0D (molfile parity) + isotopic paths | `FixSb0DParities`, `save_a_stereo_bond` | ✅ |

**Single stereobond.** A lone 2D wedge tilts the wedged end's plane normal by ~45°, which
leaves `|triple_prod|` ≈ 44 for an ideal 120° drawing, under `MIN_DOT_PROD`. With the option
on, when exactly one end is flat and both ends are 2D (atom and neighbours at z = 0, no 0D
parity), `allene_one_wedge_z` replaces the wedged end's normal by its in-plane part
perpendicular to the axis (floor `ALLENE_MIN_TILT=20` of 100). Only the magnitude changes;
the sign is the one the triple product already had. No false positives: both ends flat →
unchanged (undefined); both wedged → unchanged (a contradictory pair stays undefined); a wedge
collinear with the axis → below the floor; plain double bonds use the dot product and are not
touched; 3D input keeps its coordinates.

## 4. Requirements

Priority is MoSCoW. **Won't (this spec):** spiranes and other axial-chirality classes.

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| AL-R1 | Classic allene/odd-cumulene detection + parity | Must | ✅ gated by A1, A2 |
| AL-R2 | Emit on central atom in `/t`; `/m` inversion | Must | ✅ gated by A1 |
| AL-R7 | Dedicated allene test suite (parity, rotamer, round-trip) | Must | ✅ `test_allenes.cpp`, 6 tests |
| AL-R3 | Single-stereobond recognition (shared: atropisomers AT-R9) | Should | ✅ enhanced only, gated by A3 |
| AL-R4 | Enhanced OR (`/s2`) on allene axis | Should | ✅ gated by A4 |
| AL-R5 | Enhanced AND (`/s3`) on allene axis | Should | ✅ gated by A5 |
| AL-R6 | Combined allene + tetrahedral grouping (reuse `/t`+`/s`) | Should | ✅ gated by A6 |
| AL-R8 | Cumulene length beyond `MAX_CUMULENE_LEN=2` (if in scope) | Could | ❌ deferred, capped ("short chains for now") |

### Gates

All in `INCHI-1-TEST/tests/test_unit/test_allenes.cpp`; molecules from [DECK] slides 15–22
(see [datasets/DATASETS.md](datasets/DATASETS.md)).

- **A1** — Ra/Sa pair → `/t2-/m1/s1` vs `/t2-/m0/s1`, standard and `1B`. ✅
- **A2** — rotated drawings and reversed atom numbering → identical InChI. ✅
- **A3** — single wedge at either terminal, up or down → defined `/t2-/m{0,1}/s1` under the
  option; standard unchanged (no `/t`). Rotated draw identical. ✅
- **A4** — `STEREL1 ATOMS=(1 1)` (central) → `/t2-/s2`, either enantiomer draw, also one-wedge. ✅
- **A5** — `STERAC1 ATOMS=(1 1)` → `/t2-/s3`. ✅
- **A6** — allene + tetrahedral, all three deck strings reproduced exactly. ✅
- Undefined: both ends flat, or two contradicting wedges → no `/t`. ✅
- **Terminal-atom group** — `STERAC1`/`STEREL1` on a terminal atom is ignored: `/t2-/m1/s1`, as without it (`group_on_terminal_atom_is_ignored`; `/s` was lost before `072d35c`). ✅

## 5. Open issues / risks

- **Resolved — single-bond threshold interplay.** The threshold is not lowered; the geometry
  is reinterpreted only for the one-flat-one-wedged 2D case (§3).
- **Resolved — enhanced-on-`/t` reuse.** Works unchanged when the collection names the central
  atom; a terminal atom is ignored (§2, user decision 2026-10-08: document, do not map). Until
  0.5 "ignored" also dropped `/s` (`/t2-/m0`); fixed with Spec 1 ES-R32.
- **Cumulene length.** `MAX_CUMULENE_LEN=2` and a hard loop cap of 20 bound support; confirm
  the project's intended maximum (AL-R8).
- **A-big** (slide 21) not materialised: no molfile available.

## 6. Assumptions & dependencies

- **A-1** Handedness comes from 2D wedge codes or 3D coordinates via `half_stereo_bond_parity`.
- **A-2** "Single stereobond" support (AL-R3) assumes IUPAC accepts a one-wedge allene as
  configuration-defining (slide 15); gated behind `-EnhancedStereochemistry` so standard InChI
  does not depend on it.
- **D-1** Depends on the allene parity primitives (`half_stereo_bond_parity`,
  `triple_prod_char`) — reuse verbatim; **no new vector maths** (also an atropisomer dep).
- **D-2** Enhanced OR/AND depends on Spec 1's `/s` grouping (`ES-R2..R5`) and on the STEREL/
  STERAC parser tolerating an allene central/terminal atom as a group member.
