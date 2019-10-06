#!/usr/bin/env python3
from pyftdi import jtag
from pyftdi.bits import BitSequence as bs
from binascii import hexlify

### CONSTANTS

TO_IDLE = bs('111110')
IDLE_TO_SHIR = bs('1100')
IDLE_TO_SHDR = bs('100')


# instruction register is actually 10 bits, but that doesn't seem to matter
I_EXTEST    = bs('00000')
I_SAMPLE    = bs('00001')
I_USER1     = bs('00010')
I_USER2     = bs('00011')
I_CFG_OUT   = bs('00100')
I_CFG_IN    = bs('00101')
I_INTEST    = bs('00111')
I_INTEST    = bs('01000')
I_USERCODE  = bs('01000')
I_IDCODE    = bs('01001')
I_HIGHZ     = bs('01010')
I_JSTART    = bs('01100')
I_BYPASS    = bs('11111')

R_CRC       = bs('00000')
R_FAR       = bs('00001')
R_FDRI      = bs('00010')
R_FDRO      = bs('00011')
R_CMD       = bs('00100')
R_CTL0      = bs('00101')
R_MASK      = bs('00110')
R_STAT      = bs('00111')
R_LOUT      = bs('01000')
R_COR0      = bs('01001')
R_MFWR      = bs('01010')
R_CBC       = bs('01011')
R_IDCODE    = bs('01100')
R_AXSS      = bs('01101')
R_COR1      = bs('01110')
R_WBSTAR    = bs('10000')
R_TIMER     = bs('10001')
R_BOOTSTS   = bs('10110')
R_CTL1      = bs('11000')
R_BSPI      = bs('11111')

C_NULL      = bs('00000')
C_WCFG      = bs('00001')
C_MFW       = bs('00010')
C_DGHIGH    = bs('00011')
C_RCFG      = bs('00100')
C_START     = bs('00101')
C_RCAP      = bs('00110')
C_RCRC      = bs('00111')
C_AGHIGH    = bs('01000')
C_SWITCH    = bs('01001')
C_GRESTORE  = bs('01010')
C_SHUTDOWN  = bs('01011')
C_GCAPTURE  = bs('01100')
C_DESYNC    = bs('01101')
C_IPROG     = bs('01111')
C_CRCC      = bs('10000')
C_LTIMER    = bs('10001')
C_BSPI_READ = bs('10010')
C_FALL_EDGE = bs('10011')

W_SYNC      = b'\xaa\x99\x55\x66'
W_NOOP      = b'\x20\x00\x00\x00'
W_DUMMY     = b'\xff\xff\xff\xff'
W_readSTAT  = b'\x28\x00\xe0\x01'

### Adding utility functions to pyftdi
def configure(self, url):
  self._ftdi.open_mpsse_from_url(url, direction=self.direction, frequency=self._frequency)
  self._ftdi.write_data(bytearray(b'\x8a\x97\x8d'))
  self._ftdi.write_data(bytearray(b'\x86\xdb\x05'))
  self._ftdi.write_data(bytearray(b'\x80\xc8\xfb'))
  self._ftdi.write_data(bytearray(b'\x82\x00\x00'))
setattr(jtag.JtagController, 'configure', configure)

def rread(self, reg, bits=64):
  self.write_tms(TO_IDLE)
  self.write_tms(IDLE_TO_SHDR)
  return hexlify(bytearray(self.shift_register(bs('0' * bits)).tobytes()))
setattr(jtag.JtagController, 'rread', rread)

def readstat(self):
  self.write_tms(TO_IDLE)
  self.write_tms(IDLE_TO_SHIR)
  self.write(I_CFG_IN)
  
  self.write_tms(TO_IDLE)
  self.write_tms(IDLE_TO_SHDR)
  self._write_bytes_raw(W_SYNC + W_NOOP + W_readSTAT + W_DUMMY + W_DUMMY)
  self.sync()

  self.write_tms(TO_IDLE)
  self.write_tms(IDLE_TO_SHIR)
  self.write(I_CFG_OUT)

  self.write_tms(TO_IDLE)
  self.write_tms(IDLE_TO_SHDR)
  return hexlify(bytearray(self.shift_register(bs('0' * 32)).tobytes()))
setattr(jtag.JtagController, 'readstat', readstat)

def cwrite(self, cmd):
  self.write_tms(TO_IDLE)
  self.write_tms(IDLE_TO_SHIR)
  self.write(I_CMD)
  
  self.write_tms(TO_IDLE)
  self.write_tms(IDLE_TO_SHDR)
  self.shift_register(cmd)

  self.write_tms(TO_IDLE)
  self.write_tms(IDLE_TO_SHIR)
  self.write(I_FAR)

  self.write_tms(TO_IDLE)
  self.write_tms(IDLE_TO_SHDR)
  self.shift_register(bs('0' * 64))
setattr(jtag.JtagController, 'cwrite', cwrite)


### Redoing the config from pyftdi 'cause theirs doesn't work
j = jtag.JtagController()
url = 'ftdi://0x403:0x6010/1'
j.configure(url)

# Setup env
print(j.rread(R_IDCODE))

