---
name: inchi-feature-update
description: Bring every document of the InChI Specifications site up to date after a code change in IUPAC-InChI/InChI - a bug fix, a cherry-pick to other branches, changed output, a merged PR - or after a new decision, open question or reviewer comment in an issue. Updates the affected SPEC.md files (version, change history, requirements, open issues, gates, test counts, worked examples), sibling specs that share the changed code, the examples and explanation pages, site.json revisions and tracking, and the README status. Use whenever the user fixed or changed InChI behaviour and says "update the specs/docs/site", asks "did you update the specs for X", cherry-picks a fix, or a PR for a documented feature lands. For a feature with no documents yet, use inchi-feature-check.
---

# InChI feature update

A code change is done when the documents describing that code say what it now does.
This skill finds every document the change touches and updates it from measurements.
It shares its references with inchi-feature-check; read
`../inchi-feature-check/references/site.md` before changing the site.

## 1. Pin down the change

- Commits: `git -C ../InChI log --oneline <base>..<head>`, on every branch the change
  landed on (cherry-picks get different hashes; collect them all).
- Behaviour: run the binary before and after over all fixtures and datasets (test
  fixtures, `*/datasets/`, `*/examples/*.sdf`) and diff the InChIs. This is the ground
  truth for what changed; an empty or unexpected diff needs explaining before writing.
- No code change, only a decision or new information (an issue comment, a working-group
  ruling, a new open question): skip the commits, but still measure today's behaviour for
  the cases the decision concerns, so the spec states facts, and record who said what with
  a link to the comment. A readiness change is proposed to the user, as always.

## 2. Find the affected features

A change belongs to every feature whose output or code it touches, not only the one it
was made for. Search spec §3 tables and texts for the changed function names
(`grep -l <function> */SPEC.md`) and check each feature's examples in the diff from step 1.

Measure rather than reason: if a feature could be affected, build a small molecule that
exercises it and run it before and after. Record the result either way. "No effect on
`/b`, measured over 1,588 files" is worth a line in that spec; a surprising result
becomes an open issue marked unverified.

## 3. Update each affected SPEC.md

- Doc version +0.1 (or the next minor), Date, a Change history entry: what changed, why,
  commits per branch.
- Requirements: new row or new status; gates name the test.
- §3 implementation table: new or changed functions.
- §5: new limitations as open issues; fixed ones move to "Resolved in <version>",
  struck through, kept.
- Test counts, re-counted (`<test binary> --gtest_list_tests`), not adjusted by hand.
- ✅/❌ markers of requirements and gates: the landing page's "Done" column counts them.
- Readiness: if a decision closed (or opened) a gap, propose the new verdict to the user.
- Datasets: molecules added for the change go into `datasets/` and `DATASETS.md`.
- Worked examples: measured before/after rows.

Then the repo `README.md`: status column of each touched spec, new source documents,
molecule-ID range.

And the documentation in the InChI repo: `python tools/doc_check.py <key> --option <name>`
for each affected feature. New or changed functions need their Doxygen block, a new or
changed option its help text, README, CHANGELOG, User Guide and API Reference entries.

## 4. Update the site

- `tools/site.json`: the `new` revision of each affected feature (pinned hash containing
  the change), `old` if the comparison base moved, tracking (new issues, PRs, branches).
- Examples: add molecules that show the new behaviour at the end of `TABLES` (IDs are
  global and permanent). Existing rows simply re-render.
- Explanation pages, including "How to use it" when options or input change: the
  generators assert their strings, so a behaviour change fails the
  build. Fix the text and the assert together; the page must explain the new behaviour,
  not just stop failing.

```
python tools/rebuild.py
git diff --stat
```

Every changed page should be explained by step 1. Look at changed pages as screenshots
(`references/site.md`).

## 5. Publish

Commit (user's message rules), show the user, push with their OK, check the Pages build.

## Report

| Document | Change |
|---|---|
| enhanced-stereo/SPEC.md | 1.3: ES-R33, resolved T, open S |
| double-bond-ez/SPEC.md | 0.5: no effect, measured |

plus anything measured but unexplained.
