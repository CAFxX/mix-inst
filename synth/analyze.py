"""Analyze ABC-mapped netlist: total cell area + critical path (unit delays).
Usage: python3 analyze.py mapped.v mini.genlib

STRICTNESS: a fully-mapped netlist must contain no functional `assign`
statements. Any assign whose LHS net is consumed downstream (by a cell or a
top output) and whose RHS is not a trivial net alias is a HARD ERROR --
treating assign-driven nets as zero-delay inputs silently undercounts the
critical path (this once reported 8.9u for a design whose true delay was
86.5u). Dead assigns (unconsumed LHS) are ignored.
"""
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
        line = line[m.end():]  # PIN data follows on the same line
    m = re.match(r'.*?PIN \* \w+ \d+ \d+ ([\d.]+) \d+ ([\d.]+) \d+', line)
    if m and cur:
        delay[cur] = max(float(m.group(1)), float(m.group(2)))
# Constant-driver cells carry no PIN data in the genlib; their outputs are
# available at time 0 by definition (a silent 1.0 default would be wrong).
delay["ZERO"] = 0.0
delay["ONE"] = 0.0

text = open(vfile).read()

def expand(decl):
    m = re.match(r'\[(.*?):(.*?)\]\s*(\w+)', decl)
    if m:
        hi, lo, nm = int(m.group(1)), int(m.group(2)), m.group(3)
        return [f"{nm}[{i}]" for i in range(lo, hi + 1)]
    return [decl.strip()]

def norm(n):
    return n.replace('\\', '').replace(' ', '')

def base(n):
    return n.split('[')[0]

# A trivial RHS is a plain net/slice alias, a 1-bit constant, or a sized
# Verilog constant (e.g. 29'h00000000 -- Yosys's tie-off for zero-padded
# outputs). Sized constants are pure tie-offs: they contain no logic, so they
# cannot hide the memory_map/techmap misordering this guard exists to catch.
_trivial_rhs = re.compile(
    r"^\\?[A-Za-z_$][\w$]*(\[\d+(:\d+)?\])?$"
    r"|^1'b[01]$"
    r"|^\d+'[bB][01_]+$|^\d+'[hH][0-9a-fA-F_]+$|^\d+'[dD][0-9_]+$"
)

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
    pins = {p: norm(n) for p, n in pins.items()}
    cells.append((gtype, pins))

# nets consumed downstream (cell inputs + top outputs)
_live = set()
for _, pins in cells:
    for p, n in pins.items():
        if p != 'Y':
            _live.add(base(n))
for o in top_outputs:
    _live.add(base(o))

# validate assigns: functional assign driving a live net is a hard error;
# trivial aliases are resolved; dead assigns are ignored.
_alias = {}
for m in re.finditer(r'^\s*assign\s+([^;]+);', text, re.M):
    stmt = m.group(1).strip()
    if '=' not in stmt:
        continue
    lhs, rhs = (norm(x) for x in stmt.split('=', 1))
    if base(lhs) not in _live:
        continue  # dead wire: ignore
    if _trivial_rhs.match(rhs):
        _alias[base(lhs)] = rhs
        # slice-to-slice alias: record per-bit below if needed; arrival
        # resolution handles whole-net and single-bit forms
        _alias[lhs] = rhs
    else:
        sys.exit(f"ERROR: functional assign drives live net: assign {lhs} = {rhs}; "
                 f"-- netlist is not fully mapped; re-run synthesis with "
                 f"memory_map BEFORE techmap")

def resolve(net):
    seen = set()
    while net in _alias and net not in seen:
        seen.add(net)
        net = norm(_alias[net])
    return net

driver = {}
cell_in, cell_out = [], []
for idx, (gtype, pins) in enumerate(cells):
    outpin = 'Y' if 'Y' in pins else None
    ins = [resolve(n) for p, n in pins.items() if p != outpin]
    out = resolve(pins.get(outpin)) if outpin else None
    cell_in.append(ins)
    cell_out.append(out)
    if out:
        driver[out] = idx

arrival = {n: 0.0 for n in top_inputs}
sys.setrecursionlimit(1000000)
visiting = set()

def arr(net):
    net = resolve(net)
    if net in arrival:
        return arrival[net]
    if net in ("1'b0", "1'b1") or net not in driver:
        arrival[net] = 0.0
        return 0.0
    idx = driver[net]
    if idx in visiting:
        raise RuntimeError("combinational loop!")
    visiting.add(idx)
    t = max([arr(i) for i in cell_in[idx]], default=0.0) + delay.get(cells[idx][0], 1.0)
    visiting.discard(idx)
    arrival[net] = t
    return t

total_area = sum(area.get(g, 0) for g, _ in cells)
crit = max(arr(o) for o in top_outputs)
hist = Counter(g for g, _ in cells)
print(f"cells: {len(cells)}  total_area: {total_area:.0f}  critical_path: {crit:.1f} unit-delays")
print("histogram:", dict(sorted(hist.items())))
