module byte_ser(
  input wire reset,
  input wire clk,
  input wire [255:0] din,
  input wire [3:0] din_bytecount,
  input wire shift_begin,
  input wire shift_enable,
  output reg [7:0] out,
  output reg out_rdy
  );

  reg [4:0] state = 0;
  reg [255:0] data = 0;

  always @(posedge clk) begin
    if (reset) begin
      state = 0;
      out_rdy = 0;
    end
    else if (state == 0 && shift_begin) begin
      state = din_bytecount + 1;
      data = din;
    end
    else if (state != 0 && shift_enable) begin
      out <= data[7:0];
      data <= data >> 8;
      state <= state - 1;
      out_rdy <= 1;
    end
    else begin
      out_rdy = 0;
    end
  end
endmodule

  
