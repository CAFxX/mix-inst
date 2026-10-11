#!/usr/bin/env python3
"""def2svg.py — render an OpenROAD routed DEF as an interactive SVG die plot.

Usage:
  def2svg.py <routed.def> <sky130_fd_sc_hd.lef> <ysynth.v> -o layout.svg

What it draws:
  - die outline + standard-cell placements as rectangles, COLORED BY
    FUNCTIONAL BLOCK (see BLOCK ATTRIBUTION below)
  - P-box nets as highlightable polylines (toggle)
  - primary input (val/key) and output (out) nets highlighted (toggle)
  - pan/zoom via embedded JS; legend; wirelength stats

BLOCK ATTRIBUTION (structural netlist analysis on ysynth.v — internal RTL
wire names do not survive yosys+ABC, so attribution is by structure, not name):
  1. KEY  (key schedule):  cell output net's PI-support ⊆ {key[*]}. EXACT.
      (In practice ABC absorbs the constant-XOR key schedule into XNOR2s,
      so this block is usually empty post-mapping; kept for methodology.)
  2. TXOR (round input x^rk): XOR/XNOR cell with EXACTLY ONE input whose
     support ⊆ {key[*]} (the rk side), the other input val-dependent.
  3. SBOX (nonlinear): cell is not XOR/XNOR/INV/BUF (AND/OR/NAND/NOR/AOI/OAI/...
     — only the S-box layer is nonlinear; key schedule, key-XOR, P, L are
     all linear).
  4. LIN  (linear layer): remaining XOR/XNOR cells whose output reaches a
     primary output (or a TXOR) through linear-only cells. An XOR/XNOR that
     fails this test is S-box-internal -> reclassified SBOX.
  5. INV/BUF: inherit the block of their driving cell (PI-driven: by PI).
P-box nets (structural): nets driven by an SBOX cell with at least one
non-SBOX load — i.e. S-outputs leaving the S-box cone. P is wiring-only,
so these nets ARE the permutation's physical wires (ABC fuses many S->L
boundaries; this is the surviving observable subset).
"""
import re, sys, math, argparse, json
from collections import defaultdict

# ---------------------------------------------------------------- LEF
def parse_lef_sizes(path):
    """MACRO name -> (width_um, height_um)."""
    sizes = {}
    cur, w, h = None, None, None
    with open(path) as f:
        for line in f:
            m = re.match(r'\s*MACRO\s+(\S+)', line)
            if m:
                cur, w, h = m.group(1), None, None
                continue
            if cur:
                m = re.match(r'\s*SIZE\s+([\d.]+)\s+BY\s+([\d.]+)', line)
                if m:
                    w, h = float(m.group(1)), float(m.group(2))
                if re.match(r'\s*END\s+' + re.escape(cur), line):
                    if w and h:
                        sizes[cur] = (w, h)
                    cur = None
    return sizes

