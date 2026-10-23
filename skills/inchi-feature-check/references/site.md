# How the InChI Specifications site is built

Site: https://cm-beilstein.github.io/InChI-specs/ — GitHub Pages straight from `main`
of cm-beilstein/InChI-specs (`.nojekyll`). Pushes are mirrored to the private
IUPAC-InChI/InChI-Specifications. Code lives in IUPAC-InChI/InChI, expected as a clone
next to this repo (`../InChI`).

## Per feature (folder `<key>/`)

| File | Audience | Made by |
|---|---|---|
| `SPEC.md` | developers | hand, from `references/spec-template.md` |
| `explain.template.html` → `explain.html` | chemists | `tools/explain.py` + `tools/explain_<name>.py` |
| `examples/index.html`, `examples/<table>.sdf`, `examples/svg/` | both | `tools/build.py` from `tools/molecules.py` |
| `workflow.html` (optional) | chemists | `tools/rebuild.py` renders `tools/workflow/<table>.json` with archify (`../archify`, node) |
| `datasets/`, `datasets/DATASETS.md` | developers | molecules the spec, tests and pages use; DATASETS.md lists each with source and purpose, linked from SPEC.md |

Kick-off documents: `docs/<topic>/`, shared by features of one topic (`"docs"` in site.json).

Landing page `index.html`: one row per entry of `tools/site.json`, in that order. Row IDs
`#f1…` follow that order; append new features at the end. Columns read from the files:
**Ready** from the spec header row `| **Readiness** | <verdict> — … |`; **Done** counts the
spec's Must/Should requirement rows marked ✅ (withdrawn ⊘ excluded) and the gate items
under `### Gates` that say ✅ and not ❌. Keep those markers accurate: the column is only as
true as the spec.

## tools/site.json, one entry per feature

```json
{
  "key": "inchi-versioning",
  "title": "Versioning of InChI and InChIKey",
  "status": "implemented",            // or "proposed"
  "old": {"rev": "68afb20", "label": "dev", "options": []},
  "new": {"rev": "b40eeee", "label": "dev", "options": []},
  "inchiKey": true,                    // optional: show InChIKeys in the examples
  "markVersion": true,                 // optional: a changed version prefix counts as a change
  "docs": "inchi-versioning",          // kick-off documents: docs/<topic>/
  "tracking": {"branch": "dev", "issues": [285], "prs": [280]}
}
```

- `old` = the last revision *without* the feature, `new` = a revision *with* it. Pin
  commit hashes, not branch names, so a rebuild reproduces the same strings.
- A proposed feature has no `old`; `new` is the binary its explanation page measures with.
- `dataRev` (top level): the InChI revision whose test files and fixtures `molecules.py`
  reads molblocks from.

## Examples (tools/molecules.py)

- A table is a list of entry dicts (the module docstring lists the fields: `smiles`
  as CXSMILES, `wedges`, `coll`, `sdf`, `tests`, `edit`, …) and a line in `TABLES`.
- **Molecule IDs are global and never renumbered**: issue comments cite them
  ("entry 55"). Add new tables at the end of `TABLES`, new molecules at the end of the
  last table.
- `SPEC_OF[table] = (key, "")` puts the table on `<key>/examples/`; a second table of the
  same feature uses an anchor on its explanation page, e.g. `("enhanced-stereo", "#meso")`.
- Choose molecules that show the change, ones that must *not* change, and edge cases.
  Titles say what the row shows ("edge: …", "limitation: …").
- RDKit drops non-tetrahedral atoms (e.g. an allene's central atom) from CXSMILES
  enhanced-stereo groups; use `coll=[("STERAC1", [atoms])]` instead.

## Explanation page

- `<key>/explain.template.html`: `string.Template`, `$style` for the shared CSS, `$name`
  fields filled by `tools/explain_<name>.py` `parts()`. Register the module in
  `SPEC_MODULES` in `tools/explain.py`. Copy the head and footer of an existing template.
- Write for chemists: what the user draws, what InChI writes, why. Short sentences.
- Every InChI on the page is computed by the generator and `assert`ed, so a change in
  output breaks the build instead of silently making the page wrong. State geometry
  (cis/trans, R/S) only when checked, e.g. with a 3D embedding.
- Each `<h2 id="…">` gets its own comment thread; ids are permanent thread names.
- The last section is `<h2 id="use">How to use it</h2>`: input, command line with real
  output via `explain.cli(mol, options, name)`, the library call.

## Comments (giscus)

`tools/comments.py`; config in `tools/giscus.json` (repo, category, `specDiscussions`).
Thread titles: `<key> · general`, `<key> · molecule <id>`, `<key> · explain · <h2 id>`.
Create a feature's general discussion with `python tools/new_discussion.py <key>`
(idempotent). Never rename a key, molecule ID or h2 id that already has a thread.

## Rebuild and check

Python with RDKit ≥ 2024: `~/.venvs/inchi-specs/bin/python` (create with
`python3 -m venv ~/.venvs/inchi-specs && ~/.venvs/inchi-specs/bin/pip install rdkit`).
Headless Chromium: `~/.cache/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell`.

```
python tools/rebuild.py          # RDKit python; builds needed binaries (cached)
python tools/audit.py <key>      # ok/MISSING per document
python tools/doc_check.py <key> --option <Name>   # Doxygen + user docs in ../InChI
python tools/workflow_check.py   # quoted strings in workflow diagrams are measured
git diff --stat                  # only intended pages changed?
```

Look at new pages, not just the diff: headless Chromium screenshot (strip the Google
Fonts `<link>`s first, the sandbox has no network):

```
chrome-headless-shell --headless --no-sandbox --screenshot=out.png --window-size=1100,2400 \
    --virtual-time-budget=3000 file:///path/page.html
```

After pushing, wait for the Pages build
(`gh api repos/cm-beilstein/InChI-specs/pages/builds/latest --jq .status`) and `curl` the URL.
