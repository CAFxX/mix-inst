"""
Generate 2^18 sequential outputs from sacbic64.v using iverilog,
for Fisher/PractRand testing.
"""

import subprocess
import os

# Write testbench
tb = """
module tb;
    reg [63:0] x;
    wire [63:0] y;
    integer i;
    integer f;
    sacbic64 dut (.x(x), .y(y));
    initial begin
        f = $fopen("seq_outputs.bin", "wb");
        for (i = 0; i < 262144; i = i + 1) begin
            x = i;
            #10;
            $fwrite(f, "%u", y);
        end
        $fclose(f);
        $finish;
    end
endmodule
"""

with open("tb_sacbic.v", "w") as f:
    f.write(tb)

# Compile and run
r = subprocess.run(
    ["iverilog", "-o", "tb_sacbic", "sacbic64.v", "tb_sacbic.v"],
    capture_output=True, text=True, cwd="."
)
if r.returncode != 0:
    print("iverilog compile failed:")
    print(r.stderr[:2000])
else:
    print("Compiled OK")
    r = subprocess.run(
        ["./tb_sacbic"],
        capture_output=True, text=True, timeout=300, cwd="."
    )
    print("Sim done, rc=", r.returncode)
    if os.path.exists("seq_outputs.bin"):
        print("Output size:", os.path.getsize("seq_outputs.bin"))
