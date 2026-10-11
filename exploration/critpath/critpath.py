"""critpath.py -- extended critical-path attribution for ABC-mapped netlists.

Extends exploration/round7/audit/review_synth/critpath.py ("trace the critical
path: report cell-type sequence") with:
  * top-K DISTINCT critical paths (backtraced from top outputs by arrival),
  * per-path segmentation into NONLIN (S-box/chi DNF logic) vs XORLIN
    (linear layers / key schedule) vs BUF,
  * near-critical diversity metrics (distinct start/end bits, input-side and
    output-side funnels),
  * approximate round attribution (path split into N equal-delay segments).

Parser copied from ~/workspace/mix/synth/analyze.py (not imported): same
arrival-time algorithm, same strictness about functional assigns.

Usage:
  python3 critpath.py mapped.v mini.genlib [--topk 10] [--rounds N]
                    [--name NAME] [--json out.json]
"""
import re, sys, json, argparse
from collections import Counter

# ---------------------------------------------------------------- parser (copied)
def parse_netlist(vfile, glib):
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

    def norm(n):
        return n.replace('\\', '').replace(' ', '')

    def base(n):
        return n.split('[')[0]

    _trivial_rhs = re.compile(r"^\\?[A-Za-z_$][\w$]*(\[\d+(:\d+)?\])?$|^1'b[01]$")

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
        pins = {p: norm(n) for p, n in pins.items()}
        cells.append((gtype, pins))

    _live = set()
    for _, pins in cells:
        for p, n in pins.items():
            if p != 'Y':
                _live.add(base(n))
    for o in top_outputs:
        _live.add(base(o))

    _alias = {}
    for m in re.finditer(r'^\s*assign\s+([^;]+);', text, re.M):
        stmt = m.group(1).strip()
        if '=' not in stmt:
            continue
        lhs, rhs = (norm(x) for x in stmt.split('=', 1))
        if base(lhs) not in _live:
            continue
        if _trivial_rhs.match(rhs):
            _alias[base(lhs)] = rhs
            _alias[lhs] = rhs
        else:
            sys.exit(f"ERROR: functional assign drives live net: assign {lhs} = {rhs}; "
                     f"-- netlist is not fully mapped")

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

    return {
        'area': area, 'delay': delay, 'cells': cells,
        'top_inputs': top_inputs, 'top_outputs': top_outputs,
        'driver': driver, 'cell_in': cell_in, 'cell_out': cell_out,
        'resolve': resolve,
    }

# ---------------------------------------------------------------- arrival times
def compute_arrivals(nl):
    cells, delay = nl['cells'], nl['delay']
    driver, cell_in, resolve = nl['driver'], nl['cell_in'], nl['resolve']
    arrival = {n: 0.0 for n in nl['top_inputs']}
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

    for o in nl['top_outputs']:
        arr(o)
    return arrival, arr

# ---------------------------------------------------------------- cell classes
NONLIN = {'AND2', 'AND3', 'AND4', 'OR2', 'OR3', 'OR4',
          'NAND2', 'NAND3', 'NAND4', 'NOR2', 'NOR3', 'NOR4',
          'INV', 'AOI21', 'OAI21', 'MUX2'}
XORLIN = {'XOR2', 'XNOR2'}
BUF = {'BUF'}

def cell_class(gtype):
    if gtype in NONLIN:
        return 'NONLIN'
    if gtype in XORLIN:
        return 'XORLIN'
    if gtype in BUF:
        return 'BUF'
    return 'OTHER:' + gtype

# ---------------------------------------------------------------- path backtrace
def backtrace(nl, arrival, out_net):
    """Backtrace one max-arrival path from out_net to a top input.
    Returns list of (gtype, delay, out_net_of_cell) input->output order,
    plus the start input bit."""
    cells, delay = nl['cells'], nl['delay']
    driver, cell_in, resolve = nl['driver'], nl['cell_in'], nl['resolve']
    path = []
    net = resolve(out_net)
    in_bit = net
    while net in driver:
        idx = driver[net]
        g = cells[idx][0]
        path.append((g, delay.get(g, 1.0), net))
        ins = cell_in[idx]
        # step to the input net with max arrival
        net = resolve(max(ins, key=lambda n: arrival.get(resolve(n), 0.0)))
        in_bit = net
    path.reverse()
    return path, in_bit

def topk_paths(nl, arrival, K):
    """Backtrace from top outputs by arrival desc; dedupe by
    (start input bit, cell-type sequence); return top K distinct."""
    seen = set()
    paths = []
    outs = sorted(nl['top_outputs'], key=lambda o: arrival.get(nl['resolve'](o), 0.0),
                  reverse=True)
    for o in outs:
        o = nl['resolve'](o)
        dly = arrival.get(o, 0.0)
        path, in_bit = backtrace(nl, arrival, o)
        sig = (in_bit, tuple(g for g, _, _ in path))
        if sig in seen:
            continue
        seen.add(sig)
        paths.append({'out': o, 'delay': dly, 'in': in_bit, 'path': path})
        if len(paths) >= K:
            break
    return paths

