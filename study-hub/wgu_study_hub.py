#!/usr/bin/env python3
"""
WGU Study Hub — the only file you run.

  python3 wgu_study_hub.py                    web app (opens your browser)
  python3 wgu_study_hub.py --stop             stop a running hub
  python3 wgu_study_hub.py --cli d426         terminal REPL + drills
  python3 wgu_study_hub.py --cli d426 --quiz 10
  python3 wgu_study_hub.py --selftest         validate every course pack
  python3 wgu_study_hub.py --list             show discovered courses

Zero pip installs — Python 3.8+ standard library only. Courses are folders
under courses/; drop a new pack in and it appears on the homepage. Progress
lives in ~/.wgu_study_hub/<course>/ and is shared between web and CLI.

Unofficial personal study tool; not affiliated with or endorsed by WGU.
"""
import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.packs import discover, data_dir_for


def migrate_legacy():
    """One-time move of pre-hub D426 progress (~/.d426_sandbox)."""
    old = os.environ.get("D426_HOME") or os.path.join(
        os.path.expanduser("~"), ".d426_sandbox")
    new = data_dir_for("d426")
    if os.path.isdir(old) and not os.path.exists(new):
        shutil.copytree(old, new)
        print(f"  (migrated your existing D426 progress from {old})")


def stop_running_hub(port):
    """Find a running hub on `port` (or the ports serve() scans up to when
    the first is busy), verify it really is the hub, and ask it to stop."""
    import json
    import urllib.request

    for cand in range(port, port + 20):
        base = f"http://127.0.0.1:{cand}"
        try:
            with urllib.request.urlopen(base + "/api/courses",
                                        timeout=1) as r:
                if "courses" not in json.load(r):
                    continue  # something else lives on this port
        except Exception:
            continue
        try:
            req = urllib.request.Request(
                base + "/api/shutdown", data=b"{}",
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=3) as r:
                r.read()
            print(f"  Stopped the Study Hub on port {cand}. \U0001F989")
            return 0
        except Exception as e:
            print(f"  Found the hub on port {cand} but couldn't stop it "
                  f"({e}).")
            return 1
    print(f"  No running Study Hub found on ports {port}\u2013{port + 19}.")
    print("  (Started it on a custom port? Add --port <n>.)")
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="wgu_study_hub.py",
        description="Local WGU-themed study hub. Web app by default; "
                    "--cli for the terminal.")
    ap.add_argument("--cli", metavar="COURSE", nargs="?", const="",
                    help="terminal interface for a course (extra flags like "
                         "--quiz/--sql/--drill pass through)")
    ap.add_argument("--selftest", metavar="COURSE", nargs="?", const="all",
                    help="validate a course pack (or all) and exit")
    ap.add_argument("--list", action="store_true",
                    help="list discovered courses and exit")
    ap.add_argument("--port", type=int, default=8426,
                    help="web port (default 8426; scans up if busy)")
    ap.add_argument("--stop", action="store_true",
                    help="ask a running hub to shut down (checks --port and "
                         "the ports it scans to when busy)")
    ap.add_argument("--no-browser", action="store_true",
                    help="don't open the browser automatically")
    args, rest = ap.parse_known_args(argv)

    if args.stop:
        return stop_running_hub(args.port)

    packs = discover()
    by_slug = {p.slug: p for p in packs}

    if args.list:
        if not packs:
            print("  (no course packs installed \u2014 unzip a "
                  "<slug>-pack.zip into courses/, or start from "
                  "courses/_template/)")
            return 0
        for p in packs:
            extras = []
            if p.sample_dbs:
                extras.append(f"{len(p.sample_dbs)} dbs")
            if p.has_playground:
                extras.append(p.playground.kind + " playground")
            extras.append(f"{len(p.mcq_generators)} mcq")
            if p.sql_generators:
                extras.append(f"{len(p.sql_generators)} sql")
            if p.study_guide_path:
                extras.append("study guide")
            print(f"  {p.code:<6} {p.name}  ({', '.join(extras)})")
        return 0

    if args.selftest is not None:
        from core.harness import validate_all, validate_pack
        from core.packs import discover as disc
        if args.selftest == "all":
            return 0 if validate_all(disc(include_template=True)) else 1
        p = by_slug.get(args.selftest)
        if not p:
            sys.exit(f"No course '{args.selftest}'. Try --list.")
        print(f"[{p.code}] {p.name}")
        return 0 if validate_pack(p) else 1

    migrate_legacy()

    if args.cli is not None:
        if not packs:
            sys.exit("No course packs installed \u2014 unzip a "
                     "<slug>-pack.zip into courses/ first.")
        from core import cli
        slug = args.cli or packs[0].slug
        p = by_slug.get(slug)
        if not p:
            sys.exit(f"No course '{slug}'. Try --list.")
        return cli.main(p, data_dir_for(p.slug), rest)

    from core.webapp import serve
    serve(packs, port=args.port, open_browser=not args.no_browser)
    return 0


if __name__ == "__main__":
    sys.exit(main())