# ---------------------------------------------------------------- DEF
def parse_def(path):
    """Returns dict with diearea, units_dbu, components, pins, nets."""
    txt = open(path).read()
    d = {}
    m = re.search(r'UNITS\s+DISTANCE\s+MICRONS\s+(\d+)', txt)
    dbu = int(m.group(1)) if m else 1000
    d['dbu'] = dbu
    m = re.search(r'DIEAREA\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)', txt)
    d['diearea'] = tuple(int(m.group(i)) / dbu for i in range(1, 5))
    # components
    comps = {}
    comp_pat = re.compile(r'-\s+(\S+)\s+(\S+)\s+\+\s+(?:[\w\s]+\+\s+)?(?:FIXED|PLACED|COVER|UNPLACED)\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)\s*(\w+)')
    for m in comp_pat.finditer(txt):
        name, cell, x, y, orient = m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), m.group(5)
        comps[name] = {'cell': cell, 'x': x / dbu, 'y': y / dbu, 'orient': orient}
    d['components'] = comps
    # pins (only those with geometry)
    pins = {}
    for m in re.finditer(r'-\s+(\S+)\s+\+\s+NET\s+(\S+)\s+\+\s+DIRECTION\s+(\w+)(.*?);', txt, re.S):
        pname, net, direction, rest = m.group(1), m.group(2), m.group(3), m.group(4)
        layers = re.findall(r'\+\s*LAYER\s+(\w+)\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)', rest)
        pm = re.search(r'\+\s*PLACED\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)', rest)
        if layers and pm:
            pins[pname] = {'net': net, 'dir': direction,
                           'x': int(pm.group(1)) / dbu, 'y': int(pm.group(2)) / dbu}
    d['pins'] = pins
    # nets with routed segments
    nets = {}
    # split NETS section
    ms = re.search(r'^NETS\s+\d+\s*;\n(.*?)^END NETS', txt, re.M | re.S)
    if ms:
        sec = ms.group(1)
        # each net: lines starting with optional whitespace then '- name'
        for nm in re.finditer(r'^\s*-\s+(\S+)(.*?)(?=^\s*-\s+|\Z)', sec, re.M | re.S):
            nname, body = nm.group(1), nm.group(2)
            # routed paths: ( x1 y1 ) ( x2 y2 ) ... after a layer token, or RECT
            segs = []
            # find WIRE/ROUTED sections: look for layer followed by coord runs
            for wm in re.finditer(r'(?:\+?\s*(?:ROUTED|FIXED|COVER|NOSPECIAL)\s+)?(\w+)\s*((?:\(\s*-?\d+\s+-?\d+\s*\)\s*)+)', body):
                layer, coords = wm.group(1), wm.group(2)
                if not layer.startswith('met'):
                    continue
                pts = [(int(x) / dbu, int(y) / dbu)
                       for x, y in re.findall(r'\(\s*(-?\d+)\s+(-?\d+)\s*\)', coords)]
                # extend collinear runs into segments
                for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                    if x1 == x2 and y1 == y2:
                        continue
                    segs.append((layer, x1, y1, x2, y2))
            # also RECT shapes
            for rm in re.finditer(r'RECT\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)\s*\(\s*(-?\d+)\s+(-?\d+)\s*\)', body):
                x1, y1, x2, y2 = (int(rm.group(i)) / dbu for i in range(1, 5))
                segs.append(('rect', x1, y1, x2, y2))
            # connectivity: ( inst pin ) pairs
            conns = re.findall(r'\(\s*(\S+)\s+(\S+)\s*\)', body.split('+')[0])
            nets[nname] = {'segs': segs, 'conns': conns}
    d['nets'] = nets
    return d

# ---------------------------------------------------------------- structural verilog
def parse_struct_verilog(path):
    """Parse flat structural verilog -> (cells, nets).
    cells: name -> {'type': celltype, 'pins': {pin: net}}
    Returns also ports: {'input': [...], 'output': [...]}."""
    txt = open(path).read()
    # strip comments
    txt = re.sub(r'//.*', '', txt)
    cells, ports = {}, {'input': [], 'output': []}
    # module ports from header: module name(a, b, c);
    m = re.search(r'module\s+\w+\s*\(([^)]*)\)', txt)
    port_order = [p.strip() for p in m.group(1).split(',')] if m else []
    for pm in re.finditer(r'input\s+(?:\[(\d+):(\d+)\]\s*)?([\w$]+)\s*;', txt):
        msb, lsb, name = pm.group(1), pm.group(2), pm.group(3)
        if msb is not None:
            for i in range(int(lsb), int(msb) + 1):
                ports['input'].append(f'{name}[{i}]')
        else:
            ports['input'].append(name)
    for pm in re.finditer(r'output\s+(?:\[(\d+):(\d+)\]\s*)?([\w$]+)\s*;', txt):
        msb, lsb, name = pm.group(1), pm.group(2), pm.group(3)
        if msb is not None:
            for i in range(int(lsb), int(msb) + 1):
                ports['output'].append(f'{name}[{i}]')
        else:
            ports['output'].append(name)
    # instances: CELLTYPE instname ( .PIN(net), ... );
    for m in re.finditer(r'(\w+)\s+([\w$\\]+)\s*\((.*?)\)\s*;', txt, re.S):
        ctype, inst, pins = m.group(1), m.group(2), m.group(3)
        if ctype in ('module',):
            continue
        pd = {}
        for p in re.finditer(r'\.\s*(\w+)\s*\(\s*([^)]*?)\s*\)', pins):
            pd[p.group(1)] = p.group(2)
        if pd:
            cells[inst] = {'type': ctype, 'pins': pd}
    return cells, ports

