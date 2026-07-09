# Spec 3 — Double-bond E/Z (enhanced OR/AND for C=C stereo bonds)

- **Feature:** recognise MDL V3000 **bond** stereo collections (STEBABS / STEBREL# /
  STEBRAC#) on C=C double bonds and encode OR/AND mixtures in a new **grouped `/b` layer**.
- **Branch:** `dev`
- **Status:** **Classic absolute `/b` (cis/trans E/Z) is complete and mature. Enhanced
  OR/AND for double bonds is not done at all** — no input parsing, no data model, no output.
- **Sources:** [DECK] slides 23–30.

---

## 1. Problem

Just as tetrahedral centres can be abs/or/and, a C=C double bond can be an absolute geometry,
a *pure-but-unknown* geometry (OR), or a *racemic* mixture of E and Z (AND). Standard InChI
encodes only the absolute case (`/b`); it has no representation for unknown/mixture double
bonds beyond collapsing them to "no `/b`".

## 2. Target behaviour

From [DECK] slides 23–30:

- **Absolute** geometry: unchanged standard `/b` layer, e.g.
  `InChI=1B/C2BrCl2F/c3-1(4)2(5)6/b2-1+` (slide 25). Proposal: "for abs geometries use the
  standard InChI representation."
- **Unknown (no config):** the `/b` layer simply does not appear (slide 26); a crossed
  ("double-either") or wavy ("single-either") bond marks unknown.
- **Pure-but-unknown (OR)** — new grouped `/b`, digit `2` (analogous to `/s2`):
  `InChI=1B/C2BrCl2F/c3-1(4)2(5)6/b2(2-1-)` (slide 27). Each bond is written as its
  **canonical atom-number pair, higher number first, both signed `-`**; format `/b2(2-1-)`.
  Multiple OR geometries ordered ascending by atom-number tuple; multiple OR# blocks
  bracketed with the group `#` before the first pair, blocks separated by `,`.
- **Racemic (AND)** — new grouped `/b`, digit `3` (analogous to `/s3`):
  `InChI=1B/C2BrCl2F/c3-1(4)2(5)6/b3(2-1-)` (slide 28).
- **Input:** V3000 `MDLV30/STEBABS`, `MDLV30/STEBREL#`, `MDLV30/STEBRAC#` over `BONDS=(…)`.
- **Combined with tetrahedral/allene:** double bonds handled **separately** in `/b`; sp³ in
  `/t`+`/s` (slide 30), e.g. `…/b4-3-/t2-/m1/s1`, `…/b2(4-3-)/t2-/m1/s1`, `…/b4-3-/t2-/s3`.

## 3. Current implementation (branch `dev`)

### Classic `/b` — COMPLETE
| Stage | Location |
|-------|----------|
| Detection + half/whole bond parity | `ichister.c:2121` `half_stereo_bond_parity`, `:3009` `set_stereo_bonds_parity` (driven `:4588`) |
| Canonical storage `AT_STEREO_DBLE` → `INChI_Stereo.{nBondAtom1,nBondAtom2,b_parity}` | `ichicans.c:533-675` |
| `/b` emission (`atom2-atom1<parity>`, `parity_char="!-+u?"`) | `ichiprt2.c:2075` `MakeStereoString` (`:2089`,`:2140`); layer tag `ichiprt1.c:308` |
| Either/unknown bonds (crossed `STEREO_DBLE_EITHER=3`, wavy `STEREO_SNGL_EITHER=4`) → `u`/`?` | read `mol_fmt1.c:875`; propagate `ichister.c:3090`; `u`-vs-`?` via `SLUUD` (`ichimake.c:3776-3784`) |
| Isotopic `/b`, cumulene interplay | present |

### Enhanced OR/AND `/b` — ABSENT (confirmed by grep)
- **`grep STEB` → 0 hits.** No `STEBABS`/`STEBREL`/`STEBRAC` keyword, no `BONDS=(…)`
  collection branch — the collection parser handles `ATOMS=(…)` only (`mol_fmt3.c:734`).
- No bond-group data structure — `OAD_V3000` (`inpdef.h:394-409`) carries only atom lists.
- No grouped-`/b` emitter — `MakeStereoString` produces a flat, ungrouped `/b`.
- No double-bond enhanced tests.

### Reuse map (mirror the atom-side enhanced feature for bonds)
- **Input template:** `mol_fmt3.c:676-790` (atom collection parse) → add a `BONDS=(…)` branch
  and `STEB*` keywords (`mol_fmt.h:114-116`); extend `OAD_V3000` with `lists_stebabs/…`.
- **Output template:** `MakeSlayerString`/`MakeEnhStereoString` (`ichiprt2.c:2327/2213`) and
  driver `OutputINCHI_StereoLayer_EnhancedStereo` (`ichiprt1.c:3496`) — build the analogous
  grouped `/b` from `INChI_Stereo.{nBondAtom1,nBondAtom2,b_parity}`.
- **Gating/prefix:** reuse `ip->bEnhancedStereo` + `is_beta` `1B` (`ichiprt1.c:1713,3132`).

## 4. Dataset gates

**No double-bond stereo tests exist at all** (no `/b`, cis, trans, or `STEB*` coverage in
`test_unit/`). All gates below are new; expected strings seeded from [DECK] slides 25–30 in
[datasets/DATASETS.md](datasets/DATASETS.md).

| Gate | Content | Status |
|------|---------|--------|
| Z1 Classic absolute `/b` | `C2BrCl2F` E draw → `/b2-1+` (slide 25) | ⚠️ works in pipeline; **no unit test** |
| Z2 Unknown/either | crossed & wavy draws → **no `/b`** (slide 26) | ⚠️ works; no unit test |
| Z3 Enhanced OR | `STEBREL1 BONDS=(1 3)` → `/b2(2-1-)` (slide 27) | ❌ not implemented |
| Z4 Enhanced AND | `STEBRAC1 BONDS=(1 3)` → `/b3(2-1-)` (slide 28) | ❌ not implemented |
| Z5 Multi-group | slide 29 `C18…` → `/b12-5+,2(16-14-),3(1(15-10-)(17-11-),2(18-13-))` | ❌ not implemented |
| Z6 Combined with `/t` | slide 30 → `/b2(4-3-)/t2-/m1/s1`, `/b4-3-/t2-/s3` | ❌ not implemented |

## 5. Deliverables checklist

**Done**
- [x] Classic absolute `/b` E/Z detection, canonicalisation, emission (incl. isotopic)
- [x] Either/crossed/wavy unknown bonds → `u`/`?` (or omitted `/b`)
- [x] `SLUUD` option controlling `u` vs `?`

**Missing / to do**
- [ ] **Input:** parse `MDLV30/STEBABS|STEBREL#|STEBRAC#` with `BONDS=(…)`; add `STEB*`
      keywords and a `BONDS=` branch to the V3000 collection parser
- [ ] **Model:** extend `OAD_V3000` with bond-collection lists (+ transfer, component-split,
      free — mirror `mol2atom.c:1646-1712`, `runichi3.c:359-395`)
- [ ] **Output:** grouped `/b` emitter — `/b2(2-1-)`, `/b3(2-1-)`; canonical atom-pair,
      higher number first, both `-`; ascending tuple order; bracketed OR#/AND# blocks `,`-sep
- [ ] **Reductions/edge cases:** absolute-only ⇒ standard `/b`; only-OR / only-AND groups
      (analogous to `/s2`/`/s3` reductions)
- [ ] **Combined handling:** double bonds in `/b`, sp³/allene in `/t`+`/s`, one InChI
- [ ] **Gates Z1–Z6:** build `double_bond_ez_test_file_1.sdf` + `test_doubleBondEZ.cpp`
      (including the slide-29 multi-group stress case)
- [ ] Confirm the grouped-`/b` grammar with the [BNF] injectivity concerns (see §6)
- [ ] Document the grouped `/b` grammar in the technical manual

## 6. Open issues / risks

- **Grammar injectivity.** [BNF] flags that overloading existing layers can create ambiguous
  parses. The `/b2(2-1-)` form is unambiguous *because* it always parenthesises and signs
  both atoms of each pair — the spec must keep that invariant (never emit a bare grouped `/b`
  that could be read as a flat `/b`).
- **Alternative markers.** [DECK] notes possible alternative type markers (`o` for OR, `&`
  for AND) instead of `2`/`3`; decide and fix one convention before implementation.
- **"Either" vs OR.** A crossed/wavy bond (unknown, no `/b`) is semantically different from an
  OR mixture (`/b2(…)`); the input path must not conflate `STEREO_*_EITHER` bond flags with
  `STEBREL` collections.
- **Bond canonical numbering.** Emission needs canonical atom numbers for the bond ends
  (available in `INChI_Stereo.nBondAtom1/2`); confirm they are final canonical ranks at the
  emission point, matching how `MakeStereoString` already orders `atom2-atom1`.
