module wmult_sp6a (input wire [63:0] a, output wire [63:0] p);
  wire [63:0] pp0 = (a << 0);
  wire [63:0] pp1 = -(a << 5);
  wire [63:0] pp2 = (a << 13);
  wire [63:0] pp3 = -(a << 27);
  wire [63:0] pp4 = (a << 41);
  wire [63:0] pp5 = (a << 55);
  wire [63:0] ws0_0 = pp0 ^ pp1 ^ pp2;
  wire [63:0] wc0_0 = ((pp0 & pp1) | (pp1 & pp2) | (pp0 & pp2)) << 1;
  wire [63:0] ws0_1 = pp3 ^ pp4 ^ pp5;
  wire [63:0] wc0_1 = ((pp3 & pp4) | (pp4 & pp5) | (pp3 & pp5)) << 1;
  wire [63:0] ws1_0 = ws0_0 ^ wc0_0 ^ ws0_1;
  wire [63:0] wc1_0 = ((ws0_0 & wc0_0) | (wc0_0 & ws0_1) | (ws0_0 & ws0_1)) << 1;
  wire [63:0] ws2_0 = ws1_0 ^ wc1_0 ^ wc0_1;
  wire [63:0] wc2_0 = ((ws1_0 & wc1_0) | (wc1_0 & wc0_1) | (ws1_0 & wc0_1)) << 1;
  assign p = ws2_0 + wc2_0;
endmodule
