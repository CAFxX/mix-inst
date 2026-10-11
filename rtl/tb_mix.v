// Self-checking testbench: compares RTL against Python golden vectors.
`timescale 1ns/1ps
module tb_mix;
    reg  [63:0] val, key;
    wire [63:0] out;
    reg  [63:0] exp_val, exp_key, exp_out;

    mix_spn12 dut (.val(val), .key(key), .out(out));

    integer fd, nvec, npass, nfail, rc;
    initial begin
        fd = $fopen("vectors.hex", "r");
        if (fd == 0) begin $display("FATAL: cannot open vectors.hex"); $finish; end
        nvec = 0; npass = 0; nfail = 0;
        while (!$feof(fd)) begin
            rc = $fscanf(fd, "%h %h %h\n", exp_val, exp_key, exp_out);
            if (rc != 3) begin
                // allow trailing blank line
                if (!$feof(fd)) $display("WARN: fscanf rc=%0d at vec %0d", rc, nvec);
            end else begin
                val = exp_val; key = exp_key;
                #10;
                nvec = nvec + 1;
                if (out === exp_out) npass = npass + 1;
                else begin
                    nfail = nfail + 1;
                    if (nfail <= 5)
                        $display("MISMATCH vec %0d: val=%h key=%h rtl=%h exp=%h",
                                 nvec, val, key, out, exp_out);
                end
            end
        end
        $fclose(fd);
        $display("TB RESULT: %0d vectors, %0d pass, %0d fail", nvec, npass, nfail);
        if (nfail == 0 && nvec > 0) $display("TB PASS");
        else $display("TB FAIL");
        $finish;
    end
endmodule
