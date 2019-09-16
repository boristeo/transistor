`define CLK_PER_HALF_CYCLE 542 // for 115200 baud
//`define CLK_PER_HALF_CYCLE 208333 // for 300 baud apparently
//`define CLK_PER_HALF_CYCLE 62500000 // for 1 baud

module uart (
  input wire clk_125MHz,
  input wire [7:0] tx_d,
  input wire tx_rdy,
  output reg tx = 1,
  output reg [7:0] rx_d = 0,
  output reg rx_rdy = 0,
  input wire rx
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

  // RX state machine
  reg [3:0] rx_bit = 0;

  always @ (posedge clk_uart)
  begin
    if (rx_bit == 0)
    begin
      rx_rdy = 0;
      if (~rx)
        rx_bit = 1;
    end
    else if (rx_bit == 9)
      rx_bit <= 0;
    else
    begin
      rx_d[rx_bit - 1] <= rx;
      rx_bit <= rx_bit + 1;
      rx_rdy <= rx_bit == 8;
    end
  end
endmodule
