all: build flash
build:
	vivado -mode batch -source build.tcl -nojournal -nolog | tee log/buildlog.txt
flash:
	xsct flash.tcl
