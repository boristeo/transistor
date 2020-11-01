all: build flash
build:
	vivado -mode batch -source build.tcl -nojournal 
flash:
	sudo ../../tools/jtag/loadsvf out/a.svf
