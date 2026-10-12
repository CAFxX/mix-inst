// S5 equivalence: mult64 RTL vs yosys sky130-mapped netlist, N random vectors.
module tb_equiv_mult;
reg [63:0] a, b;
wire [63:0] p_rtl, p_syn;
integer i, seed, mism;
mul64 dut_rtl(.a(a), .b(b), .p(p_rtl));
mul64_synth dut_syn(.a(a), .b(b), .p(p_syn));
initial begin
  seed = 20261004; mism = 0;
  for (i = 0; i < 20000; i = i + 1) begin
    a = {$random(seed), $random(seed)};
    b = {$random(seed), $random(seed)};
    #10;
    if (p_rtl !== p_syn) begin
      mism = mism + 1;
      if (mism < 5) $display("MISMATCH i=%0d a=%h b=%h rtl=%h syn=%h", i, a, b, p_rtl, p_syn);
    end
  end
  if (mism == 0) $display("EQUIV-PASS 20000/20000");
  else $display("EQUIV-FAIL mism=%0d", mism);
  $finish;
end
endmodule
