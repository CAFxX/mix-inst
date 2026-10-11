#!/usr/bin/env python3
"""Summarize P&R results from wd_*/timing.rpt, power.rpt, drc.rpt, flow.log."""
import re, os, sys

def parse_wd(wd):
    out = {"wd": wd}
    try:
        t = open(f"{wd}/timing.rpt").read()
        # critical path: "data arrival time" on the max path (units: ns in this lib)
        m = re.findall(r"([\d.]+)\s+data arrival time", t)
        out["crit_ns"] = float(m[0]) if m else None
        m = re.search(r"slack \(VIOLATED\)\s+([-\d.]+)", t)
        out["wns_ns"] = float(m.group(1)) if m else 0.0
        # design area from area.rpt (post.tcl)
        try:
            a = open(f"{wd}/area.rpt").read()
            m = re.search(r"design_area_um2:\s*([\d.]+)", a)
            out["area_um2"] = float(m.group(1)) if m else None
            m = re.search(r"instances:\s*(\d+)", a)
            out["inst"] = int(m.group(1)) if m else None
        except FileNotFoundError:
            pass
    except FileNotFoundError:
        out["error"] = "no timing.rpt"
    try:
        p = open(f"{wd}/power.rpt").read()
        m = re.search(r"^Total\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", p, re.M)
        if m:
            out["power_total_uW"] = float(m.group(1)) * 1e6
            out["power_leak_uW"] = float(m.group(4)) * 1e6
    except FileNotFoundError:
        pass
    try:
        d = open(f"{wd}/drc.rpt").read()
        m = re.search(r"(\d+)\s+violations?\s+found", d)
        out["drc_viol"] = int(m.group(1)) if m else ("clean" if "violation" not in d.lower().split("detailed")[0] else "?")
        # tritonroute summary line
        m = re.search(r"Routed nets:\s*(\d+)", open(f"{wd}/flow.log").read())
        out["routed_nets"] = int(m.group(1)) if m else None
        fl = open(f"{wd}/flow.log").read()
        m = re.search(r"Total\s+\d+\s+\d+\s+[\d.]+\s+(\d+)\s*/\s*(\d+)\s*/\s*(\d+)", fl)
        out["gr_overflow"] = m.groups() if m else None
    except FileNotFoundError:
        pass
    return out

for wd in sys.argv[1:]:
    r = parse_wd(wd)
    print(f"== {r['wd']}")
    for k in ("crit_ns", "wns_ns", "area_um2", "inst", "power_total_uW", "power_leak_uW", "drc_viol", "gr_overflow", "error"):
        if k in r and r[k] is not None:
            print(f"  {k}: {r[k]}")
