#!/usr/bin/env python3
"""Trace the critical path of an ABC-mapped netlist (mini.genlib).

Usage: python3 critpath.py <mapped.v> [top_n_paths]
Prints the critical path as a gate-type sequence with cumulative delays.
"""
import re
import sys
from collections import defaultdict

vfile = sys.argv[1]
glib = "/home/hatch/workspace/mix/synth/mini.genlib"

delay = {}
cur = None
for line in open(glib):
    line = line.strip()
    m = re.match(r"GATE\s+(\w+)\s+([\d.]+)\s+Y=", line)
    if m:
        cur = m.group(1)
        line = line[m.end():]
    m = re.match(r".*?PIN \* \w+ \d+ \d+ ([\d.]+) \d+ ([\d.]+) \d+", line)
    if m and cur:
        delay[cur] = max(float(m.group(1)), float(m.group(2)))
delay["ZERO"] = 0.0
delay["ONE"] = 0.0

text = open(vfile).read()
# cell instances: GATE_TYPE inst_name (.A(net), .Y(net), ...)
cells = []  # (type, out_net, [in_nets])
for m in re.finditer(r"^\s*(\w+)\s+\\?(\S+?)\s*\((.*?)\);", text, re.M | re.S):
    gtype, pins = m.group(1), m.group(3)
    if gtype not in delay:
        continue
    outs, ins = [], []
    for pm in re.finditer(r"\.(\w+)\s*\(\s*([^)]*?)\s*\)", pins):
        port, net = pm.group(1), pm.group(2).strip()
        net = net.replace("\\", "").replace(" ", "")
        if port == "Y":
            outs.append(net)
        else:
            ins.append(net)
    if outs:
        cells.append((gtype, outs[0], ins))

# top-level inputs: assume nets starting with x[ or named x
# arrival[net] = (time, prev_cell_idx, prev_net)
arrival = defaultdict(lambda: (0.0, None, None))
# seed: nets driven by ZERO/ONE or primary inputs get 0
order = []
changed = True
# topological relaxation (netlist is a DAG)
for _ in range(200):
    changed = False
    for idx, (gtype, out, ins) in enumerate(cells):
        t_in = 0.0
        src = None
        for inn in ins:
            t, _, _ = arrival[inn]
            if t > t_in:
                t_in, src = t, inn
        t_new = t_in + delay[gtype]
        if t_new > arrival[out][0] + 1e-9:
            arrival[out] = (t_new, idx, src)
            changed = True
    if not changed:
        break

# find primary outputs: nets not consumed as inputs
consumed = set()
for _, _, ins in cells:
    consumed.update(ins)
outputs = [(arrival[net][0], net) for _, net, _ in cells
           if net not in consumed]
outputs.sort(reverse=True)
print(f"top output arrival: {outputs[0][0]:.2f} on {outputs[0][1]}")
# backtrack the critical path
path = []
net = outputs[0][1]
while True:
    t, idx, src = arrival[net]
    if idx is None:
        break
    gtype = cells[idx][0]
    path.append((gtype, delay[gtype], t))
    net = src
path.reverse()
print(f"critical path: {len(path)} gates")
seq = []
for gtype, d, t in path:
    seq.append(f"{gtype}({d})")
print(" -> ".join(seq))
from collections import Counter
print("gate mix:", dict(Counter(g for g, _, _ in path)))
