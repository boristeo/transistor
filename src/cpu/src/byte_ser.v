module byte_ser(
  input wire reset,
  input wire clk,
  input wire [255:0] din,
  input wire [3:0] din_bytecount,
  input wire shift_begin,
  input wire shift_enable,
  output reg [7:0] out,
  output wire full,
  output wire empty
  );

  reg [4:0] state = 0;
  reg [255:0] data = 0;

  assign full = state != 0;
  assign empty = state == 0;

  always @(posedge clk) begin
    if (reset) begin
      state = 0;
    end
    else if (state == 0 && shift_begin) begin
      state = din_bytecount + 1;
      data = din;
    end
    else if (shift_enable) begin
      out <= data[7:0];
      data <= data << 8;
      state <= state - 1;
    end
  end
endmodule

  
