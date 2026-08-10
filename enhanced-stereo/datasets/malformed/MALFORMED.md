# ES-R12 validation corpus — malformed enhanced-stereo collections

Eight molfiles that violate the [BIOVIA] input constraints in SPEC §2 ("a stereogenic centre
belongs to **exactly one** stereochemical group; at most one ABS collection"). Collected
2026-08-10 to give ES-R12 something to be gated against.

Measured with `inchi-1d` built from `feature/enh-stereo-hardening` @ `0f295ff`
(`-EnhancedStereochemistry -STDIO -NOLABELS`). **Every one of them reports "0 errors".**

> **Status 2026-08-10 (later the same day):** ES-R12 is now implemented in
> `MolfileV3000ReadCollections` (`StereoCollectionsAreMalformed`). All eight files now
> emit a `V3000 collections: …` warning and degrade to the standard string apart from the
> `1B` prefix. See "After the fix" at the end.

## Provenance

Two are real, upstream files; six are derived by editing only the `BEGIN COLLECTION` block of
`../rdkit_two_centers_or.mol` (RDKit `Code/GraphMol/FileParsers/test_data/two_centers_or.mol`),
so every row differs from the baseline in the collection block and nothing else.

| File | Source |
|---|---|
| `rdkit8873_one_abs_group.mol`, `rdkit8873_two_abs_groups.mol` | attachments to [rdkit/rdkit#8873](https://github.com/rdkit/rdkit/issues/8873) "Multiple absolute stereo groups shouldn't be allowed on a single mol" — reported from a real R-group-enumeration pipeline. Same structure, same stereochemistry, one vs two `STEABS` collections. |
| the other six | derived from `../rdkit_two_centers_or.mol` (baseline `STEABS(1)` + `STEREL1(4,5)`) |

## Measurements

Baseline `rdkit_two_centers_or.mol` →
`InChI=1B/C6H12BrF/c1-4(5(2)7)6(3)8/h4-6H,1-3H3/t4-,5-,6+/m1/s1(5)2(4,6)`

| Case | Collection block | Measured | Defect |
|---|---|---|---|
| `overlap_abs_rac` | `STEABS(1,4)` + `STERAC1(4,5)` | `…/t4-,5-,6+/m1/s1(4,5)3(4,6)` | atom 4 emitted as **both** absolute and racemic |
| `two_abs` | `STEABS(1)` + `STEABS(4,5)` | `…/t4-,5-,6+/m1/s1` | two ABS collections merged, then reduced to a bare `/s1` — all trace of the malformed input erased |
| `dup_within` | `STEREL1(4,4,5)` | `…/m1/s1(5)2(4,4,6)` | emits `4,4` — **violates the §6 ABNF** ("atoms MUST be in ascending canonical order") |
| `same_id_twice` | `STEREL1(4)` + `STEREL1(5)` | `…/t4-,5-,6-/m1/s1(5)2(4)(6)` | same group id twice read as two groups: blocks the ES-R17 reduction **and changes `/t`** (`6+`→`6-`) |
| `out_of_range` | `STEREL1(4,99)` | `…/m1/s1(5)2(4)` | atom 99 silently dropped; centre 6 vanishes from `/s` |
| `count_mismatch` | `STEREL1 ATOMS=(3 4 5)` (count 3, two listed) | == baseline | tolerated; benign, lowest priority |
| `rdkit8873_two_abs_groups` | `STEABS(1,3)` + `STEABS(1,4)` | `…/t7-,8-` | **`/t` differs from standard InChI** (`/t7-,8+`) and from the single-ABS file encoding the same structure — a different diastereomer |

## What the corpus establishes

1. **The corruption is not confined to `/s`.** SPEC 0.6 §5.H states it is. `same_id_twice` and
   `rdkit8873_two_abs_groups` both change `/t`, the latter breaking the §2 backward-compatibility
   invariant: with the option on, the string names a different stereoisomer than standard InChI
   gives for the same file. Each excess group runs its own whole-group sign flip in
   `invert_parities`, and two flips over overlapping/duplicated centres do not cancel.
2. **`dup_within` produces output that violates our own normative grammar**, so ES-R12 is not
   only an input-validation gap — the §6 ascending-order MUST is reachable from valid-looking input.
3. **Nothing is diagnosed.** All eight report "0 errors".

## Reference-implementation behaviour (what to match)

- **RDKit** — validates two of these at parse time in `parseEnhancedStereo`
  ([`MolFileParser.cpp`](https://github.com/rdkit/rdkit/blob/master/Code/GraphMol/FileParsers/MolFileParser.cpp)):
  a second ABS collection → `"Seen a second ABS stereo group on line N"`, and a repeated atom
  inside one collection → `"Atom N appears more than once in stereo group specification on line M!"`.
  Both **throw** under `strictParsing`, warn otherwise; the same duplicate-atom check exists for
  CXSMILES in `CXSmilesOps.cpp`. Added by
  [PR #8904](https://github.com/rdkit/rdkit/pull/8904) for #8873, which also collapses duplicate
  ABS groups in `setStereoGroups()`. RDKit does **not** check cross-collection membership
  (`overlap_abs_rac` passes silently there too).
- **Indigo** — no validation at all: `molfile_loader_v3000.cpp` writes into per-atom arrays
  (`_stereocenter_types[atom_idx] = stereo_type`), so an atom in two collections silently takes
  the **last** one. Deterministic but input-order dependent.
- On merging vs. renumbering same-id groups, RDKit's own position is unsettled — see
  [#6050](https://github.com/rdkit/rdkit/issues/6050) and the discussion in #8873: "since we don't
  have a context, I don't think we can assume merging will always be the right answer."
  For InChI the safer reading is to diagnose rather than repair, which is what ES-R12 already says.

## After the fix

`StereoCollectionsAreMalformed` (mol_fmt3.c) runs once after the collection block is read and
checks five things: more than one STEABS collection; a STEREL/STERAC group number naming two
collections; an atom in two collections; an atom listed twice in one collection; an atom the
CTab does not have. On any of them it names the violation via `AddErrorMessage` and frees all
three collection lists, so the enhanced path takes the same route as a structure with no
collection block at all (ES-R19) instead of guessing what the file meant.

Every case now measures the standard string with the `1B` prefix —
`…/t4-,5-,6+/m1/s1` for the six derived files, `…/t7-,8+` for both RDKit ones — plus a
warning. `rdkit8873_two_abs_groups` and `rdkit8873_one_abs_group` now agree, and
`same_id_twice` is back to `6+`: the `/t` corruption is gone.

Behaviour changes worth knowing:

- **`count_mismatch` is no longer benign.** `ATOMS=(3 4 5)` promises three atoms and lists two,
  so the third slot is garbage and trips the unknown-atom check. It used to produce the correct
  `/s1(5)2(4,6)` by luck; it now warns and drops the collection. Consistent with the
  diagnose-don't-guess policy, but it is a loss of output for a file that happened to work.
- **The warning appears with the option off too**, since collections are parsed regardless. The
  standard InChI *string* is unchanged in every case — only the API return goes
  `inchi_Ret_OKAY` → `inchi_Ret_WARNING` for malformed files.

Gates: `test_mol_fmt.cpp` `test_EsR12_*` (six reader-level cases including a well-formed
over-rejection guard) and `test_enhancedStereo.cpp`
`test_EnhancedStereochemistry_malformed_collections_are_not_used` (four end-to-end).
Three of the four end-to-end cases were verified to fail with the fix reverted; the second-STEABS
case cannot be distinguished end-to-end, because the laundered output coincides with the degraded
one — only the diagnostic separates them, which is why the unit test carries it.
