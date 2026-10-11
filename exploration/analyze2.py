"""Hardened cross-check analyzer for ABC-mapped netlists.
Usage: python3 analyze2.py mapped.v mini.genlib

Differences vs analyze.py (which it cross-checks, not replaces):
  - resolves `assign` aliases (x = y, x = 1'b0/1'b1, concatenations of aliases)
  - ERRORS on unknown gate types instead of silently defaulting delay to 1.0
  - topological (Kahn) critical-path computation, no recursion
  - errors on undriven non-input nets
Exit nonzero on any inconsistency.
"""
import re, sys
from collections import Counter, defaultdict, deque

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
assert area and delay, "no gates parsed from genlib"
# Constant-driver cells carry no PIN data in the genlib; their outputs are
# available at time 0 by definition.
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

top_inputs, top_outputs = [], []
for m in re.finditer(r'^\s*input\s+([^;]+);', text, re.M):
    for d in m.group(1).split(','):
        top_inputs.extend(expand(d))
for m in re.finditer(r'^\s*output\s+([^;]+);', text, re.M):
    for d in m.group(1).split(','):
        top_outputs.extend(expand(d))

# assign aliases: map lhs bit -> rhs net (only simple aliases / constants /
# vector-slice pass-throughs like `assign p[2:0] = a[2:0];`). Anything else
# is an error: silent wrong timing is worse than no result.
alias = {}
_slice_re = re.compile(r'^(\w+)\[(\d+):(\d+)\]$')
_idx_re = re.compile(r'^(\w+)\[(\d+)\]$')


_num_re = re.compile(r"^(\d+)'([bBdDhH])([0-9a-fA-F_xXzZ?]+)$")


def _is_dontcare(tok):
    m = _num_re.match(tok)
    return bool(m) and all(c in 'xXzZ?' for c in m.group(3).replace('_', ''))


def _num_bits(tok):
    # Verilog sized literal -> list of 1'b0/1'b1, MSB first
    # (x/z/? treated as 0: ABC only emits these for tied-off bits)
    m = _num_re.match(tok)
    w, base = int(m.group(1)), m.group(2).lower()
    digs = m.group(3).replace('_', '')
    digs = ''.join('0' if c in 'xXzZ?' else c for c in digs)
    v = int(digs, {'b': 2, 'h': 16, 'd': 10}[base]) & ((1 << w) - 1)
    return [f"1'b{(v >> i) & 1}" for i in range(w - 1, -1, -1)]


# declared widths, for expanding plain-net assign targets
widthof = {}


def _note_decl(kind, decls):
    for d in decls.split(','):
        d = d.strip()
        if kind == 'integer':
            widthof[d] = 32
            continue
        m = re.match(r'\[(\d+):(\d+)\]\s*(\w+)$', d)
        if m:
            widthof[m.group(3)] = int(m.group(1)) - int(m.group(2)) + 1
        elif re.fullmatch(r'\w+', d):
            widthof[d] = 1


for m in re.finditer(r'^\s*(wire|input|output|integer|reg)\s+([^;]+);', text, re.M):
    _note_decl(m.group(1), m.group(2))


cells = []
for m in re.finditer(r'^\s*(\w+)\s+_\d+_\s*\((.*?)\);', text, re.M | re.S):
    gtype, conn = m.group(1), m.group(2)
    if gtype not in delay:
        sys.exit(f"ERROR: unknown gate type '{gtype}' (no silent default)")
    pins = dict(re.findall(r'\.(\w+)\(\s*([^),]+?)\s*\)', conn))
    pins = {p: norm(n) for p, n in pins.items()}
    cells.append((gtype, pins))

# nets consumed downstream: cell inputs + top outputs (by base name).
# Assigns to dead wires (e.g. Yosys's unrolled loop temporaries) are skipped;
# assigns with functional RHS on live wires are a hard error below.
_consumed = set()
for _, _pins in cells:
    for _p, _n in _pins.items():
        if _p != 'Y':
            _consumed.add(_n.split('[')[0])
for _o in top_outputs:
    _consumed.add(_o.split('[')[0])


def _lhs_bits(lhs):
    # lhs bits, MSB first
    m = _slice_re.match(lhs)
    if m:
        nm, hi, lo = m.group(1), int(m.group(2)), int(m.group(3))
        return [f"{nm}[{i}]" for i in range(hi, lo - 1, -1)]
    if lhs in widthof and widthof[lhs] > 1:
        w = widthof[lhs]
        return [f"{lhs}[{i}]" for i in range(w - 1, -1, -1)]
    return [lhs]


