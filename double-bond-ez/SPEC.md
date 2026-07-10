# Spec 3 — Double-bond E/Z (enhanced OR/AND for C=C stereo bonds)

| | |
|---|---|
| **Doc version** | 0.2 |
| **Date** | 2026-07-10 |
| **Status** | draft |
| **Author** | C. Müller |
| **Reviewers** | TBD (InChI Trust / project 2019-017-2-800 TG) |
| **Requirement prefix** | `EZ-` |
| **Change history** | 0.1 (2026-07-09) — initial spec; verified against `dev`. 0.2 (2026-07-10) — consolidated: requirements/gates/deliverables/NFRs merged into one table (§4); ABNF grammar retained (§6). 0.3 (2026-07-10) — readability pass: added At-a-glance, split requirements from gates, tightened prose. |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

- ✅ **Works:** classic absolute `/b` (cis/trans E/Z) — detection, canonicalisation, emission,
  isotopic, and either/crossed/wavy → `u`/`?`. Mature (but has *no unit tests*).
- ❌ **Missing — the whole enhanced feature:** no input parsing, no data model, no output for
  OR/AND double bonds (`grep STEB` → 0 hits).
- ▶ **Next:** fix the type-marker convention (`2`/`3` vs `o`/`&`, **EZ-R8**) — an open decision
  that blocks the encoding — then build input parsing → data model → grouped emitter.

