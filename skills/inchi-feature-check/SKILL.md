---
name: inchi-feature-check
description: Check that an InChI feature, fix or proposal is complete end to end and create whatever is missing - kick-off documents, whether the information suffices to implement it, datasets, unit tests, the code change, Doxygen comments and user documentation (help text, README, User Guide, API reference), its specification, and its entry on the InChI Specifications site (https://cm-beilstein.github.io/InChI-specs/) with general discussion, old-vs-new examples page and explanation page for chemists. Use whenever the user points at an IUPAC-InChI/InChI issue or PR, or names an InChI feature, and asks to check it, complete it, document it, "put it on the site", add a spec/examples/explanation for it, or whether it is covered or done. Also use when starting work on a new InChI feature. To refresh documents that already exist after a code change, use inchi-feature-update instead.
---

# InChI feature check

Walk one feature through a fixed chain and fill every gap:

```
issue/PR ─▶ kick-off docs + readiness ─▶ datasets ─▶ unit tests ─▶ code ─▶ code + user docs
         ─▶ SPEC.md ─▶ site entry + discussion ─▶ examples ─▶ explanation ─▶ rebuild, verify ─▶ publish
```

Each link depends on the one before: a spec describes code that tests pin; examples and
explanations show what that code outputs. So go in order, and stop to ask the user when a
link needs a decision rather than work (see "When to stop and ask").

Repositories: code and tests in **IUPAC-InChI/InChI** (clone at `../InChI`, relative to
this repo), specs and site in **this repo** (InChI-specs). Read
`references/site.md` before touching the site; it explains the config, the generators and
the rules that keep comment threads and molecule IDs stable.

## 1. Identify the feature

- Read the issue with its comments: `gh issue view <n> -R IUPAC-InChI/InChI --json
  title,body,comments` (the plain `--comments` form fails on this repo with a
  Projects-classic GraphQL error).
  Decisions in the thread are requirements; open questions become spec open issues.
- Find the implementing PRs and branch: `gh pr list -R IUPAC-InChI/InChI --state all
  --search "<n>"`, links in the issue and PR bodies. Note whether they are merged.
- Is the feature already on the site? Search `tools/site.json` for the issue/PR numbers
  and similar titles. If it is, use its `key`. If not, choose a short kebab-case key
  (it becomes the folder name, URL and comment-thread prefix, so it is permanent).
- Run `python tools/audit.py <key>` for the starting state (a new key prints all
  MISSING; that is the expected start).

## 2. Kick-off documents and readiness

Collect what the feature was started from into `docs/<topic>/`: attachments of the issue
and PRs (slides, papers, notes), decks and documents the user provides. Several features
can share a topic (`docs/stereochemistry/` serves specs 1–4). Set `"docs": "<topic>"` in
`tools/site.json` and list each document in the README's "Source documents" with a
one-line summary and a citation tag.

Then judge whether the information suffices to implement the feature:

| Question | Where it usually is |
|---|---|
| Is the problem stated, with an example of today's output? | issue body |
| Is the target behaviour defined, with examples (input → expected InChI/InChIKey)? | issue, slides |
| Are design questions decided, and by whom? | issue thread, meeting notes |
| Is there test data, or can it be made from the examples? | attachments, PR tests |
| Are acceptance criteria clear enough to write gates? | all of the above |
| Is it clear who decides open points? | issue assignees, working group |

Propose a verdict, **ready**, **ready with open points** or **not ready**, with the gaps
as a short list. The user confirms it; only then write it into the spec header
(`| **Readiness** | <verdict> — <gaps, date> |`), where the landing page's "Ready"
column reads it. Not ready: do not implement; list the questions to ask in the issue
thread and continue only with the documents that describe today's behaviour.

## 3. Datasets

`<key>/datasets/` holds the molecules the spec, tests, examples and explanation use;
`<key>/datasets/DATASETS.md` lists each of them (file name or inline molblock/SMILES),
its source (issue, slide, test, paper) and what it shows. Gather them from the issue, its
attachments and the PR's tests; restore what copy-paste breaks (a molfile's blank title
line, `M END` spacing). Link `datasets/DATASETS.md` from the spec (Gates section), and
read example molecules from these files where possible so the three stay in step.
`audit.py` flags dataset files that `DATASETS.md` does not mention.

