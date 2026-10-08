# Spec 3 — Double-bond E/Z (enhanced OR/AND for C=C stereo bonds)

| | |
|---|---|
| **Doc version** | 0.4 |
| **Date** | 2026-10-08 |
| **Status** | draft |
| **Author** | C. Müller |
| **Reviewers** | TBD (InChI Trust / project 2019-017-2-800 TG) |
| **Requirement prefix** | `EZ-` |
| **Change history** | 0.1 (2026-07-09) — initial spec; verified against `dev`. 0.2 (2026-07-10) — consolidated: requirements/gates/deliverables/NFRs merged into one table (§4); ABNF grammar retained (§6). 0.3 (2026-07-10) — readability pass: added At-a-glance, split requirements from gates, tightened prose. 0.4 (2026-10-08) — implemented on `feature/double-bond-ez`. User decisions: EZ-R8 digits `2`/`3`; a group keeps the relative geometry of its bonds (`/s`-style normalisation, the lowest bond reads `-`); several groups use the `/s` block layout, comma-joined to the flat list (`/b12-5+,2(16-14-),3(15-10-,17-11-)(18-13-)`). Corrected: the trailing `-` of a deck pair is the normalised parity, not a sign on both atoms; `1B` prefix whenever the option is on; group numbers are never emitted. Found: component order with enhanced classes depends on input order (§5, shared with Spec 1). |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

- ✅ **Works:** classic absolute `/b`; either/crossed/wavy bonds; V3000 `STEBABS`/`STEBRELn`/
  `STEBRACn` input; grouped `/b2(…)`/`/b3(…)` output; combined with `/t`+`/s`. Test suite
  `test_doubleBondEZ` (9 tests).
- ❌ **Open:** component order is input-dependent when components differ only in enhanced
  classes (§5, shared with Spec 1); grouped `/b` in fixed-H and isotopic layers; InChI→structure
  parsing of grouped `/b`.

