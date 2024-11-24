`timescale 1ns/10ps
module processor_tb;


reg clk, rst;
wire mem_w;
wire[15:0] program_addr, data_addr, data_out;

wire[15:0] mem_data, instr_data;


always #10 clk = ~clk; // generate clk signal

//1k word memory block
reg[15:0] memory[0:999]; 
always @ (posedge clk) begin if(mem_w) memory[data_addr] = data_out; end


assign mem_data = memory[data_addr];
assign instr_data = memory[program_addr];

initial 
begin
	clk = 0;
    rst = 0;
    $readmemb("program.txt", memory); // read in program to memory
    @(posedge clk) #1;
    rst = 1; // start program
end

processor UUT(clk, rst, instr_data, mem_data, program_addr, data_addr, data_out, mem_w);

endmodule
