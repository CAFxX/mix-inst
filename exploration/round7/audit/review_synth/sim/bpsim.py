"""Independent bit-parallel simulator for the mapped netlist.

Evaluates ALL vectors simultaneously: each net holds a Python int whose
bit i = net value under vector i. Independent of iverilog/yosys/abc.
"""
import re, sys

vfile, vecfile, expfile = sys.argv[1], sys.argv[2], sys.argv[3]

vecs = []
for line in open(vecfile):
    line = line.strip()
    if line:
        v = int(line, 16)
        vecs.append((v >> 64, v & ((1 << 64) - 1)))  # (val, key)
NV = len(vecs)
MASK = (1 << NV) - 1
print(f"vectors: {NV}")

text = open(vfile).read()
def expand(decl):
    m = re.match(r'\[(.*?):(.*?)\]\s*(\w+)', decl)
    if m:
        hi, lo, nm = int(m.group(1)), int(m.group(2)), m.group(3)
        return [f"{nm}[{i}]" for i in range(lo, hi + 1)]
    return [decl.strip()]
def norm(n): return n.replace('\\', '').replace(' ', '')
def base(n): return n.split('[')[0]

top_inputs, top_outputs = [], []
for m in re.finditer(r'^\s*input\s+([^;]+);', text, re.M):
    for d in m.group(1).split(','): top_inputs.extend(expand(d))
for m in re.finditer(r'^\s*output\s+([^;]+);', text, re.M):
    for d in m.group(1).split(','): top_outputs.extend(expand(d))
cells = []
for m in re.finditer(r'^\s*(\w+)\s+_\d+_\s*\((.*?)\);', text, re.M | re.S):
    pins = {p: norm(n) for p, n in re.findall(r'\.(\w+)\(\s*([^),]+?)\s*\)', m.group(2))}
    cells.append((m.group(1), pins))
print(f"cells: {len(cells)}")

# seed input nets
val_of = {}
for b in range(64):
    bit = 0
    for i, (v, k) in enumerate(vecs):
        if (v >> b) & 1: bit |= (1 << i)
    val_of[f"val[{b}]"] = bit
    bit = 0
    for i, (v, k) in enumerate(vecs):
        if (k >> b) & 1: bit |= (1 << i)
    val_of[f"key[{b}]"] = bit

def N(x):
    x = norm(x)
    if x == "1'b0": return 0
    if x == "1'b1": return MASK
    if x not in val_of:
        ev(x)  # recursive, memoized
    return val_of[x]

sys.setrecursionlimit(1000000)
def ev(net):
    if net in val_of: return val_of[net]
    gtype, pins = driver[net]
    Y = pins.get('Y')
    ins = [N(pins[p]) for p in pins if p != 'Y']
    if gtype == 'INV': r = ~ins[0]
    elif gtype == 'BUF': r = ins[0]
    elif gtype == 'AND2': r = ins[0] & ins[1]
    elif gtype == 'AND3': r = ins[0] & ins[1] & ins[2]
    elif gtype == 'AND4': r = ins[0] & ins[1] & ins[2] & ins[3]
    elif gtype == 'NAND2': r = ~(ins[0] & ins[1])
    elif gtype == 'NAND3': r = ~(ins[0] & ins[1] & ins[2])
    elif gtype == 'NAND4': r = ~(ins[0] & ins[1] & ins[2] & ins[3])
    elif gtype == 'OR2': r = ins[0] | ins[1]
    elif gtype == 'OR3': r = ins[0] | ins[1] | ins[2]
    elif gtype == 'OR4': r = ins[0] | ins[1] | ins[2] | ins[3]
    elif gtype == 'NOR2': r = ~(ins[0] | ins[1])
    elif gtype == 'NOR3': r = ~(ins[0] | ins[1] | ins[2])
    elif gtype == 'NOR4': r = ~(ins[0] | ins[1] | ins[2] | ins[3])
    elif gtype == 'XOR2': r = ins[0] ^ ins[1]
    elif gtype == 'XNOR2': r = ~(ins[0] ^ ins[1])
    elif gtype == 'MUX2':
        A = pins['A']; B = pins['B']; S = pins['S']
        a, b, s = N(A), N(B), N(S)
        r = (s & a) | (~s & b)
    elif gtype == 'AOI21':
        a, b, c = N(pins['A']), N(pins['B']), N(pins['C'])
        r = ~((a & b) | c)
    elif gtype == 'OAI21':
        a, b, c = N(pins['A']), N(pins['B']), N(pins['C'])
        r = ~((a | b) & c)
    elif gtype == 'ZERO': r = 0
    elif gtype == 'ONE': r = MASK
    else: raise RuntimeError(f"unknown cell {gtype}")
    r &= MASK
    val_of[net] = r
    return r

driver = {}
for gtype, pins in cells:
    if 'Y' in pins:
        driver[norm(pins['Y'])] = (gtype, pins)

exps = [int(l.strip(), 16) for l in open(expfile) if l.strip()]
assert len(exps) == NV
nmatch = nmis = 0
first_mis = []
for i in range(NV):
    got = 0
    for b in range(64):
        if (ev(f"out[{b}]") >> i) & 1:
            got |= (1 << b)
    if got == exps[i]: nmatch += 1
    else:
        nmis += 1
        if len(first_mis) < 5:
            v, k = vecs[i]
            first_mis.append((i, v, k, got, exps[i]))
print(f"RESULT MATCH={nmatch} MISMATCH={nmis}")
for i, v, k, got, exp in first_mis:
    print(f"MISMATCH i={i} val={v:016x} key={k:016x} got={got:016x} exp={exp:016x}")
