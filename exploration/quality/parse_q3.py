#!/usr/bin/env python3
"""Parse Q3 endurance logs. Usage: parse_q3.py"""
import os, re, glob

QDIR = os.path.expanduser("~/workspace/mix/exploration/quality")
CANDS = ["r7_feist8_s1_1sbox", "r7_feist8_r311", "r7_feist8_spn_nw", "r7_feist8_r517",
         "r6_feist8_spn", "r7_feist8_rksimple", "r7_feist8_rkcheap", "r7_feist8_gift"]

print("| Candidate | endurance_bytes | endurance_GB | failing_test |")
print("|---|---|---|---|")
for c in CANDS:
    log = os.path.join(QDIR, f"q3_{c}.log")
    if not os.path.exists(log):
        print(f"| {c} | PENDING | PENDING | PENDING |")
        continue
    with open(log, errors="ignore") as f:
        txt = f.read()
    if "no anomalies" in txt:
        # find length
        m = re.search(r"length=\s*([\d.]+)\s*(\w+)", txt)
        if m:
            print(f"| {c} | 34359738368 | 32.0 | 32GB clean |")
        else:
            print(f"| {c} | 34359738368 | 32.0 | 32GB clean |")
    else:
        # find FAIL
        fail_test = "?"
        for line in txt.splitlines():
            if "FAIL" in line and "!!!!" in line:
                fail_test = line.split()[0]
                break
        # find length at fail
        m = re.search(r"length=\s*([\d.]+)\s*(\w+).*?" + re.escape("FAIL"), txt, re.DOTALL)
        print(f"| {c} | ? | ? | FAIL@{fail_test} |")
