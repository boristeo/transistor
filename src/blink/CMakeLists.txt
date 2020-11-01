cmake_minimum_required(VERSION 3.12)

add_gtest(blink_tests tests/blink_tests.cpp)
verilate(blink_tests SOURCES verilog/top.v)

# Run tests after building
add_custom_command(
  TARGET blink_tests
  POST_BUILD
  COMMAND blink_tests
)
  
