// S5 equivalence: validated RTL vs yosys sky130-mapped netlist, N random vectors.
module tb_equiv;
reg [63:0] val, key;
wire [63:0] out_rtl, out_syn;
integer i, seed, mism;
r22c_spn_mix4r_lp_nw dut_rtl(.val(val), .key(key), .out(out_rtl));
r22c_synth            dut_syn(.val(val), .key(key), .out(out_syn));
initial begin
  seed = 20261004; mism = 0;
  for (i = 0; i < 20000; i = i + 1) begin
    val = {$random(seed), $random(seed)};
    key = {$random(seed), $random(seed)};
    #10;
    if (out_rtl !== out_syn) begin
      mism = mism + 1;
      if (mism < 5) $display("MISMATCH i=%0d val=%h key=%h rtl=%h syn=%h", i, val, key, out_rtl, out_syn);
    end
  end
  if (mism == 0) $display("EQUIV-PASS 20000/20000");
  else $display("EQUIV-FAIL mism=%0d", mism);
  $finish;
end
endmodule
