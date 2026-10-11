// ============================================================================
// tb_pipe.v — verifies mix_spn12_pipe against the combinational mix_spn12:
//
//   1. functional equivalence: pipe output == combinational reference,
//      delayed by exactly 12 cycles;
//   2. throughput: with valid_in held high, valid_out is high every cycle
//      after the pipeline fills (1 result/cycle, no bubbles);
//   3. valid tracking: gaps in valid_in reappear as gaps in valid_out
//      exactly 12 cycles later.
// ============================================================================
`timescale 1ns/1ps

module tb_pipe;
    localparam ROUNDS  = 12;
    localparam NVEC    = 200;

    reg         clk = 0;
    reg         rst_n = 0;
    reg         valid_in = 0;
    reg  [63:0] val = 0, key = 0;
    wire [63:0] out;
    wire        valid_out;

    mix_spn12_pipe #(.ROUNDS(ROUNDS)) dut (
        .clk(clk), .rst_n(rst_n), .valid_in(valid_in),
        .val(val), .key(key), .out(out), .valid_out(valid_out)
    );

    // combinational reference on the same inputs
    wire [63:0] ref_out;
    mix_spn12 #(.ROUNDS(ROUNDS)) ref (.val(val), .key(key), .out(ref_out));

    always #5 clk = ~clk;

    // scoreboard: expected outputs with their due cycle
    reg [63:0] exp_q [0:NVEC+32];
    reg        exp_v [0:NVEC+32];
    integer    wptr, rptr, cycle;
    integer    nfail, ngap_fail, ntp_fail;
    integer    i;
    integer    p;
    reg [9:0]  pat;
    reg [63:0] lcg;

    initial begin
        nfail = 0; ngap_fail = 0; ntp_fail = 0;
        wptr = 0; rptr = 0; cycle = 0;
        lcg = 64'h9e3779b97f4a7c15;

        // reset
        repeat (4) @(posedge clk);
        rst_n = 1;
        @(posedge clk);

        // ---- phase 1: back-to-back requests, 1/cycle -----------------------
        for (i = 0; i < NVEC; i = i + 1) begin
            lcg = lcg * 64'h5851f42d4c957f2d + 64'h14057b7ef767814f;
            // sample reference BEFORE driving (ref is combinational on val/key)
            val = lcg; key = lcg ^ 64'hdeadbeefcafebabe;
            #1;
            exp_q[wptr] = ref_out;   // ref_out settled for this val/key
            exp_v[wptr] = 1'b1;
            wptr = wptr + 1;
            valid_in = 1;
            @(posedge clk);
            cycle = cycle + 1;
            check_out();
        end

        // drain the pipeline (no new requests); exactly ROUNDS cycles
        // flush the remaining scoreboard entries, then valid must drop
        valid_in = 0;
        repeat (ROUNDS) begin
            @(posedge clk);
            cycle = cycle + 1;
            check_out();
        end
        repeat (2) @(posedge clk);
        #1;
        if (valid_out) begin
            $display("DRAIN FAIL: valid_out stuck high after pipeline empty");
            nfail = nfail + 1;
        end

        // ---- phase 2: throughput check ------------------------------------
        // after fill, valid_out must be 1 on EVERY cycle while valid_in = 1
        rst_n = 0; repeat (2) @(posedge clk); rst_n = 1; @(posedge clk);
        wptr = 0; rptr = 0;
        valid_in = 1;
        for (i = 0; i < 64; i = i + 1) begin
            lcg = lcg * 64'h5851f42d4c957f2d + 1;
            val = lcg; key = ~lcg;
            @(posedge clk);
            #1;
            if (i >= ROUNDS && !valid_out) begin
                $display("TP FAIL at cycle %0d: valid_out=0 during sustained input", i);
                ntp_fail = ntp_fail + 1;
            end
        end
        valid_in = 0;

        // ---- phase 3: valid gaps track with 12-cycle latency --------------
        rst_n = 0; repeat (2) @(posedge clk); rst_n = 1; @(posedge clk);
        // pattern: 3 on, 2 off, 5 on
        begin
            pat = 10'b1110011101;
            for (p = 0; p < 10; p = p + 1) begin
                valid_in = pat[p];
                val = p; key = p * 64'h9e3779b97f4a7c15;
                @(posedge clk);
            end
            valid_in = 0;
            // valid_out after posedge t reflects valid_in sampled at t-12,
            // so pat[p] (sampled at t=p+1) is visible after t=p+13.
            for (p = 0; p < 10; p = p + 1) begin
                repeat (p == 0 ? 3 : 1) @(posedge clk);
                #1;
                if (valid_out !== pat[p]) begin
                    $display("GAP FAIL: cycle %0d valid_out=%b expected %b",
                             p, valid_out, pat[p]);
                    ngap_fail = ngap_fail + 1;
                end
            end
        end

        $display("PIPE EQUIV: %0d mismatches over %0d vectors", nfail, NVEC);
        $display("PIPE THROUGHPUT: %0d gaps during sustained 1/cycle input", ntp_fail);
        $display("PIPE VALID-TRACK: %0d failures", ngap_fail);
        if (nfail == 0 && ntp_fail == 0 && ngap_fail == 0)
            $display("TB_PIPE PASS");
        else
            $display("TB_PIPE FAIL");
        $finish;
    end

    task check_out;
        begin
            #1; // let nonblocking updates settle before sampling
            // rptr catches up once the pipeline has filled (ROUNDS cycles)
            if (cycle > ROUNDS) begin
                if (valid_out !== exp_v[rptr]) begin
                    $display("VALID MISMATCH cycle %0d: got %b exp %b",
                             cycle, valid_out, exp_v[rptr]);
                    nfail = nfail + 1;
                end else if (valid_out && out !== exp_q[rptr]) begin
                    $display("DATA MISMATCH cycle %0d: got %h exp %h",
                             cycle, out, exp_q[rptr]);
                    nfail = nfail + 1;
                end
                rptr = rptr + 1;
            end else begin
                if (valid_out) begin
                    $display("EARLY VALID cycle %0d (latency < %0d?)", cycle, ROUNDS);
                    nfail = nfail + 1;
                end
            end
        end
    endtask

endmodule
