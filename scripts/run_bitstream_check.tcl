set script_dir [file dirname [file normalize [info script]]]
set lab_dir [file normalize [file join $script_dir ..]]
set out_dir [file join $lab_dir vivado bitstream_check]

file mkdir $out_dir
cd [file join $lab_dir fpga-src]

read_verilog [file join $lab_dir source-sc alu.v]
read_verilog [file join $lab_dir source-sc ctrl.v]
read_verilog [file join $lab_dir source-sc ctrl_encode_def.v]
read_verilog [file join $lab_dir source-sc EXT.v]
read_verilog [file join $lab_dir source-sc NPC.v]
read_verilog [file join $lab_dir source-sc PC.v]
read_verilog [file join $lab_dir source-sc RF.v]
read_verilog [file join $lab_dir source-sc SCCPU.v]
read_verilog [file join $lab_dir source-sc dm.v]

read_verilog [file join $lab_dir fpga-src clk_div.v]
read_verilog [file join $lab_dir fpga-src imem.v]
read_verilog [file join $lab_dir fpga-src lab6_sid_sort_fpga_top.v]
read_verilog [file join $lab_dir fpga-src MIO_BUS.v]
read_verilog [file join $lab_dir fpga-src Multi_CH32.v]
read_verilog [file join $lab_dir fpga-src seg7x16.v]

read_xdc [file join $lab_dir constraints Nexys4DDR_Lab6_CPU.xdc]

synth_design -top lab6_sid_sort_fpga_top -part xc7a100tcsg324-1
opt_design
place_design
route_design
write_bitstream -force [file join $out_dir lab6_sid_sort_fpga_top.bit]

puts "Generated bitstream: [file join $out_dir lab6_sid_sort_fpga_top.bit]"
exit 0
