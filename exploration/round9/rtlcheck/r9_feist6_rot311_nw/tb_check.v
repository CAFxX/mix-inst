// Generic model-vs-RTL equivalence check (template; TOP substituted by check_rtl.py).
// vectors.txt lines: <val hex> <key hex> <expected hex>
`timescale 1ns/1ps
module tb_check;
    reg  [63:0] val, key;
    wire [63:0] out;
    integer fd, n, fails;
    reg [63:0] v, k, e;
    r9_feist6_rot311_nw dut (.val(val), .key(key), .out(out));
    initial begin
        fd = $fopen("vectors.txt", "r");
        if (fd == 0) begin $display("FATAL: cannot open vectors.txt"); $finish; end
        n = 0; fails = 0;
        while (!$feof(fd)) begin
            if ($fscanf(fd, "%h %h %h\n", v, k, e) != 3) begin
                // tolerate trailing blank line
                if (!$feof(fd)) begin $display("FATAL: bad vector line %0d", n); $finish; end
            end else begin
                val = v; key = k; #10;
                if (out !== e) begin
                    $display("MISMATCH %0d: val=%h key=%h got=%h exp=%h", n, v, k, out, e);
                    fails = fails + 1;
                    if (fails > 10) begin $display("FATAL: too many mismatches"); $finish; end
                end
                n = n + 1;
            end
        end
        $fclose(fd);
        if (fails == 0) $display("RTLCHECK: %0d/%0d vectors match -> PASS", n, n);
        else $display("RTLCHECK: %0d mismatches / %0d vectors -> FAIL", fails, n);
    end
endmodule
