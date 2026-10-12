// 3-stage hybrid: MUX2 -> 4-term linear -> MUX2 (V4 reconsideration).
// Budget: 2.0 + 5.5 + 2.0 = 9.5u (4-term measured 5.5u, not 2.5u).
// Bit-exact with model_hyb3.py DEFAULT parameters.
module hyb3(
    input  [63:0] v,
    input  [63:0] k,
    output [63:0] y
);
    function [63:0] rotl(input [63:0] x, input integer n);
        begin
            if (n == 0)
                rotl = x;
            else
                rotl = (x << n) | (x >> (64 - n));
        end
    endfunction

    // MUX2 #1: (rs,ra,rb) = (7,23,41). y[i] = s[i] ? b[i] : a[i].
    // (No pre-whiten; key injected at 4-term stage to save depth.)
    wire [63:0] s1 = rotl(v, 7);
    wire [63:0] a1 = rotl(v, 23);
    wire [63:0] b1 = rotl(v, 41);
    wire [63:0] m1;
    genvar i;
    generate
        for (i = 0; i < 64; i = i + 1) begin : mx1
            assign m1[i] = s1[i] ? b1[i] : a1[i];
        end
    endgenerate

    // 4-term linear: (p,q,r,s) = (4,7,17,23), plus key rotl(k,29).
    wire [63:0] rp1 = rotl(m1, 4);
    wire [63:0] rq1 = rotl(m1, 7);
    wire [63:0] rr1 = rotl(m1, 17);
    wire [63:0] rs1 = rotl(m1, 23);
    wire [63:0] t1a = rp1 ^ rq1;
    wire [63:0] t1b = rr1 ^ rs1;
    wire [63:0] t1c = t1a ^ t1b;
    wire [63:0] l1 = m1 ^ t1c ^ rotl(k, 29);

    // MUX2 #2: (rs,ra,rb) = (11,29,47).
    wire [63:0] s2 = rotl(l1, 11);
    wire [63:0] a2 = rotl(l1, 29);
    wire [63:0] b2 = rotl(l1, 47);
    wire [63:0] m2;
    generate
        for (i = 0; i < 64; i = i + 1) begin : mx2
            assign m2[i] = s2[i] ? b2[i] : a2[i];
        end
    endgenerate

    // Output: MUX2 #2 out (no post-whiten; key already injected).
    assign y = m2;
endmodule