# sky130 output pins by cell (for graph direction)
def out_pins(ctype):
    t = ctype.lower()
    if any(k in t for k in ('inv', 'buf', 'clkbuf')):
        return {'Y'}
    if 'xor' in t or 'xnor' in t:
        return {'Y'}
    # default: assume single output Y (true for all sky130 combinational)
    return {'Y'}

def attribute_blocks(cells, ports):
    """Returns (inst->block, net->driver_inst). Blocks: KEY/TXOR/SBOX/LIN."""
    # net -> driver
    net_driver = {}
    # cell input nets
    cell_inputs = {}
    for inst, c in cells.items():
        outs = out_pins(c['type'])
        for pin, net in c['pins'].items():
            if pin in outs:
                net_driver[net] = inst
        cell_inputs[inst] = [net for pin, net in c['pins'].items() if pin not in outs]
    # PI support as bitmask: val[0..63] -> bits 0..63, key[0..63] -> bits 64..127
    def pi_mask(net):
        m = re.match(r'val\[(\d+)\]$', net)
        if m:
            return 1 << int(m.group(1))
        m = re.match(r'key\[(\d+)\]$', net)
        if m:
            return 1 << (64 + int(m.group(1)))
        return None
    KEYMASK = ((1 << 128) - 1) ^ ((1 << 64) - 1)
    VALMASK = (1 << 64) - 1
    support = {}
    # topological order via simple fixpoint (design is combinational, no loops)
    changed = True
    # seed PIs
    for inst, c in cells.items():
        for pin, net in c['pins'].items():
            pm = pi_mask(net)
            if pm is not None:
                support[net] = pm
    # iterate
    for _ in range(50):
        changed = False
        for inst, c in cells.items():
            ins = cell_inputs[inst]
            if all(n in support for n in ins):
                s = 0
                for n in ins:
                    s |= support[n]
                for pin, net in c['pins'].items():
                    if pin in out_pins(c['type']) and support.get(net) != s:
                        support[net] = s
                        changed = True
        if not changed:
            break
    block = {}
    # pass 1: KEY + cell-type split
    LINEAR = ('xor', 'xnor')
    for inst, c in cells.items():
        t = c['type'].lower()
        outs = [n for p, n in c['pins'].items() if p in out_pins(c['type'])]
        s = 0
        for n in outs:
            s |= support.get(n, 0)
        if s and (s & VALMASK) == 0:
            block[inst] = 'KEY'
        elif any(k in t for k in LINEAR):
            block[inst] = 'XOR?'
        elif any(k in t for k in ('inv',)):
            block[inst] = 'INV?'
        elif 'buf' in t:
            block[inst] = 'INV?'
        else:
            block[inst] = 'SBOX'
    # pass 2: resolve XOR? -> TXOR (one key-only input) or LIN? ; INV? -> inherit
    for inst, c in cells.items():
        if block.get(inst) == 'XOR?':
            ins = cell_inputs[inst]
            keyonly = [n for n in ins if support.get(n, 0) and (support[n] & VALMASK) == 0]
            if len(keyonly) == 1 and len(ins) == 2:
                block[inst] = 'TXOR'
            else:
                block[inst] = 'LIN?'
    # pass 3: LIN? -> LIN if linear-only path to PO or TXOR exists, else SBOX
    # build forward adjacency through linear cells
    fwd = defaultdict(list)
    for inst, c in cells.items():
        for net in cell_inputs[inst]:
            drv = net_driver.get(net)
            if drv:
                fwd[drv].append(inst)
    po_nets = set(ports['output'])
    def reaches_po_or_txor(inst, seen):
        if inst in seen:
            return False
        seen.add(inst)
        for nxt in fwd.get(inst, []):
            b = block.get(nxt)
            if b == 'TXOR':
                return True
            if b in ('LIN?', 'INV?'):
                if reaches_po_or_txor(nxt, seen):
                    return True
            # check if nxt drives a PO net
            for p, n in cells[nxt]['pins'].items():
                if p in out_pins(cells[nxt]['type']) and n in po_nets:
                    return True
        # also: does inst itself drive a PO?
        for p, n in cells[inst]['pins'].items():
            if p in out_pins(cells[inst]['type']) and n in po_nets:
                return True
        return False
    for inst in list(cells):
        if block.get(inst) == 'LIN?':
            block[inst] = 'LIN' if reaches_po_or_txor(inst, set()) else 'SBOX'
    # pass 4: INV? inherit from driver; PI-driven INV/BUF classified by input support
    for _ in range(10):
        done = True
        for inst, c in cells.items():
            if block.get(inst) == 'INV?':
                ins = cell_inputs[inst]
                if not ins:
                    continue
                s = support.get(ins[0], 0)
                if s and (s & VALMASK) == 0:
                    block[inst] = 'KEY'
                    continue
                drv = net_driver.get(ins[0])
                if drv and block.get(drv) not in (None, 'INV?'):
                    block[inst] = block[drv]
                else:
                    done = False
        if done:
            break
    for inst in cells:
        if block.get(inst) in ('INV?', 'XOR?', 'LIN?', None):
            block[inst] = 'SBOX'  # conservative fallback
    # P-box nets (structural): nets driven by an SBOX cell that leave the S-box
    # cone, i.e. have at least one non-SBOX load. P is wiring-only, so these
    # nets ARE the permutation's physical wires. (ABC fuses many S->L
    # boundaries into complex cells; the surviving observable subset is what
    # we highlight. SBOX->SBOX-only nets are S-box-internal.)
    pbox_nets = set()
    for net, drv in net_driver.items():
        if block.get(drv) != 'SBOX':
            continue
        loads = [i for i, c in cells.items()
                 if drv != i and net in cell_inputs[i]]
        if loads and any(block.get(i) != 'SBOX' for i in loads):
            pbox_nets.add(net)
    return block, net_driver, pbox_nets, support

