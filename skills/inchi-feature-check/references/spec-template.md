# SPEC.md template

The shape every spec in this repo follows. Copy it to `<key>/SPEC.md` and fill it in.
Write for developers. Keep prose short; tables over paragraphs. Every InChI string
in a spec is measured with a named binary (revision + options), never typed from memory.
Code is referenced by function name, not line number (line numbers move).

`<n>` is the feature's row number in the README table (= landing row `#f<n>`).

Pick a 2–4 letter requirement prefix not used yet (`ES-`, `AL-`, `EZ-`, `AT-` are taken;
check `grep -h "Requirement prefix" */SPEC.md`).

```markdown
# Spec <n> — <Feature title>

| | |
|---|---|
| **Doc version** | 0.1 |
| **Date** | <YYYY-MM-DD> |
| **Status** | draft |
| **Author** | <name> |
| **Reviewers** | TBD |
| **Requirement prefix** | `<XX>-` |
| **Readiness** | <ready / ready with open points / not ready> — <gaps>, confirmed <YYYY-MM-DD> |
| **Kick-off documents** | [`docs/<topic>/`](../docs/<topic>/) |
| **Change history** | 0.1 (<YYYY-MM-DD>) — initial spec from <issue/PR>; measured against <rev>. |

> Normative keywords (MUST/SHOULD/MAY) per [RFC 2119](../README.md#requirement-conventions-normative);
> shared glossary and conventions in the [README](../README.md).

## At a glance

- ✅ **Works:** <what is implemented and gated>
- ❌ **Missing:** <requirement IDs not done>
- ▶ **Next:** <the next decision or task>

**Feature:** <one sentence> · **Branch:** `<branch>` · **Sources:** <issue, PR, documents>

---

## 1. Problem

<What goes wrong or is missing today, with a measured example (input → current InChI).>

## 2. Target behaviour

<The rules, numbered. Normative MUSTs. Examples as input → expected InChI/InChIKey.
Decisions taken in the issue thread go here, with who decided and when.>

## 3. Current implementation (branch `<branch>`)

| Stage | Location (function) | State |
|-------|---------------------|-------|
| <parse / normalise / output / key …> | `<file.c>` `<Function>` | ✅ / ❌ / partial |

## 4. Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| <XX>-R1 | <testable statement> | Must / Should / Could | ✅ done + gated (G1) / ❌ open |

### Gates

Molecules and their sources: [datasets/DATASETS.md](datasets/DATASETS.md).

- **G1** — <test file :: test name>: <what it pins>. ✅ passes / ❌ missing.

Test counts: <n> suites / <m> tests (`ctest` in a fresh out-of-tree build).

## 5. Open issues / risks

- **<letter>. <title>.** <what is undecided or broken, who must decide, link to the thread.>

**Resolved in <version>** (kept for traceability):

- ~~**<letter>. <title>.**~~ <what it was, how it was fixed, commit.>

## 6. Assumptions & dependencies

- <other specs, options, data tables, external decisions this relies on>

## 7. Worked examples

| input | <option> | InChI / InChIKey | before |
|---|---|---|---|
```

When a spec changes later, bump **Doc version** (0.1 → 0.2), set **Date**, append to
**Change history** (what changed, why, which commits on which branches), and keep resolved
issues in §5 struck through rather than deleting them.
