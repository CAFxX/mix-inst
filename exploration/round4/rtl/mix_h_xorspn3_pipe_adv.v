// mix_h_xorspn3_pipe_adv: ADVERSARIAL 2-cycle-latency variant.
// Same ports as mix_h_xorspn3_pipe, but an extra register stage makes
// latency exactly 2 cycles. Compiled only to validate that the testbench
// (mix_h_xorspn3_pipe_tb.v, -DADVERSARIAL) detects the latency error.
// NOT for synthesis.
module mix_h_xorspn3_pipe_adv(
  input wire clk,
  input wire [63:0] val,
  input wire [63:0] key,
  input wire valid_in,
  output wire [63:0] out,
  output wire valid_out
);
  reg [63:0] val_q1;
  reg [63:0] key_q1;
  reg valid_q1;
  reg [63:0] out_q;
  reg valid_q2;
  wire [63:0] comb_out;
  r4_h_xorspn3 u_core(.val(val_q1), .key(key_q1), .out(comb_out));
  always @(posedge clk) begin
    val_q1   <= val;
    key_q1   <= key;
    valid_q1 <= valid_in;
    out_q    <= comb_out;
    valid_q2 <= valid_q1;
  end
  assign out       = out_q;
  assign valid_out = valid_q2;
endmodule
