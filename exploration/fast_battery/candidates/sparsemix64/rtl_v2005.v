module sparsemix64(input wire [63:0] x, output wire [63:0] y);
  wire [63:0] s0;
  wire [63:0] s1;
  wire [63:0] s2;
  wire [63:0] s3;

  function [3:0] sb_0;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_0 = 4'h1;
        4'h1: sb_0 = 4'hb;
        4'h2: sb_0 = 4'h3;
        4'h3: sb_0 = 4'ha;
        4'h4: sb_0 = 4'h0;
        4'h5: sb_0 = 4'h7;
        4'h6: sb_0 = 4'hc;
        4'h7: sb_0 = 4'h2;
        4'h8: sb_0 = 4'h9;
        4'h9: sb_0 = 4'h6;
        4'ha: sb_0 = 4'h5;
        4'hb: sb_0 = 4'h8;
        4'hc: sb_0 = 4'he;
        4'hd: sb_0 = 4'h4;
        4'he: sb_0 = 4'hd;
        4'hf: sb_0 = 4'hf;
        default: sb_0 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_1;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_1 = 4'h2;
        4'h1: sb_1 = 4'h0;
        4'h2: sb_1 = 4'h3;
        4'h3: sb_1 = 4'hb;
        4'h4: sb_1 = 4'hf;
        4'h5: sb_1 = 4'ha;
        4'h6: sb_1 = 4'h4;
        4'h7: sb_1 = 4'h5;
        4'h8: sb_1 = 4'h8;
        4'h9: sb_1 = 4'h1;
        4'ha: sb_1 = 4'h9;
        4'hb: sb_1 = 4'h6;
        4'hc: sb_1 = 4'hd;
        4'hd: sb_1 = 4'hc;
        4'he: sb_1 = 4'h7;
        4'hf: sb_1 = 4'he;
        default: sb_1 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_2;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_2 = 4'h8;
        4'h1: sb_2 = 4'h3;
        4'h2: sb_2 = 4'h7;
        4'h3: sb_2 = 4'h5;
        4'h4: sb_2 = 4'h1;
        4'h5: sb_2 = 4'h4;
        4'h6: sb_2 = 4'hb;
        4'h7: sb_2 = 4'h9;
        4'h8: sb_2 = 4'hf;
        4'h9: sb_2 = 4'hc;
        4'ha: sb_2 = 4'he;
        4'hb: sb_2 = 4'h0;
        4'hc: sb_2 = 4'hd;
        4'hd: sb_2 = 4'h2;
        4'he: sb_2 = 4'h6;
        4'hf: sb_2 = 4'ha;
        default: sb_2 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_3;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_3 = 4'h8;
        4'h1: sb_3 = 4'h1;
        4'h2: sb_3 = 4'h0;
        4'h3: sb_3 = 4'hb;
        4'h4: sb_3 = 4'hd;
        4'h5: sb_3 = 4'he;
        4'h6: sb_3 = 4'h3;
        4'h7: sb_3 = 4'hc;
        4'h8: sb_3 = 4'ha;
        4'h9: sb_3 = 4'h6;
        4'ha: sb_3 = 4'h5;
        4'hb: sb_3 = 4'hf;
        4'hc: sb_3 = 4'h4;
        4'hd: sb_3 = 4'h9;
        4'he: sb_3 = 4'h7;
        4'hf: sb_3 = 4'h2;
        default: sb_3 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_4;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_4 = 4'hc;
        4'h1: sb_4 = 4'h8;
        4'h2: sb_4 = 4'h4;
        4'h3: sb_4 = 4'h7;
        4'h4: sb_4 = 4'hf;
        4'h5: sb_4 = 4'he;
        4'h6: sb_4 = 4'hb;
        4'h7: sb_4 = 4'h9;
        4'h8: sb_4 = 4'h1;
        4'h9: sb_4 = 4'h6;
        4'ha: sb_4 = 4'h2;
        4'hb: sb_4 = 4'hd;
        4'hc: sb_4 = 4'ha;
        4'hd: sb_4 = 4'h3;
        4'he: sb_4 = 4'h0;
        4'hf: sb_4 = 4'h5;
        default: sb_4 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_5;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_5 = 4'hb;
        4'h1: sb_5 = 4'h6;
        4'h2: sb_5 = 4'h7;
        4'h3: sb_5 = 4'h5;
        4'h4: sb_5 = 4'hf;
        4'h5: sb_5 = 4'h4;
        4'h6: sb_5 = 4'ha;
        4'h7: sb_5 = 4'he;
        4'h8: sb_5 = 4'hd;
        4'h9: sb_5 = 4'h9;
        4'ha: sb_5 = 4'h2;
        4'hb: sb_5 = 4'h0;
        4'hc: sb_5 = 4'h1;
        4'hd: sb_5 = 4'hc;
        4'he: sb_5 = 4'h8;
        4'hf: sb_5 = 4'h3;
        default: sb_5 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_6;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_6 = 4'hb;
        4'h1: sb_6 = 4'ha;
        4'h2: sb_6 = 4'hc;
        4'h3: sb_6 = 4'h0;
        4'h4: sb_6 = 4'hf;
        4'h5: sb_6 = 4'h5;
        4'h6: sb_6 = 4'h2;
        4'h7: sb_6 = 4'h7;
        4'h8: sb_6 = 4'he;
        4'h9: sb_6 = 4'h8;
        4'ha: sb_6 = 4'h6;
        4'hb: sb_6 = 4'h9;
        4'hc: sb_6 = 4'h4;
        4'hd: sb_6 = 4'hd;
        4'he: sb_6 = 4'h1;
        4'hf: sb_6 = 4'h3;
        default: sb_6 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_7;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_7 = 4'hd;
        4'h1: sb_7 = 4'h8;
        4'h2: sb_7 = 4'hb;
        4'h3: sb_7 = 4'he;
        4'h4: sb_7 = 4'h1;
        4'h5: sb_7 = 4'h0;
        4'h6: sb_7 = 4'hc;
        4'h7: sb_7 = 4'h7;
        4'h8: sb_7 = 4'ha;
        4'h9: sb_7 = 4'h6;
        4'ha: sb_7 = 4'h2;
        4'hb: sb_7 = 4'hf;
        4'hc: sb_7 = 4'h3;
        4'hd: sb_7 = 4'h5;
        4'he: sb_7 = 4'h9;
        4'hf: sb_7 = 4'h4;
        default: sb_7 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_8;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_8 = 4'h6;
        4'h1: sb_8 = 4'h0;
        4'h2: sb_8 = 4'h3;
        4'h3: sb_8 = 4'hc;
        4'h4: sb_8 = 4'h4;
        4'h5: sb_8 = 4'h1;
        4'h6: sb_8 = 4'ha;
        4'h7: sb_8 = 4'h8;
        4'h8: sb_8 = 4'h2;
        4'h9: sb_8 = 4'hf;
        4'ha: sb_8 = 4'h9;
        4'hb: sb_8 = 4'hd;
        4'hc: sb_8 = 4'he;
        4'hd: sb_8 = 4'h5;
        4'he: sb_8 = 4'h7;
        4'hf: sb_8 = 4'hb;
        default: sb_8 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_9;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_9 = 4'h6;
        4'h1: sb_9 = 4'h2;
        4'h2: sb_9 = 4'h1;
        4'h3: sb_9 = 4'he;
        4'h4: sb_9 = 4'hf;
        4'h5: sb_9 = 4'h9;
        4'h6: sb_9 = 4'h0;
        4'h7: sb_9 = 4'h5;
        4'h8: sb_9 = 4'ha;
        4'h9: sb_9 = 4'h3;
        4'ha: sb_9 = 4'h7;
        4'hb: sb_9 = 4'hb;
        4'hc: sb_9 = 4'hc;
        4'hd: sb_9 = 4'h4;
        4'he: sb_9 = 4'h8;
        4'hf: sb_9 = 4'hd;
        default: sb_9 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_10;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_10 = 4'h2;
        4'h1: sb_10 = 4'hd;
        4'h2: sb_10 = 4'h9;
        4'h3: sb_10 = 4'hf;
        4'h4: sb_10 = 4'h1;
        4'h5: sb_10 = 4'h0;
        4'h6: sb_10 = 4'h5;
        4'h7: sb_10 = 4'h7;
        4'h8: sb_10 = 4'h6;
        4'h9: sb_10 = 4'hc;
        4'ha: sb_10 = 4'hb;
        4'hb: sb_10 = 4'h3;
        4'hc: sb_10 = 4'he;
        4'hd: sb_10 = 4'ha;
        4'he: sb_10 = 4'h8;
        4'hf: sb_10 = 4'h4;
        default: sb_10 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_11;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_11 = 4'h1;
        4'h1: sb_11 = 4'he;
        4'h2: sb_11 = 4'hb;
        4'h3: sb_11 = 4'ha;
        4'h4: sb_11 = 4'h9;
        4'h5: sb_11 = 4'hf;
        4'h6: sb_11 = 4'h5;
        4'h7: sb_11 = 4'h6;
        4'h8: sb_11 = 4'h3;
        4'h9: sb_11 = 4'h8;
        4'ha: sb_11 = 4'h2;
        4'hb: sb_11 = 4'hd;
        4'hc: sb_11 = 4'hc;
        4'hd: sb_11 = 4'h4;
        4'he: sb_11 = 4'h0;
        4'hf: sb_11 = 4'h7;
        default: sb_11 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_12;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_12 = 4'he;
        4'h1: sb_12 = 4'h6;
        4'h2: sb_12 = 4'hd;
        4'h3: sb_12 = 4'h9;
        4'h4: sb_12 = 4'h2;
        4'h5: sb_12 = 4'h0;
        4'h6: sb_12 = 4'h1;
        4'h7: sb_12 = 4'h8;
        4'h8: sb_12 = 4'hf;
        4'h9: sb_12 = 4'h3;
        4'ha: sb_12 = 4'h5;
        4'hb: sb_12 = 4'h7;
        4'hc: sb_12 = 4'h4;
        4'hd: sb_12 = 4'hb;
        4'he: sb_12 = 4'hc;
        4'hf: sb_12 = 4'ha;
        default: sb_12 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_13;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_13 = 4'h3;
        4'h1: sb_13 = 4'h8;
        4'h2: sb_13 = 4'hb;
        4'h3: sb_13 = 4'h5;
        4'h4: sb_13 = 4'h7;
        4'h5: sb_13 = 4'h6;
        4'h6: sb_13 = 4'h9;
        4'h7: sb_13 = 4'h1;
        4'h8: sb_13 = 4'hc;
        4'h9: sb_13 = 4'he;
        4'ha: sb_13 = 4'ha;
        4'hb: sb_13 = 4'hf;
        4'hc: sb_13 = 4'h0;
        4'hd: sb_13 = 4'hd;
        4'he: sb_13 = 4'h4;
        4'hf: sb_13 = 4'h2;
        default: sb_13 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_14;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_14 = 4'h4;
        4'h1: sb_14 = 4'h2;
        4'h2: sb_14 = 4'h3;
        4'h3: sb_14 = 4'h9;
        4'h4: sb_14 = 4'he;
        4'h5: sb_14 = 4'h5;
        4'h6: sb_14 = 4'h7;
        4'h7: sb_14 = 4'hd;
        4'h8: sb_14 = 4'hb;
        4'h9: sb_14 = 4'hf;
        4'ha: sb_14 = 4'ha;
        4'hb: sb_14 = 4'h8;
        4'hc: sb_14 = 4'h6;
        4'hd: sb_14 = 4'h1;
        4'he: sb_14 = 4'hc;
        4'hf: sb_14 = 4'h0;
        default: sb_14 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_15;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_15 = 4'h9;
        4'h1: sb_15 = 4'hd;
        4'h2: sb_15 = 4'h3;
        4'h3: sb_15 = 4'hf;
        4'h4: sb_15 = 4'h5;
        4'h5: sb_15 = 4'h7;
        4'h6: sb_15 = 4'h2;
        4'h7: sb_15 = 4'h8;
        4'h8: sb_15 = 4'hb;
        4'h9: sb_15 = 4'he;
        4'ha: sb_15 = 4'h4;
        4'hb: sb_15 = 4'hc;
        4'hc: sb_15 = 4'ha;
        4'hd: sb_15 = 4'h1;
        4'he: sb_15 = 4'h6;
        4'hf: sb_15 = 4'h0;
        default: sb_15 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_16;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_16 = 4'he;
        4'h1: sb_16 = 4'hf;
        4'h2: sb_16 = 4'h6;
        4'h3: sb_16 = 4'hd;
        4'h4: sb_16 = 4'h4;
        4'h5: sb_16 = 4'h0;
        4'h6: sb_16 = 4'h7;
        4'h7: sb_16 = 4'h9;
        4'h8: sb_16 = 4'h5;
        4'h9: sb_16 = 4'h3;
        4'ha: sb_16 = 4'h1;
        4'hb: sb_16 = 4'hc;
        4'hc: sb_16 = 4'h2;
        4'hd: sb_16 = 4'hb;
        4'he: sb_16 = 4'ha;
        4'hf: sb_16 = 4'h8;
        default: sb_16 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_17;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_17 = 4'h3;
        4'h1: sb_17 = 4'ha;
        4'h2: sb_17 = 4'hc;
        4'h3: sb_17 = 4'h7;
        4'h4: sb_17 = 4'he;
        4'h5: sb_17 = 4'h8;
        4'h6: sb_17 = 4'hb;
        4'h7: sb_17 = 4'h0;
        4'h8: sb_17 = 4'hf;
        4'h9: sb_17 = 4'h6;
        4'ha: sb_17 = 4'h9;
        4'hb: sb_17 = 4'h2;
        4'hc: sb_17 = 4'hd;
        4'hd: sb_17 = 4'h5;
        4'he: sb_17 = 4'h1;
        4'hf: sb_17 = 4'h4;
        default: sb_17 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_18;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_18 = 4'hd;
        4'h1: sb_18 = 4'h9;
        4'h2: sb_18 = 4'hb;
        4'h3: sb_18 = 4'h5;
        4'h4: sb_18 = 4'h3;
        4'h5: sb_18 = 4'h1;
        4'h6: sb_18 = 4'he;
        4'h7: sb_18 = 4'h6;
        4'h8: sb_18 = 4'hf;
        4'h9: sb_18 = 4'h4;
        4'ha: sb_18 = 4'h0;
        4'hb: sb_18 = 4'h7;
        4'hc: sb_18 = 4'hc;
        4'hd: sb_18 = 4'h2;
        4'he: sb_18 = 4'h8;
        4'hf: sb_18 = 4'ha;
        default: sb_18 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_19;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_19 = 4'hb;
        4'h1: sb_19 = 4'h6;
        4'h2: sb_19 = 4'h7;
        4'h3: sb_19 = 4'h5;
        4'h4: sb_19 = 4'hf;
        4'h5: sb_19 = 4'h4;
        4'h6: sb_19 = 4'ha;
        4'h7: sb_19 = 4'he;
        4'h8: sb_19 = 4'hd;
        4'h9: sb_19 = 4'h9;
        4'ha: sb_19 = 4'h2;
        4'hb: sb_19 = 4'h0;
        4'hc: sb_19 = 4'h1;
        4'hd: sb_19 = 4'hc;
        4'he: sb_19 = 4'h8;
        4'hf: sb_19 = 4'h3;
        default: sb_19 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_20;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_20 = 4'hf;
        4'h1: sb_20 = 4'hb;
        4'h2: sb_20 = 4'ha;
        4'h3: sb_20 = 4'hd;
        4'h4: sb_20 = 4'h8;
        4'h5: sb_20 = 4'he;
        4'h6: sb_20 = 4'h7;
        4'h7: sb_20 = 4'h6;
        4'h8: sb_20 = 4'h2;
        4'h9: sb_20 = 4'h3;
        4'ha: sb_20 = 4'h0;
        4'hb: sb_20 = 4'h4;
        4'hc: sb_20 = 4'hc;
        4'hd: sb_20 = 4'h1;
        4'he: sb_20 = 4'h9;
        4'hf: sb_20 = 4'h5;
        default: sb_20 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_21;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_21 = 4'h3;
        4'h1: sb_21 = 4'h0;
        4'h2: sb_21 = 4'h2;
        4'h3: sb_21 = 4'h6;
        4'h4: sb_21 = 4'h8;
        4'h5: sb_21 = 4'h7;
        4'h6: sb_21 = 4'h5;
        4'h7: sb_21 = 4'hd;
        4'h8: sb_21 = 4'h1;
        4'h9: sb_21 = 4'he;
        4'ha: sb_21 = 4'h9;
        4'hb: sb_21 = 4'hb;
        4'hc: sb_21 = 4'hc;
        4'hd: sb_21 = 4'h4;
        4'he: sb_21 = 4'hf;
        4'hf: sb_21 = 4'ha;
        default: sb_21 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_22;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_22 = 4'h5;
        4'h1: sb_22 = 4'hc;
        4'h2: sb_22 = 4'he;
        4'h3: sb_22 = 4'h3;
        4'h4: sb_22 = 4'hb;
        4'h5: sb_22 = 4'h1;
        4'h6: sb_22 = 4'h9;
        4'h7: sb_22 = 4'h8;
        4'h8: sb_22 = 4'h0;
        4'h9: sb_22 = 4'h7;
        4'ha: sb_22 = 4'h4;
        4'hb: sb_22 = 4'hf;
        4'hc: sb_22 = 4'h2;
        4'hd: sb_22 = 4'h6;
        4'he: sb_22 = 4'hd;
        4'hf: sb_22 = 4'ha;
        default: sb_22 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_23;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_23 = 4'hf;
        4'h1: sb_23 = 4'h2;
        4'h2: sb_23 = 4'h3;
        4'h3: sb_23 = 4'hb;
        4'h4: sb_23 = 4'h0;
        4'h5: sb_23 = 4'hd;
        4'h6: sb_23 = 4'h4;
        4'h7: sb_23 = 4'h5;
        4'h8: sb_23 = 4'ha;
        4'h9: sb_23 = 4'h1;
        4'ha: sb_23 = 4'h9;
        4'hb: sb_23 = 4'h6;
        4'hc: sb_23 = 4'h7;
        4'hd: sb_23 = 4'hc;
        4'he: sb_23 = 4'h8;
        4'hf: sb_23 = 4'he;
        default: sb_23 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_24;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_24 = 4'h4;
        4'h1: sb_24 = 4'h1;
        4'h2: sb_24 = 4'h0;
        4'h3: sb_24 = 4'hc;
        4'h4: sb_24 = 4'h5;
        4'h5: sb_24 = 4'hf;
        4'h6: sb_24 = 4'h2;
        4'h7: sb_24 = 4'hd;
        4'h8: sb_24 = 4'h9;
        4'h9: sb_24 = 4'h3;
        4'ha: sb_24 = 4'he;
        4'hb: sb_24 = 4'h7;
        4'hc: sb_24 = 4'h6;
        4'hd: sb_24 = 4'hb;
        4'he: sb_24 = 4'h8;
        4'hf: sb_24 = 4'ha;
        default: sb_24 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_25;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_25 = 4'h7;
        4'h1: sb_25 = 4'ha;
        4'h2: sb_25 = 4'h9;
        4'h3: sb_25 = 4'h1;
        4'h4: sb_25 = 4'hc;
        4'h5: sb_25 = 4'h6;
        4'h6: sb_25 = 4'h8;
        4'h7: sb_25 = 4'he;
        4'h8: sb_25 = 4'hd;
        4'h9: sb_25 = 4'h2;
        4'ha: sb_25 = 4'h5;
        4'hb: sb_25 = 4'hb;
        4'hc: sb_25 = 4'hf;
        4'hd: sb_25 = 4'h3;
        4'he: sb_25 = 4'h4;
        4'hf: sb_25 = 4'h0;
        default: sb_25 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_26;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_26 = 4'hb;
        4'h1: sb_26 = 4'ha;
        4'h2: sb_26 = 4'hc;
        4'h3: sb_26 = 4'h0;
        4'h4: sb_26 = 4'hf;
        4'h5: sb_26 = 4'h5;
        4'h6: sb_26 = 4'h2;
        4'h7: sb_26 = 4'h7;
        4'h8: sb_26 = 4'he;
        4'h9: sb_26 = 4'h8;
        4'ha: sb_26 = 4'h6;
        4'hb: sb_26 = 4'h9;
        4'hc: sb_26 = 4'h4;
        4'hd: sb_26 = 4'hd;
        4'he: sb_26 = 4'h1;
        4'hf: sb_26 = 4'h3;
        default: sb_26 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_27;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_27 = 4'h5;
        4'h1: sb_27 = 4'h1;
        4'h2: sb_27 = 4'h8;
        4'h3: sb_27 = 4'ha;
        4'h4: sb_27 = 4'he;
        4'h5: sb_27 = 4'h3;
        4'h6: sb_27 = 4'h2;
        4'h7: sb_27 = 4'h6;
        4'h8: sb_27 = 4'h4;
        4'h9: sb_27 = 4'hb;
        4'ha: sb_27 = 4'h0;
        4'hb: sb_27 = 4'h9;
        4'hc: sb_27 = 4'hd;
        4'hd: sb_27 = 4'hc;
        4'he: sb_27 = 4'h7;
        4'hf: sb_27 = 4'hf;
        default: sb_27 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_28;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_28 = 4'h3;
        4'h1: sb_28 = 4'h0;
        4'h2: sb_28 = 4'h2;
        4'h3: sb_28 = 4'h6;
        4'h4: sb_28 = 4'h8;
        4'h5: sb_28 = 4'h7;
        4'h6: sb_28 = 4'h5;
        4'h7: sb_28 = 4'hd;
        4'h8: sb_28 = 4'h1;
        4'h9: sb_28 = 4'he;
        4'ha: sb_28 = 4'h9;
        4'hb: sb_28 = 4'hb;
        4'hc: sb_28 = 4'hc;
        4'hd: sb_28 = 4'h4;
        4'he: sb_28 = 4'hf;
        4'hf: sb_28 = 4'ha;
        default: sb_28 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_29;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_29 = 4'h5;
        4'h1: sb_29 = 4'hc;
        4'h2: sb_29 = 4'he;
        4'h3: sb_29 = 4'h3;
        4'h4: sb_29 = 4'hb;
        4'h5: sb_29 = 4'h1;
        4'h6: sb_29 = 4'h9;
        4'h7: sb_29 = 4'h8;
        4'h8: sb_29 = 4'h0;
        4'h9: sb_29 = 4'h7;
        4'ha: sb_29 = 4'h4;
        4'hb: sb_29 = 4'hf;
        4'hc: sb_29 = 4'h2;
        4'hd: sb_29 = 4'h6;
        4'he: sb_29 = 4'hd;
        4'hf: sb_29 = 4'ha;
        default: sb_29 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_30;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_30 = 4'h4;
        4'h1: sb_30 = 4'h2;
        4'h2: sb_30 = 4'h3;
        4'h3: sb_30 = 4'h9;
        4'h4: sb_30 = 4'he;
        4'h5: sb_30 = 4'h5;
        4'h6: sb_30 = 4'h7;
        4'h7: sb_30 = 4'hd;
        4'h8: sb_30 = 4'hb;
        4'h9: sb_30 = 4'hf;
        4'ha: sb_30 = 4'ha;
        4'hb: sb_30 = 4'h8;
        4'hc: sb_30 = 4'h6;
        4'hd: sb_30 = 4'h1;
        4'he: sb_30 = 4'hc;
        4'hf: sb_30 = 4'h0;
        default: sb_30 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_31;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_31 = 4'hc;
        4'h1: sb_31 = 4'h6;
        4'h2: sb_31 = 4'hd;
        4'h3: sb_31 = 4'h9;
        4'h4: sb_31 = 4'h2;
        4'h5: sb_31 = 4'h0;
        4'h6: sb_31 = 4'h1;
        4'h7: sb_31 = 4'h8;
        4'h8: sb_31 = 4'hf;
        4'h9: sb_31 = 4'h3;
        4'ha: sb_31 = 4'h5;
        4'hb: sb_31 = 4'h7;
        4'hc: sb_31 = 4'h4;
        4'hd: sb_31 = 4'hb;
        4'he: sb_31 = 4'he;
        4'hf: sb_31 = 4'ha;
        default: sb_31 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_32;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_32 = 4'h2;
        4'h1: sb_32 = 4'hd;
        4'h2: sb_32 = 4'h9;
        4'h3: sb_32 = 4'hf;
        4'h4: sb_32 = 4'h1;
        4'h5: sb_32 = 4'h0;
        4'h6: sb_32 = 4'h5;
        4'h7: sb_32 = 4'h7;
        4'h8: sb_32 = 4'h6;
        4'h9: sb_32 = 4'hc;
        4'ha: sb_32 = 4'hb;
        4'hb: sb_32 = 4'h3;
        4'hc: sb_32 = 4'he;
        4'hd: sb_32 = 4'ha;
        4'he: sb_32 = 4'h8;
        4'hf: sb_32 = 4'h4;
        default: sb_32 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_33;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_33 = 4'h7;
        4'h1: sb_33 = 4'h3;
        4'h2: sb_33 = 4'hb;
        4'h3: sb_33 = 4'ha;
        4'h4: sb_33 = 4'hd;
        4'h5: sb_33 = 4'h0;
        4'h6: sb_33 = 4'h6;
        4'h7: sb_33 = 4'h8;
        4'h8: sb_33 = 4'he;
        4'h9: sb_33 = 4'h4;
        4'ha: sb_33 = 4'hc;
        4'hb: sb_33 = 4'h1;
        4'hc: sb_33 = 4'h9;
        4'hd: sb_33 = 4'hf;
        4'he: sb_33 = 4'h2;
        4'hf: sb_33 = 4'h5;
        default: sb_33 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_34;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_34 = 4'h5;
        4'h1: sb_34 = 4'h1;
        4'h2: sb_34 = 4'h8;
        4'h3: sb_34 = 4'ha;
        4'h4: sb_34 = 4'he;
        4'h5: sb_34 = 4'h3;
        4'h6: sb_34 = 4'h2;
        4'h7: sb_34 = 4'h6;
        4'h8: sb_34 = 4'h4;
        4'h9: sb_34 = 4'hb;
        4'ha: sb_34 = 4'h0;
        4'hb: sb_34 = 4'h9;
        4'hc: sb_34 = 4'hd;
        4'hd: sb_34 = 4'hc;
        4'he: sb_34 = 4'h7;
        4'hf: sb_34 = 4'hf;
        default: sb_34 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_35;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_35 = 4'h5;
        4'h1: sb_35 = 4'ha;
        4'h2: sb_35 = 4'h4;
        4'h3: sb_35 = 4'h7;
        4'h4: sb_35 = 4'h6;
        4'h5: sb_35 = 4'h0;
        4'h6: sb_35 = 4'hf;
        4'h7: sb_35 = 4'hc;
        4'h8: sb_35 = 4'h8;
        4'h9: sb_35 = 4'hd;
        4'ha: sb_35 = 4'h2;
        4'hb: sb_35 = 4'hb;
        4'hc: sb_35 = 4'h1;
        4'hd: sb_35 = 4'h9;
        4'he: sb_35 = 4'he;
        4'hf: sb_35 = 4'h3;
        default: sb_35 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_36;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_36 = 4'h7;
        4'h1: sb_36 = 4'h4;
        4'h2: sb_36 = 4'ha;
        4'h3: sb_36 = 4'he;
        4'h4: sb_36 = 4'h6;
        4'h5: sb_36 = 4'h8;
        4'h6: sb_36 = 4'h0;
        4'h7: sb_36 = 4'h1;
        4'h8: sb_36 = 4'hc;
        4'h9: sb_36 = 4'hb;
        4'ha: sb_36 = 4'hf;
        4'hb: sb_36 = 4'h3;
        4'hc: sb_36 = 4'h5;
        4'hd: sb_36 = 4'hd;
        4'he: sb_36 = 4'h2;
        4'hf: sb_36 = 4'h9;
        default: sb_36 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_37;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_37 = 4'h0;
        4'h1: sb_37 = 4'he;
        4'h2: sb_37 = 4'h8;
        4'h3: sb_37 = 4'h9;
        4'h4: sb_37 = 4'h4;
        4'h5: sb_37 = 4'h1;
        4'h6: sb_37 = 4'hf;
        4'h7: sb_37 = 4'hb;
        4'h8: sb_37 = 4'h7;
        4'h9: sb_37 = 4'h2;
        4'ha: sb_37 = 4'h5;
        4'hb: sb_37 = 4'hd;
        4'hc: sb_37 = 4'h6;
        4'hd: sb_37 = 4'ha;
        4'he: sb_37 = 4'h3;
        4'hf: sb_37 = 4'hc;
        default: sb_37 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_38;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_38 = 4'he;
        4'h1: sb_38 = 4'h2;
        4'h2: sb_38 = 4'hf;
        4'h3: sb_38 = 4'hc;
        4'h4: sb_38 = 4'h7;
        4'h5: sb_38 = 4'h8;
        4'h6: sb_38 = 4'h1;
        4'h7: sb_38 = 4'h4;
        4'h8: sb_38 = 4'ha;
        4'h9: sb_38 = 4'h5;
        4'ha: sb_38 = 4'hd;
        4'hb: sb_38 = 4'h6;
        4'hc: sb_38 = 4'hb;
        4'hd: sb_38 = 4'h3;
        4'he: sb_38 = 4'h0;
        4'hf: sb_38 = 4'h9;
        default: sb_38 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_39;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_39 = 4'he;
        4'h1: sb_39 = 4'h2;
        4'h2: sb_39 = 4'h6;
        4'h3: sb_39 = 4'hd;
        4'h4: sb_39 = 4'h7;
        4'h5: sb_39 = 4'h3;
        4'h6: sb_39 = 4'h1;
        4'h7: sb_39 = 4'h0;
        4'h8: sb_39 = 4'ha;
        4'h9: sb_39 = 4'h5;
        4'ha: sb_39 = 4'h8;
        4'hb: sb_39 = 4'h4;
        4'hc: sb_39 = 4'hf;
        4'hd: sb_39 = 4'h9;
        4'he: sb_39 = 4'hc;
        4'hf: sb_39 = 4'hb;
        default: sb_39 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_40;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_40 = 4'he;
        4'h1: sb_40 = 4'h2;
        4'h2: sb_40 = 4'h6;
        4'h3: sb_40 = 4'hd;
        4'h4: sb_40 = 4'h7;
        4'h5: sb_40 = 4'h3;
        4'h6: sb_40 = 4'h1;
        4'h7: sb_40 = 4'h0;
        4'h8: sb_40 = 4'ha;
        4'h9: sb_40 = 4'h5;
        4'ha: sb_40 = 4'h8;
        4'hb: sb_40 = 4'h4;
        4'hc: sb_40 = 4'hf;
        4'hd: sb_40 = 4'h9;
        4'he: sb_40 = 4'hc;
        4'hf: sb_40 = 4'hb;
        default: sb_40 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_41;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_41 = 4'h6;
        4'h1: sb_41 = 4'h7;
        4'h2: sb_41 = 4'hb;
        4'h3: sb_41 = 4'h1;
        4'h4: sb_41 = 4'h0;
        4'h5: sb_41 = 4'h3;
        4'h6: sb_41 = 4'he;
        4'h7: sb_41 = 4'ha;
        4'h8: sb_41 = 4'h5;
        4'h9: sb_41 = 4'h9;
        4'ha: sb_41 = 4'hc;
        4'hb: sb_41 = 4'h4;
        4'hc: sb_41 = 4'hd;
        4'hd: sb_41 = 4'h2;
        4'he: sb_41 = 4'hf;
        4'hf: sb_41 = 4'h8;
        default: sb_41 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_42;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_42 = 4'h1;
        4'h1: sb_42 = 4'he;
        4'h2: sb_42 = 4'hb;
        4'h3: sb_42 = 4'hc;
        4'h4: sb_42 = 4'h5;
        4'h5: sb_42 = 4'h0;
        4'h6: sb_42 = 4'ha;
        4'h7: sb_42 = 4'h8;
        4'h8: sb_42 = 4'hf;
        4'h9: sb_42 = 4'h7;
        4'ha: sb_42 = 4'h4;
        4'hb: sb_42 = 4'h9;
        4'hc: sb_42 = 4'h6;
        4'hd: sb_42 = 4'h2;
        4'he: sb_42 = 4'h3;
        4'hf: sb_42 = 4'hd;
        default: sb_42 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_43;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_43 = 4'hc;
        4'h1: sb_43 = 4'h7;
        4'h2: sb_43 = 4'h4;
        4'h3: sb_43 = 4'h8;
        4'h4: sb_43 = 4'he;
        4'h5: sb_43 = 4'hf;
        4'h6: sb_43 = 4'hb;
        4'h7: sb_43 = 4'h9;
        4'h8: sb_43 = 4'h1;
        4'h9: sb_43 = 4'h6;
        4'ha: sb_43 = 4'h2;
        4'hb: sb_43 = 4'hd;
        4'hc: sb_43 = 4'ha;
        4'hd: sb_43 = 4'h3;
        4'he: sb_43 = 4'h0;
        4'hf: sb_43 = 4'h5;
        default: sb_43 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_44;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_44 = 4'h1;
        4'h1: sb_44 = 4'he;
        4'h2: sb_44 = 4'hb;
        4'h3: sb_44 = 4'ha;
        4'h4: sb_44 = 4'h9;
        4'h5: sb_44 = 4'hf;
        4'h6: sb_44 = 4'h5;
        4'h7: sb_44 = 4'h6;
        4'h8: sb_44 = 4'h3;
        4'h9: sb_44 = 4'h8;
        4'ha: sb_44 = 4'h2;
        4'hb: sb_44 = 4'hd;
        4'hc: sb_44 = 4'hc;
        4'hd: sb_44 = 4'h4;
        4'he: sb_44 = 4'h0;
        4'hf: sb_44 = 4'h7;
        default: sb_44 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_45;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_45 = 4'h0;
        4'h1: sb_45 = 4'h9;
        4'h2: sb_45 = 4'he;
        4'h3: sb_45 = 4'hb;
        4'h4: sb_45 = 4'h5;
        4'h5: sb_45 = 4'h1;
        4'h6: sb_45 = 4'h6;
        4'h7: sb_45 = 4'hd;
        4'h8: sb_45 = 4'h7;
        4'h9: sb_45 = 4'hf;
        4'ha: sb_45 = 4'h2;
        4'hb: sb_45 = 4'h4;
        4'hc: sb_45 = 4'hc;
        4'hd: sb_45 = 4'h3;
        4'he: sb_45 = 4'h8;
        4'hf: sb_45 = 4'ha;
        default: sb_45 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_46;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_46 = 4'h7;
        4'h1: sb_46 = 4'h3;
        4'h2: sb_46 = 4'hb;
        4'h3: sb_46 = 4'ha;
        4'h4: sb_46 = 4'hd;
        4'h5: sb_46 = 4'h5;
        4'h6: sb_46 = 4'h6;
        4'h7: sb_46 = 4'h8;
        4'h8: sb_46 = 4'he;
        4'h9: sb_46 = 4'h4;
        4'ha: sb_46 = 4'hc;
        4'hb: sb_46 = 4'h1;
        4'hc: sb_46 = 4'h9;
        4'hd: sb_46 = 4'hf;
        4'he: sb_46 = 4'h2;
        4'hf: sb_46 = 4'h0;
        default: sb_46 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_47;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_47 = 4'hc;
        4'h1: sb_47 = 4'h8;
        4'h2: sb_47 = 4'h4;
        4'h3: sb_47 = 4'h7;
        4'h4: sb_47 = 4'he;
        4'h5: sb_47 = 4'hf;
        4'h6: sb_47 = 4'hb;
        4'h7: sb_47 = 4'h9;
        4'h8: sb_47 = 4'h1;
        4'h9: sb_47 = 4'h6;
        4'ha: sb_47 = 4'h2;
        4'hb: sb_47 = 4'hd;
        4'hc: sb_47 = 4'ha;
        4'hd: sb_47 = 4'h3;
        4'he: sb_47 = 4'h0;
        4'hf: sb_47 = 4'h5;
        default: sb_47 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_48;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_48 = 4'hb;
        4'h1: sb_48 = 4'h9;
        4'h2: sb_48 = 4'h3;
        4'h3: sb_48 = 4'hf;
        4'h4: sb_48 = 4'h2;
        4'h5: sb_48 = 4'h6;
        4'h6: sb_48 = 4'h8;
        4'h7: sb_48 = 4'h0;
        4'h8: sb_48 = 4'h1;
        4'h9: sb_48 = 4'h4;
        4'ha: sb_48 = 4'ha;
        4'hb: sb_48 = 4'h5;
        4'hc: sb_48 = 4'hc;
        4'hd: sb_48 = 4'h7;
        4'he: sb_48 = 4'hd;
        4'hf: sb_48 = 4'he;
        default: sb_48 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_49;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_49 = 4'h3;
        4'h1: sb_49 = 4'ha;
        4'h2: sb_49 = 4'hc;
        4'h3: sb_49 = 4'h7;
        4'h4: sb_49 = 4'he;
        4'h5: sb_49 = 4'h8;
        4'h6: sb_49 = 4'hb;
        4'h7: sb_49 = 4'h0;
        4'h8: sb_49 = 4'hf;
        4'h9: sb_49 = 4'h6;
        4'ha: sb_49 = 4'h9;
        4'hb: sb_49 = 4'h2;
        4'hc: sb_49 = 4'hd;
        4'hd: sb_49 = 4'h5;
        4'he: sb_49 = 4'h1;
        4'hf: sb_49 = 4'h4;
        default: sb_49 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_50;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_50 = 4'he;
        4'h1: sb_50 = 4'h2;
        4'h2: sb_50 = 4'hf;
        4'h3: sb_50 = 4'hc;
        4'h4: sb_50 = 4'h7;
        4'h5: sb_50 = 4'h8;
        4'h6: sb_50 = 4'h1;
        4'h7: sb_50 = 4'h4;
        4'h8: sb_50 = 4'ha;
        4'h9: sb_50 = 4'h5;
        4'ha: sb_50 = 4'hd;
        4'hb: sb_50 = 4'h6;
        4'hc: sb_50 = 4'hb;
        4'hd: sb_50 = 4'h3;
        4'he: sb_50 = 4'h0;
        4'hf: sb_50 = 4'h9;
        default: sb_50 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_51;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_51 = 4'h2;
        4'h1: sb_51 = 4'h9;
        4'h2: sb_51 = 4'h0;
        4'h3: sb_51 = 4'hd;
        4'h4: sb_51 = 4'h1;
        4'h5: sb_51 = 4'h7;
        4'h6: sb_51 = 4'hf;
        4'h7: sb_51 = 4'h6;
        4'h8: sb_51 = 4'he;
        4'h9: sb_51 = 4'h3;
        4'ha: sb_51 = 4'h8;
        4'hb: sb_51 = 4'h4;
        4'hc: sb_51 = 4'hc;
        4'hd: sb_51 = 4'hb;
        4'he: sb_51 = 4'ha;
        4'hf: sb_51 = 4'h5;
        default: sb_51 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_52;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_52 = 4'h4;
        4'h1: sb_52 = 4'ha;
        4'h2: sb_52 = 4'h0;
        4'h3: sb_52 = 4'hb;
        4'h4: sb_52 = 4'h5;
        4'h5: sb_52 = 4'h2;
        4'h6: sb_52 = 4'hd;
        4'h7: sb_52 = 4'hf;
        4'h8: sb_52 = 4'h3;
        4'h9: sb_52 = 4'he;
        4'ha: sb_52 = 4'h8;
        4'hb: sb_52 = 4'h6;
        4'hc: sb_52 = 4'hc;
        4'hd: sb_52 = 4'h7;
        4'he: sb_52 = 4'h9;
        4'hf: sb_52 = 4'h1;
        default: sb_52 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_53;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_53 = 4'h7;
        4'h1: sb_53 = 4'h3;
        4'h2: sb_53 = 4'hb;
        4'h3: sb_53 = 4'ha;
        4'h4: sb_53 = 4'hd;
        4'h5: sb_53 = 4'h5;
        4'h6: sb_53 = 4'h6;
        4'h7: sb_53 = 4'h8;
        4'h8: sb_53 = 4'he;
        4'h9: sb_53 = 4'h4;
        4'ha: sb_53 = 4'hc;
        4'hb: sb_53 = 4'h1;
        4'hc: sb_53 = 4'h9;
        4'hd: sb_53 = 4'hf;
        4'he: sb_53 = 4'h2;
        4'hf: sb_53 = 4'h0;
        default: sb_53 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_54;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_54 = 4'hc;
        4'h1: sb_54 = 4'h8;
        4'h2: sb_54 = 4'h4;
        4'h3: sb_54 = 4'h7;
        4'h4: sb_54 = 4'hf;
        4'h5: sb_54 = 4'he;
        4'h6: sb_54 = 4'hb;
        4'h7: sb_54 = 4'h9;
        4'h8: sb_54 = 4'h1;
        4'h9: sb_54 = 4'h6;
        4'ha: sb_54 = 4'h2;
        4'hb: sb_54 = 4'hd;
        4'hc: sb_54 = 4'ha;
        4'hd: sb_54 = 4'h3;
        4'he: sb_54 = 4'h0;
        4'hf: sb_54 = 4'h5;
        default: sb_54 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_55;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_55 = 4'h7;
        4'h1: sb_55 = 4'h3;
        4'h2: sb_55 = 4'hb;
        4'h3: sb_55 = 4'ha;
        4'h4: sb_55 = 4'hd;
        4'h5: sb_55 = 4'h5;
        4'h6: sb_55 = 4'h6;
        4'h7: sb_55 = 4'h8;
        4'h8: sb_55 = 4'he;
        4'h9: sb_55 = 4'h4;
        4'ha: sb_55 = 4'hc;
        4'hb: sb_55 = 4'h1;
        4'hc: sb_55 = 4'h9;
        4'hd: sb_55 = 4'hf;
        4'he: sb_55 = 4'h2;
        4'hf: sb_55 = 4'h0;
        default: sb_55 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_56;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_56 = 4'hf;
        4'h1: sb_56 = 4'h5;
        4'h2: sb_56 = 4'hd;
        4'h3: sb_56 = 4'h6;
        4'h4: sb_56 = 4'hc;
        4'h5: sb_56 = 4'he;
        4'h6: sb_56 = 4'hb;
        4'h7: sb_56 = 4'h9;
        4'h8: sb_56 = 4'h8;
        4'h9: sb_56 = 4'ha;
        4'ha: sb_56 = 4'h4;
        4'hb: sb_56 = 4'h0;
        4'hc: sb_56 = 4'h1;
        4'hd: sb_56 = 4'h2;
        4'he: sb_56 = 4'h7;
        4'hf: sb_56 = 4'h3;
        default: sb_56 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_57;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_57 = 4'h2;
        4'h1: sb_57 = 4'h3;
        4'h2: sb_57 = 4'h1;
        4'h3: sb_57 = 4'hd;
        4'h4: sb_57 = 4'h8;
        4'h5: sb_57 = 4'hb;
        4'h6: sb_57 = 4'h6;
        4'h7: sb_57 = 4'he;
        4'h8: sb_57 = 4'h0;
        4'h9: sb_57 = 4'h7;
        4'ha: sb_57 = 4'h5;
        4'hb: sb_57 = 4'hf;
        4'hc: sb_57 = 4'h4;
        4'hd: sb_57 = 4'ha;
        4'he: sb_57 = 4'hc;
        4'hf: sb_57 = 4'h9;
        default: sb_57 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_58;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_58 = 4'h3;
        4'h1: sb_58 = 4'h2;
        4'h2: sb_58 = 4'hd;
        4'h3: sb_58 = 4'h7;
        4'h4: sb_58 = 4'h1;
        4'h5: sb_58 = 4'he;
        4'h6: sb_58 = 4'h0;
        4'h7: sb_58 = 4'h6;
        4'h8: sb_58 = 4'h9;
        4'h9: sb_58 = 4'h5;
        4'ha: sb_58 = 4'h4;
        4'hb: sb_58 = 4'hc;
        4'hc: sb_58 = 4'hf;
        4'hd: sb_58 = 4'ha;
        4'he: sb_58 = 4'hb;
        4'hf: sb_58 = 4'h8;
        default: sb_58 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_59;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_59 = 4'h4;
        4'h1: sb_59 = 4'ha;
        4'h2: sb_59 = 4'hb;
        4'h3: sb_59 = 4'h8;
        4'h4: sb_59 = 4'h0;
        4'h5: sb_59 = 4'hc;
        4'h6: sb_59 = 4'h9;
        4'h7: sb_59 = 4'hd;
        4'h8: sb_59 = 4'h2;
        4'h9: sb_59 = 4'h1;
        4'ha: sb_59 = 4'hf;
        4'hb: sb_59 = 4'h5;
        4'hc: sb_59 = 4'h3;
        4'hd: sb_59 = 4'h6;
        4'he: sb_59 = 4'h7;
        4'hf: sb_59 = 4'he;
        default: sb_59 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_60;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_60 = 4'h5;
        4'h1: sb_60 = 4'hb;
        4'h2: sb_60 = 4'h4;
        4'h3: sb_60 = 4'he;
        4'h4: sb_60 = 4'h7;
        4'h5: sb_60 = 4'h3;
        4'h6: sb_60 = 4'h0;
        4'h7: sb_60 = 4'hd;
        4'h8: sb_60 = 4'h1;
        4'h9: sb_60 = 4'h9;
        4'ha: sb_60 = 4'hc;
        4'hb: sb_60 = 4'hf;
        4'hc: sb_60 = 4'h8;
        4'hd: sb_60 = 4'h6;
        4'he: sb_60 = 4'ha;
        4'hf: sb_60 = 4'h2;
        default: sb_60 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_61;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_61 = 4'h5;
        4'h1: sb_61 = 4'h0;
        4'h2: sb_61 = 4'h3;
        4'h3: sb_61 = 4'hc;
        4'h4: sb_61 = 4'hf;
        4'h5: sb_61 = 4'h1;
        4'h6: sb_61 = 4'ha;
        4'h7: sb_61 = 4'h8;
        4'h8: sb_61 = 4'h2;
        4'h9: sb_61 = 4'h6;
        4'ha: sb_61 = 4'h9;
        4'hb: sb_61 = 4'hd;
        4'hc: sb_61 = 4'he;
        4'hd: sb_61 = 4'h4;
        4'he: sb_61 = 4'h7;
        4'hf: sb_61 = 4'hb;
        default: sb_61 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_62;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_62 = 4'h4;
        4'h1: sb_62 = 4'h1;
        4'h2: sb_62 = 4'h0;
        4'h3: sb_62 = 4'hc;
        4'h4: sb_62 = 4'h5;
        4'h5: sb_62 = 4'hf;
        4'h6: sb_62 = 4'h2;
        4'h7: sb_62 = 4'hd;
        4'h8: sb_62 = 4'h9;
        4'h9: sb_62 = 4'h3;
        4'ha: sb_62 = 4'he;
        4'hb: sb_62 = 4'h7;
        4'hc: sb_62 = 4'h6;
        4'hd: sb_62 = 4'hb;
        4'he: sb_62 = 4'h8;
        4'hf: sb_62 = 4'ha;
        default: sb_62 = 4'h0;
      endcase
    end
  endfunction

  function [3:0] sb_63;
    input [3:0] z;
    begin
      case (z)
        4'h0: sb_63 = 4'hc;
        4'h1: sb_63 = 4'hd;
        4'h2: sb_63 = 4'h3;
        4'h3: sb_63 = 4'hb;
        4'h4: sb_63 = 4'h5;
        4'h5: sb_63 = 4'h7;
        4'h6: sb_63 = 4'h6;
        4'h7: sb_63 = 4'h2;
        4'h8: sb_63 = 4'hf;
        4'h9: sb_63 = 4'h8;
        4'ha: sb_63 = 4'h9;
        4'hb: sb_63 = 4'h4;
        4'hc: sb_63 = 4'h1;
        4'hd: sb_63 = 4'h0;
        4'he: sb_63 = 4'ha;
        4'hf: sb_63 = 4'he;
        default: sb_63 = 4'h0;
      endcase
    end
  endfunction

  assign s0[3:0] = sb_0(x[3:0]);
  assign s0[7:4] = sb_1(x[7:4]);
  assign s0[11:8] = sb_2(x[11:8]);
  assign s0[15:12] = sb_3(x[15:12]);
  assign s0[19:16] = sb_4(x[19:16]);
  assign s0[23:20] = sb_5(x[23:20]);
  assign s0[27:24] = sb_6(x[27:24]);
  assign s0[31:28] = sb_7(x[31:28]);
  assign s0[35:32] = sb_8(x[35:32]);
  assign s0[39:36] = sb_9(x[39:36]);
  assign s0[43:40] = sb_10(x[43:40]);
  assign s0[47:44] = sb_11(x[47:44]);
  assign s0[51:48] = sb_12(x[51:48]);
  assign s0[55:52] = sb_13(x[55:52]);
  assign s0[59:56] = sb_14(x[59:56]);
  assign s0[63:60] = sb_15(x[63:60]);
  assign s1[3:0] = sb_16({s0[47], s0[10], s0[5], s0[0]});
  assign s1[7:4] = sb_17({s0[3], s0[14], s0[9], s0[4]});
  assign s1[11:8] = sb_18({s0[7], s0[2], s0[13], s0[8]});
  assign s1[15:12] = sb_19({s0[11], s0[6], s0[1], s0[12]});
  assign s1[19:16] = sb_20({s0[15], s0[26], s0[21], s0[16]});
  assign s1[23:20] = sb_21({s0[19], s0[30], s0[25], s0[20]});
  assign s1[27:24] = sb_22({s0[23], s0[18], s0[29], s0[24]});
  assign s1[31:28] = sb_23({s0[27], s0[22], s0[17], s0[28]});
  assign s1[35:32] = sb_24({s0[31], s0[42], s0[37], s0[32]});
  assign s1[39:36] = sb_25({s0[35], s0[46], s0[41], s0[36]});
  assign s1[43:40] = sb_26({s0[39], s0[34], s0[45], s0[40]});
  assign s1[47:44] = sb_27({s0[43], s0[38], s0[33], s0[60]});
  assign s1[51:48] = sb_28({s0[63], s0[58], s0[53], s0[48]});
  assign s1[55:52] = sb_29({s0[51], s0[62], s0[57], s0[52]});
  assign s1[59:56] = sb_30({s0[55], s0[50], s0[61], s0[56]});
  assign s1[63:60] = sb_31({s0[59], s0[54], s0[49], s0[44]});
  assign s2[3:0] = sb_32({s1[51], s1[34], s1[17], s1[0]});
  assign s2[7:4] = sb_33({s1[55], s1[42], s1[21], s1[8]});
  assign s2[11:8] = sb_34({s1[59], s1[38], s1[29], s1[4]});
  assign s2[15:12] = sb_35({s1[63], s1[46], s1[25], s1[12]});
  assign s2[19:16] = sb_36({s1[7], s1[50], s1[37], s1[28]});
  assign s2[23:20] = sb_37({s1[3], s1[54], s1[33], s1[16]});
  assign s2[27:24] = sb_38({s1[15], s1[58], s1[41], s1[24]});
  assign s2[31:28] = sb_39({s1[11], s1[62], s1[45], s1[20]});
  assign s2[35:32] = sb_40({s1[27], s1[2], s1[53], s1[32]});
  assign s2[39:36] = sb_41({s1[23], s1[14], s1[57], s1[36]});
  assign s2[43:40] = sb_42({s1[19], s1[10], s1[49], s1[40]});
  assign s2[47:44] = sb_43({s1[31], s1[6], s1[61], s1[44]});
  assign s2[51:48] = sb_44({s1[35], s1[26], s1[1], s1[48]});
  assign s2[55:52] = sb_45({s1[39], s1[18], s1[9], s1[56]});
  assign s2[59:56] = sb_46({s1[43], s1[30], s1[13], s1[52]});
  assign s2[63:60] = sb_47({s1[47], s1[22], s1[5], s1[60]});
  assign s3[3:0] = sb_48({s2[31], s2[6], s2[41], s2[16]});
  assign s3[7:4] = sb_49({s2[7], s2[62], s2[33], s2[8]});
  assign s3[11:8] = sb_50({s2[11], s2[18], s2[53], s2[32]});
  assign s3[15:12] = sb_51({s2[35], s2[22], s2[25], s2[12]});
  assign s3[19:16] = sb_52({s2[63], s2[26], s2[21], s2[0]});
  assign s3[23:20] = sb_53({s2[55], s2[46], s2[5], s2[48]});
  assign s3[27:24] = sb_54({s2[23], s2[30], s2[17], s2[60]});
  assign s3[31:28] = sb_55({s2[19], s2[54], s2[13], s2[44]});
  assign s3[35:32] = sb_56({s2[27], s2[38], s2[9], s2[20]});
  assign s3[39:36] = sb_57({s2[15], s2[34], s2[37], s2[28]});
  assign s3[43:40] = sb_58({s2[59], s2[14], s2[29], s2[40]});
  assign s3[47:44] = sb_59({s2[43], s2[2], s2[57], s2[36]});
  assign s3[51:48] = sb_60({s2[39], s2[42], s2[49], s2[24]});
  assign s3[55:52] = sb_61({s2[3], s2[10], s2[45], s2[52]});
  assign s3[59:56] = sb_62({s2[51], s2[58], s2[1], s2[4]});
  assign s3[63:60] = sb_63({s2[47], s2[50], s2[61], s2[56]});
  assign y = s3;
endmodule
