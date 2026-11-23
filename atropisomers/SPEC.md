# Spec 4 — Atropisomers (axial chirality about a hindered single bond)

| | |
|---|---|
| **Doc version** | 1.1 |
| **Date** | 2026-11-23 |
| **Status** | draft |
| **Author** | C. Müller |
| **Reviewers** | TBD (InChI Trust / project 2019-017-2-800 TG) |
| **Requirement prefix** | `AT-` |
| **Readiness** | ready with open points — C–O/C–S and enhanced OR/AND on an axis deferred; OR/AND groups lost in InChI→structure, confirmed 2026-11-23 |
| **Kick-off documents** | [`docs/stereochemistry/`](../docs/stereochemistry/) |
| **Change history** | 0.1 (2026-07-09) — initial; consolidates the former `.planning` design + plan; verified against branch `atropisomers`. 0.2 (2026-07-10) — consolidated: merged normative MUSTs into §2, requirements/gates/NFRs into one table (§4). 0.3 (2026-07-10) — readability pass: added At-a-glance, split requirements from gates, tightened prose. 0.4 (2026-10-08) — Sub-project B implemented on `atropisomers` (commits `6207f72`, `78fe01e`, `687a480`): native stereo-bond registration in `set_stereo_parity`, dissymmetry pruning by the canonical-equivalence pass, `/t`+`/m` emission on the lower-numbered atom, single-wedge axis, [ATROP] hindrance heuristic; placeholder emitter retired; gates T6–T7 pass; `test_dummy_14` root-caused (N–N axis, out of scope). Line references replaced by function names. 0.5 (2026-10-09) — `-Atropisomers` removed; detection runs under `-EnhancedStereochemistry` (`46f62cf`). Cyclic hindrance relaxation removed (`2ea128d`): a ring neighbour always counts as substituted, so ≥2 passed every endocyclic bond in a ring ≥7 (bare bridged biaryls, BIOVIA Appendix B `19?`, zearalenone `17?`); all axes now need ≥3. 0.6 (2026-10-09) — ≥3 also dropped the dataset's 8-ring lignans (mols 22–26, labelled M/P); an axis whose smallest ring has exactly 8 atoms needs only the 2 bridge positions (`844caac`). 0.7 (2026-10-23) — measured for Spec 1 §5.U (chiral-flag business rule): an axis reads the flag like a tetrahedral centre. No code change. 0.8 (2026-11-23) — C–N and N–N axes (AT-R11, `57158c0`): planar neutral N end, aryl C end, acyclic bond only; dataset mols 27–31, 33, 45 and `test_dummy_4/5/14` gain the axis; scope checked against the literature (§5). 0.9 (2026-11-23) — an axis inside a 7/8-ring needs ring-fusion atoms at both ends (`a960025`): removes ring-flipping bonds with an exocyclic =O/=NR/aryl end (§5); colchicine kept. 1.0 (2026-11-23) — reparse round-trip (AT-R8): InChI→structure restores an axis `/t` entry as a single-bond stereo bond (`0c51cef`), and 0D axis input is defined (`a8c8fcc`). 1.1 (2026-11-23) — reviewer feedback (A. Yerin, 2026-11-19): a wedged acyclic axis needs 2 substituted ortho positions instead of 3 (`3fab588`; user decision: 3→2, not dissymmetry only); 3D input and ring axes unchanged. C–N/N–N support confirmed against his literature examples. Merged with the allene and enhanced-stereo round-trip work (`a24c95c`). |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

Split into two sub-projects:

- ✅ **Sub-project A — done:** deterministic candidate detection, geometric axial parity
  (allene primitives), per-axis record. Gates T1–T5 pass.
- ✅ **Sub-project B — done:** the axis is a *native* stereo element (a chain-length-0 stereo
  bond on a single bond), so canonicalisation prunes non-dissymmetric ends, inverts it for `/m`
  and emits `/t` on the lower-numbered axis atom. Single-wedge drawings and 3D input work.
  Gates T6–T7 pass; `test_atropisomers` 39/39.
- ✅ **C–N / N–N axes** (AT-R11, `57158c0`): anilides, N-aryl imides/lactams/sulfonamides,
  N-aryl indoles/pyrroles, bi-indoles.
