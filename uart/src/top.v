module top (
  input wire clk,
  input wire [3:0] btn,
  output wire [7:0] je,
  output wire [3:0] led
);
  assign led[0] = ~je[0];

  reg [7:0] data = 65;

  uart u (
    .clk_125MHz(clk),
    .tx_d(data),
    .tx_rdy(btn[0]),
    .tx(je[0])
  );

  always @ (posedge clk)
  begin
    if (btn[3])
    begin
      if (data >= 126)
        data = 33;
      else
        data = data + 1;
    end
  end

endmodule
