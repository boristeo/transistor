module test (
  input wire clk, 
  input wire enable, 
  input wire [7:0] rx_d,
  output reg [255:0] out, 
  output reg [3:0] out_bytecount, 
  output reg out_rdy,
  input wire out_buf_busy,
  output reg done
);

  reg sent_test = 0;

  always @(negedge clk) begin
    if (enable && ~sent_test && ~out_buf_busy) begin
      out_rdy <= 1;
      out <= 16'hfefe;
      out_bytecount <= 1;
      sent_test = 1;
      done <= 1;
    end
    else if (~enable) begin
      sent_test = 0;
      out_rdy <= 0;
    end
  end

endmodule