## 4. Unit tests

Find the tests that pin the behaviour: files the PR touched under `INCHI-1-TEST/`
(`gh pr view <n> --json files`), or grep the test tree for the option, function or
example. Build and run them as described in `references/inchi-build.md`: in a detached
worktree in the scratch folder, never in the user's `../InChI` checkout or build
directories (do not switch their branch).

Missing tests: write them against the behaviour the issue asks for. The test must fail
where the behaviour is missing and pass where it exists: for a bug, fail before the fix
(the user's rule); for a merged feature, fail at the spec's `old` revision and pass at
`new`. Where the tests go is the user's call: on the feature's branch if it is still
open; for merged code, prepare a branch from `dev` in the worktree (or save a patch in
the scratch folder) and ask before pushing or opening a PR.

## 5. Code

Implemented when the change is merged or on a branch and its tests pass. If tests fail or
the behaviour is missing: a bug gets fixed (test first); a feature or a design choice
goes to the user first. A proposal without code is fine: mark it `"status": "proposed"`
and continue with the documents, which then describe today's behaviour and the target.

## 6. Documentation in the code and for users

Code is not done until people can find out how to use it. Run

```
python tools/doc_check.py <key> --option <OptionName>    # once per option the feature adds
```

It compares the spec's `old` and `new` revisions in `../InChI` (git objects only) and
reports:

- **Doxygen.** Every C function the change adds needs a `/** … */` block directly above
  its definition, in the repo's style (`@brief`, `@param`, `@return`). MISSING lines must be
  fixed. Watch for blocks that a later edit separated from their function (a `typedef`
  inserted in between attaches the comment to the typedef). "legacy" lines are old
  functions without docs that the change touched: add one when the change is large.
- **User documentation** of each option at the `new` revision: command-line help
  (`HelpCommandLineParms` in `ichiparm.c`), `README.md` (options section), `INCHI-1-DOC/CHANGELOG.md`,
  User Guide (`INCHI-1-DOC/UserGuide/InChI_UserGuide.md`) and API Reference
  (`INCHI-1-DOC/APIReference/InChI_API_Reference.md`). A feature without an option (like
  versioning) still needs its behaviour described in README, CHANGELOG and User Guide.

Write what is missing in the InChI repo, on the feature's branch (or a docs branch from
`dev` for merged code), in a scratch worktree; ask before pushing. Proposals skip this step.

## 7. Specification

`<key>/SPEC.md`. If missing, create it from `references/spec-template.md`: problem with a
measured example, target behaviour (rules + decisions from the thread, with who decided),
implementation table by function name, requirements with gates (the tests from step 4),
open issues (the undecided points from the thread), worked examples. Measure every string
with a named binary. If it exists, check it matches the current code; if not, follow
inchi-feature-update for the spec.

A proposal gets a spec too: target behaviour, requirements (all ❌ open), planned gates
and the open points. The explanation page is no substitute; it is written for chemists.

Add or update the feature's row in the repo README table. Its "Spec" column is always
`[<key>](<key>/SPEC.md)`, never another page. Its `#` is the spec number
("Spec <n>") and the landing row `#f<n>`. Update the README's molecule-ID range when
examples are added. Mark a gate ✅ only when its test is in the repo and passes; a test
that passes but is not merged yet is 🟡 "not yet in the repo", with where it lives, and a
requirement whose only gate that is stays 🟡 too. The landing page's "Done" column counts
these markers, so they must be true.

## 8. Site entry and discussion

Add the feature to `tools/site.json` (fields in `references/site.md`): title, status,
`old`/`new` revisions (last commit without / first commit with the change; pinned hashes),
options, `inchiKey`/`markVersion` when the feature is about the key or version prefix,
tracking (branch, issues, PRs). Append at the end: row IDs follow the order. Edit the
file by hand in its existing compact style (a `json.dump` rewrite reformats every line).

