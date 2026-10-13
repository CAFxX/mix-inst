// Testbench: mapped netlist (mini.genlib behavioral cells) vs Python model.
`define NV 10
module tb;
  reg [63:0] val, key;
  wire [63:0] out;
  r7_feist8_s1_1sbox dut(.val(val), .key(key), .out(out));
  reg [127:0] vecs [0:`NV-1];
  reg [63:0]  exps [0:`NV-1];
  integer i, nmatch, nmismatch;
  initial begin
    $readmemh("vectors10.hex", vecs);
    $readmemh("expected10.hex", exps);
    nmatch = 0; nmismatch = 0;
    for (i = 0; i < `NV; i = i + 1) begin
      val = vecs[i][127:64]; key = vecs[i][63:0];
      #10;
      if (out === exps[i]) nmatch = nmatch + 1;
      else begin
        nmismatch = nmismatch + 1;
        if (nmismatch <= 10)
          $display("MISMATCH i=%0d val=%h key=%h got=%h exp=%h", i, val, key, out, exps[i]);
      end
    end
    $display("RESULT MATCH=%0d MISMATCH=%0d", nmatch, nmismatch);
    $finish;
  end
endmodule
