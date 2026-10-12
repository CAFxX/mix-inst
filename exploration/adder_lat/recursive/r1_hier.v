module r1_hier (input [63:0] x, output [63:0] y);
  wire [63:0] s1, s2;
  // Stage 1: out[i] = (in[i]^in[i+1]) ^ (in[i+2]&in[i+3])
  genvar i;
  generate
    for (i = 0; i < 64; i = i + 1) begin : st1
      assign s1[i] = (x[i] ^ x[(i+1)%64]) ^ (x[(i+2)%64] & x[(i+3)%64]);
    end
    // Stage 2: out[i] = (s1[i]^s1[i+16]) ^ (s1[i+32]&s1[i+48])
    for (i = 0; i < 64; i = i + 1) begin : st2
      assign s2[i] = (s1[i] ^ s1[(i+16)%64]) ^ (s1[(i+32)%64] & s1[(i+48)%64]);
    end
    // Stage 3: out[i] = (s2[i]^s2[i+4]) ^ (s2[i+8]&s2[i+12])
    for (i = 0; i < 64; i = i + 1) begin : st3
      assign y[i] = (s2[i] ^ s2[(i+4)%64]) ^ (s2[(i+8)%64] & s2[(i+12)%64]);
    end
  endgenerate
endmodule
