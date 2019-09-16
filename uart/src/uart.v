`define CLK_PER_HALF_CYCLE 542 // for 115200 baud
//`define CLK_PER_HALF_CYCLE 208333 // for 300 baud apparently
//`define CLK_PER_HALF_CYCLE 62500000 // for 1 baud

module uart (
  input wire clk_125MHz,
  input wire [7:0] tx_d,
  input wire tx_rdy,
  output reg tx = 1
);
  // Clock divider
  reg [31:0] clk_counter = 0;
  reg clk_uart = 0;

  always @ (posedge clk_125MHz)
  begin
    if (clk_counter == `CLK_PER_HALF_CYCLE)
    begin
      clk_counter = 0;
      clk_uart = ~clk_uart;
    end
    else
      clk_counter = clk_counter + 1;
  end

  // TX state machine
  reg [3:0] tx_bit = 0;

  always @ (posedge clk_uart)
  begin
    if (tx_bit == 0)
    begin
      tx <= 1;
      if (tx_rdy)
        tx_bit = 1;
    end
    else if (tx_bit == 1)
    begin
      tx <= 0;
      tx_bit <= 2;
    end
    else if (tx_bit == 10)
    begin
      tx <= 1;
      tx_bit <= 0;
    end
    else
    begin
      tx <= tx_d[tx_bit - 2];
      tx_bit <= tx_bit + 1;
    end
  end
endmodule
