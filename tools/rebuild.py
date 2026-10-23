"""Rebuild the site: examples pages, explanation pages, landing page.

Usage (from the repo root; RDKit needed; an InChI clone next to this repo):
  python tools/rebuild.py [--inchi ../InChI] [spec ...]

Builds every inchi-1 revision named in tools/site.json once (cached in
~/.cache/inchi-specs/<rev>/inchi-1), checks out site.json 'dataRev' for the
molblocks that tests and fixtures provide, then runs tools/build.py and,
per spec with an explain module, tools/explain.py with that spec's 'new'
binary (INCHI_NEW) and its 'old' one (INCHI_OLD), and renders each workflow
diagram tools/workflow/<table>.json to <key>/workflow.html with archify
(a checkout at ../archify and node; skipped with a note if either is
missing). Prints which generated files changed (git status).

Touches the InChI clone only through 'git fetch' and temporary detached
worktrees (removed again); its checked-out branch and files stay as they are.

  spec  only regenerate these specs' explanation pages (examples and the
        landing page are always rebuilt: molecule IDs are global)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "inchi-specs")
CLI_SOURCE = "INCHI-1-SRC/INCHI_EXE/inchi-1/src"
ARCHIFY = os.path.join(os.path.dirname(ROOT), "archify", "archify", "bin", "archify.mjs")


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def full_rev(inchi, rev):
    return subprocess.run(["git", "-C", inchi, "rev-parse", "--verify", rev + "^{commit}"],
                          check=True, capture_output=True, text=True).stdout.strip()


def worktree(inchi, rev, path):
    """Detached checkout of 'rev' at 'path'."""
    run(["git", "-C", inchi, "worktree", "add", "-f", "--detach", path, rev],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def binary(inchi, rev):
    """Path to inchi-1 built at 'rev', building it on first use."""
    commit = full_rev(inchi, rev)
    exe = os.path.join(CACHE, commit, "inchi-1")
    if os.path.exists(exe):
        return exe

    print(f"building inchi-1 at {rev} ...", file=sys.stderr)
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "src")
        worktree(inchi, commit, src)
        try:
            build = os.path.join(tmp, "build")
            run(["cmake", "-S", os.path.join(src, CLI_SOURCE), "-B", build,
                 "-DCMAKE_BUILD_TYPE=Release"], stdout=subprocess.DEVNULL)
            run(["cmake", "--build", build, "-j", str(os.cpu_count() or 4)],
                stdout=subprocess.DEVNULL)
            os.makedirs(os.path.dirname(exe), exist_ok=True)
            os.replace(os.path.join(build, "bin", "inchi-1"), exe)
        finally:
            run(["git", "-C", inchi, "worktree", "remove", "--force", src])
    return exe


def workflows():
    """Render tools/workflow/<table>.json to the table's feature folder."""
    from molecules import SPEC_OF
    folder = os.path.join(TOOLS, "workflow")
    sources = sorted(f for f in os.listdir(folder) if f.endswith(".json"))
    if not sources:
        return
    if not os.path.exists(ARCHIFY) or shutil.which("node") is None:
        print(f"skipped {len(sources)} workflow diagrams: need node and {ARCHIFY}", file=sys.stderr)
        return
    for source in sources:
        key = SPEC_OF[source[:-len(".json")]][0]
        run(["node", ARCHIFY, "render", "workflow", os.path.join(folder, source),
             os.path.join(ROOT, key, "workflow.html"), "--quality", "showcase"],
            stdout=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inchi", default=os.path.join(os.path.dirname(ROOT), "InChI"))
    ap.add_argument("specs", nargs="*")
    args = ap.parse_args()
    inchi = os.path.abspath(args.inchi)

    site = json.load(open(os.path.join(TOOLS, "site.json")))
    run(["git", "-C", inchi, "fetch", "-q", "origin"])

    # Every revision any spec compares
    revs = {site["dataRev"]}
    for spec in site["specs"]:
        for side in ("old", "new"):
            if side in spec:
                revs.add(spec[side]["rev"])
    bins = {rev: binary(inchi, rev) for rev in sorted(revs)}

    with tempfile.TemporaryDirectory() as tmp:
        # Sources the molecule list reads: InChI at dataRev, this repo
        sources = os.path.join(tmp, "sources")
        os.makedirs(sources)
        worktree(inchi, full_rev(inchi, site["dataRev"]), os.path.join(sources, "InChI"))
        os.symlink(ROOT, os.path.join(sources, "InChI-specs"))
        try:
            env = dict(os.environ, INCHI_BINS=json.dumps(bins), INCHI_SOURCES=sources)

            # Explanation pages first: the landing page links those that exist
            sys.path.insert(0, TOOLS)
            from explain import SPEC_MODULES
            for spec in site["specs"]:
                key = spec["key"]
                if key not in SPEC_MODULES or (args.specs and key not in args.specs):
                    continue
                old = bins[spec["old"]["rev"]] if "old" in spec else ""
                run([sys.executable, os.path.join(TOOLS, "explain.py"), key], cwd=ROOT,
                    env=dict(env, INCHI_NEW=bins[spec["new"]["rev"]], INCHI_OLD=old))

            # Workflow diagrams before the landing page, which links them
            workflows()
            run([sys.executable, os.path.join(TOOLS, "build.py")], cwd=ROOT, env=env,
                stderr=subprocess.DEVNULL)
        finally:
            run(["git", "-C", inchi, "worktree", "remove", "--force",
                 os.path.join(sources, "InChI")])

    run(["git", "-C", ROOT, "status", "--short", "--", "."])


if __name__ == "__main__":
    main()
