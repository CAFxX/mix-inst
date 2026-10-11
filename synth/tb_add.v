
`timescale 1ns/1ps
module tb;
reg [63:0] a,b,exp; wire [63:0] s;
add64 dut(.a(a),.b(b),.s(s));
integer fd,rc,nf,np; reg [63:0] ea,eb,ee;
initial begin
  fd=$fopen("add_vec.txt","r"); nf=0; np=0;
  while (!$feof(fd)) begin
    rc=$fscanf(fd,"%h %h %h\n",ea,eb,ee);
    if (rc==3) begin a=ea;b=eb; #10; nf=nf+1; if(s===ee)np=np+1;
      else if(np<3)$display("MIS %h %h -> %h exp %h",a,b,s,ee); end
  end
  $display("ADD_CHECK %0d/%0d pass",np,nf); $finish;
end
endmodule
