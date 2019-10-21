module decode (
  input wire clk,
  input wire enable,
  input wire [31:0] word,
  output reg [16:0] op,
  output reg [63:0] arg1,
  output reg [63:0] arg2
);

  always @(posedge clk) begin
    if (enable) begin
      op[6:0] = word[6:0];
      op[9:7] = word[14:12];
      op[16:10] = word[31:25];
    end
  end

endmodule

