# From the Transistor to the Web Browser: My Attempt

Let's see how feasible this is.

## Day 1
Finally got Vivado installed and understood roughly how to use it. Made a blinker.

Starting attempt at a UART. Using LED as TX pin; it seems to behave correctly at 1 baud :)

^ Really wish I had a scope. Just spent a couple hours wondering why nothing worked. Finally broke down and wrote a little Arduino program to take samples on a digital pin every 100us, and tried running the UART at 300 baud. This showed that my clock was roughly 28/11 times faster than the FTDI I was using as a referece. Turns out I was expecting a 50MHz clock but it was actually 125MHz. Now it all works very well.

## Day 2
Thinking about how to do this whole CPU thing... I actually have very little idea of how to approach it. I think step 1 is to make the 32 registers, and make a state machine that takes opcodes in over serial (this will be easy, just collect 4 bytes; no support for RV-C) then returns the result over serial. This will let me quickly test the decode and ALU. Then I need to figure out how memory works.

Speaking of memory, I want to have caches. Probably just L1 for now. In case I want L2 and L3, Intel seems to do 32k L1I, 32 L1D, 256k L2 per core then 2m * #cores shared L3. I'll worry about this later.
