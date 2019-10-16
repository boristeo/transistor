set PART "xc7z010clg400-1"
set OUTDIR "out"
set SRCDIR "src"
set XDCDIR "xdc"

read_verilog $SRCDIR/top.v
read_verilog $SRCDIR/uart.v
read_xdc $XDCDIR/zybo.xdc

synth_design -top top -part $PART
write_checkpoint -force $OUTDIR/post_synth.dcp

opt_design
write_checkpoint -force $OUTDIR/post_opt.dcp

place_design
write_checkpoint -force $OUTDIR/post_place.dcp

route_design
write_checkpoint -force $OUTDIR/post_route.dcp

write_debug_probes -force $OUTDIR/debug.ltx
write_bitstream -force $OUTDIR/a.bit
