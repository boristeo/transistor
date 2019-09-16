//`define CLK_PER_HALF_CYCLE 83333 // for 300 baud
`define CLK_PER_HALF_CYCLE 50000000 // for 1 baud
module top (
  input wire clk,
  input wire [3:0] btn,
  output wire [3:0] led
);
  reg [31:0] clk_counter;

  reg clk_uart = 0;

  reg [7:0] d_to_tx = 8'b01010101;
  reg [3:0] tx_bit = 0;

  reg out = 1;

  assign led[0] = out;
  assign led[3] = clk_uart;

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

  always @ (posedge clk_uart)
  begin
    if (tx_bit == 0)
    begin
      out <= 1;
      if (btn[0])
        tx_bit = 1;
    end
    else if (tx_bit == 1)
    begin
      out <= 0;
      tx_bit <= 2;
    end
    else if (tx_bit == 10)
    begin
      out <= 1;
      tx_bit <= 0;
    end
    else
    begin
      out <= d_to_tx[tx_bit - 2];
      tx_bit <= tx_bit + 1;
    end
  end
endmodule
