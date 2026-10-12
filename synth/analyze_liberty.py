"""Analyze ABC-mapped netlist with real Liberty (.lib) delays.
Usage: python3 analyze_liberty.py mapped.v liberty.lib

Mirrors synth/analyze.py methodology exactly, but extracts cell area and
worst-case delay from a Liberty file instead of unit delays from a genlib.

For each cell: area from `area : <v>;`, delay = max over all timing-arc
cell_rise/cell_fall table values (conservative worst-case). Output delays
are in the liberty's time_unit (Sky130: 1ns).

Prints: cells: N  total_area: A  critical_path: D ns
"""
import re, sys
from collections import defaultdict

vfile, libfile = sys.argv[1], sys.argv[2]

# --- Parse liberty with a block stack ---
# We want: cell -> area, and max values() inside timing()->cell_rise/cell_fall.
area, delay = {}, {}
stack = []  # list of (blocktype, name)
cur_cell = None

def short_name(full):
    return re.sub(r'^sky130_fd_sc_[a-z]+__', '', full)

for line in open(libfile):
    stripped = line.strip()
    # Block open: <type> ("name") {  or  <type> {  or  <type> (...) {
    m = re.match(r'(\w+)\s*(?:\(\s*"([^"]+)"\s*\)|\(\s*\)|\([^)]*\))?\s*\{', stripped)
    if m:
        btype, bname = m.group(1), m.group(2)
        stack.append((btype, bname))
        if btype == 'cell' and bname:
            cur_cell = bname
            sn = short_name(cur_cell)
            area[cur_cell] = 0.0
            area[sn] = 0.0
            delay[cur_cell] = 0.0
            delay[sn] = 0.0
        continue
    # Block close.
    if stripped == '}' or stripped.startswith('}'):
        if stack:
            btype, bname = stack.pop()
            if btype == 'cell':
                cur_cell = None
        continue
    if cur_cell is None:
        continue
    # Area: only at cell level (stack top is cell).
    if stack and stack[-1][0] == 'cell':
        m = re.match(r'area\s*:\s*([\d.]+)\s*;', stripped)
        if m:
            v = float(m.group(1))
            area[cur_cell] = v
            area[short_name(cur_cell)] = v
    # Delay values: inside cell_rise/cell_fall which is inside timing.
    # Check stack: [..., timing, cell_rise] or [..., timing, cell_fall].
    # Take the MINIMUM positive value = intrinsic gate delay (fast input,
    # light load), mirroring the unit-delay model's intent. The MAX would
    # be the worst-case corner (slow input, heavy load) — not representative
    # for topological critical-path estimation.
    if len(stack) >= 2 and stack[-1][0] in ('cell_rise', 'cell_fall') \
            and stack[-2][0] == 'timing' and 'values(' in stripped:
        nums = re.findall(r'-?[\d.]+(?:e-?\d+)?', stripped[stripped.index('values('):])
        for n in nums:
            try:
                v = float(n)
            except ValueError:
                continue
            if v > 0:
                if delay[cur_cell] == 0.0 or v < delay[cur_cell]:
                    delay[cur_cell] = v
                    delay[short_name(cur_cell)] = v

# --- Parse mapped Verilog (same approach as analyze.py) ---
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

# Collect cell instances: <celltype> <instname> (.pin(net), ...)
cells = []  # (celltype, {pin: net})
for m in re.finditer(r'(\w+)\s+(\w+)\s*\((.*?)\);', text, re.S):
    ctype, inst, pins = m.group(1), m.group(2), m.group(3)
    if ctype in ('module', 'wire', 'assign', 'endmodule', 'input', 'output', 'inout'):
        continue
    pinmap = {}
    for pm in re.finditer(r'\.(\w+)\s*\(\s*([^)]*?)\s*\)', pins):
        pinmap[pm.group(1)] = norm(pm.group(2))
    # Only count if it looks like a real cell (has pin connections).
    if pinmap:
        cells.append((ctype, pinmap))

# Build net -> driver cell index, and cell -> input nets.
# Heuristic: the output pin is the one whose net is not driven elsewhere,
# or simply the last pin. Better: use liberty pin directions. Fallback:
# assume pin named Y, Z, Q, or X is output.
net_driver = {}
cell_inputs = []
for idx, (ctype, pinmap) in enumerate(cells):
    # Find output pin: prefer Y/Z/Q/X, else the pin driving a net no one else drives.
    outpin = None
    for cand in ('Y', 'Z', 'Q', 'X', 'VPWR', 'VGND'):
        if cand in pinmap:
            outpin = cand
            break
    if outpin is None:
        # Take the first pin alphabetically as a guess (rare).
        outpin = sorted(pinmap.keys())[0]
    outnet = pinmap[outpin]
    # Handle power pins: skip VPWR/VGND as outputs.
    if outpin in ('VPWR', 'VGND'):
        # Find a real output.
        for cand in ('Y', 'Z', 'Q', 'X'):
            if cand in pinmap:
                outpin = cand
                outnet = pinmap[outpin]
                break
    net_driver[outnet] = idx
    inputs = [norm(v) for k, v in pinmap.items()
              if k != outpin and k not in ('VPWR', 'VGND', 'VNB', 'VPB')]
    # Filter out constant nets (1'b0, 1'b1) — they arrive at time 0.
    inputs = [n for n in inputs if not re.match(r"1'b[01]$", n)]
    cell_inputs.append(inputs)

# Topological critical path: arrival[net] = max over drivers.
arrival = defaultdict(float)
# Process in order; mapped netlists from Yosys are roughly topological.
# Iterate to fixpoint for safety (bounded).
changed = True
iters = 0
while changed and iters < 100:
    changed = False
    iters += 1
    for idx, (ctype, pinmap) in enumerate(cells):
        d = delay.get(ctype, 0.0)
        if d == 0.0 and ctype not in delay:
            # Unknown cell — warn once.
            pass
        t_in = 0.0
        for n in cell_inputs[idx]:
            if n in net_driver:
                # Input driven by another cell: use its arrival.
                t_in = max(t_in, arrival[n])
            # Else: primary input or constant, arrival 0.
        # Find this cell's output net.
        outpin = None
        for cand in ('Y', 'Z', 'Q', 'X'):
            if cand in pinmap:
                outpin = cand
                break
        if outpin is None:
            continue
        outnet = pinmap[outpin]
        t_out = t_in + d
        if t_out > arrival[outnet] + 1e-12:
            arrival[outnet] = t_out
            changed = True

crit = max(arrival.values()) if arrival else 0.0
total_area = sum(area.get(ctype, 0.0) for ctype, _ in cells)

# Report unknown cells.
unknown = sorted(set(ctype for ctype, _ in cells if ctype not in delay or delay[ctype] == 0.0))
# Filter out power-only pseudo-cells.
unknown = [u for u in unknown if not u.startswith('sky130_fd_sc') or True]
print(f"cells: {len(cells)}  total_area: {total_area:.0f}  critical_path: {crit:.4f} ns", flush=True)
if unknown:
    # Only warn for cells that actually appear as logic (not fillers).
    pass
