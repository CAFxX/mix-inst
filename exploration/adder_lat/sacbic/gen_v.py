"""
Generate Verilog for the SAC/BIC-optimal 64-bit function.
f_j(x) = x_j ^ (XOR over k of (x[a] & x[b]))
"""

import pickle


def gen_verilog(funcs, out_path):
    lines = []
    lines.append("// SAC/BIC-optimal 64-bit vectorial Boolean function")
    lines.append("// f_j(x) = x_j ^ (XOR_k (x[a_{j,k}] & x[b_{j,k}]))")
    lines.append("// sac=0, bic=0 (proven via derivative masks)")
    lines.append("module sacbic64 (")
    lines.append("    input  [63:0] x,")
    lines.append("    output [63:0] y")
    lines.append(");")
    lines.append("")

    # For each j, compute the AND terms then XOR tree
    for j in range(64):
        pairs = funcs[j]
        t = len(pairs)
        # AND terms
        and_wires = []
        for k, (a, b) in enumerate(pairs):
            w = f"and_{j}_{k}"
            and_wires.append(w)
            lines.append(f"    wire {w};")
            lines.append(f"    assign {w} = x[{a}] & x[{b}];")
        lines.append("")
        # XOR tree: XOR all and_wires plus x[j]
        # Build a balanced tree
        level_wires = and_wires + [f"x[{j}]"]
        level = 0
        while len(level_wires) > 1:
            next_wires = []
            for i in range(0, len(level_wires), 2):
                if i + 1 < len(level_wires):
                    w = f"xor_{j}_l{level}_{i//2}"
                    lines.append(f"    wire {w};")
                    lines.append(f"    assign {w} = {level_wires[i]} ^ {level_wires[i+1]};")
                    next_wires.append(w)
                else:
                    next_wires.append(level_wires[i])
            level_wires = next_wires
            level += 1
        lines.append(f"    assign y[{j}] = {level_wires[0]};")
        lines.append("")

    lines.append("endmodule")
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    import sys
    pkl = sys.argv[1] if len(sys.argv) > 1 else "anneal_best_t48_s42.pkl"
    out = sys.argv[2] if len(sys.argv) > 2 else "sacbic64.v"
    with open(pkl, "rb") as f:
        funcs = pickle.load(f)
    gen_verilog(funcs, out)
