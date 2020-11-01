cmake_minimum_required(VERSION 3.12)

add_gtest(uart_tests tests/uart_tests.cpp)
verilate(uart_tests SOURCES verilog/uart.v)

# Run tests after building
add_custom_command(
  TARGET uart_tests
  POST_BUILD
  COMMAND uart_tests
)
  
