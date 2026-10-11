// Testbench: drive r7_feist8_s1_1sbox with vectors from vectors.hex
// Format per line: val_hex key_hex expected_hex
`timescale 1ns/1ps
module tb;
    reg [63:0] val, key, expected;
    wire [63:0] out;
    integer f, n, nmatch, nfail, rc;
    integer first_fail;

    r7_feist8_s1_1sbox dut(.val(val), .key(key), .out(out));

    initial begin
        n = 0; nmatch = 0; nfail = 0; first_fail = -1;
        f = $fopen("vectors.hex", "r");
        if (f == 0) begin
            $display("FATAL: cannot open vectors.hex");
            $finish;
        end
        while (!$feof(f)) begin
            rc = $fscanf(f, "%h %h %h\n", val, key, expected);
            if (rc != 3) begin
                // allow trailing blank line
            end else begin
                #1;
                n = n + 1;
                if (out === expected) begin
                    nmatch = nmatch + 1;
                end else begin
                    nfail = nfail + 1;
                    if (first_fail < 0) first_fail = n;
                    if (nfail <= 5)
                        $display("MISMATCH #%0d: val=%h key=%h rtl=%h model=%h",
                                 n, val, key, out, expected);
                end
            end
        end
        $fclose(f);
        $display("RESULT total=%0d match=%0d fail=%0d first_fail=%0d",
                 n, nmatch, nfail, first_fail);
        $finish;
    end
endmodule
