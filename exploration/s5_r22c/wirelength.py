#!/usr/bin/env python3
"""Compute HPWL wirelength stats from placed DEF + structural netlist.
For r22c: also computes P-box net HPWL (structural attribution).
Usage: wirelength.py <placed.def> <ysynth.v> [--plain]
"""
import sys, re, json
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/s5_r22c')
from def2svg import parse_def, parse_struct_verilog, attribute_blocks

def hpwl_stats(def_file, verilog, plain=False):
    defd = parse_def(def_file)
    cells, ports = parse_struct_verilog(verilog)
    if plain:
        pbox_nets = set()
    else:
        _, _, pbox_nets, _ = attribute_blocks(cells, ports)
    # component positions (center)
    # parse LEF sizes quickly from def2svg's parse_lef_sizes
    from def2svg import parse_lef_sizes
    lef = '/home/hatch/.volare/volare/sky130/versions/c6d73a35f524070e85faff4a6a9eef49553ebc2b/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef'
    sizes = parse_lef_sizes(lef)
    pos = {}
    for name, c in defd['components'].items():
        w, h = sizes.get(c['cell'], (1.0, 1.0))
        pos[name] = (c['x'] + w/2, c['y'] + h/2)
    # pin positions (from DEF pins)
    for name, p in defd['pins'].items():
        pos['PIN:'+name] = (p['x'], p['y'])
    # build net -> points from verilog connectivity + def positions
    # map instance -> nets
    from collections import defaultdict
    net_pts = defaultdict(list)
    # instance pins
    for inst, c in cells.items():
        if inst not in pos: continue
        for pin, net in c['pins'].items():
            net_pts[net].append(pos[inst])
    # port nets: add pin positions
    for net in list(net_pts.keys()):
        for pfx, pname in (('val[', None), ('key[', None), ('out[', None)):
            pass
    # add PIN positions for port nets (val[i], key[i], out[i], a[i], b[i], p[i])
    for name, p in defd['pins'].items():
        if name in net_pts:
            net_pts[name].append((p['x'], p['y']))
    tot, n, mx = 0.0, 0, 0.0
    ptot, pn, pmx = 0.0, 0, 0.0
    for net, pts in net_pts.items():
        if len(pts) < 2: continue
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        hpwl = (max(xs)-min(xs)) + (max(ys)-min(ys))
        n += 1; tot += hpwl; mx = max(mx, hpwl)
        if net in pbox_nets:
            pn += 1; ptot += hpwl; pmx = max(pmx, hpwl)
    return {
        'nets': n, 'total_um': round(tot,1), 'avg_um': round(tot/n,2) if n else 0,
        'max_um': round(mx,2),
        'pbox_nets': pn, 'pbox_total_um': round(ptot,1),
        'pbox_avg_um': round(ptot/pn,2) if pn else 0, 'pbox_max_um': round(pmx,2),
    }

if __name__ == '__main__':
    plain = '--plain' in sys.argv
    stats = hpwl_stats(sys.argv[1], sys.argv[2], plain)
    print(json.dumps(stats, indent=2))
