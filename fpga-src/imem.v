module imem #(
    parameter INIT_FILE = "rv32_sid_sort_fpga.mem"
)(
    input [6:0] a,
    output [31:0] spo
);

    (* rom_style = "block" *) reg [31:0] rom [0:127];
    integer i;

    initial begin
        for (i = 0; i < 128; i = i + 1) begin
            rom[i] = 32'h0000_0013;
        end
        $readmemh(INIT_FILE, rom);
    end

    assign spo = rom[a];

endmodule
