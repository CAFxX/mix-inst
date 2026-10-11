// testbench for mix_h_xorspn3_pipe (or mix_h_xorspn3_pipe_adv with -DADVERSARIAL)
// 128 golden vectors (h_xorspn3 scalar model, scalar==numpy cross-checked).
// Checks: (a) equivalence, (b) back-to-back 1/cycle throughput,
// (c) exact 1-cycle latency probe (distinguishes 0/1/2 cycles),
// (d) valid tracking through bubbles and drain (no stale outputs).
`timescale 1ps/1ps
module tb_mix_h_xorspn3_pipe;
  reg clk = 0;
  reg [63:0] val; reg [63:0] key; reg valid_in;
  wire [63:0] out; wire valid_out;
`ifdef ADVERSARIAL
  mix_h_xorspn3_pipe_adv dut(.clk(clk), .val(val), .key(key), .valid_in(valid_in), .out(out), .valid_out(valid_out));
`else
  mix_h_xorspn3_pipe dut(.clk(clk), .val(val), .key(key), .valid_in(valid_in), .out(out), .valid_out(valid_out));
`endif
  always #5 clk = ~clk;
  integer i; integer j; integer errs; integer n_valid;
  reg [63:0] out_hold;
  parameter N = 128;
  reg [63:0] TVAL [0:127];
  reg [63:0] TKEY [0:127];
  reg [63:0] TEXP [0:127];
  initial begin
    TVAL[0] = 64'h0000000000000000; TKEY[0] = 64'h123456789abcdef0; TEXP[0] = 64'h726ecd2eeb1fb24f;
    TVAL[1] = 64'h0000000000000001; TKEY[1] = 64'h123456789abcdef0; TEXP[1] = 64'h92ca3642c8c8a2b0;
    TVAL[2] = 64'h0000000000000002; TKEY[2] = 64'h123456789abcdef0; TEXP[2] = 64'h0d32c414e260787e;
    TVAL[3] = 64'h0000000000000003; TKEY[3] = 64'h123456789abcdef0; TEXP[3] = 64'h8d59d6baa6ee37d1;
    TVAL[4] = 64'h0000000000000004; TKEY[4] = 64'h123456789abcdef0; TEXP[4] = 64'h60261a66e8d08afc;
    TVAL[5] = 64'h0000000000000005; TKEY[5] = 64'h123456789abcdef0; TEXP[5] = 64'h964440383c254159;
    TVAL[6] = 64'h0000000000000006; TKEY[6] = 64'h123456789abcdef0; TEXP[6] = 64'h2a7047be476c0888;
    TVAL[7] = 64'h0000000000000007; TKEY[7] = 64'h123456789abcdef0; TEXP[7] = 64'h432ffc59d461e2c3;
    TVAL[8] = 64'h0000000000000008; TKEY[8] = 64'h123456789abcdef0; TEXP[8] = 64'h198e134abb96bfaa;
    TVAL[9] = 64'h0000000000000009; TKEY[9] = 64'h123456789abcdef0; TEXP[9] = 64'h07009aca3dd0a2c5;
    TVAL[10] = 64'h000000000000000a; TKEY[10] = 64'h123456789abcdef0; TEXP[10] = 64'h895773ddd08a666d;
    TVAL[11] = 64'h000000000000000b; TKEY[11] = 64'h123456789abcdef0; TEXP[11] = 64'h19cca2812a31e504;
    TVAL[12] = 64'h000000000000000c; TKEY[12] = 64'h123456789abcdef0; TEXP[12] = 64'ha185bbcb7d5533d9;
    TVAL[13] = 64'h000000000000000d; TKEY[13] = 64'h123456789abcdef0; TEXP[13] = 64'hdb5c113e6c234c9a;
    TVAL[14] = 64'h000000000000000e; TKEY[14] = 64'h123456789abcdef0; TEXP[14] = 64'h6ec5114b538dd837;
    TVAL[15] = 64'h000000000000000f; TKEY[15] = 64'h123456789abcdef0; TEXP[15] = 64'h89c72607de69a721;
    TVAL[16] = 64'h0000000000000010; TKEY[16] = 64'h123456789abcdef0; TEXP[16] = 64'hd01c9a85de5d75dc;
    TVAL[17] = 64'h0000000000000011; TKEY[17] = 64'h123456789abcdef0; TEXP[17] = 64'h8d3d13718aebc7db;
    TVAL[18] = 64'h0000000000000012; TKEY[18] = 64'h123456789abcdef0; TEXP[18] = 64'hf53a34d92db6bf24;
    TVAL[19] = 64'h0000000000000013; TKEY[19] = 64'h123456789abcdef0; TEXP[19] = 64'hd15bed32966c462d;
    TVAL[20] = 64'h0000000000000014; TKEY[20] = 64'h123456789abcdef0; TEXP[20] = 64'he0b1a0a533657601;
    TVAL[21] = 64'h0000000000000015; TKEY[21] = 64'h123456789abcdef0; TEXP[21] = 64'hda9bcef8a9eeb676;
    TVAL[22] = 64'h0000000000000016; TKEY[22] = 64'h123456789abcdef0; TEXP[22] = 64'h049af5c2635b097a;
    TVAL[23] = 64'h0000000000000017; TKEY[23] = 64'h123456789abcdef0; TEXP[23] = 64'hfc871f4f4d4bb441;
    TVAL[24] = 64'h0000000000000018; TKEY[24] = 64'h123456789abcdef0; TEXP[24] = 64'h6637d159057eea4a;
    TVAL[25] = 64'h0000000000000019; TKEY[25] = 64'h123456789abcdef0; TEXP[25] = 64'h09fe5c99db31f0a6;
    TVAL[26] = 64'h000000000000001a; TKEY[26] = 64'h123456789abcdef0; TEXP[26] = 64'hcf2e24ff074faa03;
    TVAL[27] = 64'h000000000000001b; TKEY[27] = 64'h123456789abcdef0; TEXP[27] = 64'hd8f9b24fa57b1128;
    TVAL[28] = 64'h000000000000001c; TKEY[28] = 64'h123456789abcdef0; TEXP[28] = 64'h50f970312afc333b;
    TVAL[29] = 64'h000000000000001d; TKEY[29] = 64'h123456789abcdef0; TEXP[29] = 64'h99b7ffc79b7b8940;
    TVAL[30] = 64'h000000000000001e; TKEY[30] = 64'h123456789abcdef0; TEXP[30] = 64'h80e498d89f7ba1fa;
    TVAL[31] = 64'h000000000000001f; TKEY[31] = 64'h123456789abcdef0; TEXP[31] = 64'hc970c1076b61ae4b;
    TVAL[32] = 64'h0000000000000000; TKEY[32] = 64'h0000000000000000; TEXP[32] = 64'he8aa0581be8e17cc;
    TVAL[33] = 64'h0000000000000001; TKEY[33] = 64'h0000000000000000; TEXP[33] = 64'hd871570f7646e3a1;
    TVAL[34] = 64'h0000000000000002; TKEY[34] = 64'h0000000000000000; TEXP[34] = 64'h6b6be2af29acad5c;
    TVAL[35] = 64'h0000000000000003; TKEY[35] = 64'h0000000000000000; TEXP[35] = 64'h26d308a247d0bd66;
    TVAL[36] = 64'h0000000000000004; TKEY[36] = 64'h0000000000000000; TEXP[36] = 64'hda6d1008efa48e4d;
    TVAL[37] = 64'h0000000000000005; TKEY[37] = 64'h0000000000000000; TEXP[37] = 64'h17ab3d8d9a849744;
    TVAL[38] = 64'h0000000000000006; TKEY[38] = 64'h0000000000000000; TEXP[38] = 64'h6c6c92210f1eafdb;
    TVAL[39] = 64'h0000000000000007; TKEY[39] = 64'h0000000000000000; TEXP[39] = 64'hc5d99cb1b286fc0c;
    TVAL[40] = 64'h0000000000000008; TKEY[40] = 64'h0000000000000000; TEXP[40] = 64'hd2e002f9c6572d0e;
    TVAL[41] = 64'h0000000000000009; TKEY[41] = 64'h0000000000000000; TEXP[41] = 64'h075bbd9de8df67ac;
    TVAL[42] = 64'h000000000000000a; TKEY[42] = 64'h0000000000000000; TEXP[42] = 64'hed90f352018b47c4;
    TVAL[43] = 64'h000000000000000b; TKEY[43] = 64'h0000000000000000; TEXP[43] = 64'h26d862a7f6fc10e7;
    TVAL[44] = 64'h000000000000000c; TKEY[44] = 64'h0000000000000000; TEXP[44] = 64'h3c5bea04ec251779;
    TVAL[45] = 64'h000000000000000d; TKEY[45] = 64'h0000000000000000; TEXP[45] = 64'h4867196e26ef197a;
    TVAL[46] = 64'h000000000000000e; TKEY[46] = 64'h0000000000000000; TEXP[46] = 64'h9cd69f81968cc58b;
    TVAL[47] = 64'h000000000000000f; TKEY[47] = 64'h0000000000000000; TEXP[47] = 64'h23c8c0b02ba02849;
    TVAL[48] = 64'h0000000000000010; TKEY[48] = 64'h0000000000000000; TEXP[48] = 64'h723dfa03debc0f18;
    TVAL[49] = 64'h0000000000000011; TKEY[49] = 64'h0000000000000000; TEXP[49] = 64'hae022691cd1af706;
    TVAL[50] = 64'h0000000000000012; TKEY[50] = 64'h0000000000000000; TEXP[50] = 64'h588fdb82aefcaa0e;
    TVAL[51] = 64'h0000000000000013; TKEY[51] = 64'h0000000000000000; TEXP[51] = 64'hcf55f71fb77ab443;
    TVAL[52] = 64'h0000000000000014; TKEY[52] = 64'h0000000000000000; TEXP[52] = 64'h3c996c218a62cd7c;
    TVAL[53] = 64'h0000000000000015; TKEY[53] = 64'h0000000000000000; TEXP[53] = 64'h9a2ced7f98ae6db1;
    TVAL[54] = 64'h0000000000000016; TKEY[54] = 64'h0000000000000000; TEXP[54] = 64'h2b4a5fedc205253a;
    TVAL[55] = 64'h0000000000000017; TKEY[55] = 64'h0000000000000000; TEXP[55] = 64'hf069bfa329600e6c;
    TVAL[56] = 64'h0000000000000018; TKEY[56] = 64'h0000000000000000; TEXP[56] = 64'hc5b9d568b77a79b3;
    TVAL[57] = 64'h0000000000000019; TKEY[57] = 64'h0000000000000000; TEXP[57] = 64'h29dc8b69a976f34b;
    TVAL[58] = 64'h000000000000001a; TKEY[58] = 64'h0000000000000000; TEXP[58] = 64'hc67ed4b5c686ab77;
    TVAL[59] = 64'h000000000000001b; TKEY[59] = 64'h0000000000000000; TEXP[59] = 64'ha0f45da912e1bff1;
    TVAL[60] = 64'h000000000000001c; TKEY[60] = 64'h0000000000000000; TEXP[60] = 64'he29a19aef0f999ae;
    TVAL[61] = 64'h000000000000001d; TKEY[61] = 64'h0000000000000000; TEXP[61] = 64'ha7c987d273932e57;
    TVAL[62] = 64'h000000000000001e; TKEY[62] = 64'h0000000000000000; TEXP[62] = 64'hcaa676dabad75b44;
    TVAL[63] = 64'h000000000000001f; TKEY[63] = 64'h0000000000000000; TEXP[63] = 64'h9d1199c5eb6f14a3;
    TVAL[64] = 64'h0000000000000000; TKEY[64] = 64'hffffffffffffffff; TEXP[64] = 64'hf44d3424969b2772;
    TVAL[65] = 64'h0000000000000001; TKEY[65] = 64'hffffffffffffffff; TEXP[65] = 64'hb76b8daa48219d7a;
    TVAL[66] = 64'h0000000000000002; TKEY[66] = 64'hffffffffffffffff; TEXP[66] = 64'hc161804c432e4ca3;
    TVAL[67] = 64'h0000000000000003; TKEY[67] = 64'hffffffffffffffff; TEXP[67] = 64'hfdea8fec85083dce;
    TVAL[68] = 64'h0000000000000004; TKEY[68] = 64'hffffffffffffffff; TEXP[68] = 64'h07ac6a7945922095;
    TVAL[69] = 64'h0000000000000005; TKEY[69] = 64'hffffffffffffffff; TEXP[69] = 64'h623b1ac30738b110;
    TVAL[70] = 64'h0000000000000006; TKEY[70] = 64'hffffffffffffffff; TEXP[70] = 64'hda382cd923e9deff;
    TVAL[71] = 64'h0000000000000007; TKEY[71] = 64'hffffffffffffffff; TEXP[71] = 64'hf7c88479735fadfa;
    TVAL[72] = 64'h0000000000000008; TKEY[72] = 64'hffffffffffffffff; TEXP[72] = 64'hcaf127e94d67aac8;
    TVAL[73] = 64'h0000000000000009; TKEY[73] = 64'hffffffffffffffff; TEXP[73] = 64'h4ef3d53be0938030;
    TVAL[74] = 64'h000000000000000a; TKEY[74] = 64'hffffffffffffffff; TEXP[74] = 64'h5bc7db72e6e65fc2;
    TVAL[75] = 64'h000000000000000b; TKEY[75] = 64'hffffffffffffffff; TEXP[75] = 64'h252ad1526ee81844;
    TVAL[76] = 64'h000000000000000c; TKEY[76] = 64'hffffffffffffffff; TEXP[76] = 64'hf312117c87022931;
    TVAL[77] = 64'h000000000000000d; TKEY[77] = 64'hffffffffffffffff; TEXP[77] = 64'hcc7c25d7607e05fe;
    TVAL[78] = 64'h000000000000000e; TKEY[78] = 64'hffffffffffffffff; TEXP[78] = 64'h239ee4b820bef408;
    TVAL[79] = 64'h000000000000000f; TKEY[79] = 64'hffffffffffffffff; TEXP[79] = 64'h032cde28f82cec82;
    TVAL[80] = 64'h0000000000000010; TKEY[80] = 64'hffffffffffffffff; TEXP[80] = 64'hdd7f8b3f5e475e2a;
    TVAL[81] = 64'h0000000000000011; TKEY[81] = 64'hffffffffffffffff; TEXP[81] = 64'h7ef9880f0af1ef66;
    TVAL[82] = 64'h0000000000000012; TKEY[82] = 64'hffffffffffffffff; TEXP[82] = 64'hc2933591f5b6557c;
    TVAL[83] = 64'h0000000000000013; TKEY[83] = 64'hffffffffffffffff; TEXP[83] = 64'he6aaa0e17ca43fe9;
    TVAL[84] = 64'h0000000000000014; TKEY[84] = 64'hffffffffffffffff; TEXP[84] = 64'hf0694c5848493735;
    TVAL[85] = 64'h0000000000000015; TKEY[85] = 64'hffffffffffffffff; TEXP[85] = 64'h48ee90d2cc377cd8;
    TVAL[86] = 64'h0000000000000016; TKEY[86] = 64'hffffffffffffffff; TEXP[86] = 64'h1e7f8f6000a0133e;
    TVAL[87] = 64'h0000000000000017; TKEY[87] = 64'hffffffffffffffff; TEXP[87] = 64'hcccc8ee01bd3b98c;
    TVAL[88] = 64'h0000000000000018; TKEY[88] = 64'hffffffffffffffff; TEXP[88] = 64'he404d91a0a870024;
    TVAL[89] = 64'h0000000000000019; TKEY[89] = 64'hffffffffffffffff; TEXP[89] = 64'h00aca6351560582c;
    TVAL[90] = 64'h000000000000001a; TKEY[90] = 64'hffffffffffffffff; TEXP[90] = 64'hc05e93a1997ef2ac;
    TVAL[91] = 64'h000000000000001b; TKEY[91] = 64'hffffffffffffffff; TEXP[91] = 64'hbfe57d7b0db2ad46;
    TVAL[92] = 64'h000000000000001c; TKEY[92] = 64'hffffffffffffffff; TEXP[92] = 64'h22df543d66b40098;
    TVAL[93] = 64'h000000000000001d; TKEY[93] = 64'hffffffffffffffff; TEXP[93] = 64'h921cff3bd74778ec;
    TVAL[94] = 64'h000000000000001e; TKEY[94] = 64'hffffffffffffffff; TEXP[94] = 64'ha7467db435d9053f;
    TVAL[95] = 64'h000000000000001f; TKEY[95] = 64'hffffffffffffffff; TEXP[95] = 64'h474d7b586ad86708;
    TVAL[96] = 64'h0000000000000000; TKEY[96] = 64'h9e3779b97f4a7c15; TEXP[96] = 64'h4166e0fa75bb45b2;
    TVAL[97] = 64'h0000000000000001; TKEY[97] = 64'h9e3779b97f4a7c15; TEXP[97] = 64'h99ef7ad9bde76f01;
    TVAL[98] = 64'h0000000000000002; TKEY[98] = 64'h9e3779b97f4a7c15; TEXP[98] = 64'h23aa6b15695d3e8f;
    TVAL[99] = 64'h0000000000000003; TKEY[99] = 64'h9e3779b97f4a7c15; TEXP[99] = 64'h06564d626d59aeb6;
    TVAL[100] = 64'h0000000000000004; TKEY[100] = 64'h9e3779b97f4a7c15; TEXP[100] = 64'h95d965357ca6a4dd;
    TVAL[101] = 64'h0000000000000005; TKEY[101] = 64'h9e3779b97f4a7c15; TEXP[101] = 64'h394ec70c967512e8;
    TVAL[102] = 64'h0000000000000006; TKEY[102] = 64'h9e3779b97f4a7c15; TEXP[102] = 64'hf58ea84cc5472adb;
    TVAL[103] = 64'h0000000000000007; TKEY[103] = 64'h9e3779b97f4a7c15; TEXP[103] = 64'h0be00a1166f46a33;
    TVAL[104] = 64'h0000000000000008; TKEY[104] = 64'h9e3779b97f4a7c15; TEXP[104] = 64'h398aa734064fdd43;
    TVAL[105] = 64'h0000000000000009; TKEY[105] = 64'h9e3779b97f4a7c15; TEXP[105] = 64'h04dd574be7db8fa6;
    TVAL[106] = 64'h000000000000000a; TKEY[106] = 64'h9e3779b97f4a7c15; TEXP[106] = 64'h30960092450fb418;
    TVAL[107] = 64'h000000000000000b; TKEY[107] = 64'h9e3779b97f4a7c15; TEXP[107] = 64'h3d1bab6070258d6f;
    TVAL[108] = 64'h000000000000000c; TKEY[108] = 64'h9e3779b97f4a7c15; TEXP[108] = 64'h339a79978ca926da;
    TVAL[109] = 64'h000000000000000d; TKEY[109] = 64'h9e3779b97f4a7c15; TEXP[109] = 64'hbce38231401beb75;
    TVAL[110] = 64'h000000000000000e; TKEY[110] = 64'h9e3779b97f4a7c15; TEXP[110] = 64'hd2baba78179c3f99;
    TVAL[111] = 64'h000000000000000f; TKEY[111] = 64'h9e3779b97f4a7c15; TEXP[111] = 64'hc679c7ece5c32ffd;
    TVAL[112] = 64'h0000000000000010; TKEY[112] = 64'h9e3779b97f4a7c15; TEXP[112] = 64'h37546068e5a7df79;
    TVAL[113] = 64'h0000000000000011; TKEY[113] = 64'h9e3779b97f4a7c15; TEXP[113] = 64'h6b10a895b5d91dab;
    TVAL[114] = 64'h0000000000000012; TKEY[114] = 64'h9e3779b97f4a7c15; TEXP[114] = 64'h924c21392deadce5;
    TVAL[115] = 64'h0000000000000013; TKEY[115] = 64'h9e3779b97f4a7c15; TEXP[115] = 64'hb8e83f2fa487971b;
    TVAL[116] = 64'h0000000000000014; TKEY[116] = 64'h9e3779b97f4a7c15; TEXP[116] = 64'h6fa2e587260877bd;
    TVAL[117] = 64'h0000000000000015; TKEY[117] = 64'h9e3779b97f4a7c15; TEXP[117] = 64'h9cd8b29637dc73b0;
    TVAL[118] = 64'h0000000000000016; TKEY[118] = 64'h9e3779b97f4a7c15; TEXP[118] = 64'h6f925def9c1dc991;
    TVAL[119] = 64'h0000000000000017; TKEY[119] = 64'h9e3779b97f4a7c15; TEXP[119] = 64'hcbd2768683653ff8;
    TVAL[120] = 64'h0000000000000018; TKEY[120] = 64'h9e3779b97f4a7c15; TEXP[120] = 64'h74c845ca4ca111da;
    TVAL[121] = 64'h0000000000000019; TKEY[121] = 64'h9e3779b97f4a7c15; TEXP[121] = 64'hb869f730000491b8;
    TVAL[122] = 64'h000000000000001a; TKEY[122] = 64'h9e3779b97f4a7c15; TEXP[122] = 64'h7ca9c4648c3e6733;
    TVAL[123] = 64'h000000000000001b; TKEY[123] = 64'h9e3779b97f4a7c15; TEXP[123] = 64'h5f6909aaf33b752a;
    TVAL[124] = 64'h000000000000001c; TKEY[124] = 64'h9e3779b97f4a7c15; TEXP[124] = 64'hdc283fbba44a504d;
    TVAL[125] = 64'h000000000000001d; TKEY[125] = 64'h9e3779b97f4a7c15; TEXP[125] = 64'hdfbf222136b41dc1;
    TVAL[126] = 64'h000000000000001e; TKEY[126] = 64'h9e3779b97f4a7c15; TEXP[126] = 64'hc36099b59d50773c;
    TVAL[127] = 64'h000000000000001f; TKEY[127] = 64'h9e3779b97f4a7c15; TEXP[127] = 64'h0472cad2012b5488;

    errs = 0; n_valid = 0;
    valid_in = 0; val = 0; key = 0;
    @(posedge clk); @(posedge clk); // settle: registers reach 0, valid_out=0

    // ---- Phase A: back-to-back inputs, 1 per cycle (no bubbles) ----
    // 1-cycle latency: input i presented before posedge i -> out==TEXP[i], valid_out==1 after posedge i.
    for (i = 0; i < N; i = i + 1) begin
      val = TVAL[i]; key = TKEY[i]; valid_in = 1;
      @(posedge clk);
      #1;
      if (!valid_out) begin $display("THROUGHPUT-FAIL: valid_out low at i=%0d", i); errs = errs + 1; end
      else n_valid = n_valid + 1;
      if (out !== TEXP[i]) begin $display("MISMATCH i=%0d: got %h exp %h", i, out, TEXP[i]); errs = errs + 1; end
    end
    if (n_valid !== N) begin $display("THROUGHPUT-COUNT-FAIL: %0d valid cycles, expected 128", n_valid); errs = errs + 1; end

    // ---- Phase B: exact 1-cycle latency probe (distinguishes 0/1/2-cycle designs) ----
    j = 42; // arbitrary vector
    val = TVAL[j]; key = TKEY[j]; valid_in = 1;
    @(posedge clk); #1;
    // exactly 1 cycle after presentation: result must be visible and valid
    if (!valid_out) begin $display("LATENCY-FAIL: valid_out not asserted 1 cycle after valid input"); errs = errs + 1; end
    if (out !== TEXP[j]) begin $display("LATENCY-FAIL: out=%h, exp=%h 1 cycle after valid input", out, TEXP[j]); errs = errs + 1; end
    // prove registered input stage (not 0-cycle combinational): capture out, change
    // inputs mid-cycle; a registered design must not move out until the next posedge
    out_hold = out;
    val = TVAL[j+1]; key = TKEY[j+1]; valid_in = 0;
    #1;
    if (out !== out_hold) begin $display("REG-FAIL: output changed before clock edge (looks 0-cycle)"); errs = errs + 1; end
    @(posedge clk); #1;
    // bubble was presented before this posedge -> valid_out must drop NOW (1-cycle latency)
    if (valid_out) begin $display("DRAIN-FAIL: valid_out did not drop 1 cycle after bubble"); errs = errs + 1; end
    // out is don't-care while valid_out=0, but the data path must stay live:
    // out always reflects f(val_q), i.e. the bubble input just registered
    if (out !== TEXP[j+1]) begin $display("DRAIN-FLOW-FAIL: out=%h did not follow registered bubble input, exp %h", out, TEXP[j+1]); errs = errs + 1; end
    @(posedge clk); #1;
    if (valid_out) begin $display("DRAIN-FAIL2: valid_out stuck high"); errs = errs + 1; end

    // ---- Phase C: intermittent valid (bubble every 3rd) ----
    for (i = 0; i < 12; i = i + 1) begin
      val = TVAL[i]; key = TKEY[i]; valid_in = (i % 3 != 2);
      @(posedge clk); #1;
      if (i % 3 != 2) begin
        if (!valid_out) begin $display("INTERMITTENT-FAIL: valid_out low at i=%0d", i); errs = errs + 1; end
        if (out !== TEXP[i]) begin $display("INTERMITTENT-MISMATCH i=%0d: got %h exp %h", i, out, TEXP[i]); errs = errs + 1; end
      end else begin
        if (valid_out) begin $display("INTERMITTENT-VALID-FAIL at i=%0d (bubble cycle)", i); errs = errs + 1; end
      end
    end

    valid_in = 0;
    repeat (4) @(posedge clk);
    $display("VECTORS-CHECKED: 128 back-to-back + 1 latency probe + 12 intermittent");
    if (errs == 0) $display("PIPECHECK PASS");
    else $display("PIPECHECK FAIL: %0d errors", errs);
    $finish;
  end
endmodule