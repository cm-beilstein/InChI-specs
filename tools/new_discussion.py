"""Create a feature's general discussion, once, and record it.

Usage (from the repo root; gh logged in with write access):
  python tools/new_discussion.py <key>

Creates '<key> · general' in the giscus category of tools/giscus.json, with
the hidden sha1 marker giscus matches in strict mode, so the landing page's
Comment button opens this discussion instead of creating a second one.
Writes its number to giscus.json 'specDiscussions'. Does nothing if the
feature already has one.
"""

import hashlib
import json
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://cm-beilstein.github.io/InChI-specs"
REPO_URL = "https://github.com/cm-beilstein/InChI-specs/blob/main"

sys.path.insert(0, TOOLS)
from comments import spec_term  # noqa: E402

MUTATION = """mutation($r:ID!,$c:ID!,$t:String!,$b:String!){
  createDiscussion(input:{repositoryId:$r,categoryId:$c,title:$t,body:$b}){discussion{number}}}"""


def body(spec, row, issue_url):
    key, title = spec["key"], spec["title"]
    lines = [f"General discussion of **{title}** in InChI.", ""]
    if issue_url:
        lines.append(f"- Issue: {issue_url}")
    lines += [f"- Overview of all features: {SITE_URL}/#f{row}",
              f"- Specification: {REPO_URL}/{key}/SPEC.md", "",
              "Comments on a single molecule or explanation section: use its "
              "**Comment** button on those pages."]
    return "\n".join(lines)


def main(key):
    gpath = os.path.join(TOOLS, "giscus.json")
    giscus = json.load(open(gpath))
    numbers = giscus.setdefault("specDiscussions", {})
    if key in numbers:
        print(f"{key}: already #{numbers[key]}")
        return

    site = json.load(open(os.path.join(TOOLS, "site.json")))
    row, spec = next((i, s) for i, s in enumerate(site["specs"], 1) if s["key"] == key)
    issues = spec["tracking"].get("issues", [])
    issue_url = f'{site["inchiRepo"]}/issues/{issues[0]}' if issues else ""

    term = spec_term(key)
    text = body(spec, row, issue_url) + f"\n\n<!-- sha1: {hashlib.sha1(term.encode()).hexdigest()} -->"
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={MUTATION}",
                          "-f", f"r={giscus['repoId']}", "-f", f"c={giscus['categoryId']}",
                          "-f", f"t={term}", "-f", f"b={text}",
                          "--jq", ".data.createDiscussion.discussion.number"],
                         check=True, capture_output=True, text=True).stdout.strip()

    numbers[key] = int(out)
    open(gpath, "w").write(json.dumps(giscus, indent=2, ensure_ascii=False) + "\n")
    print(f"{key}: created #{out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
