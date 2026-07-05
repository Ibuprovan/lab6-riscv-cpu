`timescale 1ns / 1ps

module clk_div(
    input clk,
    input rst,
    input SW15,
    output Clk_CPU
);

    reg [31:0] clkdiv;

    always @(posedge clk or posedge rst) begin
        if (rst)
            clkdiv <= 32'b0;
        else
            clkdiv <= clkdiv + 1'b1;
    end

    assign Clk_CPU = SW15 ? clkdiv[25] : clkdiv[2];

endmodule
