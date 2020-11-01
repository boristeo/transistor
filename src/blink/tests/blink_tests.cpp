#include <stdlib.h>
#include <iostream>
#include <iomanip>
#include <bitset>

#include "gtest/gtest.h"

#include "Vtop.h"
#include "verilated.h"

TEST(blink_tests, BlinkTest) {
	Vtop m{};

  for (auto i = 0; i < (1 << 25) - 1; ++i) {
    auto last = m.led;
    m.clk = 0;
    m.eval();
    m.clk = 1;
    m.eval();

    ASSERT_NE(m.led, 1);
  }
  for (auto i = 0; i < (1 << 25) - 1; ++i) {
    auto last = m.led;
    m.clk = 0;
    m.eval();
    m.clk = 1;
    m.eval();

    ASSERT_EQ(m.led, 1);
  }
}
