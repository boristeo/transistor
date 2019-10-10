#!/usr/bin/env python3
from binascii import hexlify
from array import array
from pyftdi.ftdi import Ftdi
from pyftdi.bits import BitSequence
bs = BitSequence

### CONSTANTS


# By default Zynq has PL portion and PS portion in cascaded mode:
# DAP FIRST IN CHAIN BY DEFAULT
# PL TAP IR is 6 bits. PS DAP IR is 4 bits 
# DAP bypassed when PS not in reset

# Instructions expected with LSB first, so I reverse them and shift MSB first
# Shift 1 on TMS in parallel with final bit
TAP_EXTEST               = bs('000000').reverse()
TAP_SAMPLE               = bs('000001').reverse()
TAP_USER1                = bs('000010').reverse()
TAP_USER2                = bs('000011').reverse()
TAP_USER3                = bs('100010').reverse()
TAP_USER4                = bs('100011').reverse()
TAP_CFG_OUT              = bs('000100').reverse()
TAP_CFG_IN               = bs('000101').reverse()
TAP_USERCODE             = bs('001000').reverse()
TAP_IDCODE               = bs('001001').reverse()
TAP_ISC_ENABLE           = bs('010000').reverse()
TAP_ISC_PROGRAM          = bs('010001').reverse()
TAP_ISC_PROGRAM_SECURITY = bs('010010').reverse()
TAP_ISC_NOOP             = bs('010100').reverse()
TAP_ISC_READ             = bs('101011').reverse()
TAP_ISC_DISABLE          = bs('010111').reverse()
TAP_BYPASS               = bs('111111').reverse()

DAP_ABORT                = bs('1000').reverse()
DAP_DPACC                = bs('1010').reverse()
DAP_APACC                = bs('1011').reverse()
DAP_ARM_IDCODE           = bs('1110').reverse()
DAP_BYPASS               = bs('1111').reverse()

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

TO_RESET               = bs('11111')
TO_IDLE                = bs('0')
TO_DR                  = bs('1')
TO_IR                  = bs('11')
TO_SHIFT               = bs('00')
TO_PAUSE               = bs('10')
TO_RESUME              = bs('10')
TO_STOP                = bs('11')

