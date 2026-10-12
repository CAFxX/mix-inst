// 4-term rotl-xor linear: y = x ^ rotl(x,P) ^ rotl(x,Q) ^ rotl(x,R) ^ rotl(x,S).
// DIFF-clean form from w4term (O134). 4-term XOR tree = 2 XOR levels (~2.5u).
module lin4 #(
    parameter P = 4,
    parameter Q = 7,
    parameter R = 17,
    parameter S = 23
)(
    input  [63:0] x,
    output [63:0] y
);
    function [63:0] rotl(input [63:0] v, input integer n);
        begin
            if (n == 0)
                rotl = v;
            else
                rotl = (v << n) | (v >> (64 - n));
        end
    endfunction

    // 2-level XOR tree: t1=p^q, t2=r^s (level 1); t3=t1^t2 (level 2); y=x^t3.
    // Written flat; abc builds the tree.
    wire [63:0] rp = rotl(x, P);
    wire [63:0] rq = rotl(x, Q);
    wire [63:0] rr = rotl(x, R);
    wire [63:0] rs = rotl(x, S);
    wire [63:0] t1 = rp ^ rq;
    wire [63:0] t2 = rr ^ rs;
    wire [63:0] t3 = t1 ^ t2;
    assign y = x ^ t3;
endmodule
