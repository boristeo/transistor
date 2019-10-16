module uart (
  input wire clk_uart,
  input wire [7:0] tx_d,
  input wire tx_en,
  output wire tx_rdy,
  output reg tx = 1,
  output reg [7:0] rx_d = 0,
  output reg rx_rdy = 0,
  input wire rx
);

  // TX state machine
  reg [3:0] tx_bit = 0;
  assign tx_rdy = tx_bit == 0;

  always @ (posedge clk_uart)
  begin
    if (tx_bit == 0)
    begin
      tx <= 1;
      if (tx_en)
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
    begin
      rx_bit <= 0;
      rx_rdy <= 1;
    end
    else
    begin
      rx_d[rx_bit - 1] <= rx;
      rx_bit <= rx_bit + 1;
    end
  end
endmodule
