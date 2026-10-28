#!/usr/bin/env python3
"""
Regenerate the GitHub-Pages build from any new editions and push to GitHub.

Runs the repo's own publish.py (the Pages build: relative nav, archive.html
listing, index.html redirect), then commits and pushes. The push triggers the
repo's .github/workflows/pages.yml, which deploys static/blockbuster to Pages.

Safe no-op (exit 0) if the repo isn't initialized.
"""
import os
import re
import subprocess
import sys

REPO_DIR = os.environ.get("BB_REPO_DIR", os.path.expanduser("~/blockbuster"))
SRC_DIR = os.environ.get("BB_SRC_DIR", os.path.expanduser("~"))


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def main():
    if not os.path.isdir(os.path.join(REPO_DIR, ".git")):
        print("git push: repo not initialized at %s — skipping" % REPO_DIR)
        return 0

    # 1. Regenerate the Pages build (copies new editions, shrinks posters,
    #    injects relative nav, rebuilds archive.html + index.html redirect).
    pub = os.path.join(REPO_DIR, "scripts", "publish.py")
    env = dict(os.environ)
    env["BB_SRC_DIR"] = SRC_DIR
    env["BB_STATIC_DIR"] = os.path.join(REPO_DIR, "static", "blockbuster")
    if os.path.exists(pub):
        r = run([sys.executable, pub], env=env, cwd=REPO_DIR)
        for line in (r.stdout or "").splitlines():
            if line.strip():
                print("publish:", line.strip())
        if r.returncode != 0:
            print("publish.py failed:", (r.stderr or "").strip(), file=sys.stderr)
            return 1
    else:
        print("git push: publish.py missing — skipping regen", file=sys.stderr)

    # 2. Commit + push if anything changed.
    git = lambda *a: run(["git", "-C", REPO_DIR, *a])
    if git("add", "-A").returncode != 0:
        print("git push: 'git add' failed", file=sys.stderr)
        return 1

    archive = os.path.join(REPO_DIR, "static", "blockbuster")
    dates = []
    for f in os.listdir(archive):
        m = re.search(r"(\d{4}-\d{2}-\d{2})", f)
        if m and f.startswith("blockbuster_") and f.endswith(".html"):
            dates.append(m.group(1))
    label = max(dates) if dates else "update"
    msg = "Publish Blockbuster edition %s" % label

    r = git("commit", "-m", msg)
    if r.returncode != 0:
        print("git push: nothing to commit")
        return 0

    r = git("push", "origin", "HEAD")
    if r.returncode != 0:
        print("git push FAILED: %s" % (r.stderr or r.stdout).strip(), file=sys.stderr)
        return 1

    print("git push: committed and pushed '%s'" % msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
