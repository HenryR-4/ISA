`define opcode instruction[15:12]
`define reg1   instruction[10:8]
`define reg2   instruction[7:5]
`define Im     instruction[11]
`define pc     registers[0]
module processor(input clk, rst, input[15:0] instruction, data_in, output[15:0] program_address, address, data_out, output mem_w)

    reg[15:0] registers[0:7]; // register file

    reg[2:0] sr; // 3 bit status register

    // control signals
    wire br, hlt, reg_w, mem_r;

    // sign extended values
    wire[15:0] immediate, offset, address;
    assign immediate = { 8{instruction[7]}, instruction[7:0]};
    assign offset = {11{instruction[4]}, instruction[4:0]};
    assign address = {5'b0, instruction[10:0]};

    // other internal signals
    wire[15:0] next_pc;
    wire[15:0] op2; // second operand to alu, first is always reg1
    wire[15:0] reg_in; // input to regfile

    assign op2 = `Im ? immediate : (registers[`reg2] + offset);
    assign reg_in = mem_r ? data_in : data_out;

    always @ (posedge clk)
    begin
        // active low reset
        if(!rst)
        begin
            // clear all registers to 0
            `pc <= 16'b0; // setting pc = 0 will release from halt, assuming first instruction isn't a halt
            registers[1] <= 16'b0;
            registers[2] <= 16'b0;
            registers[3] <= 16'b0;
            registers[4] <= 16'b0;
            registers[5] <= 16'b0;
            registers[6] <= 16'b0;
            registers[7] <= 16'b0;
            sr <= 3'b0;
        end
        else
        begin
            `pc <= next_pc; // program counter
            
            // writeback
            if(reg_w)
                registers[`reg1] <= reg_in;

            // status register = {eq, lt, gt}
            if(data_out === 0)
                sr <= 3'b100;
            else if(data_out[15] === 1)
                sr <= 3'b010;
            else
                sr <= 3'b001;
        end
    end
    
    assign program_address = `pc; // instruction address
    assign address = `Im ? immediate : (registers[`reg2] + offset); // address for mem instructions

    always @*
    begin
        // control signals
        case(`opcode)
            0: // halt
                mem_w = 0;
                mem_r = 0;
                reg_w = 0;
                br = 0;
                hlt = 1;
            1,2,3,4,5,6: // ALU operations
                mem_w = 0;
                mem_r = 0;
                reg_w = 1;
                br = 0;
                hlt = 0;
            8: // b
                mem_w = 0;
                mem_r = 0;
                reg_w = 0;
                br = 1;
                hlt = 0;
            9: // be
                mem_w = 0;
                mem_r = 0;
                reg_w = 0;
                br = sr[0];
                hlt = 0;
            10: // bl
                mem_w = 0;
                mem_r = 0;
                reg_w = 0;
                br = sr[1];
                hlt = 0;
            11: // bg
                mem_w = 0;
                mem_r = 0;
                reg_w = 0;
                br = sr[2];
                hlt = 0;
            12: // lw
                mem_w = 0;
                mem_r = 1;
                reg_w = 1;
                br = 0;
                hlt = 0;
            13: // sw
                mem_w = 1;
                mem_r = 0;
                reg_w = 0;
                br = 0;
                hlt = 0;
            default: // cmp and nop
                mem_w = 0;
                mem_r = 0;
                reg_w = 0;
                br = 0;
                hlt = 0;
        endcase

        // branch and halt control
        if(!hlt)
        begin
            if(br)
                next_pc = `Im ? (registers[`reg1] + immediate) : address;
            else 
                next_pc = `pc + 1;
        end
        else
            next_pc = `pc; // if hlt = 1 don't update pc

        // alu operations
        case(`opcode)
            1: // add
                data_out = registers[`reg1] + op2;
            2: // sub
                data_out = registers[`reg1] - op2;
            3: // and
                data_out = registers[`reg1] & op2;
            4: // or
                data_out = registers[`reg1] | op2;
            5: // lsl
                data_out = registers[`reg1] << op2;
            6: // mov
                data_out = op2;
            13: // sw
                data_out = registers[`reg1];
            default:
                data_out = 0;
        endcase
    end

endmodule
