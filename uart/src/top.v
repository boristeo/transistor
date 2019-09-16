`define CLK_PER_HALF_CYCLE 542 // for 115200 baud
//`define CLK_PER_HALF_CYCLE 208333 // for 300 baud apparently
//`define CLK_PER_HALF_CYCLE 62500000 // for 1 baud
module top (
  input wire clk,
  input wire [3:0] btn,
  output wire [7:0] je,
  output wire [3:0] led
);
  reg [31:0] clk_counter = 0;

  reg clk_uart = 0;

  reg [7:0] d_to_tx = 65;
  reg [3:0] tx_bit = 0;

  reg out = 1;

  assign led[0] = ~out;
  assign je[0] = out;

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
