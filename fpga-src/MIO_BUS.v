`timescale 1ns / 1ps

module MIO_BUS(
    input mem_w,
    input [15:0] sw_i,
    input [31:0] cpu_data_out,
    input [31:0] cpu_data_addr,
    input [31:0] ram_data_out,
    output reg [31:0] cpu_data_in,
    output reg [31:0] ram_data_in,
    output reg [6:0] ram_addr,
    output reg [31:0] cpuseg7_data,
    output reg ram_we,
    output reg seg7_we
);

    always @* begin
        ram_addr = 7'h0;
        ram_data_in = 32'h0;
        cpuseg7_data = 32'h0;
        cpu_data_in = 32'h0;
        seg7_we = 1'b0;
        ram_we = 1'b0;

        case (cpu_data_addr)
        32'hffff0004: begin
            cpu_data_in = {16'h0, sw_i};
        end
        32'hffff000c: begin
            cpuseg7_data = cpu_data_out;
            seg7_we = mem_w;
        end
        default: begin
            ram_addr = cpu_data_addr[8:2];
            ram_data_in = cpu_data_out;
            ram_we = mem_w;
            cpu_data_in = ram_data_out;
        end
        endcase
    end

endmodule
