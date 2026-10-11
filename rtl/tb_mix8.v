// check ROUNDS=8 vs python golden vectors
`timescale 1ns/1ps
module tb_mix8;
    reg [63:0] val, key; wire [63:0] out;
    reg [63:0] ev, ek, eo;
    mix_spn12 #(.ROUNDS(8)) dut (.val(val), .key(key), .out(out));
    integer fd, rc, np, nf;
    initial begin
        fd = $fopen("vectors8.hex","r"); np=0; nf=0;
        if (fd==0) begin $display("FATAL: vectors8.hex not found"); $finish; end
        while (!$feof(fd)) begin
            rc = $fscanf(fd, "%h %h %h\n", ev, ek, eo);
            if (rc==3) begin val=ev; key=ek; #10; nf=nf+1;
                if (out===eo) np=np+1; else $display("MIS %h %h -> %h exp %h",val,key,out,eo); end
        end
        $display("TB8: %0d/%0d pass", np, nf);
        if (np==nf && nf>0) $display("TB8 VERDICT: PASS");
        else $display("TB8 VERDICT: FAIL");
        $finish;
    end
endmodule