def _concat_bits(rhs):
    # `{p[5:3],a[2:0]}` -> rhs bits, MSB first
    parts, depth, cur = [], 0, ''
    for ch in rhs[1:-1]:
        if ch == ',' and depth == 0:
            parts.append(cur)
            cur = ''
        else:
            depth += (ch == '{') - (ch == '}')
            cur += ch
    parts.append(cur)
    if depth != 0:
        sys.exit(f"ERROR: unbalanced concat: {rhs}")
    bits = []
    for p in parts:
        p = p.strip()
        if re.fullmatch(r"1'b[01]", p):
            bits.append(p)
        elif _slice_re.match(p):
            m = _slice_re.match(p)
            bits += [f"{m.group(1)}[{i}]" for i in
                     range(int(m.group(2)), int(m.group(3)) - 1, -1)]
        elif _idx_re.match(p) or re.fullmatch(r'\w+', p):
            bits.append(p)
        elif _num_re.match(p):
            bits += _num_bits(p)
        else:
            sys.exit(f"ERROR: unsupported concat element: {p}")
    return bits


for m in re.finditer(r'^\s*assign\s+([^;]+);', text, re.M):
    stmt = m.group(1).strip()
    if '=' not in stmt:
        continue
    lhs, rhs = stmt.split('=', 1)
    lhs, rhs = norm(lhs.strip()), norm(rhs.strip())
    if lhs.startswith('{') and lhs.endswith('}'):
        # concat LHS (e.g. Yosys's `assign { y[63:59], y[8:0] } = ...`):
        # live if ANY member base is consumed downstream.
        _lb = {p.strip().split('[')[0] for p in lhs[1:-1].split(',')}
        if not (_lb & _consumed):
            continue  # dead wire: nothing downstream can observe it
    elif lhs.split('[')[0] not in _consumed:
        continue  # dead wire: nothing downstream can observe it
    if lhs.startswith('{') and lhs.endswith('}'):
        lbits = _concat_bits(lhs)
    else:
        lbits = _lhs_bits(lhs)
    if re.fullmatch(r"1'b[01]", rhs):
        rbits = [rhs] * len(lbits)
    elif _num_re.match(rhs):
        rbits = _num_bits(rhs)
        if len(rbits) != len(lbits):
            if _is_dontcare(rhs):
                rbits = ["1'b0"] * len(lbits)  # tie-off: arrival 0, as before
            else:
                sys.exit(f"ERROR: width mismatch: assign {lhs} = {rhs};")
    elif rhs.startswith('{') and rhs.endswith('}'):
        rbits = _concat_bits(rhs)
    elif _idx_re.match(rhs) or _slice_re.match(rhs) or re.fullmatch(r'\w+', rhs):
        rbits = _lhs_bits(rhs)
    else:
        sys.exit(f"ERROR: functional assign is not mappable logic "
                 f"(netlist not fully mapped?): assign {lhs} = {rhs};")
    if len(lbits) != len(rbits):
        sys.exit(f"ERROR: width mismatch: assign {lhs} = {rhs};")
    for l, r in zip(lbits, rbits):
        alias[l] = r

def resolve(net):
    seen = set()
    while net in alias and net not in seen:
        seen.add(net)
        rhs = alias[net]
        if re.fullmatch(r"1'b[01]", rhs):
            return rhs
        net = norm(rhs)
    return net

# cells were parsed above (before the assign filter); now apply alias
# resolution to their pins.
cells = [(gtype, {p: resolve(n) for p, n in pins.items()})
         for gtype, pins in cells]

driver = {}
for idx, (gtype, pins) in enumerate(cells):
    out = pins.get('Y')
    if out:
        if out in driver:
            sys.exit(f"ERROR: net {out} driven twice")
        driver[out] = idx

# topological arrival times
indeg = [0] * len(cells)
succ = defaultdict(list)
cell_ins = []
for idx, (gtype, pins) in enumerate(cells):
    ins = [n for p, n in pins.items() if p != 'Y']
    cell_ins.append(ins)
    for n in ins:
        if n in ("1'b0", "1'b1"):
            continue
        if n in top_inputs:
            continue
        if n not in driver:
            sys.exit(f"ERROR: undriven net '{n}' into cell {idx} ({gtype})")
        d = driver[n]
        succ[d].append(idx)
        indeg[idx] += 1

arr_cell = [0.0] * len(cells)
q = deque([i for i in range(len(cells)) if indeg[i] == 0])
seen_n = 0
while q:
    i = q.popleft()
    seen_n += 1
    t_in = 0.0
    for n in cell_ins[i]:
        if n in ("1'b0", "1'b1") or n in top_inputs:
            continue
        t_in = max(t_in, arr_cell[driver[n]])
    arr_cell[i] = t_in + delay[cells[i][0]]
    for s in succ[i]:
        indeg[s] -= 1
        if indeg[s] == 0:
            q.append(s)
if seen_n != len(cells):
    sys.exit("ERROR: combinational loop detected")

out_t = []
for o in top_outputs:
    o = resolve(o)
    if o in ("1'b0", "1'b1") or o in top_inputs:
        out_t.append(0.0)
    elif o in driver:
        out_t.append(arr_cell[driver[o]])
    else:
        sys.exit(f"ERROR: undriven top output '{o}'")
crit = max(out_t)
total_area = sum(area[g] for g, _ in cells)
hist = Counter(g for g, _ in cells)
print(f"cells: {len(cells)}  total_area: {total_area:.0f}  critical_path: {crit:.1f} unit-delays")
print("histogram:", dict(sorted(hist.items())))