- ✅ **Round-trip** (AT-R8, `a8c8fcc`, `0c51cef`): InChI → structure → InChI keeps the axis;
  the library returns it as a DoubleBond-type 0D record on the single bond.
- ❌ **Missing:** AT-R15 (C–O / C–S axes, enhanced OR/AND on an axis), the "overcrowded
  alkene" cases (dataset mols 46–49).
- ▶ **Next:** TG review.

**Feature:** recognise a stereogenic single-bond axis (biaryl / aryl-amide type), compute its
axial configuration, and encode it in the `/t`+`/m` layers (allene-analogous). · **Branch:**
`atropisomers` · **Prefix:** `InChI=1B/…` (beta) · **Scope:** C–C, C–N and N–N axes.
**Sources:** [ATROP] (authoritative for recognition + encoding), [DECK] slides 3/13, [BNF]
(atropisomer-in-`/t` parsing ambiguity), [ATROP-BG] (Metrano 2018 — background). ·
**Consolidates** the former `.planning` design + plan (now retired; this is the single source
of truth).

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
topological + geometric. [ATROP] restricts v1 to carbon; C–N and N–N axes were added in 0.8 (AT-R11).
C–O/C–S and Si/N⁺/P⁺ remain deferred (AT-R15).

## 2. Target behaviour & normative rules (from [ATROP])

Three procedures: (1) recognise the candidate axis, (2) assign configuration, (3) encode.
Atropisomers reuse the **tetrahedral/allene `/t`+`/m`** layers — no new layer. Output is `1B`
(beta), consistent with the other enhanced-stereo features. The encoding rules below are
normative (each **MUST**).

**Recognition — [ATROP] §1**
- **Bonding/valence/element:** single bond between two atoms `A`; common case both ends
  four-valent carbon (flat, no implicit H). Formally `A` may also be Si, N⁺, P⁺ (deferred). A
  three-valent N end qualifies when it is neutral, has no H and is planar, i.e. conjugated through
  a neighbour other than the axis partner (amide, imide, urea, sulfonamide, pyrrole, indole,
  aniline). The C end of a C–N axis must be a ring atom (aryl), which keeps the amide C(=O)–N
  bond out; C–N and N–N axes must be acyclic (`is_atrop_axis_end`, `is_atrop_axis_bond`).
- **Dissymmetry:** the two substituents `X` at *each* end must be pairwise distinguishable;
  structural stability heuristic ≈ "≥2 non-H substituents at ≥3 of the X positions" ([ATROP]'s
  cyclic special case, two X per end, is not applied: see §5). This is the property that makes the axis stereogenic.
  An axis that is a topological candidate but **not** dissymmetric **MUST NOT** be emitted
  (pruned by the canonical-equivalence pass, B). The heuristic is implemented as: ≥3 of the four
  ortho positions carry a non-H substituent, ≥2 when the smallest ring through the axis has exactly
  8 atoms (`is_atrop_axis_bond`).
- **Stereobonds required:** the axis must be designated by wedge stereobonds (or 3D coords).
  Acceptable arrangements mirror allenes (two stereobonds, or **one** stereobond — which
  IUPAC accepts and which InChI must therefore support). Decorative/unrelated stereobonds are
  ignored.
- **Cyclic axes:** an axis inside a large ring may be atropisomeric; small rigid rings must be
  excluded.
- **3D:** biphenyl torsion ≈ 44° — recognition must work from 3D coordinates too.

**Assignment — [ATROP] §2:** "practically the same as already implemented for allenes"; reuse
the allene parity procedures. A candidate with undefined geometry **MUST** render as `?` or be
omitted, never a guessed parity. B: it follows the standard undefined-stereo rule — omitted
(with the "Omitted undefined stereo" warning) unless another defined stereo element makes the
`/t` layer appear, then `?` (e.g. `/t15?,16?,19-`). Two wedges on the *same* side of the axis
(dataset mols 15/16) are a degenerate drawing and count as undefined.

**Encoding — [ATROP] §3:** cite the axis in the `/t` layer.
- A recognised, dissymmetric, geometry-defined axis **MUST** contribute exactly **one** `/t`
  entry, cited on the **lower-numbered** of the two axis atoms (`/t11-`), not both (`/t` count
  = number of chirality units).
