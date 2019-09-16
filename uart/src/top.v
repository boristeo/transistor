module top (
  input wire clk,
  input wire [3:0] btn,
  inout wire [7:0] je,
  output wire [3:0] led
);

  reg tx_rdy;
  reg [7:0] tx_d = 65;

  wire rx_rdy;
  wire [7:0] rx_d;

  assign led[3:0] = rx_d[3:0];

  uart u (
    .clk_125MHz(clk),
    .tx_d(tx_d),
    .tx_rdy(tx_rdy),
    .tx(je[0]),
    .rx_d(rx_d),
    .rx_rdy(rx_rdy),
    .rx(je[1])
  );

  always @ (posedge clk)
  begin
    tx_rdy <= rx_rdy;
    if (rx_rdy)
    begin
      if (rx_d >= 65 && rx_d <= 90)
        tx_d <= rx_d + 32;
      else if (rx_d >= 97 && rx_d <= 122)
        tx_d <= rx_d - 32;
      else
        tx_d <= rx_d;
    end
  end

endmodule
