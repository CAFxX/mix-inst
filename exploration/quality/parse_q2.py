#!/usr/bin/env python3
"""Parse Q2 v2 logs into Table 2. Usage: parse_q2.py"""
import os, re, glob

QDIR = os.path.expanduser("~/workspace/mix/exploration/quality")
CANDS = ["r7_feist8_s1_1sbox", "r7_feist8_r311", "r7_feist8_spn_nw", "r7_feist8_r517",
         "r6_feist8_spn", "r7_feist8_rksimple", "r7_feist8_rkcheap", "r7_feist8_gift"]
SEQS = ["s1", "s8", "s256", "s4k", "s64k", "s4g"]
REDS = ["low8", "low16", "low32", "high32", "xor32", "lemire1e9p7", "mod1e9p7", "mod1000"]
POW2 = {"low8", "low16", "low32", "high32", "xor32"}

def cell_status(cand, seq, red):
    log = os.path.join(QDIR, f"q2_{cand}_{seq}_{red}.log")
    if not os.path.exists(log):
        return "PENDING"
    with open(log, errors="ignore") as f:
        txt = f.read()
    if "no anomalies" in txt:
        return "PASS"
    m = re.search(r"FAIL\s+!+", txt)
    if m:
        # find test name on FAIL line
        for line in txt.splitlines():
            if "FAIL" in line and "!!!!" in line:
                name = line.split()[0]
                return f"FAIL@{name}"
        return "FAIL@?"
    if "anomal" in txt.lower():
        return "SUSPICIOUS"
    return "INCOMPLETE"

print("# Q2 v2 results")
print("\n## Pow2 reductions (low8/low16/low32/high32/xor32 per seq)")
hdr = "| cand | " + " | ".join(SEQS) + " |"
print(hdr)
print("|" + "---|" * (len(SEQS) + 1))
for c in CANDS:
    row = [c]
    for s in SEQS:
        cells = [cell_status(c, s, r) for r in POW2]
        # compress: all PASS -> PASS, else list fails
        if all(x == "PASS" for x in cells):
            row.append("PASS×5")
        else:
            row.append("/".join(cells))
    print("| " + " | ".join(row) + " |")

print("\n## Non-pow2 reductions (lemire1e9p7/mod1e9p7/mod1000 per seq) — artifact, see CONTROL_NOTE.md")
hdr = "| cand | " + " | ".join(SEQS) + " |"
print(hdr)
print("|" + "---|" * (len(SEQS) + 1))
for c in CANDS:
    row = [c]
    for s in SEQS:
        cells = [cell_status(c, s, r) for r in ["lemire1e9p7", "mod1e9p7", "mod1000"]]
        row.append("/".join(cells))
    print("| " + " | ".join(row) + " |")
