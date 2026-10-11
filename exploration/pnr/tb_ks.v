module tb;
reg [63:0] a, b; wire [63:0] y;
add64_ks dut(a, b, y);
integer i, seed;
initial begin
  seed = 42;
  for (i = 0; i < 2000; i = i + 1) begin
    a = $random(seed); b = $random(seed);
    a = {a[31:0], $random(seed)}; b = {b[31:0], $random(seed)};
    #1;
    if (y !== a + b) begin $display("MISMATCH %h %h -> %h", a, b, y); $finish; end
  end
  $display("KS ADDER OK");
  $finish;
end
endmodule