# ---------------------------------------------------------------- SVG
BLOCK_COLORS = {
    'SBOX': '#e8830c',   # orange
    'LIN':  '#2b7fff',   # blue
    'KEY':  '#22a06b',   # green
    'TXOR': '#8b5cf6',   # purple
    'FILL': '#c9ced4',   # light grey (filler/tap/decap)
    'PLAIN': '#6b7280',  # grey (non-SPN design, no block attribution)
}
BLOCK_LABELS = {
    'SBOX': 'S-box layer (nonlinear)',
    'LIN': 'Linear layer L (XOR)',
    'KEY': 'Key schedule',
    'TXOR': 'Round input XOR (x^rk)',
    'FILL': 'Filler / tap / decap',
    'PLAIN': 'Standard cells (no block attribution)',
}

def build_svg(defd, sizes, block, pbox_nets, title, stats):
    da = defd['diearea']
    x0, y0, x1, y1 = da
    W, H = x1 - x0, y1 - y0
    parts = []
    parts.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="#f4f5f7" stroke="#333"/>')
    # cells
    cell_rects = {b: 0 for b in BLOCK_COLORS}
    for name, c in defd['components'].items():
        w, h = sizes.get(c['cell'], (0.5, 3.0))
        # orientation handling (only N/S/E/W flips relevant for rect footprint)
        b = block.get(name, 'FILL')
        if name.startswith(('FILLER_', 'TAP_', 'DECAP_', 'PHY_')):
            b = 'FILL'
        col = BLOCK_COLORS.get(b, '#999')
        cell_rects[b] = cell_rects.get(b, 0) + 1
        # y-flip: DEF y-up -> SVG y-down
        sx, sy = c['x'], y1 - (c['y'] + h)
        parts.append(f'<rect class="cell" data-b="{b}" x="{sx:.3f}" y="{sy:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{col}"/>')
    # nets
    y_top = y1
    def net_path(net, segs):
        d = []
        for s in segs:
            if s[0] == 'rect':
                _, x1, y1_, x2, y2 = s
                yy1, yy2 = y_top - y1_, y_top - y2
                d.append(f'M{x1:.2f},{yy1:.2f}h{x2-x1:.2f}v{yy2-yy1:.2f}h{x1-x2:.2f}Z')
            else:
                _, x1, y1_, x2, y2 = s
                yy1, yy2 = y_top - y1_, y_top - y2
                d.append(f'M{x1:.2f},{yy1:.2f}L{x2:.2f},{yy2:.2f}')
        return ''.join(d)
    # P-box nets group
    ppaths = []
    for n in sorted(pbox_nets):
        nd = defd['nets'].get(n)
        if nd and nd['segs']:
            ppaths.append(f'<path d="{net_path(n, nd["segs"])}" fill="none" stroke="#d40000" stroke-width="0.35" opacity="0.85"/>')
    parts.append(f'<g id="g-pbox" style="display:none">{"".join(ppaths)}</g>')
    # in/out nets
    io_paths = []
    for pname, p in defd['pins'].items():
        nd = defd['nets'].get(p['net'])
        if nd and nd['segs']:
            col = '#00b3b3' if p['dir'] == 'INPUT' else '#c000c0'
            io_paths.append(f'<path d="{net_path(p["net"], nd["segs"])}" fill="none" stroke="{col}" stroke-width="0.3" opacity="0.8"/>')
    parts.append(f'<g id="g-io" style="display:none">{"".join(io_paths)}</g>')
    svg_body = ''.join(parts)
    # legend html
    leg = ''.join(f'<label style="margin-right:12px"><input type="checkbox" data-blk="{b}" checked> '
                  f'<span style="display:inline-block;width:11px;height:11px;background:{BLOCK_COLORS[b]}"></span> '
                  f'{BLOCK_LABELS[b]} ({cell_rects.get(b,0)})</label>' for b in BLOCK_COLORS)
    html = f"""<div style="font-family:system-ui,sans-serif;max-width:1100px;margin:0 auto">
<h3 style="margin:4px 0">{title}</h3>
<div style="font-size:12px;margin:4px 0">
<label style="margin-right:12px"><input type="checkbox" id="t-pbox"> P-box nets ({len(ppaths)})</label>
<label style="margin-right:12px"><input type="checkbox" id="t-io"> In/out wires (val/key/out)</label>
</div>
<div style="font-size:12px;margin:4px 0">{leg}</div>
<div style="font-size:11px;color:#555;margin:4px 0">{stats}</div>
<svg id="die" viewBox="{x0} 0 {W} {H}" style="width:100%;border:1px solid #999;background:#fff;cursor:grab">
{svg_body}
</svg>
<script>
(function(){{
var svg=document.getElementById('die'), vb={{x:{x0},y:0,w:{W},h:{H}}};
function apply(){{svg.setAttribute('viewBox',vb.x+' '+vb.y+' '+vb.w+' '+vb.h);}}
svg.addEventListener('wheel',function(e){{e.preventDefault();var f=e.deltaY>0?1.25:0.8;
var mx=vb.x+vb.w/2,my=vb.y+vb.h/2;vb.w*=f;vb.h*=f;vb.x=mx-vb.w/2;vb.y=my-vb.h/2;apply();}},{{passive:false}});
var drag=null;
svg.addEventListener('mousedown',function(e){{drag={{x:e.clientX,y:e.clientY,vx:vb.x,vy:vb.y}};}});
window.addEventListener('mousemove',function(e){{if(!drag)return;
var r=svg.getBoundingClientRect();vb.x=drag.vx-(e.clientX-drag.x)*vb.w/r.width;
vb.y=drag.vy-(e.clientY-drag.y)*vb.h/r.height;apply();}});
window.addEventListener('mouseup',function(){{drag=null;}});
document.getElementById('t-pbox').addEventListener('change',function(e){{
document.getElementById('g-pbox').style.display=e.target.checked?'inline':'none';}});
document.getElementById('t-io').addEventListener('change',function(e){{
document.getElementById('g-io').style.display=e.target.checked?'inline':'none';}});
document.querySelectorAll('[data-blk]').forEach(function(cb){{
cb.addEventListener('change',function(){{var b=cb.getAttribute('data-blk');
document.querySelectorAll('.cell[data-b="'+b+'"]').forEach(function(r){{
r.style.display=cb.checked?'inline':'none';}});}});}});
}})();
</script>
</div>"""
    return html

