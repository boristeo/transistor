`define CLK_PER_HALF_CYCLE 542 // for 115200 baud
//`define CLK_PER_HALF_CYCLE 208333 // for 300 baud apparently
//`define CLK_PER_HALF_CYCLE 62500000 // for 1 baud

module top (
  input wire clk,
  inout wire [7:0] je,
  output reg [3:0] led
);

  reg tx_en;
  wire tx_rdy;
  reg [7:0] tx_d = 65;

  wire rx_rdy;
  wire [7:0] rx_d;

  // Clock divider
  reg [31:0] clk_counter = 0;
  reg clk_uart = 0;

  always @ (posedge clk)
  begin
    if (clk_counter == `CLK_PER_HALF_CYCLE)
    begin
      clk_counter = 0;
      clk_uart = ~clk_uart;
    end
    else
      clk_counter = clk_counter + 1;
  end

  uart u (
    .clk_uart(clk_uart),
    .tx_d(tx_d),
    .tx_en(tx_en),
    .tx_rdy(tx_rdy),
    .tx(je[0]),
    .rx_d(rx_d),
    .rx_rdy(rx_rdy),
    .rx(je[1])
  );

  reg [31:0] registers [1:31];
  reg [31:0] instruction = 0;
  reg [3:0] filled = 0;
  reg sending = 0;

  always @ (negedge clk_uart)
  begin
    if (~sending)
    begin
      tx_en <= 0;
      if (rx_rdy)
      begin
        instruction <= instruction | (rx_d << filled * 8);
        filled <= filled + 1;
        led[filled] <= 1;
        if (filled + 1 >= 4)
          sending = 1;
      end
    end
    else
    begin
      if (tx_rdy)
      begin
        tx_d <= (instruction >> (filled - 1) * 8) & 8'hFF;
        tx_en <= 1;
        filled <= filled - 1;
        led[filled - 1] <= 0;
        if (filled - 1 == 0)
        begin
          sending <= 0;
          instruction <= 0;
        end
      end
    end
  end

endmodule
