set script_dir [file dirname [file normalize [info script]]]
set lab_dir [file normalize [file join $script_dir ..]]
set project_dir [file join $lab_dir vivado lab6_sid_sort_fpga]

file mkdir $project_dir

create_project lab6_sid_sort_fpga $project_dir -part xc7a100tcsg324-1 -force

set board_name "digilentinc.com:nexys4_ddr:part0:1.1"
if {[llength [get_board_parts -quiet $board_name]] > 0} {
    set_property board_part $board_name [current_project]
} else {
    puts "Board part $board_name is not installed; using device part xc7a100tcsg324-1 only."
}

add_files [file join $lab_dir source-sc alu.v]
add_files [file join $lab_dir source-sc ctrl.v]
add_files [file join $lab_dir source-sc ctrl_encode_def.v]
add_files [file join $lab_dir source-sc EXT.v]
add_files [file join $lab_dir source-sc NPC.v]
add_files [file join $lab_dir source-sc PC.v]
add_files [file join $lab_dir source-sc RF.v]
add_files [file join $lab_dir source-sc SCCPU.v]
add_files [file join $lab_dir source-sc dm.v]

add_files [file join $lab_dir fpga-src clk_div.v]
add_files [file join $lab_dir fpga-src imem.v]
add_files [file join $lab_dir fpga-src lab6_sid_sort_fpga_top.v]
add_files [file join $lab_dir fpga-src MIO_BUS.v]
add_files [file join $lab_dir fpga-src Multi_CH32.v]
add_files [file join $lab_dir fpga-src seg7x16.v]

add_files [file join $lab_dir fpga-src rv32_sid_sort_fpga.mem]
set mem_file [get_files [file join $lab_dir fpga-src rv32_sid_sort_fpga.mem]]
if {[llength $mem_file] > 0} {
    set_property file_type {Memory File} $mem_file
}

add_files -fileset constrs_1 [file join $lab_dir constraints Nexys4DDR_Lab6_CPU.xdc]

set_property top lab6_sid_sort_fpga_top [current_fileset]
update_compile_order -fileset sources_1

puts "Created Vivado project: $project_dir"