def wire_stats(defd, pbox_nets):
    tot = mx = n = 0
    ptot = pmx = pn = 0
    for name, nd in defd['nets'].items():
        L = 0
        for s in nd['segs']:
            if s[0] == 'rect':
                _, x1, y1, x2, y2 = s
                L += abs(x2 - x1) + abs(y2 - y1)
            else:
                _, x1, y1, x2, y2 = s
                L += abs(x2 - x1) + abs(y2 - y1)
        if L > 0:
            n += 1
            tot += L
            mx = max(mx, L)
            if name in pbox_nets:
                pn += 1
                ptot += L
                pmx = max(pmx, L)
    return {'nets': n, 'total_um': tot, 'avg_um': tot / n if n else 0, 'max_um': mx,
            'pbox_nets': pn, 'pbox_total_um': ptot,
            'pbox_avg_um': ptot / pn if pn else 0, 'pbox_max_um': pmx}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('defile')
    ap.add_argument('leffile')
    ap.add_argument('verilog')
    ap.add_argument('-o', required=True)
    ap.add_argument('--title', default='P&R layout')
    ap.add_argument('--plain', action='store_true',
                    help='skip SPN block attribution (non-SPN design); all cells grey')
    a = ap.parse_args()
    print('parsing LEF...', flush=True)
    sizes = parse_lef_sizes(a.leffile)
    print(f'  {len(sizes)} macros', flush=True)
    print('parsing DEF...', flush=True)
    defd = parse_def(a.defile)
    print(f"  {len(defd['components'])} components, {len(defd['nets'])} nets", flush=True)
    print('parsing netlist + attribution...', flush=True)
    cells, ports = parse_struct_verilog(a.verilog)
    if a.plain:
        block = {i: 'PLAIN' for i in cells}
        pbox_nets, net_driver, support = set(), {}, {}
    else:
        block, net_driver, pbox_nets, support = attribute_blocks(cells, ports)
    from collections import Counter
    print('  blocks:', dict(Counter(block.values())), flush=True)
    print('  pbox nets:', len(pbox_nets), flush=True)
    ws = wire_stats(defd, pbox_nets)
    stats = (f"routed wirelength: total {ws['total_um']:.0f} µm over {ws['nets']} nets "
             f"(avg {ws['avg_um']:.2f} µm, max {ws['max_um']:.1f} µm) | "
             f"P-box nets: {ws['pbox_nets']} nets, total {ws['pbox_total_um']:.0f} µm "
             f"(avg {ws['pbox_avg_um']:.2f} µm, max {ws['pbox_max_um']:.1f} µm)")
    print(' ' + stats, flush=True)
    print('emitting SVG...', flush=True)
    html = build_svg(defd, sizes, block, pbox_nets, a.title, stats)
    with open(a.o, 'w') as f:
        f.write('<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>')
        f.write(html)
        f.write('</body></html>')
    print('wrote', a.o, flush=True)
    with open(a.o + '.wirelength.json', 'w') as f:
        json.dump(ws, f, indent=1)

if __name__ == '__main__':
    main()
