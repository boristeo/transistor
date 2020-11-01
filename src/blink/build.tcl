set PART "xc7z010clg400-1"
set OUTDIR "out"
set SRCDIR "verilog"
set XDCDIR "xdc"

read_verilog $SRCDIR/top.v

synth_design -top top -part $PART
write_checkpoint -force $OUTDIR/post_synth.dcp

read_xdc $XDCDIR/zybo.xdc

opt_design
write_checkpoint -force $OUTDIR/post_opt.dcp

place_design
write_checkpoint -force $OUTDIR/post_place.dcp

route_design
write_checkpoint -force $OUTDIR/post_route.dcp

write_debug_probes -force $OUTDIR/debug.ltx
write_bitstream -force $OUTDIR/a.bit

open_hw
connect_hw_server -quiet

create_hw_target zybo
open_hw_target [get_hw_targets -regexp .*/zybo]
set device0 [create_hw_device -part $PART]
set_property PROGRAM.FILE $OUTDIR/a.bit $device0
report_hw_targets
program_hw_devices -force -svf_file $OUTDIR/a.svf $device0
close_hw_target


