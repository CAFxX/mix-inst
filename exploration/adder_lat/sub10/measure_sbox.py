"""Generate 16-parallel 4-bit S-box layer Verilog and measure S0 delay."""
import subprocess, os, sys, re

MIX = "/home/hatch/workspace/mix/exploration"
SUB10 = os.path.join(MIX, "adder_lat/sub10")

# Candidate S-boxes: (name, table as 16 ints)
CANDIDATES = [
    ("present",  [0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2]),
    ("midori0",  [0xC,0xA,0xD,0x3,0xE,0xB,0xF,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6]),
    ("midori1",  [0x1,0x0,0x5,0x3,0xE,0x2,0xF,0x7,0xD,0xA,0x9,0xB,0xC,0x8,0x4,0x6]),
]

# Add 3 from D3 pool (first 3 lines)
with open(os.path.join(MIX, "round24/sbox_pool/S4D3C1_L8U4.txt")) as f:
    for i, line in enumerate(f):
        if i >= 3: break
        line = line.strip().rstrip(',')
        vals = [int(x.strip(), 16) for x in line.split(',') if x.strip()]
        if len(vals) == 16:
            CANDIDATES.append((f"d3_{i}", vals))

VERILOG_TMPL = """// 16x {name} 4-bit S-box
module sbox4_{name}(
    input  [63:0] x,
    output [63:0] y
);
    function [3:0] sbox(input [3:0] a);
        case (a)
{cases}
        endcase
    endfunction
    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin : sb
            assign y[i*4+3:i*4] = sbox(x[i*4+3:i*4]);
        end
    endgenerate
endmodule
"""

def gen_verilog(name, table):
    cases = "\n".join(f"            4'h{v:X}: sbox = 4'h{t:X};" for v, t in enumerate(table))
    return VERILOG_TMPL.format(name=name, cases=cases)

def synth(name, table):
    vpath = os.path.join(SUB10, f"sbox4_{name}.v")
    wdir = os.path.join(SUB10, f"s0_{name}")
    os.makedirs(wdir, exist_ok=True)
    with open(vpath, "w") as f:
        f.write(gen_verilog(name, table))
    r = subprocess.run(
        ["nice", "-n", "10", "python3", os.path.join(MIX, "run_synth.py"),
         vpath, f"sbox4_{name}", wdir],
        capture_output=True, text=True, timeout=300)
    m = re.search(r"DUT \S+: cells=(\d+) area=[\d.]+ crit=([\d.]+)", r.stdout)
    if m:
        return int(m.group(1)), float(m.group(2))
    print(f"FAIL {name}: {r.stdout[-200:]} {r.stderr[-200:]}")
    return None, None

if __name__ == "__main__":
    print(f"{'name':10} {'cells':>6} {'crit':>6}")
    for name, table in CANDIDATES:
        cells, crit = synth(name, table)
        print(f"{name:10} {cells if cells else '-':>6} {crit if crit else '-':>6}")
