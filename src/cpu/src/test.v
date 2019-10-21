module test (
  input wire clk, 
  input wire enable, 
  input wire [7:0] rx_d,
  output reg [255:0] out, 
  output reg [3:0] out_bytecount, 
  output reg out_rdy 
);

  reg sent_test = 0;

  always @(negedge clk) begin
    if (enable && ~sent_test) begin
      out_rdy <= 1;
      out <= 8'hfe;
      out_bytecount <= 0;
      sent_test = 1;
    end
    else if (~enable) begin
      sent_test = 0;
      out_rdy <= 0;
    end
  end

endmodule
