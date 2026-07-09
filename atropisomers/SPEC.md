# Spec 4 — Atropisomers (axial chirality about a hindered single bond)

- **Feature:** recognise a stereogenic single-bond axis (biaryl / aryl-amide type), compute
  its axial configuration, and encode it in the InChI `/t`+`/m` layers (allene-analogous).
- **Branch:** `atropisomers` · **Prefix:** `InChI=1B/…` (beta)
- **Status:** **Partly implemented.** *Sub-project A* (deterministic detection + geometric
  axial parity + per-axis record, string-neutral) is **done and verified**. *Sub-project B*
  (native stereo-element registration, dissymmetry pruning, `/t`/`/m` emission) is **not
  started**.
- **Sources:** [ATROP] (`InChI encoding of atropisomers.docx`, authoritative for
  recognition + encoding), [DECK] slides 3/13, [BNF] (atropisomer-in-`/t` parsing ambiguity),
  [ATROP-BG] (Metrano 2018 review — background: scaffold taxonomy, descriptors, barriers).
- **Consolidates:** the former `.planning/specs/2026-07-06-atropisomer-deterministic-detection-design.md`
  and `.planning/plans/2026-07-06-atropisomer-deterministic-detection.md` — this document is
  now the single source of truth; those may be retired.

---

## 1. Problem