- The enantiomer **MUST** be distinguished by `/m`:
  ```
  InChI=1S/C12H6Br2Cl2/c…/t11-/m0/s1      (one isomer)
  InChI=1S/C12H6Br2Cl2/c…/t11-/m1/s1      (enantiomer)
  ```
- **Single-atom citation is mandatory ([BNF]).** A bare `/t3+,7-` is ambiguous (two
  tetrahedral centres vs. one axis pair); the single lower-numbered form is unambiguous and
  **MUST** be used. If a future revision cites both ends, it **MUST** introduce a
  disambiguator (a distinct `/a` layer or `;` separator) — decide before B.

**Invariants (all MUST):**
- *Canonical reproducibility* — the emitted axial layer MUST be canonical and reproducible;
  this is why the post-canonicalisation bolt-on was neutralised and B uses a native stereo
  element (§5).
- *Determinism / order-independence* — candidate detection and parity MUST be independent of
  input atom order (met in A — gate T3).
- *Backward compatibility* — without `-EnhancedStereochemistry` output MUST be unchanged (gate T5;
  B verified: zero diffs on `InChI_TestSet_ext.sdf` and all fixtures).
- *Enantiomer/rotamer invariants* — Ra/Sa share skeleton + `/t`, differ in `/m`; rotamers of
  one enantiomer give one InChI (gates T6–T7, met in B). Reparse round-trip met in 1.0
  (`0c51cef`): InChI → structure → InChI reproduces the axis.
- *Reuse discipline* — parity MUST reuse InChI allene machinery, no new vector maths (met in A).

## 3. Current implementation (branch `atropisomers`)

### Sub-project A — DONE

| Capability | Location | State |
|-----------|----------|-------|
| Deterministic candidate predicate (single bond; both ends valence ≥3; not in ring ≤ `ATROP_MIN_ROTATABLE_RING=6`; negative ring filter only) | `atropisomers.c` `find_atropisomeric_atoms_and_bonds`; commit `be4d41a` | ✅ replaces old magic-weight scoring |
| Geometric axial parity via allene primitives (`half_stereo_bond_parity` + `triple_prod_char`, `MIN_DOT_PROD` cut) | commit `dc441f2` | ✅ reused verbatim, no new vector math |
| Per-axis `ATROP_AXIS` record (atoms, parity, `z_dir`s) on `ORIG_ATOM_DATA`; legacy `bAtropisomeric`/`bAtropisomer` kept as derived flags | commit `dc441f2` | ✅ |
| Tests + fixture-path fix (`FIXTURES_DIR`) | `test_atropisomers.cpp`; commits `cc66782`, `bca9ae6` | ✅ |

Call site: the detector runs on `inp_ATOM` (`out_at`) in `CreateOneStructureINChI`
(`ichimake.c`), before normalisation; it only *flags* atoms (`bAtropisomeric`).

### Sub-project B — DONE (commits `6207f72`, `78fe01e`, `687a480`)

| Capability | Location | State |
|-----------|----------|-------|
| Native registration: each flagged C–C single bond becomes a stereo bond of chain length 0 (both layers, isotopic too); the bond re-checks the predicate (single, both ends C with 3 heavy neighbours and no H, not in a ring ≤ 6, hindered ortho positions) | `ichister.c` `set_atrop_axes_parity`, `is_atrop_axis_bond`, `set_atrop_axis_parity`, `save_atrop_axis`, hooked at the end of `set_stereo_parity` | ✅ |
| Parity: `half_stereo_bond_parity` at both ends + `triple_prod_char`, `allene_one_wedge_z` for a lone wedge (`TG_FLAG_ALLENE_ONE_WEDGE`, set by `-EnhancedStereochemistry`), `MIN_DOT_PROD` cut → `AB_PARITY_UNDF` | `ichister.c`, `ichiparm.c` | ✅ |
| Axis vs double bond downstream: `IS_ATROP_AXIS()` = chain length 0 on a `BOND_SINGLE` | `extr_ct.h` | ✅ |
| Dissymmetry pruning: the existing canonical-equivalence pass (`UnmarkNonStereo`) removes an axis whose end has two equivalent neighbours — nothing atropisomer-specific | `ichicans.c` (unchanged) | ✅ |
| `/m`: `InvertStereo` flips an axis exactly like an allene (parity of the lower atom + both bond parities) | `ichicans.c` | ✅ |
| `/t`: `Copy2StereoBondOrAllene` turns the axis into a stereo centre on the lower-numbered axis atom (`LinearCTStereoDble.at_num2`) | `ichimak2.c` | ✅ |
| Placeholder `set_Atropisomer_t_m_layers` and its `ichiprt1.c` call removed | `strutil.c/.h`, `ichiprt1.c` | ✅ |
| Hindrance heuristic (`ATROP_MIN_HINDERED` = 3, acyclic and cyclic) | `ichister.c` `count_hindered_ortho` | ✅ |
| C–N / N–N ends: planar neutral N, aryl C, acyclic bond; the 8-ring exemption stays C–C (`57158c0`) | `ichister.c` `is_atrop_axis_end`, `is_atrop_axis_bond` | ✅ |
| Axis inside a 7/8-ring: both ends ring-fusion atoms (`a960025`) | `ichister.c` `is_fused_atom`, `is_atrop_axis_bond` | ✅ |
| 0D axis input: end-plane normals set perpendicular via `FixSb0DParities` (`a8c8fcc`) | `ichister.c` `set_atrop_axis_parity` | ✅ |
| Reversal: axis `/t` entry → single-bond 0D stereo bond (`0c51cef`) | `ichirvr2.c` `set_axis_0D_parity`, `find_axis_partner`, `is_rev_axis_end`, `SetStereoBondTypeFor0DParity` | ✅ |

