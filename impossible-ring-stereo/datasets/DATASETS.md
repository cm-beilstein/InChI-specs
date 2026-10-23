# Impossible ring stereo datasets

Molecules used by the [explanation page](../explain.html). Proposal: no spec or tests yet.

| File / input | Molecule | Source | Shows |
|---|---|---|---|
| `bicyclononane_in_out.mol` | 9-(methylsulfonyl)-3-oxa-9-azabicyclo[3.3.1]nonan-7-amine, bridgehead H on atom 8 drawn pointing into the cage | issue #287 (bridged-ring example 8); blank title line restored | impossible in/out bridgeheads: `/t7-,8-/m0/s1` with "Ambiguous stereo" |
| same file, bond 8 `CFG=1` → `CFG=3` | same, both bridgehead H outside | issue #287 | the real compound: `/t6-,7+,8-` |
| `C1CC[C@H]2C[C@H]2C1` | cis-bicyclo[4.1.0]heptane (norcarane) | — | possible fusion |
| `C1CC[C@H]2C[C@@H]2C1` | trans-bicyclo[4.1.0]heptane | — | impossible trans fusion, no warning |

cis/trans of the bicycloheptanes checked with an RDKit 3D embedding (MMFF).
