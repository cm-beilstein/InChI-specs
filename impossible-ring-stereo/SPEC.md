# Spec 5 — Physically impossible ring stereo (in/out bridgeheads, trans fusion)

| | |
|---|---|
| **Doc version** | 0.1 |
| **Date** | 2026-10-23 |
| **Status** | draft — proposal, not implemented |
| **Author** | C. Müller |
| **Reviewers** | TBD |
| **Requirement prefix** | `RS-` |
| **Readiness** | ready with open points — warn-only behaviour agreed in #287; ring-size limits unverified, confirmed 2026-10-23 |
| **Kick-off documents** | [`docs/impossible-ring-stereo/`](../docs/impossible-ring-stereo/) |
| **Change history** | 0.1 (2026-10-23) — initial spec from [IUPAC-InChI/InChI#287]; strings measured with `atropisomers` 09043c1, standard options. |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

- ✅ **Works:** nothing yet; the problem is measured and the behaviour agreed (warn, keep the InChI).
- ❌ **Missing:** all requirements (RS-R1–RS-R7).
- ▶ **Next:** check the ring-size limits (§5.A), then implement RS-R1–RS-R3 with their gates.

**Feature:** warn when a drawing shows ring stereo that cannot exist: a bridgehead
substituent pointing into a small cage, or a small ring fused trans. · **Branch:** none yet
· **Sources:** [IUPAC-InChI/InChI#287] ([snapshot](../docs/impossible-ring-stereo/issue-287.md)).

---

## 1. Problem

InChI encodes physically impossible ring stereo without a specific warning, so two drawings
of one compound get two InChIs. From #287, bridged-ring example 8 (`datasets/bicyclononane_in_out.mol`),
standard options:

| Drawing | InChI stereo layers | Warning |
|---|---|---|
| as drawn: both bridgehead wedges the same way, one H inside the cage | `/t7-,8-/m0/s1` | "Ambiguous stereo: center(s)" |
| H on atom 8 flipped: both H outside (the real compound) | `/t6-,7+,8-` | "Ambiguous stereo: center(s); Not chiral" |

trans-Bicyclo[4.1.0]heptane, which cannot exist, gets `/t6-,7-/m0/s1` with no warning at all;
the real cis form gives `/t6-,7+`.

## 2. Target behaviour

Agreed in #287 (proposal by cm-beilstein; gblanke02 agreed to the warn-only behaviour,
2026-10-20, "under the assumption that the programming efforts are overseeable"):

1. **Warn, do not change the InChI.** InChI identifies what was drawn, not what was meant.
   The warning names the problem, e.g. "Impossible ring stereo", and the atoms involved.
2. **In/out bridgeheads (bridged bicycles, bridge length z ≥ 1).** Order each bridgehead's
   neighbours (bridge a, bridge b, bridge c, exo substituent) and compare the two local
   parities. Looking along the bridgehead–bridgehead axis the bridges run clockwise from one
   end and anticlockwise from the other, so out,out always gives mirror-image parities.
   Equal parities mean in,out. Flag at bridge sum ≤ 8 ([2.2.1], [2.2.2], [3.2.1], [3.3.1]);
   "in" is known only for large cages (about bicyclo[4.4.4], bridge sum ≈ 12).
3. **Trans ring fusion (z = 0).** Same test with a zero-atom bridge:

   | Smaller ring | Trans-fused partner |
   |---|---|
   | 3 | impossible below 7 (trans-bicyclo[5.1.0] isolable) |
   | 4 | impossible below 5 (trans-bicyclo[3.2.0] strained, known) |
   | ≥ 5 | allowed |

4. **Small rings with multiple bonds** (warnings, not stereo): E double bond below 8 (ring
   E/Z already ignored below 8), allene below 9, triple bond below 8, bridgehead double bond
   (Bredt) below bridge sum 7.
5. **Cages:** rule 2 for every bridgehead pair whose rings share ≥ 2 atoms; anything beyond
   that is left to 3D validators.

## 3. Current implementation

| Stage | Location (function) | State |
|-------|---------------------|-------|
| Ring systems | `ichinorm.c` `MarkRingSystemsInp` | ✅ exists, reusable |
| Stereo parities | `ichister.c` (tetrahedral parities) | ✅ exists, reusable |
| Ambiguous-stereo marking and warning | `ichimak2.c` `MarkAmbiguousStereo`, `runichi4.c` `GetProcessingWarningsOneInChI` | ✅ exists; does not say what is wrong |
| In/out and trans-fusion test | — | ❌ missing |

## 4. Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| RS-R1 | In/out bridgeheads with bridge sum ≤ 8 MUST raise a warning naming the bridgehead atoms. | Must | ❌ open |
| RS-R2 | Trans fusion of a 3-ring to a ring below 7, or of a 4-ring to a ring below 5, MUST raise the same kind of warning. | Must | ❌ open |
| RS-R3 | The InChI and InChIKey MUST stay byte-identical with and without the check. | Must | ❌ open |
| RS-R4 | Cages: the test SHOULD run for every bridgehead pair whose rings share ≥ 2 atoms. | Should | ❌ open |
| RS-R5 | An allene in a ring below 9 SHOULD warn (with Spec 2, allenes). | Should | ❌ open |
| RS-R6 | A triple bond in a ring below 8 and a bridgehead double bond below bridge sum 7 COULD warn. | Could | ❌ open |
| RS-R7 | Tethered atropisomer axes too short for the drawn twist COULD warn (with Spec 4). | Could | ❌ open |

### Gates

Molecules and their sources: [datasets/DATASETS.md](datasets/DATASETS.md).

- **G1** — the #287 molfile as drawn warns, naming atoms 2 and 8; with the wedge on atom 8 flipped it does not. ❌ not written.
- **G2** — trans-bicyclo[4.1.0]heptane warns, the cis form does not; trans-bicyclo[5.1.0]octane does not. ❌ not written.
- **G3** — for G1 and G2 inputs, InChI and InChIKey equal those without the check (RS-R3). ❌ not written.

## 5. Open issues / risks

- **A. Ring-size limits unverified.** The bridge-sum threshold (8) and the trans-fusion table
  are approximate literature values (#287); check them against the literature before
  implementing, and name the source in §2.
- **B. Warning text and channel.** Wording, and whether the new warning replaces
  "Ambiguous stereo" for these atoms or comes in addition, is not decided.
- **C. Cost.** gblanke02's agreement assumes moderate effort; estimate after RS-R1.

## 6. Assumptions & dependencies

- Reuses ring perception and parities; needs no new input data.
- RS-R5 touches Spec 2 (allenes), RS-R7 Spec 4 (atropisomers).

## 7. Worked examples

| input | standard InChI today | warning today | wanted |
|---|---|---|---|
| `datasets/bicyclononane_in_out.mol` | `…/t7-,8-/m0/s1` | Ambiguous stereo | + "Impossible ring stereo" (atoms 2, 8) |
| same, atom 8 H flipped | `…/t6-,7+,8-` | Ambiguous stereo; Not chiral | unchanged |
| `C1CC[C@H]2C[C@@H]2C1` (trans) | `…/t6-,7-/m0/s1` | none | "Impossible ring stereo" |
| `C1CC[C@H]2C[C@H]2C1` (cis) | `…/t6-,7+` | none | none |

[IUPAC-InChI/InChI#287]: https://github.com/IUPAC-InChI/InChI/issues/287