**Feature:** recognise MDL V3000 **bond** stereo collections (STEBABS / STEBREL# / STEBRAC#) on
C=C double bonds and encode OR/AND mixtures in a **grouped `/b` layer**. · **Branch:**
`feature/double-bond-ez` · **Sources:** [DECK] slides 23–30.

---

## 1. Problem

Just as a tetrahedral centre can be abs/or/and, a C=C double bond can be an absolute geometry,
a *pure-but-unknown* geometry (OR), or a *racemic* E/Z mixture (AND). Standard InChI encodes
only the absolute case (`/b`) — it has no representation for unknown/mixture double bonds
beyond collapsing them to "no `/b`".

## 2. Target behaviour

From [DECK] slides 23–30. The normative grammar is in §6. With `-EnhancedStereochemistry` the
prefix is `1B` in every case, including pure-absolute output.

- **Absolute** geometry (STEBABS, or a stereo bond in no collection): standard flat `/b`
  entries, e.g. `InChI=1B/C2BrCl2F/c3-1(4)2(5)6/b2-1+` (slide 25).
- **Unknown (no config):** a crossed or wavy bond gives no `/b` entry under default options
  (`u`/`?` only with `-SUU`), slide 26. It never joins an OR/AND group.
- **Pure-but-unknown (OR)**, digit `2`: `InChI=1B/C2BrCl2F/c3-1(4)2(5)6/b2(2-1-)` (slide 27).
- **Racemic (AND)**, digit `3`: `InChI=1B/C2BrCl2F/c3-1(4)2(5)6/b3(2-1-)` (slide 28).
- **Pair notation.** Each bond is written as in flat `/b`: higher canonical atom, `-`, lower
  atom, parity (`-` or `+`). The deck's `2-1-` is that pair with parity `-`.
- **Relative geometry (user decision 2026-10-08).** A group flips as a whole so that its lowest
  bond reads `-`; the other bonds keep their parity relative to it. Two bonds drawn (E,Z) and
  (Z,E) give one string, (E,E) and (Z,Z) another: `3(4-2-,5-3+)` vs `3(4-2-,5-3-)`. A
  single-bond group always reads `-`, as on the deck.
- **Several groups (user decision 2026-10-08).** Flat entries first, then all OR groups after
  one `2`, then all AND groups after one `3`, comma-joined; within a class one parenthesised
  block per group, ordered by its lowest bond: `/b12-5+,2(16-14-),3(15-10-,17-11-)(18-13-)`.
  Group numbers (`STEBREL2`) are never emitted, as in `/s`.
- **Input:** V3000 `MDLV30/STEBABS`, `MDLV30/STEBREL#`, `MDLV30/STEBRAC#` over `BONDS=(…)`.
- **Combined with tetrahedral/allene:** independent; double bonds group in `/b`, centres in
  `/t`+`/s` (slide 30): `…/b4-3-/t2-/m1/s1`, `…/b2(4-3-)/t2-/m1/s1`, `…/b4-3-/t2-/s3`.
- **Malformed collections** (more than one STEBABS, a group number used twice, an unknown bond,
  a bond in two collections) are diagnosed and dropped; `/b` falls back to standard. An OR/AND
  bond group spanning components is diagnosed and dropped with all collections, as in Spec 1.

**Invariants (all MUST):**
- *Backward compatibility* — classic `/b` output unchanged; without OR/AND bond groups the
  output is byte-identical (verified on `InChI_TestSet_ext.sdf` and all fixtures).
- *Grammar injectivity* — a grouped entry starts `digit (`, a flat one `digits -`; one
  character after the leading number decides.
- *Determinism* — identical input ⇒ identical output. Atom-order invariance holds within a
  component; across identical components see §5.
- *Either ≠ OR* — only bonds with defined parity join a group.

## 3. Current implementation (branch `feature/double-bond-ez`)

| Stage | Location |
|-------|----------|
| Classic `/b` detection, canonical storage, emission | `ichister.c` `set_stereo_bonds_parity`; `ichicans.c`; `ichiprt2.c` `MakeStereoString` |
| Parse `STEBABS`/`STEBREL#`/`STEBRAC#` `BONDS=(…)` | `mol_fmt3.c` `MolfileV3000ReadCollections`; bond index → atom pair in `BondsToAtomPairs` |
| Validate | `mol_fmt3.c` `BondCollectionsAreMalformed` |
| Data model | `MOL_FMT_v3000.steb*` (`mol_fmt.h`), `OAD_V3000.lists_steb*` (`inpdef.h`): atom-pair lists `[n, 2·bonds, a1, b1, …]` |
| Transfer, copy, free, renumber | `mol2atom.c` (`CopyIntLists`, `FreeIntLists`), `runichi3.c` (deep copy, `DropStereoCollections`), `permutation_util.c` |
| Spanning groups | `runichi3.c` `StereoGroupSpansComponents` (now also STEBREL/STEBRAC) |
| Grouped `/b` emitter | `ichiprt2.c` `MakeBlayerString` → `MakeBlayerComponent` → `MarkBondGroups`; called from `ichiprt1.c` `OutputINCHI_StereoLayer_EnhancedStereo` in the main layer when OR/AND bond groups exist |

Bonds are stored as atom pairs so every atom-list path (copy, renumber, component split) handles
them unchanged. Normalisation is emission-only: the `INChI_Stereo.b_parity` values are not
modified.

## 4. Requirements

Priority is MoSCoW. **Won't (this spec):** allene/atropisomer bonds (those are `/t`, Specs 2 & 4).

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| EZ-R1 | Classic absolute `/b` E/Z | Must | ✅ gated by Z1 |
| EZ-R2 | Either/unknown bonds → omitted (`u`/`?` with `-SUU`) | Must | ✅ gated by Z2 |
| EZ-R3 | Parse `STEBABS`/`STEBREL#`/`STEBRAC#` `BONDS=()` | Must | ✅ |
| EZ-R4 | Bond-collection data model (lists + transfer/copy/free/renumber/span) | Must | ✅ |
| EZ-R5 | Grouped `/b2(…)`/`/b3(…)` emitter (§6 grammar) | Must | ✅ main layer |
| EZ-R6 | Reductions: no OR/AND bond group ⇒ standard flat `/b` | Must | ✅ (no bare-digit form exists for `/b`) |
| EZ-R8 | Type-marker convention | Must | ✅ digits `2`/`3` (user decision) |
| EZ-R10 | Grammar injectivity | Must | ✅ §2 invariant |
| EZ-R7 | Combined `/b` + `/t`+`/s` independence | Should | ✅ gated by Z6 |
| EZ-R9 | Classic `/b` unit tests | Should | ✅ Z1, Z2 |
| EZ-R11 | Canonical order of components differing only in enhanced classes | Must | ❌ §5 |
| EZ-R12 | Grouped `/b` in fixed-H and isotopic layers | Could | ❌ flat there |

### Gates

All in `INCHI-1-TEST/tests/test_unit/test_doubleBondEZ.cpp`.

- **Z1** — absolute (no collection, STEBABS) → flat `/b2-1-`/`/b2-1+`; standard unchanged. ✅
- **Z2** — crossed double bond, wavy single bond, crossed bond in STEBREL → no `/b`. ✅
- **Z3/Z4** — single bond OR/AND, either drawing → `/b2(2-1-)`, `/b3(2-1-)`. ✅
- **Relative geometry** — two-bond AND group, four drawings → two strings. ✅
- **Z5** — multi-group layouts (flat + OR, flat + AND, OR + AND, two AND groups). The slide-29
  molecule itself is not materialised (no molfile). ✅ layout
- **Z6** — double bond + tetrahedral centre, the three deck strings exactly. ✅
- Non-stereo bond in a collection ignored; atom renumbering invariant; malformed collections
  dropped. ✅

## 5. Open issues / risks

- **Component order (EZ-R11, also Spec 1).** Components identical in every standard layer are
  ordered by input order, and components differing only in the raw parity of an OR/AND element
  are ordered by that meaningless parity, because the component sort runs before enhanced
  normalisation. Two BrClC=CClF components with STEBREL1 on one and STEBRAC1 on the other give
  `/b2(2-1-);3(2-1-)` or `/b3(2-1-);2(2-1-)` depending on which copy carries which collection.
  The same holds for `/s` (`/s2;3` vs `/s3;2`).
- **Haptic bonds.** A `BONDS=(k)` index is taken as the k-th bond line; with haptic bonds present
  the bond collections are treated as unknown and dropped.
- **InChI→structure.** `ichiread.c` rejects grouped `/b` (as it rejects grouped `/s` from Spec 1);
  parsing `1B` grouped layers is out of scope for both specs.
- **Fixed-H / isotopic `/b`.** Grouped only in the main layer; elsewhere flat (EZ-R12).

## 6. Normative grammar (enhanced `/b` layer)

ABNF ([RFC 5234]). The flat `/b` is unchanged; this extends it with groups.

```abnf
b-enh-layer = "/b" ( flat-list ["," b-groups] / b-groups )
flat-list   = b-pair *("," b-pair)             ; existing flat /b entries
b-groups    = b-class ["," b-class]            ; OR class before AND class
b-class     = b-type 1*b-block
b-type      = "2" / "3"                         ; 2 = OR/relative, 3 = AND/racemic
b-block     = "(" b-pair *("," b-pair) ")"     ; one group
b-pair      = hi "-" lo b-par                   ; e.g. "4-2-"
b-par       = "-" / "+" / "u" / "?"             ; "u"/"?" only in flat-list
hi          = 1*DIGIT                            ; higher canonical atom number
lo          = 1*DIGIT                            ; lower canonical atom number
```

Rules (each **MUST** hold):
- An absolute E/Z bond emits the standard flat entry.
- `b-pair`s ascend by (hi, lo) within the flat list and within a block; blocks within a class
  ascend by their first pair.
- The first pair of every block has `b-par` `-` (whole-group flip); the others keep their
  parity relative to it.
- Only `-`/`+` bonds join a block; either/unknown bonds stay in the flat list or are omitted.
- Components are separated by `;`, equal consecutive non-empty components fold to `n*`, as in
  other layers.

## 7. Assumptions & dependencies

- **A-1** Enhanced double-bond input arrives as V3000 `STEBABS`/`STEBREL#`/`STEBRAC#`
  `BONDS=()` collections — a channel that does **not** exist in V2000.
- **A-2** The `1B` beta prefix is reused (as for Spec 1); no new version machinery.
- **D-1** The classic `/b` pipeline (`INChI_Stereo.{nBondAtom1,nBondAtom2,b_parity}`) is the
  parity source; `nBondAtom1` is the higher canonical number by construction.
- **D-2** Bond collections reuse the atom-collection paths via the atom-pair layout.

[RFC 5234]: https://www.rfc-editor.org/rfc/rfc5234