Why chain length 0 and not a pseudo-allene chain: every cumulene walker (`ichimap1.c`,
`Copy2StereoBondOrAllene`, `MarkAmbiguousStereo`) expects `chain_length` middle atoms of
valence 2; an axis has none. A single-bond stereo bond needs no walking, and the only places
that must know it is chiral (inversion, centre emission) test `IS_ATROP_AXIS()`.

## 4. Requirements

Priority is MoSCoW; the **A/B** column marks which sub-project owns each. **Won't (this spec):**
spiranes and other axial-chirality classes; name-level `aR`/`aS`/`M`/`P` descriptors (InChI
uses parity, not CIP names).

| ID | Requirement | Priority | A/B | Status |
|----|-------------|----------|-----|--------|
| AT-R1 | Deterministic candidate-axis predicate | Must | A | ✅ `atropisomers.c` (be4d41a) |
| AT-R2 | Geometric axial parity (allene primitives) | Must | A | ✅ (dc441f2) |
| AT-R3 | Per-axis `ATROP_AXIS` record | Must | A | ✅ (dc441f2) |
| AT-R4 | String neutrality (A emits nothing vs baseline) | Must | A | ✅ (f4289f7) |
| AT-R12 | `/t` disambiguation decision ([BNF]) | Must | A | ✅ resolved by single-atom form |
| AT-R5 | Dissymmetry pruning via canonical ranks | Must | B | ✅ `UnmarkNonStereo` (6207f72) |
| AT-R6 | Register axis as native stereo element | Must | B | ✅ `set_atrop_axes_parity` (6207f72) |
| AT-R7 | Emit `/t` on lower-numbered atom + real `/m` | Must | B | ✅ (6207f72) |
| AT-R8 | Enantiomer/rotamer/round-trip invariants | Must | B | ✅ enantiomer + rotamer (687a480); reparse round-trip (a8c8fcc, 0c51cef) |
| AT-R13 | Re-bake baseline expected-InChI strings once layer lands | Must | B | ✅ (687a480) |
| AT-R9 | Single-stereobond axis (shared with allenes AL-R3) | Should | B | ✅ `allene_one_wedge_z` under `-EnhancedStereochemistry` (6207f72) |
| AT-R10 | Cyclic-axis handling (ring ≥7 vs ≤6) end-to-end | Should | B | ✅ ≤6 rings locked; 7/8-ring axes need fused ends (a960025); 8-ring lignans mols 22–26 → `/t19-` (844caac); bare 7-ring `test_dummy_12` → no axis (2ea128d) |
| AT-R11 | C–N and N–N axes | Could | B | ✅ (57158c0) |
| AT-R15 | Enhanced OR/AND on an axis; C–O/C–S, Si/N⁺/P⁺ and acyclic enamide axes | Could | — | ❌ deferred |
| AT-R14 | [ATROP] hindrance heuristic (≥3 substituted ortho positions; 2 in an 8-ring) | Should | B | ✅ (78fe01e, 2ea128d, 844caac) |
| AT-R16 | A wedged acyclic axis (2D, up/down wedge at an axis end) needs 2 substituted ortho positions, not 3 | Should | B | ✅ (3fab588) |

