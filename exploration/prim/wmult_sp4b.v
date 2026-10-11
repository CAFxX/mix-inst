module wmult_sp4b (input wire [63:0] a, output wire [63:0] p);
  wire [63:0] pp0 = (a << 0);
  wire [63:0] pp1 = (a << 13);
  wire [63:0] pp2 = -(a << 29);
  wire [63:0] pp3 = (a << 48);
  wire [63:0] ws0_0 = pp0 ^ pp1 ^ pp2;
  wire [63:0] wc0_0 = ((pp0 & pp1) | (pp1 & pp2) | (pp0 & pp2)) << 1;
  wire [63:0] ws1_0 = ws0_0 ^ wc0_0 ^ pp3;
  wire [63:0] wc1_0 = ((ws0_0 & wc0_0) | (wc0_0 & pp3) | (ws0_0 & pp3)) << 1;
  assign p = ws1_0 + wc1_0;
endmodule