class JTAG2232:
  def __init__(self, url, noreset=False):
    self._ftdi = Ftdi()
    self._ftdi.open_mpsse_from_url(url, direction=0, frequency=1)
    # Configure MPSSE, frequency and pinmode
    self._ftdi.write_data(bytearray(b'\x8a\x97\x8d'))
    # TCK = 60MHz /((1 + [(1 + (0x00) * 256) | (0x1e)])*2)
    self._ftdi.write_data(bytearray(b'\x86\x1e\x00'))
    self._ftdi.write_data(bytearray(b'\x80\xc8\xfb'))
    self._ftdi.write_data(bytearray(b'\x82\x00\x00'))

    self._last = None
    self._write_buff = array('B')
    self._state = 'UNKNOWN'
    if not noreset:
      self.reset()
    
    # Chain setup
    self.HIR = bs()
    self.TIR = bs()
    self.HDR = bs()
    self.TDR = bs()

    self.ENDDR = 'DRSTOP'
    self.ENDIR = 'IRSTOP'

  def shift_register(self, out, use_last=False):
    if len(out) == 0:
      return BitSequence()
    if not isinstance(out, BitSequence):
      return Exception('Expect a BitSequence')
    length = len(out)
    if use_last:
      (out, self._last) = (out[:-1], int(out[-1]))
    byte_count = len(out)//8
    pos = 8*byte_count
    bit_count = len(out)-pos
    if not byte_count and not bit_count:
      raise Exception("Nothing to shift")
    if byte_count:
      blen = byte_count-1
      cmd = array('B', (Ftdi.RW_BYTES_PVE_NVE_LSB, blen, (blen >> 8) & 0xff))
      cmd.extend(out[:pos].tobytes(msby=True))
      self._stack_cmd(cmd)
    if bit_count:
      cmd = array('B', (Ftdi.RW_BITS_PVE_NVE_LSB, bit_count-1))
      cmd.append(out[pos:].tobyte())
      self._stack_cmd(cmd)
    self._sync()
    bs = BitSequence()
    byte_count = length//8
    pos = 8*byte_count
    bit_count = length-pos
    if byte_count:
      data = self._ftdi.read_data_bytes(byte_count, 4)
      if not data:
        raise Exception('Unable to read data from FTDI')
      byteseq = BitSequence(bytes_=data, length=8*byte_count)
      bs.append(byteseq)
    if bit_count:
      data = self._ftdi.read_data_bytes(1, 4)
      if not data:
        raise Exception('Unable to read data from FTDI')
      byte = data[0]
      # need to shift bits as they are shifted in from the MSB in FTDI
      byte >>= 8-bit_count
      bitseq = BitSequence(byte, length=bit_count)
      bs.append(bitseq)
    assert len(bs) == length
    return bs

  def _change_state(self, tms):
      """Change the TAP controller state"""
      if not isinstance(tms, BitSequence):
        raise Exception('Expect a BitSequence')
      length = len(tms)
      if not (0 < length < 8):
        raise Exception('Invalid TMS length')
      out = BitSequence(tms, length=8)
      # apply the last TDO bit
      if self._last is not None:
        out[7] = self._last
      # print("TMS", tms, (self._last is not None) and 'w/ Last' or '')
      # reset last bit
      self._last = None
      cmd = array('B', (Ftdi.WRITE_BITS_TMS_NVE, length-1, out.tobyte()))
      self._stack_cmd(cmd)
      self._sync()

  def write(self, out, use_last=True, msb=True):
    if len(out) == 0:
      return
    if isinstance(out, bytes):
      if not use_last:
        self._write_bytes(out, msb=msb)
        return
      if len(out) > 1:
        self._write_bytes(out[:-1], msb=msb)
      out = BitSequence(value=out[-1])
      if msb:
        out.reverse()
    elif not isinstance(out, BitSequence):
      out = BitSequence(out)
    if use_last:
      (out, self._last) = (out[:-1], bool(out[-1]))
    byte_count = len(out)//8
    if byte_count > 0 and not msb:
      raise Exception('ONLY MSB SUPPORTED FOR BITS')
    pos = 8*byte_count
    bit_count = len(out)-pos
    if byte_count:
      self._write_bytes(out[:pos].tobytes(msby=True))
    if bit_count:
      self._write_bits(out[pos:])

  def _write_bytes(self, out, msb=False):
    olen = len(out)-1
    order = Ftdi.WRITE_BYTES_NVE_MSB if msb else Ftdi.WRITE_BYTES_NVE_LSB
    cmd = array('B', (order, olen & 0xff, (olen >> 8) & 0xff))
    cmd.extend(out)
    self._stack_cmd(cmd)

  def _write_bits(self, out):
    length = len(out)
    byte = out.tobyte()
    cmd = array('B', (Ftdi.WRITE_BITS_NVE_LSB, length-1, byte))
    self._stack_cmd(cmd)

  def _stack_cmd(self, cmd):
    if not isinstance(cmd, array):
      raise TypeError('Expect a byte array')
    if not self._ftdi:
      raise Exception("FTDI controller terminated")
    # Currrent buffer + new command + send_immediate
    FTDI_PIPE_LEN = 512
    if (len(self._write_buff)+len(cmd)+1) >= FTDI_PIPE_LEN:
      self._sync()
    self._write_buff.extend(cmd)

  def _sync(self):
    if not self._ftdi:
      raise Exception("FTDI controller terminated")
    if self._write_buff:
      self._ftdi.write_data(self._write_buff)
      self._write_buff = array('B')
  
  def reset(self):
    self._change_state(TO_RESET)
    self._state = 'RESET'

  def scanIR(self, data, *, capture=True):
    if self._state == 'RESET':
      self._change_state(TO_IDLE + TO_IR + TO_SHIFT)
    elif self._state in ['IDLE', 'IRSTOP', 'DRSTOP']:
      self._change_state(TO_IR + TO_SHIFT)
    else:
      raise Exception('Begin state ' + self._state + ' not supported')
    self._state='IRSHIFT'

    captured = self._scan_reg(self.HIR, data, self.TIR, self.ENDIR, capture=capture)
    if capture:
      return captured

  def scanDR(self, data, *, capture=True):
    if self._state == 'RESET':
      self._change_state(TO_IDLE + TO_DR + TO_SHIFT)
    elif self._state in ['IDLE', 'IRSTOP', 'DRSTOP']:
      self._change_state(TO_DR + TO_SHIFT)
    else:
      raise Exception('Begin state ' + self._state + ' not supported')
    self._state='DRSHIFT'

    captured = self._scan_reg(self.HDR, data, self.TDR, self.ENDDR, capture=capture)
    if capture:
      return captured

  def _scan_reg(self, pre, data, post, endstate, *, capture):
    assert self._state in ['DRSHIFT', 'IRSHIFT']

    self.write(pre, use_last=False)
    last_in_data = len(post) == 0
    if capture:
      captured = self.shift_register(data, use_last=last_in_data)
    else:
      self.write(data, msb=True, use_last=last_in_data)
    self.write(post, use_last=True)

    if endstate in ['IRSTOP', 'DRSTOP']:
      assert self._state[:2] == endstate[:2] 
      self._change_state(TO_STOP)
    elif endstate == 'IDLE':
      self._change_state(TO_STOP + TO_IDLE)
    elif endstate == 'RESET':
      self._change_state(TO_RESET)
    elif endstate == self._state:
      pass
    else:
      raise Exception('End state ' + endstate + ' not supported')

    self._state = endstate

    if capture:
      return captured

    
class ZynqJTAG:
  def __init__(self, url):
    self._jtag = JTAG2232(url)
    self._jtag.HIR = bs()
    self._jtag.TIR = bs('1111')
    self._jtag.HDR = bs()
    self._jtag.TDR = bs('1')

  def readIDCODE(self):
    self._jtag.scanIR(TAP_IDCODE, capture=False)
    bits = self._jtag.scanDR(bs('0' * 32))
    return hexlify(bytearray(bits.tobytes()))

  def readSTAT(self):
    self._jtag.scanIR(TAP_CFG_IN, capture=False)
    self._jtag.scanDR(W_SYNC + W_NOOP + W_readSTAT + W_DUMMY + W_DUMMY, capture=False)
    self._jtag.scanIR(TAP_CFG_OUT, capture=False)
    bits = self._jtag.scanDR(bs('0' * 32))
    return hexlify(bytearray(bits.tobytes()))

j = ZynqJTAG('ftdi://0x403:0x6010/1')

print('ID:  ', j.readIDCODE())
print('STAT:', j.readSTAT())
