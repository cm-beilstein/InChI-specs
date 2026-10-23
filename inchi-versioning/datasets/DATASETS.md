# Versioning datasets

Molecules used by the [spec](../SPEC.md), the [explanation page](../explain.html) and the
[examples](../examples/) (IDs 116–129), with their source. Strings are measured with
`dev` 68afb20 (before PR #280) and b40eeee (after); see the examples page for both.

| ID | Molecule | Input (SMILES) | Source | Shows |
|---|---|---|---|---|
| 116 | ethanol | `CCO` | issue #285 | organic: `1S`/`SA` unchanged |
| 117 | L-alanine | `C[C@H](N)C(=O)O` | — | organic with stereo unchanged |
| 118 | cisplatin | `[NH3]->[Pt](<-[NH3])(Cl)Cl` | issue #285 | new layers and `1BB`/`BB`; needs the dative bonds to reproduce the issue (`N[Pt](N)(Cl)Cl` gives NH2 ligands) |
| 119 | sodium chloride | `[Na+].[Cl-]` | issue #285 | same layers, new prefix |
| 120 | sodium acetate | `CC(=O)[O-].[Na+]` | — | salt: prefix only |
| 121 | methyllithium | `C[Li]` | `test_inchi_dll_b.cpp` (G1) | Li–C bond kept |
| 122 | methylmagnesium bromide | `C[Mg]Br` | — | bonds kept |
| 123 | ferrocene, ionic drawing | `[cH-]1cccc1.[cH-]1cccc1.[Fe+2]` | `test_inchi_dll_b.cpp` (G1) | prefix only |
| 124 | tin(IV) chloride | `Cl[Sn](Cl)(Cl)Cl` | — | bonds kept |
| 125 | antimony trichloride | `Cl[Sb](Cl)Cl` | issue #285 thread | Sb counted as metal |
| 126 | arsenic trichloride | `Cl[As](Cl)Cl` | issue #285 thread | As not a metal: unchanged |
| 127 | germanium tetrachloride | `Cl[Ge](Cl)(Cl)Cl` | issue #285 thread | Ge not a metal: unchanged |
| 128 | tellurium tetrachloride | `Cl[Te](Cl)(Cl)Cl` | issue #285 thread | Te not a metal: unchanged |
| 129 | ethanol + NaCl | `CCO.[Na+].[Cl-]` | — | one metal marks the whole InChI |

Further test inputs live in IUPAC-InChI/InChI: `INCHI-1-TEST/tests/test_unit/test_inchi_dll_b.cpp`,
`test_molecularInorganics.cpp`, `INCHI-1-TEST/tests/test_executable/test_roundtrip.py`
(gates G1–G5, G7), and the proposed `test_github_285.cpp` (G6, not yet in the repo).
