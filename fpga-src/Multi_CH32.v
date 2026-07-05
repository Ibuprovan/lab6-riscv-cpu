`timescale 1ns / 1ps

module Multi_CH32(
    input clk,
    input rst,
    input EN,
    input [5:0] ctrl,
    input [31:0] Data0,
    input [31:0] data1,
    input [31:0] data2,
    input [31:0] data3,
    input [31:0] data4,
    input [31:0] data5,
    input [31:0] data6,
    input [31:0] data7,
    input [31:0] reg_data,
    output reg [31:0] seg7_data
);

    reg [31:0] disp_data = 32'hAA55_55AA;

    always @* begin
        casex (ctrl)
        6'b000000: seg7_data = disp_data;
        6'b000001: seg7_data = data1;
        6'b000010: seg7_data = data2;
        6'b000011: seg7_data = data3;
        6'b000100: seg7_data = data4;
        6'b000101: seg7_data = data5;
        6'b000110: seg7_data = data6;
        6'b000111: seg7_data = data7;
        6'b001xxx: seg7_data = 32'hFFFF_FFFF;
        6'b01xxxx: seg7_data = 32'hFFFF_FFFF;
        6'b1xxxxx: seg7_data = reg_data;
        endcase
    end

    always @(posedge rst or posedge clk) begin
        if (rst)
            disp_data <= 32'hAA55_55AA;
        else if (EN)
            disp_data <= Data0;
    end

endmodule
