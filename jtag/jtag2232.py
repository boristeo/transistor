from array import array
from pyftdi.ftdi import Ftdi
from pyftdi.bits import BitSequence
import time

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
    self._write_buff = array('B')

    self.set_freq(10000000)
    # Configure MPSSE and pinmode
    self._stack_cmd(array('B', [0x80, 0xc8, 0xfb]))
    self._stack_cmd(array('B', [0x82, 0x00, 0x00]))

    self._last = None
    self._state = 'UNKNOWN'
    if not noreset:
      self.reset()
    
    # Chain setup
    self.HIR = bytearray()
    self.TIR = bytearray()
    self.HDR = bytearray()
    self.TDR = bytearray()

    self.ENDDR = 'IDLE'
    self.ENDIR = 'IDLE'

  def set_freq(self, freq):
    # 8b (8a) - enables (disables) div by 5
    # 96 (97) - enables (disable) adaptive clocking
    # 8c (8d) - enables (disable) 3-phase clocking
    self._stack_cmd(array('B', [0x8a, 0x97, 0x8d]))

    base = 60000000
    divider = base // freq
    # TCK = 60MHz /((1 + [(1 + (0x00) * 256) | (0x1e)])*2)
    divider = divider // 2 - 1
    high = divider >> 8
    assert high < 0xff
    low = divider & 0xff
    self._stack_cmd(array('B', [0x86, low, high]))
    self.freq = freq
  
  def runtest(self, clocks):
    assert self._state in ['RESET', 'IDLE', 'RUN']
    while clocks > 7: 
      chunk = 0xffff if 524288 < clocks else clocks // 8 - 1
      self._stack_cmd(array('B', [0x8f, chunk & 0xff, chunk >> 8]))
      clocks -= chunk * 8 + 8
      self._sync()
      time.sleep(chunk * 8 / self.freq)
    if clocks > 0:
      self._stack_cmd(array('B', [0x8e, clocks - 1]))
      
  def __getitem__(self, item):
    return {'HDR': self.HDR, 'TDR': self.TDR, 'HIR': self.HIR, 'TIR': self.TIR}[item]

  def __setitem__(self, item, value):
    if item in ['HDR', 'TDR', 'HIR', 'TIR']:
      if isinstance(value, BitSequence):
        pass
      elif isinstance(value, tuple):
        assert len(value) == 2
        assert isinstance(value[0], int)
        assert isinstance(value[1], bytearray)
      else:
        value = BitSequence(value)

      if item == 'HDR':
        self.HDR = value
      elif item == 'TDR':
        self.TDR = value
      elif item == 'HIR':
        self.HIR = value
      elif item == 'TIR':
        self.TIR = value

  def shift_register(self, out, use_last=False):
    if len(out) == 0:
      return bytearray()
    if isinstance(out, tuple):
      out = BitSequence(bytes_=out[1])[:out[0]]
    elif isinstance(out, bytearray):
      out = BitSequence(bytes_=out)
    elif not isinstance(out, BitSequence):
      raise Exception('Expect a BitSequence')
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
    return bytearray(bs.tobytes())

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

  def write(self, data, *, use_last=True, reversebytes=False, reversebits=False):
    chunksize = 65536
    if isinstance(data, bytearray) and len(data) > chunksize:
      bytecount = len(data)
      sent_bytes = 0
      chunks = bytecount // chunksize
      if reversebytes:
        data.reverse()
      for _ in range(chunks):
        self._write(data[sent_bytes:sent_bytes + chunksize], use_last=False, reversebytes=False, reversebits=reversebits)
        self._sync()
        sent_bytes += chunksize
      self._write(data[sent_bytes:], use_last=True, reversebytes=False, reversebits=reversebits)
    else:
      self._write(data, use_last=use_last, reversebytes=reversebytes, reversebits=reversebits)
        

  def _write(self, data, *, use_last=True, reversebytes=False, reversebits=False):
    if isinstance(data, tuple):
      assert len(data) == 2
      assert isinstance(data[0], int)
      assert isinstance(data[1], bytearray) or isinstance(data[1], bytes)
      bitcount = data[0]
      data = data[1]
    elif isinstance(data, bytearray):
      bitcount = 8 * len(data) 
    elif isinstance(data, BitSequence):
      bitcount = len(data)
      print('Warning: writing a bitsequence: ' + str(data))
      data = data.tobytes(msby=True)
    else:
      raise Exception('Data type incorrect for writing: ' + str(data))

    if bitcount <= 0:
      return

    bytecount = len(data)
    assert (bitcount <= 8 * bytecount)
    assert bytecount <= 65536

    bitcount -= 1 if use_last else 0
    full_bytes = bitcount // 8
    remainder = bitcount - 8 * full_bytes

    if reversebytes:
      data.reverse()

    if use_last:
      lastbitmask = (1 << (7 - remainder)) if not reversebits else (1 << remainder)
      self._last = 1 if data[-1] & lastbitmask else 0

    if full_bytes > 0:
      self._write_bytes(data[:full_bytes], reverse=reversebits)
    if remainder > 0:
      self._write_bits(data[-1], count=remainder, reverse=reversebits)

  def _write_bytes(self, out, reverse=False):
    olen = len(out) - 1
    order = Ftdi.WRITE_BYTES_NVE_MSB if not reverse else Ftdi.WRITE_BYTES_NVE_LSB
    cmd = array('B', (order, olen & 0xff, (olen >> 8) & 0xff))
    cmd.extend(out)
    self._stack_cmd(cmd)

  def _write_bits(self, out, count, reverse=False):
    assert count < 8
    order = Ftdi.WRITE_BITS_NVE_MSB if not reverse else Ftdi.WRITE_BITS_NVE_LSB
    if isinstance(out, BitSequence):
      byte = out.tobyte()
      count = len(out)
    else:
      byte = out
    cmd = array('B', (order, count-1, byte))
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

  def idle(self):
    if self._state in ['IDLE', 'RUN']:
      return
    assert self._state in ['RESET', 'IRUPDATE', 'IRUPDATE']
    self._change_state(TO_IDLE)
    self._state = 'IDLE'

  def scan_reg(self, reg, data, *, capture):
    assert reg in ['IR', 'DR']

    TO_R = TO_IR if reg == 'IR' else TO_DR
    H = self.HIR if reg == 'IR' else self.HDR
    T = self.TIR if reg == 'IR' else self.TDR
    END = self.ENDIR if reg == 'IR' else self.ENDDR

    if self._state == 'RESET':
      self._change_state(TO_IDLE + TO_R + TO_SHIFT)
    elif self._state in ['IDLE', 'IRUPDATE', 'IRUPDATE']:
      self._change_state(TO_R + TO_SHIFT)
    else:
      raise Exception('Begin state ' + self._state + ' not supported')
    self._state = reg + 'SHIFT'

    captured = self._scan_reg(H, data, T, END, capture=capture, reverse=True)
    if capture:
      return captured


  def _scan_reg(self, pre, data, post, endstate, *, capture, reverse):
    assert self._state in ['DRSHIFT', 'IRSHIFT']

    self.write(pre, use_last=False, reversebits=reverse, reversebytes=reverse)
    last_in_data = len(post) == 0
    if capture:
      captured = self.shift_register(data, use_last=last_in_data)
    else:
      self.write(data, use_last=last_in_data, reversebits=reverse, reversebytes=reverse)
    self.write(post, use_last=True, reversebits=reverse, reversebytes=reverse)

    if endstate in ['IRUPDATE', 'IRUPDATE']:
      assert self._state[:2] == endstate[:2] 
      self._change_state(TO_STOP)
    elif endstate in ['IDLE', 'RUN']:
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


