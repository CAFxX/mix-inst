// Probe: S1 S-box (minimized DNF) delay in isolation
module s1_dnf_probe(input wire [3:0] x, output wire [3:0] y);
    // y0 = -1-0 + 1--0 + -001  (x3 x2 x1 x0)
    wire y0 = ( x[2] & ~x[0]) | (x[3] & ~x[0]) | (~x[2] & ~x[1] & x[0]);
    // y1 = 110- + 01-0 + 101- + 0-10 + 11-1
    wire y1 = (x[3] & x[2] & ~x[1]) | (~x[3] & x[2] & ~x[0]) | (x[3] & ~x[2] & x[1])
            | (~x[3] & x[1] & ~x[0]) | (x[3] & x[2] & x[0]);
    // y2 = 110- + 0-11 + 10-1 + -110
    wire y2 = (x[3] & x[2] & ~x[1]) | (~x[3] & x[1] & x[0]) | (x[3] & ~x[2] & x[0])
            | (x[2] & x[1] & ~x[0]);
    // y3 = -11- + -1-1 + 10-0
    wire y3 = (x[2] & x[1]) | (x[2] & x[0]) | (x[3] & ~x[2] & ~x[0]);
    assign y = {y3, y2, y1, y0};
endmodule
