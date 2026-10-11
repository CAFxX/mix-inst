// check default ROUNDS=10 RTL against golden_vectors.txt (comments start with '#')
`timescale 1ns/1ps
module tb_golden;
    reg [63:0] val, key; wire [63:0] out;
    reg [63:0] ev, ek, eo;
    reg [8*128:1] line;
    mix_spn12 dut (.val(val), .key(key), .out(out));
    integer fd, rc, np, nf;
    initial begin
        fd = $fopen("../golden_vectors.txt","r"); np=0; nf=0;
        if (fd==0) begin $display("FATAL: ../golden_vectors.txt not found"); $finish; end
        while (!$feof(fd)) begin
            rc = $fgets(line, fd);
            if (rc>0 && line[8*128-1 -: 8] != "#") begin
                rc = $sscanf(line, "%h %h %h", ev, ek, eo);
                if (rc==3) begin val=ev; key=ek; #10; nf=nf+1;
                    if (out===eo) np=np+1; else $display("MIS %h %h -> %h exp %h",val,key,out,eo); end
            end
        end
        $display("GOLDEN: %0d/%0d pass", np, nf);
        if (np==nf && nf>0) $display("GOLDEN VERDICT: PASS");
        else $display("GOLDEN VERDICT: FAIL");
        $finish;
    end
endmodule