### Gates

Dataset: `atropisomers_test_file_1_v2.sdf` (+ `_orig.sdf`); see
[datasets/DATASETS.md](datasets/DATASETS.md). Test run: **39/39 pass**. `test_dummy_14`
is an N–N axis (2,2'-diethyl-1,1'-biindole) → `/t21-/m0/s1` since 0.8.

- **T1** detection recall — every true axis (mol 1–4, 13, 14, 43 acyclic, 44 amide) is a candidate; the bare 7-ring bridged biaryl `test_dummy_12` is no longer an axis (2ea128d). ✅ (A)
- **T2** negative guards — benzene / ≤6-ring bonds not flagged; no "must touch a ring" rule (mol 43 has zero rings). ✅ (A)
- **T3** determinism — permuted input → identical candidate set + parities. ✅ (A)
- **T4** parity unit — hand-built Ra/Sa → opposite parity; flat/no-wedge → `AB_PARITY_UNDF` (mol 44). ✅ (A)
- **T5** string neutrality — A changes no emitted InChI vs baseline. ✅ (A)
- **T6** enantiomer invariants — Ra/Sa share skeleton + `/t`, opposite `/m`; 3D rotamers at 44°, 90°, 120° → one InChI, −44° → the enantiomer; every dataset `M` label → `/m0`, every `P` → `/m1`, 2D and 3D alike. ✅ (B) Reparse round-trip ✅ (`test_atropisomers_roundtrip`: biaryl M/P, C–N indole, N–N biindole M/P, axis + centre; 0D axis input).
- **T7** encoding — `C12H6Br2Cl2` biaryl → `…/t11-/m0/s1` and enantiomer `…/t11-/m1/s1` ([ATROP] §3). ✅ (B)
- **T8** dissymmetry / hindrance — 2,6-dichloro end → no layer; 3,3'-bipyridine → no layer; symmetric amide `C7–N8` never an axis (C–N). ✅ (B)
- **T10** C–N / N–N — dataset mols 27/28 → `/t19-/m0`, 29 → `/t21-/m0`, 30 → `/t21-/m1`, 33 → `/t13-/m1` (labels M → `/m0`, P → `/m1` as for C–C); sp³ pyrroline N (mol 32) → no axis; `test_dummy_4_cn_axis_anilide` → `/t18-/m0`; flat `test_dummy_5_cn_axis_flat_omitted` → omitted with warning. ✅ (`57158c0`)
- **T11** ring axes — a 7/8-ring axis needs fused ends: thieno-benzothiepinone C–C(=O) → no axis (`ring_axis_with_exocyclic_end_not_emitted`); colchicine → `/t14-,16+/m1/s1` (`ring_axis_with_fused_ends_emitted`). ✅ (`a960025`)
- **T9** single wedge — one-wedge draw equals the two-wedge draw; flat draw → omitted with warning. ✅ (B)

- **T12** wedged axes — the 1,3-diaxis phenylene of [REVIEW-AY] (biaryl C–C + N-aryl pyrimidinone C–N, two ortho groups per axis) wedged → `/t15-,18+/m1/s1`, mirror `/m0` (`wedged_axis_needs_no_hindrance_count`); a 3D 2,2'-dimethylbiphenyl stays without `/t` (`unhindered_3d_axis_not_emitted`); 3,3'-bipyridine wedged stays without (T8). ✅ (`3fab588`)

## 5. Open issues / risks

- **Post-canonicalisation vs native.** The A-era bolt-on is gone; the axis is a native stereo
  bond. Do **not** revive the bolt-on.
- **Dissymmetry needs ranks.** Handled by the existing equivalence pass; nothing to tune.
- **Resolved — cyclic relaxation of the hindrance rule.** [ATROP]'s ≥2 for a ring axis was
  vacuous: the ring-continuation neighbours always count as substituted, so every endocyclic
  bond in a ring ≥7 between two 3-connected carbons became an axis (bare bridged biaryls,
  BIOVIA Appendix B `19?`, zearalenone `17?`). These ring-invert below the atropisomer barrier.
  Now ≥3, except an axis whose smallest ring has exactly 8 atoms: 2 bridge positions suffice
  there (dibenzocyclooctadiene lignans, mols 22–26, are configurationally stable; dropping them
  in 2ea128d was a regression, fixed in 844caac). Substituted bridged axes (vancomycin `30?`)
  still qualify. Deviates from [ATROP] wording; for TG review.
