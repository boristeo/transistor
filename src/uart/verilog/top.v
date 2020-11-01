`define CLK_PER_HALF_CYCLE 542 // for 115200 baud
//`define CLK_PER_HALF_CYCLE 208333 // for 300 baud apparently
//`define CLK_PER_HALF_CYCLE 62500000 // for 1 baud

module top (
  input wire clk,
  input wire [3:0] btn,
  input wire rx,
  output wire tx,
  output wire [3:0] led
);

  reg tx_rdy;
  reg [7:0] tx_byte = 65;

  wire rx_rdy;
  wire [7:0] rx_byte;

  assign led[3:0] = rx_byte[3:0];

  // Clock divider
  reg [31:0] clk_counter = 0;
  reg clk_uart = 0;

  always @ (posedge clk)
  begin
    if (clk_counter == `CLK_PER_HALF_CYCLE)
    begin
      clk_counter <= 0;
      clk_uart <= ~clk_uart;
    end
    else
      clk_counter <= clk_counter + 1;
  end

  uart u (
    .clk(clk_uart),
    .tx_byte(tx_byte),
    .tx_rdy(tx_rdy),
    .tx(tx),
    .rx_byte(rx_byte),
    .rx_rdy(rx_rdy),
    .rx(rx)
  );

  always @ (negedge clk_uart)
  begin
    tx_rdy <= rx_rdy;
    if (rx_rdy)
    begin
      if (rx_byte >= 65 && rx_byte <= 90)
        tx_byte <= rx_byte + 32;
      else if (rx_byte >= 97 && rx_byte <= 122)
        tx_byte <= rx_byte - 32;
      else
        tx_byte <= rx_byte;
    end
  end

endmodule
