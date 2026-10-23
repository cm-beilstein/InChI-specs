<!-- Snapshot of https://github.com/IUPAC-InChI/InChI/issues/287 taken 2026-10-23; the issue is the source of truth. -->
# Detect physically impossible ring stereo (in/out bridgeheads, trans fusion)

IUPAC-InChI/InChI#287, opened by cm-beilstein on 2026-10-15T09:15:14Z

## Problem

InChI encodes physically impossible ring stereo without warning. Two depictions of the same compound give different InChIs.

Example: 9-(methylsulfonyl)-3-oxa-9-azabicyclo[3.3.1]nonan-7-amine, bridged-ring example 8 ("alternative depiction to example 3, physically not possible"). Both bridgehead H wedges point the same way, so one bridgehead H points *into* the cage.

| Input | InChI |
|---|---|
| as drawn (impossible) | `InChI=1S/C8H16N2O3S/c1-14(11,12)10-7-2-6(9)3-8(10)5-13-4-7/h6-8H,2-5,9H2,1H3/t7-,8-/m0/s1` (warning: Ambiguous stereo) |
| H on atom 8 flipped (feasible) | `.../t6-,7+,8-` (achiral; C6 becomes an endo/exo centre) |

Standard InChI and `-EnhancedStereochemistry` behave the same.

<details><summary>Molfile (as drawn)</summary>

```
  ACCLDraw10122612332D

  0  0  0     0  0            999 V3000
M  V30 BEGIN CTAB
M  V30 COUNTS 16 17 0 0 1
M  V30 BEGIN ATOM
M  V30 1 H 24.2276 -19.1496 0 0
M  V30 2 C 23.9219 -18.0087 0 0 CFG=1
M  V30 3 N 22.9368 -16.6737 0 0 CFG=3
M  V30 4 S 23.8032 -16.0572 0 0 CFG=3
M  V30 5 C 24.7948 -15.248 0 0
M  V30 6 O 24.294 -16.9303 0 0
M  V30 7 O 23.435 -15.4475 0 0
M  V30 8 C 22.7411 -15.1582 0 0 CFG=2
M  V30 9 H 22.4347 -14.0647 0 0
M  V30 10 C 21.9062 -15.9931 0 0
M  V30 11 O 21.9062 -17.1739 0 0
M  V30 12 C 22.7411 -18.0087 0 0
M  V30 13 C 23.9219 -15.1582 0 0
M  V30 14 C 24.7567 -15.993 0 0 CFG=2
M  V30 15 N 25.7796 -15.4025 0 0
M  V30 16 C 24.7567 -17.1739 0 0
M  V30 END ATOM
M  V30 BEGIN BOND
M  V30 1 1 2 1 CFG=3
M  V30 2 1 2 3
M  V30 3 1 3 4
M  V30 4 1 4 5
M  V30 5 2 4 6
M  V30 6 2 4 7
M  V30 7 1 8 3
M  V30 8 1 8 9 CFG=1
M  V30 9 1 10 8
M  V30 10 1 11 10
M  V30 11 1 11 12
M  V30 12 1 12 2
M  V30 13 1 8 13
M  V30 14 1 14 13
M  V30 15 1 14 15 CFG=3
M  V30 16 1 16 14
M  V30 17 1 2 16
M  V30 END BOND
M  V30 BEGIN COLLECTION
M  V30 MDLV30/STEABS ATOMS=(3 2 8 14)
M  V30 END COLLECTION
M  V30 END CTAB
M  END
```
</details>

## Proposed detection rules

Size limits are approximate literature values and need checking.

1. **In/out bridgeheads (bridged bicycles, z ≥ 1).** Compute each bridgehead's parity with neighbours ordered (bridge a, bridge b, bridge c, exo substituent). Opposite parities: out,out (normal). Equal parities: in,out. Looking along the bridgehead–bridgehead axis, the bridges run clockwise from one end and anticlockwise from the other, so out,out always gives mirror-image local parities. "In" is known only for large cages (~bicyclo[4.4.4], bridge sum ≈ 12). Flag at bridge sum ≤ 8 ([2.2.1], [2.2.2], [3.2.1], [3.3.1]).
2. **Trans ring fusion (z = 0).** Same test, zero-atom bridge.

   | Smaller ring | Trans-fused partner |
   |---|---|
   | 3 | impossible below 7 (trans-[5.1.0] isolable) |
   | 4 | impossible below 5 (trans-[3.2.0] strained, known) |
   | ≥ 5 | allowed |
3. **Ring size limits for unsaturation.**

   | Feature | Smallest isolable ring | Status |
   |---|---|---|
   | E double bond | 8 | already handled: ring E/Z ignored below 8 |
   | allene | 9 | add to allene support |
   | triple bond | 8 | not stereo; warning only |
   | bridgehead double bond (Bredt) | bridge sum S ≥ 7 | not stereo; warning only |
4. **Tethered atropisomer axes.** Too short a tether can't support the drawn twist. Lower priority.
5. **Cages.** Apply rule 1 to every bridgehead pair whose rings share ≥ 2 atoms. Anything beyond that needs 3D embedding; leave it to upstream validators.

## Proposed behaviour

Emit a warning (e.g. "Impossible ring stereo"). Leave the InChI unchanged: InChI identifies what was drawn, not what was meant.

Rules 1–2 catch the example and reuse existing parities and ring perception.


## Comments

### gblanke02 (2026-10-20T22:42:49Z)

Quite interestingly, none of the standard cheminformatic  toolkits seem to take care of these limitations so that the InChI has to give an answer in these cases. Therefore I agree with the proposed behaviour to emit a warning  under the assumption that the programming efforts are overseeable. 
