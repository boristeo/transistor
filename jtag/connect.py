#!/usr/bin/env python3
from binascii import hexlify
from jtag2232 import JTAG2232
from pyftdi.bits import BitSequence
bs = BitSequence


# By default Zynq has PL portion and PS portion in cascaded mode:
# DAP FIRST IN CHAIN BY DEFAULT
# PL TAP IR is 6 bits. PS DAP IR is 4 bits 
# DAP bypassed when PS not in reset

# Instructions expected with LSB first, so I reverse them and shift MSB first
# Shift 1 on TMS in parallel with final bit
TAP_EXTEST               = (6, bytes([0b000000]))
TAP_SAMPLE               = (6, bytes([0b000001]))
TAP_USER1                = (6, bytes([0b000010]))
TAP_USER2                = (6, bytes([0b000011]))
TAP_USER3                = (6, bytes([0b100010]))
TAP_USER4                = (6, bytes([0b100011]))
TAP_CFG_OUT              = (6, bytes([0b000100]))
TAP_CFG_IN               = (6, bytes([0b000101]))
TAP_USERCODE             = (6, bytes([0b001000]))
TAP_IDCODE               = (6, bytes([0b001001]))
TAP_ISC_ENABLE           = (6, bytes([0b010000]))
TAP_ISC_PROGRAM          = (6, bytes([0b010001]))
TAP_ISC_PROGRAM_SECURITY = (6, bytes([0b010010]))
TAP_ISC_NOOP             = (6, bytes([0b010100]))
TAP_ISC_READ             = (6, bytes([0b101011]))
TAP_ISC_DISABLE          = (6, bytes([0b010111]))
TAP_BYPASS               = (6, bytes([0b111111]))

DAP_ABORT                = (4, bytes([0b1000]))
DAP_DPACC                = (4, bytes([0b1010]))
DAP_APACC                = (4, bytes([0b1011]))
DAP_ARM_IDCODE           = (4, bytes([0b1110]))
DAP_BYPASS               = (4, bytes([0b1111]))

R_CRC                  = bs('00000')
R_FAR                  = bs('00001')
R_FDRI                 = bs('00010')
R_FDRO                 = bs('00011')
R_CMD                  = bs('00100')
R_CTL0                 = bs('00101')
R_MASK                 = bs('00110')
R_STAT                 = bs('00111')
R_LOUT                 = bs('01000')
R_COR0                 = bs('01001')
R_MFWR                 = bs('01010')
R_CBC                  = bs('01011')
R_IDCODE               = bs('01100')
R_AXSS                 = bs('01101')
R_COR1                 = bs('01110')
R_WBSTAR               = bs('10000')
R_TIMER                = bs('10001')
R_BOOTSTS              = bs('10110')
R_CTL1                 = bs('11000')
R_BSPI                 = bs('11111')

C_NULL                 = bs('00000')
C_WCFG                 = bs('00001')
C_MFW                  = bs('00010')
C_DGHIGH               = bs('00011')
C_RCFG                 = bs('00100')
C_START                = bs('00101')
C_RCAP                 = bs('00110')
C_RCRC                 = bs('00111')
C_AGHIGH               = bs('01000')
C_SWITCH               = bs('01001')
C_GRESTORE             = bs('01010')
C_SHUTDOWN             = bs('01011')
C_GCAPTURE             = bs('01100')
C_DESYNC               = bs('01101')
C_IPROG                = bs('01111')
C_CRCC                 = bs('10000')
C_LTIMER               = bs('10001')
C_BSPI_READ            = bs('10010')
C_FALL_EDGE            = bs('10011')

W_SYNC                 = b'\xaa\x99\x55\x66'
W_NOOP                 = b'\x20\x00\x00\x00'
W_DUMMY                = b'\xff\xff\xff\xff'
W_readSTAT             = b'\x28\x00\xe0\x01'


class ZynqJTAG:
  def __init__(self, url):
    self._jtag = JTAG2232(url)
    self._jtag.TIR = DAP_BYPASS
    self._jtag.TDR = (1, b'\x01')

  def readIDCODE(self):
    self._jtag.scan_reg('IR', TAP_IDCODE, capture=False)
    bits = self._jtag.scan_reg('DR', bs('0' * 32))
    return hexlify(bits)

  def readSTAT(self):
    self._jtag.scan_reg('IR', TAP_CFG_IN, capture=False)
    self._jtag.scan_reg('DR', W_SYNC + W_NOOP + W_readSTAT + W_DUMMY + W_DUMMY, capture=False)
    self._jtag.scan_reg('IR', TAP_CFG_OUT, capture=False)
    bits = self._jtag.scan_reg('DR', bs('0' * 32))
    return hexlify(bits)


j = ZynqJTAG('ftdi://0x403:0x6010/1')

print('ID:  ', j.readIDCODE())
print('STAT:', j.readSTAT())
