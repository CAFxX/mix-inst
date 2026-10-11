// Round 4, family H: keyed 32-bit Murmur-fmix on halves + bijective cross.
// fmix32(h,k): h^=k; h^=h>>16; h*=0x85ebca6b; h^=h>>13; h*=0xc2b2ae35; h^=h>>16.
// CROSS=0 (H1): fmix halves; a^=b^kc; b^=ROTL32(a,9)^kd.
// CROSS=1 (H2): cross; fmix; cross sandwich.
// All rotations are constant part-select concatenations (no variable shifts).
module r4_fmix32h #(parameter CROSS = 0)
    (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    function automatic [31:0] fmix32(input [31:0] h, input [31:0] k);
        reg [31:0] x;
        begin
            x = h ^ k;
            x = x ^ (x >> 16);
            x = x * 32'h85ebca6b;
            x = x ^ (x >> 13);
            x = x * 32'hc2b2ae35;
            x = x ^ (x >> 16);
            fmix32 = x;
        end
    endfunction
    wire [63:0] x0 = val ^ key;
    wire [31:0] ka = key[31:0];
    wire [31:0] kb = key[63:32];
    wire [31:0] kaxb = ka ^ kb;
    wire [31:0] kc0 = {kaxb[28:0], kaxb[31:29]};   // ROTL32(kaxb,3)
    // pre-cross (H2 only; identity for H1)
    wire [31:0] pa = (CROSS == 1) ? (x0[31:0] ^ x0[63:32]) : x0[31:0];
    wire [31:0] pb = (CROSS == 1) ? (x0[63:32] ^ {pa[28:0], pa[31:29]} ^ kc0) : x0[63:32];
    wire [31:0] fa = fmix32(pa, ka);
    wire [31:0] fb = fmix32(pb, kb);
    wire [31:0] kc = {kaxb[24:0], kaxb[31:25]};     // ROTL32(kaxb,7)
    wire [31:0] kd = kc ^ 32'h9E3779B9;
    wire [31:0] qa = fa ^ fb ^ kc;
    wire [31:0] qb = fb ^ {qa[22:0], qa[31:23]} ^ kd;  // ROTL32(qa,9)
    assign out = {qb, qa};
endmodule

// Thin wrappers
module r4_fmix32h_a (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    r4_fmix32h #(.CROSS(0)) u (.val(val), .key(key), .out(out));
endmodule
module r4_fmix32h_b (input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);
    r4_fmix32h #(.CROSS(1)) u (.val(val), .key(key), .out(out));
endmodule
