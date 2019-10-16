# From the Transistor to the Web Browser: My Attempt

The old 'README' is now in PROGRESS.md. This file now contains instructions for recreating my results.

## What I'm using
* Digilent Zybo Zynq-7000 Development Board
* Xilinx Vivado Webpack Edition (Running headless in a VM or Docker container is sufficient)
* Unix-based development platform (USB stuff doesn't seem to work on Windows and I have no plans to fix it) 
* FTDI 232RL-based USB-serial converter board

## Project structure
```
project root/
|-- tools/
|   |-- jtag/ 
|   |   |-- jtag2232.py : USB FTDI JTAG library
|   |   |-- loadSVE     : SVE file interpreter tool
|   | 
|   |-- asm/
|       |-- rvas        : RV64MI assembler
|
|-- src/ 
    |-- blink/
    |   |-- ...         : hello world
    |
    |-- uart/
    |   |-- ...         : Interface with FTDI breakout board 
    |
    |-- cpu/
        |-- ...         : RISC-V pipeline 
```

## Building a subproject
Each subproject directory contains a Makefile that uses Vivado to synthesize the sources, then writes a bitstream in .bit format (a.bit) as well as an SVF file (a.svf) in the /out subdirectory. 

## Using loadSVE to flash bitstream to FPGA
loadSVE is a simple tool I made for executing JTAG routines described by SVF statements. It is a far simpler, though less robust solution than using Xilinx's xsct along with the Digilent plugin.

Run loadSVF like:
```
./loadSVE [-ip] <file>
```
If no file is provided, the tool parses input from stdin, making it possible to do: 
```
./loadSVE < file
```
This comes in useful when working over ssh.



