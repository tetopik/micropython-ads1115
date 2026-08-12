from micropython import const
from time import sleep_ms

try: from asyncio import sleep_ms as asleep_ms
except ImportError: pass

'''
OS
    1: [W] Set to start a single-conversion
    1: [R] Bit=1 when no conversion is in progress
    
MUX
    0: Differential P=AIN0, N=AIN1 (default)
    1: Differential P=AIN0, N=AIN3
    2: Differential P=AIN1, N=AIN3
    3: Differential P=AIN2, N=AIN3
    4: Single-ended AIN0
    5: Single-ended AIN1
    6: Single-ended AIN2
    7: Single-ended AIN3
    
PGA
    0: +/-6.144V range = Gain 2/3
    1: +/-4.096V range = Gain 1
    2: +/-2.048V range = Gain 2 (default)
    3: +/-1.024V range = Gain 4
    4: +/-0.512V range = Gain 8
    5: +/-0.256V range = Gain 16

MODE
    0: Continuous conversion mode
    1: Power-down single-shot mode (default)

RATE
    0:   8 samples per second
    1:  16 samples per second
    2:  32 samples per second
    3:  64 samples per second
    4: 128 samples per second (default)
    5: 250 samples per second
    6: 475 samples per second
    7: 860 samples per Second

CMODE
    0: Traditional comparator with hysteresis (default)
    1: Window comparator

CPOL
    0: ALERT/RDY pin is low when active (default)
    1: ALERT/RDY pin is high when active

CLAT
    0: Non-latching comparator (default)
    1: Latching comparator

CQUE
    0: Assert ALERT/RDY after 1 conversion
    1: Assert ALERT/RDY after 2 conversions
    2: Assert ALERT/RDY after 4 conversions
    3: Disable the comparator and put ALERT/RDY in high state (default)
'''

_CONV_REG = const(0)
_CONF_REG = const(1)

_OS_POS   = const(15)
_MUX_POS  = const(12)
_PGA_POS  = const(9)
_MODE_POS = const(8)
_RATE_POS = const(5)
_CMOD_POS = const(4)
_CPOL_POS = const(3)
_CLAT_POS = const(2)
_CQUE_POS = const(0)

_OS_READY = const(1 << _OS_POS)
_GAINS_V  = (6.144, 4.096, 2.048, 1.024, 0.512, 0.256)
_DR_SPS   = (8, 16, 32, 64, 128, 250, 475, 860)

class ADS1115:
    def __init__(self, i2c,
                 addr: int = 0x48,
                 channels: tuple = (0,),
                 gain: int = 2,
                 mode: int = 1,
                 rate: int = 4,
                 cmod: int = 0,
                 cpol: int = 0,
                 clat: int = 0,
                 cque: int = 3
        ) -> None:

        self._i2c  = i2c
        self._addr = addr
        self._mux  = channels
        self._pga  = gain
        self._mode = mode
        self._rate = rate
        self._cmod = cmod
        self._cpol = cpol
        self._clat = clat
        self._cque = cque

        self._gain = _GAINS_V[self._pga]
        self._hold = int(1000 / _DR_SPS[self._rate])
        self._buff = bytearray(2)

        self._conf = []
        for i in range(len(self._mux)):
            self._conf.append((self._mode   <<  _OS_POS)|
                              (self._mux[i] << _MUX_POS)|
                              (self._pga   <<  _PGA_POS)|
                              (self._mode  << _MODE_POS)|
                              (self._rate  << _RATE_POS)|
                              (self._cmod  << _CMOD_POS)|
                              (self._cpol  << _CPOL_POS)|
                              (self._clat  << _CLAT_POS)|
                              (self._cque  << _CQUE_POS))
        self._conf = tuple(self._conf)

    def start(self, channel: int = 0) -> None:
        self._buff[0], self._buff[1] = self._conf[channel] >> 8, self._conf[channel] & 0xff
        self._i2c.writeto_mem(self._addr, _CONF_REG, self._buff)

    def read(self) -> None|float:
        self._i2c.readfrom_mem_into(self._addr, _CONF_REG, self._buff)
        if not (self._buff[0] << 8) & _OS_READY: return None
        self._i2c.readfrom_mem_into(self._addr, _CONV_REG, self._buff)
        _tmp = (self._buff[0] << 8) | self._buff[1]
        if _tmp & (1 << 15): _tmp -= (1 << 16)
        return _tmp * self._gain / (1 << 15)

    def read_blocking(self, channel: int = 0) -> None|float:
        self.start(channel)
        sleep_ms(self._hold)
        _tmp = self.read()
        while _tmp is None:
            sleep_ms(1)
            _tmp = self.read()
        return _tmp

    async def read_async(self, channel: int = 0) -> None|float:
        self.start(channel)
        await asleep_ms(self._hold)
        _tmp = self.read()
        while _tmp is None:
            await asleep_ms(1)
            _tmp = self.read()
        return _tmp
