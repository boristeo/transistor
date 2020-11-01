module uart (
  input wire clk,
  input wire [7:0] tx_byte,
  input wire tx_rdy,
  output reg tx = 1,
  output reg [7:0] rx_byte = 0,
  output reg rx_rdy = 0,
  input wire rx
);

  // TX state machine
  reg [3:0] tx_state = 0;
  // When idle, tx pin high
  always @ (posedge clk)
  begin
    // State 0 - if tx_ready high, send start bit and move to state 1
    if (tx_state == 0) begin
      if (tx_rdy) begin
        tx_state <= 1;
        tx <= 0;
      end
      else
        tx <= 1;
    end
    // State 9 - send stop bit
    else if (tx_state == 9) begin
      tx <= 1;
      tx_state <= 0;
    end
    // State 1-8 - write bit from tx_byte to tx
    else begin
      tx <= tx_byte[tx_state - 1];
      tx_state <= tx_state + 1;
    end
  end


  // RX state machine
  reg [3:0] rx_state = 0;
  // When idle, rx pin high
  always @ (posedge clk)
  begin
    // State 0 - if rx pin low, move to state 1
    if (rx_state == 0) begin
      rx_rdy <= 0;
      if (~rx)
        rx_state <= 1;
    end
    // State 9 - Done reading byte. Back to state 0
    else if (rx_state == 9) begin
      rx_state <= 0;
      rx_rdy <= 1; // WRONG: may set rdy before last bit copied to rx_byte
    end
    // States 1-8 - Record incoming rx bit in rx_byte
    else begin
      rx_byte[rx_state - 1] <= rx;
      rx_state <= rx_state + 1;
    end
  end
endmodule
