`define CLK_PER_HALF_CYCLE 542 // for 115200 baud
//`define CLK_PER_HALF_CYCLE 208333 // for 300 baud apparently
//`define CLK_PER_HALF_CYCLE 62500000 // for 1 baud

module top (
  input wire clk,
  inout wire [7:0] je,
  output wire [3:0] led
);


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

  wire rx_rdy;
  wire [7:0] rx_d;

  wire [7:0] tx_d;
  wire tx_en;
  wire tx_rdy;

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

  wire tx_shift_begin;
  wire [255:0] tx_shift_d;
  wire [3:0] tx_shift_bytecount;
  wire tx_shift_empty;
  byte_ser s (
    .reset(0),
    .clk(clk),
    .din(tx_shift_d),
    .din_bytecount(tx_shift_bytecount),
    .shift_begin(tx_shift_begin),
    .shift_enable(tx_rdy),
    .out(tx_d),
    .out_rdy(tx_en)
  );

  reg [31:0] registers [1:31];
  reg [31:0] pc;

  reg testing = 0;
  wire test_done;
  reg reset_pending = 0;

  assign led[0] = testing;

  reg [7:0] instruction = 0;

  test t (
    .clk(clk),
    .enable(testing),
    .rx_d(rx_d),
    .out(tx_shift_d),
    .out_bytecount(tx_shift_bytecount),
    .out_rdy(tx_shift_begin),
    .out_buf_busy(tx_en),
    .done(test_done)
  );
    

  always @(negedge clk_uart) begin
    if (rx_rdy) begin
      if (rx_d == 8'hFF) begin
        // reset
        if (test_done || reset_pending) begin
          // force recover control
          testing = 0;
        end
        else begin
          reset_pending = 1;
        end
      end
      else if (rx_d == 8'hFE) begin
        // test begin
        testing = 1;
      end
    end
    if (reset_pending && test_done) begin
      testing = 0;
    end
  end

endmodule
