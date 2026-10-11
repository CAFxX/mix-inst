"""Analyze ABC-mapped netlist: total cell area + critical path (unit delays).
Usage: python3 analyze.py mapped.v mini.genlib
"""
import re, sys
from collections import Counter

vfile, glib, FO_K = sys.argv[1], sys.argv[2], float(sys.argv[3])

area, delay = {}, {}
cur = None
for line in open(glib):
    line = line.strip()
    m = re.match(r'GATE\s+(\w+)\s+([\d.]+)\s+Y=', line)
    if m:
        cur, area[cur] = m.group(1), float(m.group(2))
        line = line[m.end():]  # PIN data follows on the same line
    m = re.match(r'.*?PIN \* \w+ \d+ \d+ ([\d.]+) \d+ ([\d.]+) \d+', line)
    if m and cur:
        delay[cur] = max(float(m.group(1)), float(m.group(2)))

text = open(vfile).read()

def expand(decl):
    m = re.match(r'\[(.*?):(.*?)\]\s*(\w+)', decl)
    if m:
        hi, lo, nm = int(m.group(1)), int(m.group(2)), m.group(3)
        return [f"{nm}[{i}]" for i in range(lo, hi + 1)]
    return [decl.strip()]

top_inputs, top_outputs = [], []
for m in re.finditer(r'^\s*input\s+([^;]+);', text, re.M):
    for d in m.group(1).split(','):
        top_inputs.extend(expand(d))
for m in re.finditer(r'^\s*output\s+([^;]+);', text, re.M):
    for d in m.group(1).split(','):
        top_outputs.extend(expand(d))

cells = []
for m in re.finditer(r'^\s*(\w+)\s+_\d+_\s*\((.*?)\);', text, re.M | re.S):
    gtype, conn = m.group(1), m.group(2)
    pins = dict(re.findall(r'\.(\w+)\(\s*([^),]+?)\s*\)', conn))
    # normalize net names: strip backslash-escapes and spaces
    pins = {p: n.replace('\\', '').replace(' ', '') for p, n in pins.items()}
    cells.append((gtype, pins))

driver = {}
from collections import Counter
fanout = Counter()
cell_in, cell_out = [], []
for idx, (gtype, pins) in enumerate(cells):
    outpin = 'Y' if 'Y' in pins else None
    ins = [n for p, n in pins.items() if p != outpin]
    out = pins.get(outpin)
    cell_in.append(ins)
    cell_out.append(out)
    if out:
        driver[out] = idx
for idx, (gtype, pins) in enumerate(cells):
    for p, n in pins.items():
        if p != ('Y' if 'Y' in pins else None):
            fanout[n] += 1

arrival = {n: 0.0 for n in top_inputs}
sys.setrecursionlimit(1000000)
visiting = set()

def arr(net):
    if net in arrival:
        return arrival[net]
    if net in ("1'b0", "1'b1") or net not in driver:
        arrival[net] = 0.0
        return 0.0
    idx = driver[net]
    if idx in visiting:
        raise RuntimeError("combinational loop!")
    visiting.add(idx)
    t = max([arr(i) for i in cell_in[idx]], default=0.0) + delay.get(cells[idx][0], 1.0) + FO_K * fanout.get(net, 0)
    visiting.discard(idx)
    arrival[net] = t
    return t

total_area = sum(area.get(g, 0) for g, _ in cells)
crit = max(arr(o) for o in top_outputs)
hist = Counter(g for g, _ in cells)
print(f"cells: {len(cells)}  total_area: {total_area:.0f}  critical_path: {crit:.1f} unit-delays")
print("histogram:", dict(sorted(hist.items())))
