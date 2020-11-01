all: build flash
build:
	vivado -mode batch -source build.tcl -nojournal -nolog | tee buildlog.txt
flash:
	sudo ../../tools/jtag/loadsvf out/a.svf
