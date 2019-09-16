module top (input wire clk, output wire [3:0] led);
  reg [31:0] counter;
  assign led[0] = counter[25];

  always @ (posedge clk) begin
    counter = counter + 1;
  end
endmodule
