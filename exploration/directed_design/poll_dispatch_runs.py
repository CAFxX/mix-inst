#!/usr/bin/env python3
"""Poll CAFxX/fanout dispatch workflow runs for the batch-10 campaigns.
Usage: poll_dispatch_runs.py  (prints matching runs for dd10-batch10-20261010*)
"""
import json
import sys
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

OWNER = "CAFxX"
REPO = "fanout"


def api_get(path):
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "muse-dispatch-poll")
    add_surrogate_to_request(req, "custom.github-pat", allowed_hosts=["api.github.com"])
    return read_json_response(urllib.request.urlopen(req))


def main():
    data = api_get(f"/repos/{OWNER}/{REPO}/actions/workflows/dispatch.yml/runs?per_page=15")
    for r in data.get("workflow_runs", []):
        name = r.get("name", "")
        dn = (r.get("display_title", "") or "")
        if "dd10-batch10" in name or "dd10-batch10" in dn:
            print(f"run {r['id']}: name={name!r} title={dn!r} "
                  f"status={r['status']} conclusion={r['conclusion']} "
                  f"created={r['created_at']} head={r['head_sha'][:8]}")
    print("--- latest 5 dispatch runs (any) ---")
    for r in data.get("workflow_runs", [])[:5]:
        print(f"run {r['id']}: name={r.get('name','')!r} status={r['status']} "
              f"conclusion={r['conclusion']} created={r['created_at']}")


if __name__ == "__main__":
    main()
