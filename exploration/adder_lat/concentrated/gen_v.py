#!/usr/bin/env python3
"""Generate Verilog for concentrated XIG: f_i = x_i XOR g_i."""
import random
random.seed(42)

TERMS = [
    (7,), (6,), (2,),
    (1,2,3,5,6),
    (3,4), (0,5), (1,7), (1,6),
    (1,4,7), (1,5,6), (1,2,4), (0,2,4),
    (0,1,4,5), (4,5,6,7),
]

def build_wiring():
    wiring = []
    for i in range(64):
        low = [b for b in range(6) if b != i]
        random.shuffle(low)
        n_low = 4 if len(low) >= 4 else len(low)
        cand = low[:n_low]
        high = [b for b in range(6, 18) if b != i and b not in cand]
        random.shuffle(high)
        cand.extend(high[:8-len(cand)])
        if len(cand) < 8:
            rest = [b for b in range(64) if b != i and b not in cand]
            random.shuffle(rest)
            cand.extend(rest[:8-len(cand)])
        random.shuffle(cand)
        wiring.append(cand)
    return wiring

WIRING = build_wiring()

def term_verilog(t, inp_names):
    """t: tuple of local indices. inp_names: list of 8 wire names."""
    if len(t) == 1:
        return inp_names[t[0]]
    # Build AND tree
    wires = [inp_names[li] for li in t]
    # Pairwise AND
    lvl = 0
    while len(wires) > 1:
        nxt = []
        for j in range(0, len(wires), 2):
            if j+1 < len(wires):
                wn = f"and_{lvl}_{j//2}"
                nxt.append(wn)
            else:
                nxt.append(wires[j])
        wires = nxt
        lvl += 1
    return wires[0], lvl  # need to emit assigns

# Simpler: emit explicit assigns
lines = ["module conc_xig(input [63:0] x, output [63:0] y);"]
lines.append("  wire [63:0] g;")

for i in range(64):
    w = WIRING[i]
    inps = [f"x[{b}]" for b in w]  # local 0..7 -> w[0..7]
    # For each term, create AND chain
    term_wires = []
    for ti, t in enumerate(TERMS):
        if len(t) == 1:
            term_wires.append(inps[t[0]])
        else:
            # AND tree
            cur = inps[t[0]]
            for li in t[1:]:
                wn = f"  wire g{i}_t{ti}_{li};"
                lines.append(wn)
                lines.append(f"  assign g{i}_t{ti}_{li} = {cur} & {inps[li]};")
                cur = f"g{i}_t{ti}_{li}"
            term_wires.append(cur)
    # XOR all terms
    lines.append(f"  wire g{i}_xor;")
    xor_expr = " ^ ".join(term_wires)
    lines.append(f"  assign g{i}_xor = {xor_expr};")
    lines.append(f"  assign g[{i}] = g{i}_xor;")

lines.append("  assign y = x ^ g;")
lines.append("endmodule")

with open("conc_xig.v", "w") as f:
    f.write("\n".join(lines) + "\n")
print("Wrote conc_xig.v")