# ---------------------------------------------------------------- analysis
def analyze_path(p, rounds=None):
    gates = p['path']
    total = sum(d for _, d, _ in gates)
    cls = Counter()
    cls_d = Counter()
    for g, d, _ in gates:
        c = cell_class(g)
        cls[c] += 1
        cls_d[c] += d
    rec = {
        'out_bit': p['out'], 'in_bit': p['in'], 'delay': round(total, 1),
        'levels': len(gates),
        'nonlin_levels': cls.get('NONLIN', 0),
        'xorlin_levels': cls.get('XORLIN', 0),
        'buf_levels': cls.get('BUF', 0),
        'nonlin_delay': round(cls_d.get('NONLIN', 0.0), 1),
        'xorlin_delay': round(cls_d.get('XORLIN', 0.0), 1),
        'gate_types': [g for g, _, _ in gates],
        'gate_hist': dict(sorted(Counter(g for g, _, _ in gates).items())),
    }
    if rounds:
        # approximate round attribution: split path into N equal-delay segments
        seg_target = total / rounds
        segs, cur, cur_d, r = [], [], 0.0, 1
        for g, d, _ in gates:
            cur.append(g)
            cur_d += d
            if cur_d >= seg_target and r < rounds:
                segs.append({'round': r, 'levels': len(cur),
                             'delay': round(cur_d, 1),
                             'nonlin': sum(1 for x in cur if cell_class(x) == 'NONLIN'),
                             'xorlin': sum(1 for x in cur if cell_class(x) == 'XORLIN')})
                cur, cur_d, r = [], 0.0, r + 1
        segs.append({'round': r, 'levels': len(cur), 'delay': round(cur_d, 1),
                     'nonlin': sum(1 for x in cur if cell_class(x) == 'NONLIN'),
                     'xorlin': sum(1 for x in cur if cell_class(x) == 'XORLIN')})
        rec['round_segments_approx'] = segs
    return rec

def diversity(paths):
    """Near-critical diversity: distinct start/end bits, funnels."""
    ins = [p['in'] for p in paths]
    outs = [p['out'] for p in paths]
    seqs = [[g for g, _, _ in p['path']] for p in paths]
    # output-side funnel: longest common SUFFIX (from output end)
    lcsuf = 0
    if seqs:
        for tup in zip(*[s[::-1] for s in seqs]):
            if len(set(tup)) == 1:
                lcsuf += 1
            else:
                break
    # input-side funnel: longest common PREFIX (from input end)
    lcpre = 0
    if seqs:
        for tup in zip(*seqs):
            if len(set(tup)) == 1:
                lcpre += 1
            else:
                break
    dlys = [p['delay'] for p in paths]
    return {
        'n_paths': len(paths),
        'distinct_in_bits': len(set(ins)),
        'distinct_out_bits': len(set(outs)),
        'common_suffix_levels': lcsuf,   # shared tail near outputs
        'common_prefix_levels': lcpre,   # shared head near inputs
        'delay_spread': round(max(dlys) - min(dlys), 1) if dlys else 0.0,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mapped')
    ap.add_argument('genlib')
    ap.add_argument('--topk', type=int, default=10)
    ap.add_argument('--rounds', type=int, default=0)
    ap.add_argument('--name', default='')
    ap.add_argument('--json', default='')
    args = ap.parse_args()

    nl = parse_netlist(args.mapped, args.genlib)
    arrival, _ = compute_arrivals(nl)
    crit = max(arrival.get(nl['resolve'](o), 0.0) for o in nl['top_outputs'])
    paths = topk_paths(nl, arrival, args.topk)
    analyzed = [analyze_path(p, rounds=args.rounds or None) for p in paths]
    div = diversity(paths)
    hist = Counter(g for g, _ in nl['cells'])

    result = {
        'name': args.name or args.mapped,
        'crit': round(crit, 1),
        'cells': len(nl['cells']),
        'cell_histogram': dict(sorted(hist.items())),
        'topk': analyzed,
        'diversity': div,
    }
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(result, f, indent=1)

    # human-readable summary
    print(f"=== {result['name']}: crit={result['crit']:.1f}u, cells={result['cells']} ===")
    for i, a in enumerate(analyzed):
        print(f"path#{i}: {a['in_bit']} -> {a['out_bit']}  "
              f"{a['delay']:.1f}u  levels={a['levels']} "
              f"(NONLIN {a['nonlin_levels']}/{a['nonlin_delay']:.1f}u, "
              f"XORLIN {a['xorlin_levels']}/{a['xorlin_delay']:.1f}u, "
              f"BUF {a['buf_levels']})")
    print(f"diversity: in_bits={div['distinct_in_bits']} out_bits={div['distinct_out_bits']} "
          f"common_suffix={div['common_suffix_levels']} common_prefix={div['common_prefix_levels']} "
          f"delay_spread={div['delay_spread']:.1f}u")
    if analyzed:
        a = analyzed[0]
        print("crit path gate sequence:")
        print("  " + " -> ".join(a['gate_types']))
        if 'round_segments_approx' in a:
            print("round segments (approx, equal-delay split):")
            for s in a['round_segments_approx']:
                print(f"  round {s['round']}: {s['delay']:.1f}u "
                      f"levels={s['levels']} (NONLIN {s['nonlin']}, XORLIN {s['xorlin']})")

if __name__ == '__main__':
    main()
