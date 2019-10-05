#!/usr/bin/env python3
from pyftdi import jtag
from pyftdi.bits import BitSequence as bs
from binascii import hexlify


# Adding utility functions to write directly to ftdi
def put(self, data):
  self._ftdi.write_data(bytearray(data))
setattr(jtag.JtagController, 'put', put)

def get(self, bytes_ct):
  return self._ftdi.read_data(bytes_ct)
setattr(jtag.JtagController, 'get', get)


# redoing the config from pyftdi 'cause theirs doesn't work
j = jtag.JtagController()
url = 'ftdi://0x403:0x6010/1'
j.configure(url)
j.put(b'\x8a\x97\x8d')
j.put(b'\x86\xdb\x05')
j.put(b'\x80\xc8\xfb')
j.put(b'\x82\x00\x00')


### CONSTANTS

TO_IDLE = bs('111110')
IDLE_TO_SHIR = bs('1100')
IDLE_TO_SHDR = bs('100')

I_IDCODE = bs('00000110')

def read_dr(bits=64):
  j.write_tms(TO_IDLE)
  j.write_tms(IDLE_TO_SHDR)
  return hexlify(bytearray(j.shift_register(bs('0' * bits)).tobytes()))
  
def write_instruction(instr):
  j.write_tms(TO_IDLE)
  j.write_tms(IDLE_TO_SHIR)
  j.shift_register(instr)

# Setup env
j.write_tms(TO_IDLE)
