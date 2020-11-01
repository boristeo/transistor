#include <stdlib.h>
#include <iostream>
#include "Vuart.h"
#include "verilated.h"
#include <gtest/gtest.h>

#include <iomanip>
#include <cstdint>
#include <bitset>

// Testing just the uart module
TEST(uart_tests, RXTest) {
	Vuart m{};

  // Reads start on posedge, make sure clk low
  m.clk = 0;
  m.eval();

  // Master signals start of write by low bit
  m.rx = 0;
  m.clk = 1;
  m.eval();
  m.clk = 0;
  m.eval();

  // Master starts transferring byte
  uint8_t test_input = 0b11110101;
  for (auto i = 0; i < 8; ++i) {
    m.rx = (test_input >> i) & 1;
    m.clk = 1;
    m.eval();
    m.clk = 0;
    m.eval();
  }
  EXPECT_EQ(m.rx_rdy, 0) << "UART ready before last clock";
  m.rx = 0; // stop bit
  m.clk = 1;
  m.eval();
  m.clk = 0;
  m.eval();
  EXPECT_EQ(m.rx_rdy, 1) << "UART not ready after full byte received";
  EXPECT_EQ(m.rx_byte, test_input) << "UART received incorrect data";
}

TEST(uart_tests, TXTest) {
	Vuart m{};

  // Writes start on posedge, make sure clk low
  m.clk = 0;
  m.eval();

  // Set data to write and clock to begin tx
  m.tx_byte = 0b10101111;
  m.tx_rdy = 1;
  m.clk = 1;
  m.eval();
  m.clk = 0;
  m.eval();
  EXPECT_EQ(m.tx, 0) << "TX did not start";

  // 
  uint8_t data_sent = 0;
  for (auto i = 0; i < 8; ++i) {
    m.clk = 1;
    m.eval();
    data_sent |= m.tx << i;
    m.clk = 0;
    m.eval();
  }
  // One more clock for stop bit
  m.clk = 1;
  m.eval();
  EXPECT_EQ(m.tx, 1) << "TX not sending stop bit";

  EXPECT_EQ(m.tx_byte, data_sent) << "UART sent (TX) incorrect data";
}
