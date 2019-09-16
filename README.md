# From the Transistor to the Web Browser: My Attempt

Let's see how feasible this is.

## Day 1
Finally got Vivado installed and understood roughly how to use it. Made a blinker.

Starting attempt at a UART. Using LED as TX pin; it seems to behave correctly at 1 baud :)

^ Really wish I had a scope. Just spent a couple hours wondering why nothing worked. Finally broke down and wrote a little Arduino program to take samples on a digital pin every 100us, and tried running the UART at 300 baud. This showed that my clock was roughly 28/11 times faster than the FTDI I was using as a referece. Turns out I was expecting a 50MHz clock but it was actually 125MHz. Now it all works very well.
