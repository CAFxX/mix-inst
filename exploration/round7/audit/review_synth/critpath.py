"""Trace the critical path of a mapped netlist: report cell-type sequence."""
import re, sys
from collections import Counter

vfile, glib = sys.argv[1], sys.argv[2]
area, delay = {}, {}
cur = None
for line in open(glib):
    line = line.strip()
    m = re.match(r'GATE\s+(\w+)\s+([\d.]+)\s+Y=', line)
    if m:
        cur, area[cur] = m.group(1), float(m.group(2))
        line = line[m.end():]
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
def norm(n): return n.replace('\\', '').replace(' ', '')
def base(n): return n.split('[')[0]
_trivial = re.compile(r"^\\?[A-Za-z_$][\w$]*(\[\d+(:\d+)?\])?$|^1'b[01]$")

top_inputs, top_outputs = [], []
for m in re.finditer(r'^\s*input\s+([^;]+);', text, re.M):
    for d in m.group(1).split(','): top_inputs.extend(expand(d))
for m in re.finditer(r'^\s*output\s+([^;]+);', text, re.M):
    for d in m.group(1).split(','): top_outputs.extend(expand(d))
cells = []
for m in re.finditer(r'^\s*(\w+)\s+_\d+_\s*\((.*?)\);', text, re.M | re.S):
    pins = {p: norm(n) for p, n in re.findall(r'\.(\w+)\(\s*([^),]+?)\s*\)', m.group(2))}
    cells.append((m.group(1), pins))
_live = set()
for _, pins in cells:
    for p, n in pins.items():
        if p != 'Y': _live.add(base(n))
for o in top_outputs: _live.add(base(o))
_alias = {}
for m in re.finditer(r'^\s*assign\s+([^;]+);', text, re.M):
    stmt = m.group(1).strip()
    if '=' not in stmt: continue
    lhs, rhs = (norm(x) for x in stmt.split('=', 1))
    if base(lhs) not in _live: continue
    if _trivial.match(rhs):
        _alias[base(lhs)] = rhs; _alias[lhs] = rhs
    else:
        sys.exit(f"functional assign: {lhs}={rhs}")
def resolve(net):
    seen = set()
    while net in _alias and net not in seen:
        seen.add(net); net = norm(_alias[net])
    return net
driver, cell_in, cell_out = {}, [], []
for idx, (gtype, pins) in enumerate(cells):
    outpin = 'Y' if 'Y' in pins else None
    ins = [resolve(n) for p, n in pins.items() if p != outpin]
    out = resolve(pins.get(outpin)) if outpin else None
    cell_in.append(ins); cell_out.append(out)
    if out: driver[out] = idx
arrival = {n: 0.0 for n in top_inputs}
sys.setrecursionlimit(1000000)
visiting = set()
def arr(net):
    net = resolve(net)
    if net in arrival: return arrival[net]
    if net in ("1'b0", "1'b1") or net not in driver:
        arrival[net] = 0.0; return 0.0
    idx = driver[net]
    if idx in visiting: raise RuntimeError("loop")
    visiting.add(idx)
    t = max([arr(i) for i in cell_in[idx]], default=0.0) + delay.get(cells[idx][0], 1.0)
    visiting.discard(idx); arrival[net] = t; return t
# find worst output, then backtrack
worst, warr = None, -1
for o in top_outputs:
    a = arr(o)
    if a > warr: warr, worst = a, o
path = []
net = resolve(worst)
while net in driver:
    idx = driver[net]
    g = cells[idx][0]
    path.append((g, delay.get(g, 1.0)))
    # step to the input with max arrival
    ins = cell_in[idx]
    net = resolve(max(ins, key=lambda n: arr(n)))
path.reverse()
print(f"worst output: {worst} arrival={warr:.1f}")
print(f"path length: {len(path)} cells")
print("type histogram on crit path:", dict(sorted(Counter(g for g, _ in path).items())))
print("cumulative delay by cell (type:delay):")
cum = 0.0
for g, d in path:
    cum += d
print("  " + " -> ".join(f"{g}({d:g})" for g, d in path))
print(f"total={cum:.1f}")
