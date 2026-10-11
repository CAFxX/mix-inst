
`timescale 1ns/1ps
module tbm;
reg [63:0] v,k,exp; wire [63:0] o;
mix_spn10 dut(.val(v),.key(k),.out(o));
integer fd,rc,nf,np; reg [63:0] a,b,c;
initial begin
  fd=$fopen("mix_vec.txt","r"); nf=0; np=0;
  while (!$feof(fd)) begin
    rc=$fscanf(fd,"%h %h %h\n",a,b,c);
    if (rc==3) begin v=a;k=b; #50; nf=nf+1; if(o===c)np=np+1;
      else if(np<3)$display("MIS %h %h -> %h exp %h",v,k,o,c); end
  end
  $display("MIX_CHECK %0d/%0d pass",np,nf); $finish;
end
endmodule
