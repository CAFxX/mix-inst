"""Generate Verilog for Repair A (bipartite Toffoli) stages.

Stage E (parity 0): even bits are Toffoli targets (controls odd, frozen);
                    odd bits pass through.
Stage O (parity 1): mirror.
Usage: python3 gen_toffoli.py E1a E1b O1a O1b [E2a E2b]
"""
import sys

def verilog(modname, seq):
    lines = [f"module {modname}(input  [63:0] din, output [63:0] dout);"]
    nst = len(seq)
    lines.append("  wire [63:0] s0 = din;")
    for s in range(1, nst):
        lines.append(f"  wire [63:0] s{s};")
    for s, (a, b, p) in enumerate(seq):
        src = f"s{s}"
        dst = "dout" if s == nst - 1 else f"s{s+1}"
        lines.append(f"  // stage {s}: {'even' if p == 0 else 'odd'} targets, offsets ({a},{b})")
        for t in range(64):
            if t % 2 == p:
                lines.append(
                    f"  assign {dst}[{t}] = {src}[{t}] ^ "
                    f"({src}[{(t + a) % 64}] & {src}[{(t + b) % 64}]);"
                )
            else:
                lines.append(f"  assign {dst}[{t}] = {src}[{t}];")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    v = list(map(int, sys.argv[1:]))
    assert len(v) in (4, 6) and all(x % 2 == 1 for x in v), \
        "need 4 or 6 ODD offsets: E1a E1b O1a O1b [E2a E2b]"
    E1, O1 = (v[0], v[1]), (v[2], v[3])
    E2 = (v[4], v[5]) if len(v) == 6 else E1
    cfgs = {
        "toffoli1": [(E1[0], E1[1], 0)],
        "toffoli2": [(E1[0], E1[1], 0), (O1[0], O1[1], 1)],
        "toffoli3": [(E1[0], E1[1], 0), (O1[0], O1[1], 1), (E2[0], E2[1], 0)],
    }
    for name, seq in cfgs.items():
        with open(f"{name}.v", "w") as f:
            f.write(verilog(name, seq))
        print(f"wrote {name}.v  stages={len(seq)} seq={seq}", flush=True)
