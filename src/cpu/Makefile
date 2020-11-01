all: build flash
build:
	vivado -mode batch -source build.tcl -nojournal
flash:
	xsct flash.tcl