- **Undefined axes are visible** when another stereo element is defined (`?` entry) — standard
  InChI behaviour, but it adds entries to many drawings once the option is on.
- **Resolved in 1.0 — reparse round-trip (AT-R8).** The reversal read an axis `/t` entry as a
  tetrahedral centre on a three-connected sp² atom (self-check: "Stereo centers/allenes: Missing
  known"). `RestoreAtomConnectionsSetStereo` (`ichirvr2.c`, `set_axis_0D_parity`) now restores a
  `/t` atom that is a neutral C or planar N with three heavy neighbours, no H and exactly one
  higher-numbered partner across a candidate axis bond like a `/b` bond of length 1; both ends
  get `bAtropisomeric`, so `SetStereoBondTypeFor0DParity` keeps the bond single. 0D axis input
  was always undefined: `set_atrop_axis_parity` now calls `FixSb0DParities` like an allene.
  Library output: a DoubleBond-type `inchi_Stereo0D` on the single bond, no API change.
  Measured on 21,956 InChIs (fixtures, examples, `InChI_TestSet_ext`, mcule 20k): 18 more
  round-trip unchanged, none newly fail.
- **OR/AND groups do not survive InChI→structure.** `/s2`, `/s3` come back as `/s1` because 0D
  records carry no groups; this affects tetrahedral centres too (Spec 1).
- **Two candidate partners** (e.g. a C between two qualifying ends) keep the tetrahedral reading
  in the reversal; not seen in the 21,956 InChIs.
- **`-InChI2InChI -EnhancedStereochemistry` crashes** on any InChI with stereo, on `dev` too:
  `OutputINCHI_StereoLayer_EnhancedStereo` (`ichiprt1.c`) dereferences `orig_inp_data`, which is
  NULL on that path. Not an atropisomer bug; Spec 1.
- **Overcrowded alkenes** (dataset mols 46–49, "Z,M"): the chirality axis *is* the C=C bond
  inside fused rings — no single-bond candidate exists. Out of scope for this spec.
- **`/t` grammar ambiguity** ([BNF]) — resolved by the single-lower-atom encoding; keep it.
- **Element scope** — C, and since 0.8 planar neutral N (AT-R11). Si/N⁺/P⁺, C–O/C–S and
  acyclic enamide C–N axes are deferred (AT-R15).
- **C–N / N–N scope check (0.8, literature).** Isolable atropisomers are reported for every
  admitted N class: N–N bi-indoles and indole–indoline axes (pyramidalised indoline N, strong
  configurational stability) [Centonze 2023, anie.202303966]; N-aminoindoles (barriers
  30–40 kcal/mol); o-tBu anilides (Curran 1994); N-(2,6-disubstituted phenyl)sulfonamides
  (PMC9698006); N-aryl-N-methyl-2-tBu-6-methylanilines. Dataset mol 31 (labelled "no
  atropisomers?") therefore gets its N–N axis: `/t18-,21-/m1/s1` (axis plus the C2 centre).
  `test_dummy_5` is Merck's ATM inhibitor whose atropisomers are claimed in WO2020193660A1.
- **Hindrance counts substituents, not size (C–N).** N-ethyl-N-phenyl-2,6-dihalo-anilines pass
  ≥3 but are probably below the Ōki threshold; diarylamines need four ortho groups (Costil
  2020). N-methyl anilides with a single ortho tBu score 2 and are missed. Same ceiling as C–C.
- **Measured (0.8).** mcule 20k: 76 C–N/N–N candidates before pruning, 0 InChI strings
  changed (flat 2D), 29 more "Omitted undefined stereo" warnings. Without the acyclic rule 11
  bonds inside benzodiazepinone-type 7-rings passed.
- **Resolved in 0.9 — C–C bonds inside 7/8-rings.** Of 13 mcule candidates, 5 are bridged
  biaryls (BINOL chlorophosphite #2054, binaphthyl azepine #6660, thiepine-fused furans
  #19993 ×2, dibenzodioxocine #14245, the last uncertain); 8 are bonds of the flexible ring with
  an exocyclic =O/=NR/aryl end (#4262, #11769 ×2, #11957, #14978, #18212 ×2, #19701 tropone),
  which ring-flip. Rule (`is_fused_atom`): both ends must be ring-fusion atoms. Effect: mcule
  −8 candidates, #14978 loses a false `?`; `InChI_TestSet_ext` #1865 (C18H8) loses a spurious
  `/b18-17-` and now equals standard InChI; fixtures and spec examples unchanged. Allenes, E/Z and enhanced-stereo fixtures and examples: no diff.
- **Reuse discipline** — parity must come from InChI's allene machinery, not new vector code
  (already honoured in A).
- **Enhanced-stereo collections name the lower axis atom only.** `lookup_stereo_centre` finds
  an axis via its lower-numbered atom; a collection that cites the higher-numbered end is
  dropped silently.
- **Hindrance heuristic prunes some real atropisomers.** 1,1'-binaphthyl counts only 2
  hindered ortho positions (acyclic threshold 3) and gets no axis, while BINOL passes.
  v1 limitation; follows [ATROP] literally.
- **Ring detection (resolved).** The A-phase simple-cycle enumeration was exponential on
  dense inputs (metal clusters, `InChI_TestSet_ext.sdf` 126–145 stalled for minutes). The
  candidate filter now uses InChI's bounded BFS `is_bond_in_Nmax_memb_ring`; the
  `ring_detection` module is gone.
- **Axis in stereo-bond slot [1] (resolved).** An axis end that also owns a C=C or a second
  axis stores the axis in slot [1]; `Copy2StereoBondOrAllene`, `InvertStereo` and
  `MarkAmbiguousStereo` read slot [0] only, giving `STEREOCOUNT_ERR` or an axis printed in
  `/b`. They now locate the slot by partner atom (`find_stereo_bond_slot`).

- **Chiral flag (Spec 1 §5.U, undecided).** The C12H6Br2Cl2 biaryl drawn (M) with chiral flag 0
  and no collections: `/t11-/m0/s1` with `-EnhancedStereochemistry` (flag ignored), `/t11-/s2`
  with `-SUCF` added, exactly like a tetrahedral centre. Whatever rule Spec 1 adopts applies here.

- **Reviewer feedback [REVIEW-AY] (A. Yerin, 2026-11-19).** "Stability is not so important.
  Chemists should have a possibility to specify each stereoisomer." C–N and N–N axes must be
  supported (done in 0.8): his marinopyrrole A (N–C), 1,1'-biindole 4a/4af and N-aminoindole 7d
  (N–N) give enantiomer pairs (examples 138–140). His 1,3-diaxis phenylene (four separable
  isomers, two ortho groups per axis) got no axis under the ≥3 rule; a wedge now lowers the count
  to 2 for acyclic axes (AT-R16, examples 136/137). Not taken further: "dissymmetry only" would
  give axes to wedged unsubstituted biaryls (3,3'-bipyridine, T8) and bare 7-ring-bridged
  biaryls (AT-R10); 3D keeps ≥3 because a conformer is not a choice. Side effect: a wedge drawn
  on another acyclic sp²–sp² bond with two ortho groups (e.g. aryl–CO₂Me) is an axis too.

## 6. Assumptions & dependencies

- **A-1** Axes are **C–C, C–N or N–N single bonds**, both ends sp²/planar without H;
  C–O/C–S and Si/N⁺/P⁺ ends are deferred (§4, AT-R15).
- **A-2** The axis is designated by wedge stereobonds or 3D coordinates; decorative
  stereobonds MUST be ignored; a single stereobond SHOULD suffice (shared with Spec 2 AL-R3).
- **D-1** **Dissymmetry pruning depends on canonical ranks**, which exist only after
  canonicalisation — this is the architectural reason for the A/B split (detection over-flags;
  B prunes).
- **D-2** Depends on the allene parity primitives (reuse verbatim — see Spec 2 D-1) and on
  registering the axis as a **pseudo-allene** native stereo element so canonicalisation /
  `InvertStereo` handle it (B).
- **D-3** Reuses `/t`+`/m` emission and the `1B` prefix.
