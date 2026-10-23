"""Page parts for impossible-ring-stereo/explain.html (proposal, IUPAC-InChI/InChI#287).

Nothing here is implemented: the page shows what standard InChI does today
with ring stereo that cannot exist, and the proposed check.
"""

import html
import os
import re

from explain import SPECS, inchi, mark, picture, stereo_tail, warning

DATA = os.path.join(SPECS, "impossible-ring-stereo", "datasets")

# Issue #287, bridged-ring example 8: bridgehead C8 carries H9; bond 8 is its wedge
DRAWN_H = "M  V30 8 1 8 9 CFG=1"
FLIPPED_H = "M  V30 8 1 8 9 CFG=3"

# Bicyclo[4.1.0]heptane, junction atoms 3 and 5 (cis/trans from a 3D model)
CIS = "C1CC[C@H]2C[C@H]2C1"
TRANS = "C1CC[C@H]2C[C@@H]2C1"


def standard(mol):
    """Stereo tail of the standard InChI (no options)."""
    return stereo_tail(inchi(mol, [])[0])


def bridged():
    """In/out bridgeheads: the drawing from the issue and its feasible twin."""
    block = open(os.path.join(DATA, "bicyclononane_in_out.mol")).read()

    # Standard InChI only: drop the STEABS collection the file carries
    block = re.sub(r"M  V30 BEGIN COLLECTION\n.*?M  V30 END COLLECTION\n", "", block, flags=re.S)
    flipped = block.replace(DRAWN_H, FLIPPED_H)
    assert flipped != block

    drawn_tail, flipped_tail = standard(block), standard(flipped)
    assert drawn_tail == "/t7-,8-/m0/s1", drawn_tail
    assert flipped_tail == "/t6-,7+,8-", flipped_tail

    warn = warning(block)
    assert "Ambiguous stereo" in warn, warn

    return dict(drawn_pic=picture(block, numbers=False), drawn_tail=mark(drawn_tail),
                drawn_warn=html.escape(warn),
                flipped_pic=picture(flipped, numbers=False), flipped_tail=mark(flipped_tail))


def fused():
    """Trans fusion: a cyclopropane cannot be trans-fused to a cyclohexane."""
    cis_tail, trans_tail = standard(CIS), standard(TRANS)
    assert cis_tail != trans_tail, cis_tail
    assert warning(TRANS) == "", warning(TRANS)

    return dict(cis_pic=picture(CIS, numbers=False), cis_tail=mark(cis_tail),
                trans_pic=picture(TRANS, numbers=False), trans_tail=mark(trans_tail))


def parts():
    return dict(**bridged(), **fused())
