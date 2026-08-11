from micropython import const

'''
OS
    - Set to start a single-conversion
    - Get 1 when no conversion is in progress
    
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
    2: +/-2.048V range = Gain 2 (default),
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

_OS_MASK   = const(15)
_MUX_MASK  = const(12)
_PGA_MASK  = const(9)
_MODE_MASK = const(8)
_RATE_MASK = const(5)
_CMOD_MASK = const(4)
_CPOL_MASK = const(3)
_CLAT_MASK = const(2)
_CQUE_MASK = const(0)
_CONF_REG  = const(1)
_CONV_REG  = const(0)
_GAINS_V   = (6.144, 4.096, 2.048, 1.024, 0.512, 0.256)

class ADS1115:
    def __init__(self, i2c, **kwargs) -> None:
        self._i2c  = i2c
        self._buff = bytearray(2)
        self._addr = kwargs.get('addr', 0x48)
        self._mux  = kwargs.get('channels', (0,))
        self._pga  = kwargs.get('gain', 2)
        self._rate = kwargs.get('rate', 4)
        self._cmod = kwargs.get('cmod', 0)
        self._cpol = kwargs.get('cpol', 0)
        self._clat = kwargs.get('clat', 0)
        self._cque = kwargs.get('cque', 3)
        self._gain = _GAINS_V[self._pga]

        self._conf = []
        for i in range(len(self._mux)):
            self._conf.append((1 << _OS_MASK)|(1 << _MODE_MASK)|
                              (self._mux[i] << _MUX_MASK) |
                              (self._pga    << _PGA_MASK) |
                              (self._rate   << _RATE_MASK)|
                              (self._cmod   << _CMOD_MASK)|
                              (self._cpol   << _CPOL_MASK)|
                              (self._clat   << _CLAT_MASK)|
                              (self._cque   << _CQUE_MASK))
        self._conf = tuple(self._conf)

    def start(self, channel: int = 0) -> None:
        self._buff[0], self._buff[1] = self._conf[channel] >> 8, self._conf[channel] & 0xff
        self._i2c.writeto_mem(self._addr, _CONF_REG, self._buff)

    def read(self) -> None|float:
        self._i2c.readfrom_mem_into(self._addr, _CONF_REG, self._buff)
        if not (self._buff[0] << 8) & (1 << _OS_MASK): return None
        self._i2c.readfrom_mem_into(self._addr, _CONV_REG, self._buff)
        _ = (self._buff[0] << 8) | self._buff[1]
        if _ & (1 << 15): _ -= (1 << 16)
        return _ * self._gain / (1 << 15)