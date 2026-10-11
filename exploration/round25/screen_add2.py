#!/usr/bin/env python3
"""Screen literature_add2 pool (27 S-boxes) standalone via run_synth.py.
Same emission/flow as screen_broad.py. Ranks by unit-delay."""
import json, os, sys, subprocess

EXP = "/home/hatch/workspace/mix/exploration"
R25 = os.path.join(EXP, "round25")
OUT = os.path.join(R25, "sbox_screen_add2")
sys.path.insert(0, R25)
sys.path.insert(0, os.path.join(R25, "models"))
import gen_r25

pool = json.load(open(os.path.join(R25, 'pool_add2.json')))
os.makedirs(OUT, exist_ok=True)

results = []
for p in pool:
    name = 'add2_' + p['name'].lower()
    sb = p['table']
    lines = [f"module sbox_{name}(input [63:0] x, output [63:0] y);",
             "reg [63:0] y;",
             "always @(*) begin"]
    lines += ["    " + l.strip() for l in gen_r25._v_sbox16_stmts(sb, "x", "y")]
    lines += ["end", "endmodule"]
    vp = os.path.join(OUT, f"sbox_{name}.v")
    with open(vp, "w") as f:
        f.write("\n".join(lines) + "\n")
    wd = os.path.join(OUT, f"synth_{name}")
    os.makedirs(wd, exist_ok=True)
    r = subprocess.run(
        [sys.executable, os.path.join(EXP, "run_synth.py"), vp, f"sbox_{name}", wd],
        capture_output=True, text=True, timeout=600)
    out = r.stdout + r.stderr
    delay = None
    for line in out.split("\n"):
        if line.startswith("RESULT"):
            for tok in line.split():
                if tok.startswith("crit="):
                    delay = float(tok.split("=")[1])
    results.append({'name': p['name'], 'delay': delay,
                    'table': ''.join(f'{v:x}' for v in sb)})
    print(f"{p['name']}: standalone delay = {delay}u", flush=True)

ranked = sorted((r for r in results if r['delay'] is not None), key=lambda r: r['delay'])
json.dump({'all': results, 'ranked': [r['name'] for r in ranked]},
          open(os.path.join(OUT, 'ranked.json'), 'w'), indent=1)
print("\n=== RANKED (add2 pool) ===")
for r in ranked:
    print(f"  {r['delay']:.1f}u  {r['name']}")
