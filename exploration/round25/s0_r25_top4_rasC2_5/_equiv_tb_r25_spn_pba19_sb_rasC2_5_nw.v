module tb_equiv;
  reg [63:0] in1, in2; wire [63:0] outw;
  r25_spn_pba19_sb_rasC2_5_nw dut(.val(in1), .key(in2), .out(outw));
  reg [63:0] x, y, e; integer f, n, err;
  initial begin
    f = $fopen("/home/hatch/workspace/mix/exploration/round25/s0_r25_top4_rasC2_5/_equiv_vecs_r25_spn_pba19_sb_rasC2_5_nw.txt", "r"); n = 0; err = 0;
    while ($fscanf(f, "%h %h %h", x, y, e) == 3) begin
      in1 = x; in2 = y; #1; n = n + 1;
      if (outw !== e) begin err = err + 1;
        if (err < 5) $display("MISMATCH x=%h y=%h got=%h exp=%h", x, y, outw, e); end
    end
    $display("EQUIV n=%0d err=%0d", n, err); $finish;
  end
endmodule
