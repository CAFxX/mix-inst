// mix_h_xorspn3_pipe: 1-cycle-latency registered pipeline for h_xorspn3.
// Latency model (matches round-3 pipe convention):
//   inputs (val, key, valid_in) are sampled at posedge i;
//   out = h_xorspn3(val_q, key_q) and valid_out = valid_q are visible
//   after posedge i + combinational delay  => exactly 1 cycle latency.
//   Back-to-back inputs therefore give 1 result/cycle after the 1-cycle fill.
// Port convention follows rtl/r3/mix_pipe2_base.v: clk, val, key, valid_in, out, valid_out
// (no rst, same as the round-3 base).
module mix_h_xorspn3_pipe(
  input wire clk,
  input wire [63:0] val,
  input wire [63:0] key,
  input wire valid_in,
  output wire [63:0] out,
  output wire valid_out
);
  // input registers
  reg [63:0] val_q;
  reg [63:0] key_q;
  reg valid_q;
  always @(posedge clk) begin
    val_q   <= val;
    key_q   <= key;
    valid_q <= valid_in;
  end
  // combinational core operates on the registered inputs
  wire [63:0] comb_out;
  r4_h_xorspn3 u_core(.val(val_q), .key(key_q), .out(comb_out));
  // registered-latency outputs: valid 1 cycle after input presentation
  assign out       = comb_out;
  assign valid_out = valid_q;
endmodule