An atropisomer arises from hindered rotation about a single bond between two flat sp²(-like)
ends (most commonly biaryls), giving isolable *M*/*P* (Ra/Sa) conformers. InChI does not
recognise atropisomerism, so the two isomers share one identifier ([ATROP] §intro). The axis
is a chirality **axis** (like an allene), not a centre — so it is natural to encode it with
the tetrahedral/allene centres in `/t`+`/m`.

**Scaffold scope ([ATROP-BG]).** Real atropisomeric axes span many bond types: chiral C–C
axes (biaryls, tertiary benzamides, α-styrenes, imines), chiral **C–N** axes (anilides,
carbamates, imides, ureas, indoles, pyrroles, quinazolinones, lactams, barbiturates), and
chiral **C–O / C–S** axes (diaryl ethers/sulfides, sulfoxides, sulfones), plus
C(sp²)–C(sp³) and C(sp³)–C(sp³) cases. Configuration is named CIP `(aR)`/`(aS)` or helical
`M`/`P`; InChI encodes neither name directly — it uses canonical odd/even parity in `/t` with
`/m` distinguishing the enantiomeric pair (the `M`/`P` distinction). The stability threshold
(Ōki: t½ > 1000 s) is chemistry, not something InChI computes — recognition is purely
topological + geometric. **v1 is carbon-only** per [ATROP]; the C–N/C–O/C–S and heteroatom
classes above are the explicit deferral list (§5).

## 2. Target behaviour (from [ATROP])

Three procedures: (1) recognise the candidate axis, (2) assign configuration, (3) encode.

**Recognition — [ATROP] §1**
- **Bonding/valence/element:** single bond between two atoms `A`; common case both ends
  four-valent carbon (flat, no implicit H). Formally `A` may also be Si, N⁺, P⁺ — restrict to
  C for v1. A minor class has three-valent `T` ends (mostly N).
- **Dissymmetry:** the two substituents `X` at *each* end must be pairwise distinguishable;
  structural stability heuristic ≈ "≥2 non-H substituents at ≥3 of the X positions" (a cyclic
  special case needs only two X per end). This is the property that makes the axis
  stereogenic.
- **Stereobonds required:** the axis must be designated by wedge stereobonds (or 3D coords).
  Acceptable arrangements mirror allenes (two stereobonds, or **one** stereobond — which
  IUPAC accepts and which InChI must therefore support). Decorative/unrelated stereobonds are
  ignored.
- **Cyclic axes:** an axis inside a large ring may be atropisomeric; small rigid rings must be
  excluded.
- **3D:** biphenyl torsion ≈ 44° — recognition must work from 3D coordinates too.

**Assignment — [ATROP] §2:** "practically the same as already implemented for allenes"; reuse
the allene parity procedures.

**Encoding — [ATROP] §3:** cite the axis in the `/t` layer. Two options were weighed:
cite both axis atoms (`/t11-,12-/`) or **cite only the lower-numbered atom** (`/t11-/`). The
document recommends the **single lower-numbered atom** (shorter; `/t` count = number of
chirality units). Enantiomer via `/m`:
```
InChI=1S/C12H6Br2Cl2/c…/t11-/m0/s1      (one isomer)
InChI=1S/C12H6Br2Cl2/c…/t11-/m1/s1      (enantiomer)
```
**[BNF] caveat:** a bare `/t3+,7-` is ambiguous (two tetrahedral centres vs. one axis pair).
The single-atom encoding sidesteps this. If both atoms are ever cited, a disambiguator
(separate `/a` layer, or `;` separator) is required — decide before B.

## 3. Current implementation (branch `atropisomers`)

### Sub-project A — DONE + VERIFIED (this session: `test_atropisomers` 24 pass / 1 fail; the
one failure `test_dummy_14` is an unrelated return-code issue, not detection)

| Capability | Location | State |
|-----------|----------|-------|
| Deterministic candidate predicate (single bond; both ends valence ≥3; not in ring ≤ `ATROP_MIN_ROTATABLE_RING=6`; negative ring filter only) | `atropisomers.c` `find_atropisomeric_atoms_and_bonds`; commit `be4d41a` | ✅ replaces old magic-weight scoring |
| Geometric axial parity via allene primitives (`half_stereo_bond_parity` + `triple_prod_char`, `MIN_DOT_PROD` cut) | commit `dc441f2` | ✅ reused verbatim, no new vector math |
| Per-axis `ATROP_AXIS` record (atoms, parity, `z_dir`s) on `ORIG_ATOM_DATA`; legacy `bAtropisomeric`/`bAtropisomer` kept as derived flags | commit `dc441f2` | ✅ |
| String-neutrality: `set_Atropisomer_t_m_layers` emitter body emptied (no `/t`/`/m` emitted yet) | `strutil.c`; commit `f4289f7` | ✅ zero output-string change |
| Tests + string-neutrality gate; fixture-path fix (`FIXTURES_DIR`) | `test_atropisomers.cpp`; commits `cc66782`, `bca9ae6` | ✅ 24/25 pass |

Call site: detector runs on `inp_ATOM` (`out_at`) at `ichimake.c:3914`, before
`set_stereo_parity`. Design detail in this repo's git history and the (now-consolidated)
`.planning` spec.

### Sub-project B — NOT STARTED
- **Dissymmetry pruning** — A intentionally over-flags candidates; B must drop
  non-dissymmetric axes using canonical ranks (which only exist downstream). Falls out of the
  same canonical-equivalence pass that drops equivalent sp³ centres.
- **Native stereo-element registration** — register each surviving axis as a *pseudo-allene*
  stereo element in `set_stereo_parity` so canonicalisation perceives, canonicalises, prunes
  and inverts it (cumulene-aware ranking already exists in `ichicans.c`).
- **`/t` + `/m` emission** — real canonical odd/even parity on the lower-numbered axis atom;
  `/m` from `nCompInv2Abs`/`InvertStereo`; retire the placeholder `set_Atropisomer_t_m_layers`.
- **Single-stereobond support** — shared with allenes (spec 2 A3).
- **Enhanced OR/AND** — if in scope, group axes into `/s2`/`/s3` like tetrahedral centres.

## 4. Dataset gates

Dataset: `INCHI-1-TEST/tests/test_unit/fixtures/atropisomers_test_file_1_v2.sdf` (+
`_orig.sdf`); see [datasets/DATASETS.md](datasets/DATASETS.md).

| Gate | Content | Status |
|------|---------|--------|
| T1 Detection recall | mol 1–4, 12 (8-ring bridged biaryl), 13, 14, 43 (fully acyclic), 44 (aryl amide) + `test_file_1_v2.sdf` axes → every true axis is a candidate | ✅ **passes** (A) |
| T2 Negative guards | benzene / ≤6-ring single bond **not** flagged; no "must touch a ring" rule (mol 43 passes with zero rings) | ✅ **passes** (A) |
| T3 Determinism / order-independence | permuted input → identical candidate set + parities | ✅ **passes** (A) |
| T4 Parity unit | hand-built Ra/Sa pair → opposite parity; flat/no-wedge → `AB_PARITY_UNDF` (mol 44) | ✅ **passes** (A) |
| T5 String neutrality | A changes **no** emitted InChI string vs baseline | ✅ **passes** (A) |
| T6 Enantiomer invariants (B) | Ra/Sa pair: same skeleton + `/t`, opposite `/m`; two rotamers of one enantiomer → identical InChI; reparse reproduces | ❌ **not yet** (needs B) |
| T7 Encoding (B) | `C12H6Br2Cl2` biaryl → `…/t11-/m0/s1` and enantiomer `…/t11-/m1/s1` ([ATROP] §3) | ❌ **not yet** (needs B) |
| — | `test_dummy_14_atropisomer` end-to-end (return 0 vs 1) | ❌ pre-existing, unrelated to detection |

## 5. Deliverables checklist

**Done (Sub-project A)**
- [x] Deterministic candidate-axis predicate (valence + ring-size filter), no magic weights
- [x] Geometric axial parity reusing allene primitives (numbering-invariant, `MIN_DOT_PROD`)
- [x] Per-axis `ATROP_AXIS` record; legacy flags retained as derived
- [x] String-neutral neutralisation of the placeholder emitter
- [x] Detection/parity/determinism/negative-guard unit tests + string-neutrality gate
- [x] Fixture-path robustness (`FIXTURES_DIR` CMake define)

**Missing (Sub-project B)**
- [ ] Dissymmetry pruning via canonical equivalence (drop symmetric candidates, e.g. mol 44
      amide `C7–N8`; keep `C3–C7`)
- [ ] Register axis as native pseudo-allene stereo element in `set_stereo_parity`
- [ ] Emit `/t` on the **lower-numbered** axis atom ([ATROP] recommendation) + real `/m`
- [ ] Re-bake baseline expected-InChI strings once the axial layer lands
- [ ] Enantiomer-invariant gates T6–T7 on curated Ra/Sa pairs
- [ ] Single-stereobond axis support (shared with allenes, spec 2)
- [ ] Decide `/t` disambiguation vs [BNF] ambiguity (single-atom encoding resolves it)
- [ ] Cyclic-axis handling verification (ring ≥7 candidate; small ring excluded) end-to-end
- [ ] (If in scope) enhanced OR/AND grouping of axes; element/scaffold extension beyond
      carbon C–C — the C–N (anilides, ureas, quinazolinones…), C–O and C–S axis classes
      from [ATROP-BG], and Si/N⁺/P⁺ ends from [ATROP]
- [ ] Fix unrelated `test_dummy_14` return-code (separate cleanup)

## 6. Open issues / risks

- **Post-canonicalisation vs native.** The A-era `/t`/`/m` emission was a post-canonicalisation
  bolt-on and could not guarantee canonical reproducibility — the reason it was neutralised.
  B's native pseudo-allene registration is what makes emission reproducible; do **not** revive
  the bolt-on.
- **Dissymmetry needs ranks.** Recognition of a *stereogenic* axis (vs a mere candidate)
  depends on canonical ranks that only exist after canonicalisation — hence the A/B split.
- **`/t` grammar ambiguity** ([BNF]) — resolved by the single-lower-atom encoding; keep it.
- **Element scope** — v1 is carbon-only per [ATROP]; Si/N⁺/P⁺ and the three-valent-N class
  are explicitly deferred.
- **Reuse discipline** — parity must come from InChI's allene machinery, not new vector code
  (already honoured in A).
