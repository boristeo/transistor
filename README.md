# From the Transistor to the Web Browser: My Attempt

Let's see how feasible this is.

## Day 1
Finally got Vivado installed and understood roughly how to use it. Made a blinker.

Starting attempt at a UART. Using LED as TX pin; it seems to behave correctly at 1 baud :)

^ Really wish I had a scope. Just spent a couple hours wondering why nothing worked. Finally broke down and wrote a little Arduino program to take samples on a digital pin every 100us, and tried running the UART at 300 baud. This showed that my clock was roughly 28/11 times faster than the FTDI I was using as a referece. Turns out I was expecting a 50MHz clock but it was actually 125MHz. Now it all works very well.

## Day 2
Thinking about how to do this whole CPU thing... I actually have very little idea of how to approach it. I think step 1 is to make the 32 registers, and make a state machine that takes opcodes in over serial (this will be easy, just collect 4 bytes; no support for RV-C) then returns the result over serial. This will let me quickly test the decode and ALU. Then I need to figure out how memory works.

Speaking of memory, I want to have caches. Probably just L1 for now. In case I want L2 and L3, Intel seems to do 32k L1I, 32 L1D, 256k L2 per core then 2m * #cores shared L3. I'll worry about this later.

## Day 3
Started writing a RISC-V assembler in Python. Other than that I've just been researching how real systems do all this stuff

## Day 4
Assembler is starting to work. Only did R and I instructions for now, but the others should be just a couple lines of code

## Day 19 (though I'm gonna consider it day 7)
Took a break of about two weeks. Decided that it was annoying to have to be at home to be working on this. Started writing a utility to program the FPGA over JTAG around Wednesday of this past week(?).

Coerced someone's Python FTDI library into working. Rewriting it would be too much hassles, though it's too bloated for my liking.

Also, turns out there was a logic analyzer in the room across mine all along. It's heavy, loud, and older than me, but saved me a ton of time in realizing that the FTDI's clock output was inverted.

## Day 14 - Update on the past week
My JTAG idea worked. Still doesn't solve my problem of not knowing how to load things into SPI, but at least I can test my Verilog designs now.

The JTAG solution has two parts: the first is an FTDI-JTAG adapter class that interfaces with the FTDI 2232H on the Zybo dev board I'm using, and the second part is an SVF file interpreter that calls the appropriate functions from the FTDI-JTAG adapter. A lot of the code is questionable, but now that I have a way to test without having to pull out the logic analyzer, I'll refactor it.

Next steps for this project are to add UART functionality to the FTDI - this should not be hard as that's basically its intended purpose. This will not add any new functionality to the FPGA designs, but it will keep me from having to use a second FTDI and two wires any time I want to work on this.

