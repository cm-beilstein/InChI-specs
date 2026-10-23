# Spec 6 — Versioning of InChI and InChIKey

| | |
|---|---|
| **Doc version** | 0.1 |
| **Date** | 2026-10-23 |
| **Status** | draft |
| **Author** | Christoph Mueller |
| **Reviewers** | TBD |
| **Requirement prefix** | `VR-` |
| **Readiness** | ready with open points — combining subversion letters, metalloids, letter lookup table undecided (§5), confirmed 2026-10-23 |
| **Kick-off documents** | [`docs/inchi-versioning/`](../docs/inchi-versioning/) |
| **Change history** | 0.1 (2026-10-23) — initial spec from [#285](https://github.com/IUPAC-InChI/InChI/issues/285) and PR [#280](https://github.com/IUPAC-InChI/InChI/pull/280); measured against `dev` `b40eeee` (old: `68afb20`). |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

- ✅ **Works:** prefixes `1S`/`1B`/`1N` + subversion `B`; key flags `SA`/`SB`/`BA`/`BB`/`NA`/`NB`; `InChI=1/` read as `1N/`; Molecular Inorganics (MI) on by default, emitted as `1BB`; `-LegacyMetalHandling` (VR-R1–R8, merged in #280).
- ❌ **Missing:** VR-R9 (letter combination), VR-R10 (metalloid set), VR-R11 (letter lookup table) — undecided; VR-R12 (old readers) contradicts measured behaviour (§5.D).
- ▶ **Next:** working-group decisions on §5.A–C; land the four gates of `test_github_285.cpp` (G6).

**Feature:** the InChI version prefix and the InChIKey version flags show the calculation
class (standard, beta, non-standard) and which feature set made the string · **Branch:** `dev`
· **Sources:** [#285](https://github.com/IUPAC-InChI/InChI/issues/285) (body, PDF
"InChITrust-Chicago InChI Meeting - Versioning", thread to 2026-10-20),
[#280](https://github.com/IUPAC-InChI/InChI/pull/280), `INCHI-1-DOC/CHANGELOG.md`.

---

## 1. Problem

Molecular Inorganics changes the InChI of about 5 % of structures (metal compounds); organic
InChIs stay the same. Users must see which algorithm made a string. In the InChIKey only the
two version letters (positions 24–25) can show it.

Before #280 (`68afb20`, default options), cisplatin drawn with dative N→Pt bonds:

| | old (`68afb20`) | new (`b40eeee`) |
|---|---|---|
| InChI | `InChI=1S/2ClH.2H3N.Pt/h2*1H;2*1H3;/q;;;;+2/p-2` | `InChI=1BB/Cl2H6N2Pt/c1-5(2,3)4/h3-4H3` |
| InChIKey | `LXZZYRPGZAFOLE-UHFFFAOYSA-L` | `NKTISDOLGLLLMZ-UHFFFAOYBB-N` |

Also before #280: non-standard InChI had no class letter (`InChI=1/`), and the key's last
version letter was always `A`.

## 2. Target behaviour

1. **Prefix grammar.** `InChI=1<class>[<subversion>]/`. Class: `S` standard, `B` beta,
   `N` non-standard. Subversion: absent = base InChI v1; `B` = Molecular Inorganics; `C`, `D`,
   … reserved for later features (issue body).
2. **Subversion trigger.** `B` is set when MI processing is on and the input contains at least
   one atom flagged in the MI element table (`molecular_inorganics_data.c`, `MolInOrg*` type ≠ 0),
   even when the layers are byte-identical to 1.07 (NaCl). Decided by gblanke02, 2026-10-13:
   "1SB has to be used whenever a structure with a metal atom goes through the new algorithm".
3. **Metalloids.** Current table: Sb is a metal; Ge, As, Te are not. Kept for this beta
   (gblanke02, 2026-10-13); final set is for the working group (§5.B).
4. **Beta in this release.** MI is beta, so MI structures are `InChI=1BB/` with key `…BB-…`.
   `1SB` is accepted on input for the future standard MI release (gblanke02, 2026-10-13; #280).
5. **Precedence.** A non-standard option makes the class `N` even when a beta feature is on
   (`-FixedH` + MI → `1NB`; #280).
6. **Explicit non-standard.** Output writes `InChI=1N/` instead of `InChI=1/`. Input
   `InChI=1/` is still accepted and rewritten as `1N/` (issue body; #280).
7. **InChIKey flags.** Position 24 mirrors the class (`S`/`B`/`N`), position 25 the subversion
   (`A` = base, `B` = MI). The hash covers only the layers after the prefix.
8. **Legacy mode.** `-LegacyMetalHandling` restores 1.07 metal/salt handling, turns MI off,
   and is non-standard (`1N`, no subversion). It is rejected for MI input in InChI2InChI.
9. **Compatibility.** Release notes MUST say that the new prefixes are not readable by 1.07.x
   or older (gblanke02, 2026-10-13).
10. **Lookup table.** Release notes MUST list which subversion letter stands for which feature
    set (gblanke02, 2026-10-13).

## 3. Current implementation (branch `dev`, `b40eeee`)

| Stage | Location (function) | State |
|-------|---------------------|-------|
| MI on by default, `LegacyMetalHandling` | `ichiparm.c` `set_common_options_by_parg`, `ReadCommandLineParms` | ✅ |
| subversion trigger (any MI-table atom) | `ichiprt1.c` `OutputINChI1` → `strutil.c` `getElTypeforMolecularInorganics` | ✅ |
| prefix output, `N` before `B` | `ichiprt1.c` `OutputINCHI_VersionAndKind` | ✅ |
| prefix input (InChI2InChI / InChI2Struct), `1/` → `1N/` | `ichiread.c` `ReadInChILine`, `ConvertInChI2InChI`, `DetectInputINChIFileType` (`ichiparm.c`) | ✅ |
| API validation | `inchi_dll_a.c` `CheckINCHI`; `inchi_dll.c` `GetINCHI1` | ✅ |
| key flags | `ikey_dll.c` `GetINCHIKeyFromINCHI` | ✅ |
| key validation (`A` or `B` at pos. 25) | `ikey_dll.c` `CheckINCHIKey` | ✅ |
| several subversions at once | — | ❌ undecided (§5.A) |

## 4. Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| VR-R1 | Standard InChI of a structure without MI-table atoms MUST be unchanged (`1S`, key `SA`). | Must | 🟡 done; gate G6 not yet in the repo |
| VR-R2 | A structure with an MI-table atom MUST get subversion `B` in InChI and key, also when its layers are unchanged. | Must | ✅ done + gated (G1, G6) |
| VR-R3 | MI output MUST be class `B` (beta) in this release. | Must | ✅ done + gated (G1) |
| VR-R4 | A non-standard option MUST give class `N`, also with a beta feature. | Must | ✅ done + gated (G5, G6) |
| VR-R5 | Output MUST write `1N/` for non-standard; input `1/` MUST be read as `1N/`. | Must | ✅ done + gated (G3, G7) |
| VR-R6 | Readers (`CheckINCHI`, InChI2InChI) MUST accept `1S`, `1SB`, `1B`, `1BB`, `1N`, `1NB` and keep class and subversion. | Must | ✅ done + gated (G2, G3) |
| VR-R7 | Key flags MUST mirror class and subversion; `CheckINCHIKey` MUST accept `A` and `B` at position 25. | Must | ✅ done + gated (G4) |
| VR-R8 | `-LegacyMetalHandling` MUST give the 1.07 layers with prefix `1N`, and MUST be rejected for MI input in InChI2InChI. | Must | ✅ done + gated (G5, G7) |
| VR-R9 | How subversion letters combine when a structure uses two features (`B` + `C`). | Must | ❌ open (§5.A) |
| VR-R10 | The set of elements that trigger `B` (metalloids). | Must | ❌ open (§5.B) |
| VR-R11 | Release notes MUST carry a lookup table of subversion letters. | Should | ❌ open (§5.C) |
| VR-R12 | Release notes MUST state that the new prefixes are not readable by 1.07.x. | Should | partial: in CHANGELOG; contradicted by the old CLI (§5.D) |

### Gates

Molecules and their sources: [datasets/DATASETS.md](datasets/DATASETS.md).

- **G1** — `test_inchi_dll_b.cpp` :: `test_MakeINCHIFromMolfileText`, `test_STDINCHIGEN_MolecularInorganics`: ferrocene and CH3Li give `InChI=1BB/…`. ✅ passes.
- **G2** — `test_inchi_dll_b.cpp` :: `test_CheckINCHI_version_prefixes`: all six prefixes and historical `1/` validate with the right class. ✅ passes.
- **G3** — `test_inchi_dll_b.cpp` :: `test_GetINCHIfromINCHI_version_prefixes`, `test_GetINCHIfromINCHI_historical_nonstandard_prefix`: prefixes survive InChI2InChI; `1/` → `1N/`. ✅ passes.
- **G4** — `test_inchi_dll_b.cpp` :: `test_CheckINCHIKey_version_flags`, `test_GetINCHIKeyFromINCHI_version_flags`: the six flag pairs. ✅ passes.
- **G5** — `test_inchi_dll_b.cpp` :: `test_MakeINCHIFromMolfileText_LegacyMetalHandling`, `test_GetINCHIfromINCHI_rejects_LegacyMetalHandling_for_MI_input`: `InChI=1N/CH3.Li/h1H3;`; MI input rejected. ✅ passes.
- **G6** — `test_github_285.cpp` (new, not yet in the repo): ethanol stays `1S`/`SA`; NaCl `1BB`/`BB` with 1.07 layers; SbCl3 `1BB`, AsCl3/GeCl4/TeCl4 `1S`; `-FixedH` gives `1N`/`NA` and `1NB`/`NB`. 🟡 passes at `b40eeee`, 3 of 4 fail at `68afb20`; counts once merged.
- **G7** — `test_executable/test_roundtrip.py` :: `test_inchi2inchi_legacy_metal_handling_rejects_mi_input_and_continues`, `test_inchi2inchi_unknown_class_letter_gets_no_mi_marker`. ✅ passes.
- Regression references (`inchi.sdf`, `mcule`) regenerated in #280: 141 prefix-only and 308 layer changes, all on MI structures.

Test counts: 20 suites / 194 tests (`ctest` in a fresh out-of-tree build at `b40eeee` plus `test_github_285.cpp`); `test_roundtrip.py` 3 passed, 1 xfailed.

## 5. Open issues / risks

- **A. Combining subversions.** Slide 6 of the PDF says "latest feature wins"; the thread
  (fbaensch-beilstein, comment 6) asks whether `1SB` can still be made once `1SC` exists.
  gblanke02: "needs further discussions by the stakeholders". Blocks VR-R9.
- **B. Metalloids.** Sb counts as metal; Ge, As, Te do not (MI table). Older tables disagree
  (`strutil.c` vs `eldata.c` `is_el_a_metal`, thread comment 2). Working group to decide;
  changing the set changes the prefix and key of every affected compound. Blocks VR-R10.
- **C. Letter lookup table.** 25 letters left (`B`–`Z`); who maintains the table and where
  (release notes only?) is open. schatzsc (2026-10-19) argues against letters at all and asks
  for a design review in a meeting. Blocks VR-R11.
- **D. Old readers do not reject.** 1.07-era CLI (`68afb20`) reads
  `InChI=1BB/Cl2H6N2Pt/c1-5(2,3)4/h3-4H3` with `-InChI2InChI` without error and writes
  `InChI=1/Cl2H6N2Pt/c1-5(2,3)4/h3-4H3`: both markers silently lost. The API calls reject
  (thread comment 3). Release notes should say so; nothing in InChI can fix old binaries.
- **E. Whole-structure trigger.** The subversion is set per input structure, not per
  component: ethanol mixed with NaCl gets `1BB` for both components.
- **F. `1BB` readability.** schatzsc (2026-10-19): "never know if the double-B is a mistake".
  Part of C.

## 6. Assumptions & dependencies

- Molecular Inorganics (#259, merged with #280) decides the layers; this spec only the prefix and flags.
- Enhanced stereochemistry (`-EnhancedStereochemistry`, specs 1–4) also sets class `B`; on a metal compound both give `1BB`.
- The MI element table `molecular_inorganics_data.c` is the trigger (§2.2).

## 7. Worked examples

All measured with `inchi-1` from `68afb20` (before) and `b40eeee`, default options unless noted.

| input | option | InChI / InChIKey | before |
|---|---|---|---|
| ethanol | — | `InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3` · `LFQSCWFLJHTTHZ-UHFFFAOYSA-N` | same |
| cisplatin (N→Pt dative) | — | `InChI=1BB/Cl2H6N2Pt/c1-5(2,3)4/h3-4H3` · `NKTISDOLGLLLMZ-UHFFFAOYBB-N` | `InChI=1S/2ClH.2H3N.Pt/h2*1H;2*1H3;/q;;;;+2/p-2` · `LXZZYRPGZAFOLE-UHFFFAOYSA-L` |
| NaCl | — | `InChI=1BB/ClH.Na/h1H;/q;+1/p-1` · `FAPWRFPIFSIZLT-UHFFFAOYBB-M` | `InChI=1S/ClH.Na/h1H;/q;+1/p-1` · `FAPWRFPIFSIZLT-UHFFFAOYSA-M` |
| SbCl3 | — | `InChI=1BB/Cl3Sb/c1-4(2)3` · `AWUJNTVNMLYCBF-UHFFFAOYBB-N` | `InChI=1S/3ClH.Sb/h3*1H;/q;;;+3/p-3` |
| AsCl3 | — | `InChI=1S/AsCl3/c2-1(3)4` · `OEYOHULQRFXULB-UHFFFAOYSA-N` | same |
| ethanol | `-FixedH` | `InChI=1N/C2H6O/c1-2-3/h3H,2H2,1H3` · `LFQSCWFLJHTTHZ-UHFFFAOYNA-N` | `InChI=1/C2H6O/c1-2-3/h3H,2H2,1H3` |
| NaCl | `-FixedH` | `InChI=1NB/ClH.Na/h1H;/q;+1/p-1/fCl.Na/h1h;/q-1;m` · `FAPWRFPIFSIZLT-VHFVCOHVNB-M` | `InChI=1/…` · `…-VHFVCOHVNA-M` |
| cisplatin | `-LegacyMetalHandling` | `InChI=1N/2ClH.2H3N.Pt/h2*1H;2*1H3;/q;;;;+2/p-2` · `LXZZYRPGZAFOLE-UHFFFAOYNA-L` | (option did not exist) |
| ethanol | `-EnhancedStereochemistry` | `InChI=1B/C2H6O/c1-2-3/h3H,2H2,1H3` · `LFQSCWFLJHTTHZ-UHFFFAOYBA-N` | same |