Then `python tools/new_discussion.py <key>` (asks GitHub; needs `gh` with write access).

## 9. Examples page

A proposal skips this step (`audit.py` says n/a): old vs. new needs a new InChI. Its
explanation page shows today's output instead.

Add a table to `tools/molecules.py`, at the **end** of `TABLES`, and its `SPEC_OF` line.
5–15 molecules: those that show the change, those that must not change, edge cases and
known limitations, each with a title saying which. Prefer molecules from the issue, the
PR's tests and the spec's datasets, so readers recognise them.

Check that each input reproduces the strings the issue or tests quote: SMILES are easy
to get subtly wrong (cisplatin as `N[Pt](N)(Cl)Cl` gives NH2 ligands; the dative
`[NH3]->[Pt](<-[NH3])(Cl)Cl` matches the issue). Molblocks read with `tests=`/`sdf=` come
from site.json `dataRev`, which may predate the feature; copy such molblocks into
`<key>/datasets/` and read them from there.

## 10. Explanation page

`<key>/explain.template.html` plus `tools/explain_<name>.py`, registered in `SPEC_MODULES`
in `tools/explain.py`. Audience: chemists who never read C. Lead with what changes for
them, show measured examples side by side, explain rules in plain words, end with what is
open. Assert every computed string in the generator. `explain.EXE` is the spec's `new`
binary, `explain.OLD_EXE` its `old` one (empty for proposals), for before/after rows.

Every page ends with `<h2 id="use">How to use it</h2>`: what the input must contain and
how to draw it, the command line with its real output (`explain.cli(mol, options, name)`
runs it and returns the block), the same without the option where that shows the
difference, and the library call. A proposal shows what a user sees today. For a proposal, say at the top that
nothing is implemented. One `<h2 id>` per topic: each becomes a comment thread.

## 11. Rebuild and verify

```
python tools/rebuild.py      # needs a Python with RDKit
python tools/audit.py <key>  # every line 'ok'
git diff --stat              # pages of other features unchanged unless intended
```

`rebuild.py` runs `git fetch` and adds temporary detached worktrees in the InChI clone
(removed afterwards); it never changes the checked-out branch or files.

Open the new pages as screenshots (see `references/site.md`) and read them as a chemist
would: wrong pictures, cis/trans or R/S claims and broken links show up there, not in the
diff. Without a headless browser, say so in the report and ask the user to look.

The examples page and landing texts are shared by all features. If a sentence there does
not fit the new feature (e.g. stereo labels on a non-stereo page), fix the generator
(`tools/build.py`) instead of living with it, and check the other pages stay the same.

## 12. Publish

Update the repo `README.md` with the change: the feature's row in the spec table (status,
readiness), "Source documents" for new kick-off documents, and the molecule-ID range.

Commit in this repo (the user's commit-message rules apply), and in `../InChI` if tests or
code were added. The site is public and the repo is mirrored to IUPAC: show the user what
will be published and push only with their OK. After the push, wait for the Pages build
and check the URLs answer.

## When to stop and ask

- The readiness verdict (propose, the user confirms).
- Implementing a feature (not a bug), or any feature that is not ready.
- Choosing between designs.
- Undecided points in the issue thread that the spec would have to settle.
- Anything that renames an existing key, molecule ID or section id (breaks comment threads).
- Pushing, opening PRs, commenting on issues.

## Report

End with one table, one row per link of the chain:

| Step | Found | Done now |
|---|---|---|
| Kick-off documents | slides attached to the issue | saved to `docs/<topic>/` |
| Readiness | — | proposed: ready with open points (A, B) |
| Datasets | 2 molfiles in the issue | `datasets/` + `DATASETS.md` |
| Unit tests | `test_x.cpp` (12 tests, pass) | — |
| Doxygen | 2 new functions without comment | added `/** @brief … */` (branch `x`) |
| User docs | option missing from help and User Guide | added (branch `x`) |
| Specification | missing | created `<key>/SPEC.md` v0.1 |

and the open decisions for the user.
