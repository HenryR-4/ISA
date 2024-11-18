`timescale 1ns/10ps
module processor_tb;


wire clk, rst, mem_w;
wire[15:0] program_addr, data_addr, data_out;

always #10 clk = ~clk; // generate clk signal

//1k word memory block
reg[15:0] memory[0:999]; 
always @ (mem_w)
    memory[data_addr] = data_out; 

initial 
begin
    rst = 0;
    $readmemb("program.txt", memory); // read in program to memory
    @(posedge clk) #1;
    rst = 1; // start program
end

processor UUT(clk, rst, memory[program_addr], memory[data_addr], program_addr, data_addr, data_out, mem_w);

endmodule
