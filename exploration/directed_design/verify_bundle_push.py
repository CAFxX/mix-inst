#!/usr/bin/env python3
"""Verify batch-10 candidate bundles landed on CAFxX/fanout@main via GitHub API.

Checks projects/mix-sbox-search/battery/candidates/<name>/{impl.c,meta.json,model.py,rtl.v}
exist for each batch-10 candidate. Uses the PAT surrogate credential (read-only GET).
Usage: verify_bundle_push.py
"""
import json
import sys
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

OWNER = "CAFxX"
REPO = "fanout"
NAMES = ["dd10_scsc_linsbox_a", "dd10_scsc_linchi_a", "dd10_sccs_linsbox_a",
         "dd10_scsc_singlerot_a", "dd10_scsc_singlerot_linsbox_a",
         "dd10_scsc_linsbox_rm"]
FILES = ["impl.c", "meta.json", "model.py", "rtl.v"]


def api_get(path):
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "muse-bundle-verify")
    add_surrogate_to_request(req, "custom.github-pat", allowed_hosts=["api.github.com"])
    return read_json_response(urllib.request.urlopen(req))


def main():
    ok = True
    for name in NAMES:
        p = f"projects/mix-sbox-search/battery/candidates/{name}"
        try:
            listing = api_get(f"/repos/{OWNER}/{REPO}/contents/{p}?ref=main")
        except Exception as e:
            print(f"{name}: LISTING FAILED: {e}")
            ok = False
            continue
        have = {e["name"] for e in listing if e["type"] == "file"}
        missing = [f for f in FILES if f not in have]
        if missing:
            print(f"{name}: MISSING {missing} (have {sorted(have)})")
            ok = False
        else:
            # rtl_top gate: meta.json rtl_top must be present
            import base64
            raw = api_get(f"/repos/{OWNER}/{REPO}/contents/{p}/meta.json?ref=main")
            meta = json.loads(base64.b64decode(raw["content"]).decode())
            print(f"{name}: 4/4 files present, rtl_top={meta['rtl_top']}")
    print("BUNDLE VERIFY " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
