from array import array
from pyftdi.ftdi import Ftdi
from pyftdi.bits import BitSequence

TO_RESET               = BitSequence('11111')
TO_IDLE                = BitSequence('0')
TO_DR                  = BitSequence('1')
TO_IR                  = BitSequence('11')
TO_SHIFT               = BitSequence('00')
TO_PAUSE               = BitSequence('10')
TO_RESUME              = BitSequence('10')
TO_STOP                = BitSequence('11')

    
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
    self.HIR = BitSequence()
    self.TIR = BitSequence()
    self.HDR = BitSequence()
    self.TDR = BitSequence()

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


