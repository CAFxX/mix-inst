// Behavioral simulation models for mini.genlib cells (S0 mapped-netlist
// equivalence spot-check). Port names match the genlib definitions.
module INV(input A, output Y); assign Y = ~A; endmodule
module BUF(input A, output Y); assign Y = A; endmodule
module AND2(input A, B, output Y); assign Y = A & B; endmodule
module AND3(input A, B, C, output Y); assign Y = A & B & C; endmodule
module AND4(input A, B, C, D, output Y); assign Y = A & B & C & D; endmodule
module NAND2(input A, B, output Y); assign Y = ~(A & B); endmodule
module NAND3(input A, B, C, output Y); assign Y = ~(A & B & C); endmodule
module NAND4(input A, B, C, D, output Y); assign Y = ~(A & B & C & D); endmodule
module OR2(input A, B, output Y); assign Y = A | B; endmodule
module OR3(input A, B, C, output Y); assign Y = A | B | C; endmodule
module OR4(input A, B, C, D, output Y); assign Y = A | B | C | D; endmodule
module NOR2(input A, B, output Y); assign Y = ~(A | B); endmodule
module NOR3(input A, B, C, output Y); assign Y = ~(A | B | C); endmodule
module NOR4(input A, B, C, D, output Y); assign Y = ~(A | B | C | D); endmodule
module XOR2(input A, B, output Y); assign Y = A ^ B; endmodule
module XNOR2(input A, B, output Y); assign Y = ~(A ^ B); endmodule
module MUX2(input A, B, S, output Y); assign Y = S ? A : B; endmodule // genlib: Y=(S*A)+(!S*B)
module AOI21(input A, B, C, output Y); assign Y = ~((A & B) | C); endmodule
module OAI21(input A, B, C, output Y); assign Y = ~((A | B) & C); endmodule
