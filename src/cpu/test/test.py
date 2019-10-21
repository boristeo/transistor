#!/usr/bin/env python3

import serial

class CPUDebugServer:
  def __init__(self, port, xlen_bytes=4):
    self.serial = serial.Serial(port, 115200, timeout=1)
    self.reset()
    self.test_begin()
    response = self.serial.read(2)
    print(response)
    if response != b'\xfe\xfe':
      raise Exception('Expected 0xFE response on test begin')
    self._xlen_bytes = xlen_bytes

  def reset(self):
    self.serial.write(bytes([0xff]))

  def test_begin(self):
    self.serial.write(bytes([0xfe]))

  def locking_test(self):
    self.serial.write(bytes([0xff, 0xfe, 0xff, 0xfe, 0xff, 0xfe, 0xff, 0xfe, 0xff]))
    response = self.serial.read(8)
    print(response)
    if response != b'\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe':
      raise Exception('Expected 4 test begin responses')



  def read_reg(self, reg):
    if not 0 <= reg <= 31: raise Exception('Register index out of bounds')
    self.serial.write(bytes([reg]))
    self.serial.read(self._xlen_bytes)

  def write_reg(self, reg, value):
    if isinstance(value, int):
      value = value.to_bytes('big')
    if not isinstance(value, bytes) and not isinstance(value, bytearray): raise Exception('Can write register only with bytes')
    if not len(value) != self._xlen_bytes: raise Exception('Value must match size of register')
    if not 0 <= reg <= 31: raise Exception('Register index out of bounds')
    self.serial.write(bytes([0x80 & reg]) + value)


cpu = CPUDebugServer('/dev/tty.usbserial-AD01V58N')
cpu.locking_test()