**Feature:** recognise MDL V3000 **bond** stereo collections (STEBABS / STEBREL# / STEBRAC#) on
C=C double bonds and encode OR/AND mixtures in a new **grouped `/b` layer**. · **Branch:** `dev`
· **Sources:** [DECK] slides 23–30.

---

## 1. Problem

Just as a tetrahedral centre can be abs/or/and, a C=C double bond can be an absolute geometry,
a *pure-but-unknown* geometry (OR), or a *racemic* E/Z mixture (AND). Standard InChI encodes
only the absolute case (`/b`) — it has no representation for unknown/mixture double bonds
beyond collapsing them to "no `/b`".

## 2. Target behaviour

From [DECK] slides 23–30. The normative encoding grammar is in §6; the behavioural rules:

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

**Invariants (all MUST):**
- *Backward compatibility* — classic `/b` output MUST be unchanged; enhancement is purely
  additive.
- *Grammar injectivity* — the grouped `/b` MUST parse unambiguously vs the flat `/b` and MUST
  round-trip (parse an emitted `/b2(…)`/`/b3(…)` and reproduce it).
- *Determinism* — identical input ⇒ identical output; group/tuple ordering fully determined by
  canonical numbers.
- *Either ≠ OR* — unknown/either (crossed/wavy) bonds MUST NOT be conflated with OR groups.

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

## 4. Requirements

Priority is MoSCoW. **Won't (this spec):** allene/atropisomer bonds (those are `/t`, Specs 2 & 4).

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| EZ-R1 | Classic absolute `/b` E/Z | Must | ✅ `ichiprt2.c:2075` (works; *no unit test*) |
| EZ-R2 | Either/unknown bonds → `u`/`?` or omitted | Must | ✅ `ichister.c:3090` (works; *no unit test*) |
| EZ-R3 | Parse `STEBABS`/`STEBREL#`/`STEBRAC#` `BONDS=()` | Must | ❌ not done |
| EZ-R4 | Bond-collection data model (`OAD_V3000` lists + transfer/split/free) | Must | ❌ mirror `mol2atom.c:1646-1712`, `runichi3.c:359-395` |
| EZ-R5 | Grouped `/b2(…)`/`/b3(…)` emitter (§6 grammar) | Must | ❌ not done |
| EZ-R6 | Reductions (absolute-only ⇒ flat `/b`; only-OR/only-AND) | Must | ❌ not done |
| EZ-R8 | Fix type-marker convention (`2`/`3` vs `o`/`&`) | Must | ❌ **open decision** *(§5)* |
| EZ-R10 | Confirm grouped-`/b` grammar vs [BNF] injectivity | Must | ❌ *(§5)* |
| EZ-R7 | Combined `/b` + `/t`+`/s` independence | Should | ❌ not done |
| EZ-R9 | Classic `/b` unit tests (none exist) | Should | ❌ none |

### Gates

No double-bond stereo tests exist at all (no `/b`, cis, trans, or `STEB*` coverage in
`test_unit/`). All gates are new; expected strings seeded from [DECK] slides 25–30 in
[datasets/DATASETS.md](datasets/DATASETS.md).

- **Z1** — classic absolute: `C2BrCl2F` E draw → `/b2-1+` (slide 25). ⚠️ works in pipeline, *no test*.
- **Z2** — unknown/either: crossed & wavy draws → **no `/b`** (slide 26). ⚠️ works, *no test*.
- **Z3** — enhanced OR: `STEBREL1 BONDS=(1 3)` → `/b2(2-1-)` (slide 27). ❌
- **Z4** — enhanced AND: `STEBRAC1 BONDS=(1 3)` → `/b3(2-1-)` (slide 28). ❌
- **Z5** — multi-group stress: `C18…` → `/b12-5+,2(16-14-),3(1(15-10-)(17-11-),2(18-13-))` (slide 29). ❌
- **Z6** — combined with `/t`: `/b2(4-3-)/t2-/m1/s1`, `/b4-3-/t2-/s3` (slide 30). ❌

## 5. Open issues / risks

- **Grammar injectivity.** [BNF] flags that overloading existing layers can create ambiguous
  parses. The `/b2(2-1-)` form is unambiguous *because* it always parenthesises and signs
  both atoms of each pair — the spec must keep that invariant (never emit a bare grouped `/b`
  that could be read as a flat `/b`).
- **Alternative markers.** [DECK] notes possible alternative type markers (`o` for OR, `&`
  for AND) instead of `2`/`3`; decide and fix one convention before implementation (EZ-R8).
- **"Either" vs OR.** A crossed/wavy bond (unknown, no `/b`) is semantically different from an
  OR mixture (`/b2(…)`); the input path must not conflate `STEREO_*_EITHER` bond flags with
  `STEBREL` collections.
- **Bond canonical numbering.** Emission needs canonical atom numbers for the bond ends
  (available in `INChI_Stereo.nBondAtom1/2`); confirm they are final canonical ranks at the
  emission point, matching how `MakeStereoString` already orders `atom2-atom1`.

## 6. Normative grammar (enhanced `/b` layer)

ABNF ([RFC 5234]). The **absolute** `/b` layer is unchanged; the grammar below defines the
**grouped OR/AND** extension. `b-pair` is a stereo bond as its two canonical atoms, **higher
number first, both signed `-`**.

```abnf
b-enh-layer = "/b" [abs-list] *b-group     ; abs-list = the existing flat /b entries
b-group     = b-type 1*b-block
b-type      = "2" / "3"                     ; 2 = OR/relative, 3 = AND/racemic
b-block     = "(" b-pair *("," b-pair) ")"  ; one relationship group
b-pair      = hi "-" lo "-"                 ; e.g. "2-1-"
hi          = 1*DIGIT                        ; higher canonical atom number
lo          = 1*DIGIT                        ; lower canonical atom number, hi > lo
```

Rules (each **MUST** hold):
- An absolute E/Z bond **MUST** emit the standard flat `/b` (no grouping, no `1B` divergence
  for the pure-absolute case).
- In a `b-pair` the higher canonical atom number **MUST** come first; both atoms **MUST** be
  signed `-`. `b-pair`s within a block, and blocks within a `b-type`, **MUST** be ordered
  ascending by atom-number tuple.
- The grammar **MUST** remain unambiguous vs the flat `/b`: a grouped `/b` **MUST** always
  parenthesise ([BNF] injectivity requirement §5).
- An "either"/crossed/wavy (unknown) bond is **not** OR: it **MUST** be omitted from `/b`
  (or rendered `u`/`?`), **never** encoded as a `b-group`.
- The type-marker convention (`2`/`3` vs the `o`/`&` alternative) **MUST** be fixed before
  implementation (§5, EZ-R8).

## 7. Assumptions & dependencies

- **A-1** Enhanced double-bond input arrives as V3000 `STEBABS`/`STEBREL#`/`STEBRAC#`
  `BONDS=()` collections — a channel that does **not** exist in V2000.
- **A-2** The `1B` beta prefix is reused (as for Spec 1); no new version machinery.
- **D-1** Depends on the existing classic `/b` pipeline (`INChI_Stereo.{nBondAtom1,nBondAtom2,
  b_parity}`, `MakeStereoString`) as the parity source of truth.
- **D-2** Input model depends on extending `OAD_V3000` with bond-collection lists (mirrors the
  atom-collection path); output depends on the Spec 1 grouped-emitter pattern.
- **D-3** Assumes bond-end canonical ranks are final at the emission point (see §5).

[RFC 5234]: https://www.rfc-editor.org/rfc/rfc5234
