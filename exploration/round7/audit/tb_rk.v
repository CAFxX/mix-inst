// Testbench: check the RTL's internal rk() function against model vectors.
// Format per line: key_hex round_int expected_rk_hex. Uses hierarchical call dut.rk.
`timescale 1ns/1ps
module tb_rk;
    reg [63:0] key, expected, got;
    reg [63:0] kval;
    integer round, f, n, nfail, rc;
    reg [63:0] dummy_val;
    wire [63:0] dummy_out;

    r7_feist8_s1_1sbox dut(.val(dummy_val), .key(kval), .out(dummy_out));

    initial begin
        n = 0; nfail = 0;
        dummy_val = 0; kval = 0;
        f = $fopen("rk_vectors.hex", "r");
        if (f == 0) begin $display("FATAL: cannot open rk_vectors.hex"); $finish; end
        while (!$feof(f)) begin
            rc = $fscanf(f, "%h %d %h\n", key, round, expected);
            if (rc == 3) begin
                n = n + 1;
                got = dut.rk(key, round);
                #0;
                if (got !== expected) begin
                    nfail = nfail + 1;
                    $display("RK MISMATCH: key=%h round=%0d rtl=%h model=%h",
                             key, round, got, expected);
                end
            end
        end
        $fclose(f);
        $display("RK RESULT total=%0d fail=%0d", n, nfail);
        $finish;
    end
endmodule
