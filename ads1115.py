_REGISTER_CONVERS  = const(0)
_REGISTER_CONFIG   = const(1)
_REGISTER_LOTHRESH = const(2)
_REGISTER_HITHRESH = const(3)

_OS_SINGLE  = const(1 << 15)  # Write: Set to start a single-conversion
_OS_BUSY    = const(0 << 15)  # Read: Bit=0 when conversion is in progress
_OS_NOTBUSY = const(1 << 15)  # Read: Bit=1 when no conversion is in progress

_MUX_CONF = (
    const(0 << 12),  # Differential P=AIN0, N=AIN1 (default)
    const(1 << 12),  # Differential P=AIN0, N=AIN3
    const(2 << 12),  # Differential P=AIN1, N=AIN3
    const(3 << 12),  # Differential P=AIN2, N=AIN3
    const(4 << 12),  # Single-ended AIN0
    const(5 << 12),  # Single-ended AIN1
    const(6 << 12),  # Single-ended AIN2
    const(7 << 12))  # Single-ended AIN3

_PGA_CONF = (
    const(0 << 9),  # +/-6.144V range = Gain 2/3
    const(1 << 9),  # +/-4.096V range = Gain 1
    const(2 << 9),  # +/-2.048V range = Gain 2 (default),
    const(3 << 9),  # +/-1.024V range = Gain 4
    const(4 << 9),  # +/-0.512V range = Gain 8
    const(5 << 9))  # +/-0.256V range = Gain 16

_GAINS_V = (
    6.144,  # 2/3x
    4.096,  # 1x
    2.048,  # 2x
    1.024,  # 4x
    0.512,  # 8x
    0.256)  # 16x

_MODE_CONTIN = const(0 << 8)  # Continuous conversion mode
_MODE_SINGLE = const(1 << 8)  # Power-down single-shot mode (default)

_DR_CONF = (
    const(0 << 5),  #  128 /   8 samples per second
    const(1 << 5),  #  250 /  16 samples per second
    const(2 << 5),  #  490 /  32 samples per second
    const(3 << 5),  #  920 /  64 samples per second
    const(4 << 5),  # 1600 / 128 samples per second (default)
    const(5 << 5),  # 2400 / 250 samples per second
    const(6 << 5),  # 3300 / 475 samples per second
    const(7 << 5))  #    - / 860 samples per Second

_CMODE_TRAD = const(0 << 4)  # Traditional comparator with hysteresis (default)
_CMODE_WNDW = const(1 << 4)  # Window comparator

_CPOL_ACTVLO = const(0 << 3)  # ALERT/RDY pin is low when active (default)
_CPOL_ACTVHI = const(1 << 3)  # ALERT/RDY pin is high when active

_CLAT_NONLAT = const(0 << 2)  # Non-latching comparator (default)
_CLAT_LATCH  = const(1 << 2)  # Latching comparator

_CQUE_CONF = (
    const(3),  # 0: Disable the comparator and put ALERT/RDY in high state (default)
    const(0),  # 1: Assert ALERT/RDY after 1 conversion
    const(1),  # 2: Assert ALERT/RDY after 2 conversions
    const(2))  # 3: Assert ALERT/RDY after 4 conversions


class ADS1115:
    def __init__(self, i2c, **kwargs) -> None:
        self.i2c = i2c
        self.addr: int = kwargs.get('addr', 0x48)
        self._mux: tuple[int] = kwargs.get('channel', (0,))
        self._pga: int = kwargs.get('gain', 2)
        self._rate: int = kwargs.get('rate', 4)
        self._comp: int = kwargs.get('comp', 3)
        self._gain: float = _GAINS_V[self._pga]
        self._buff = bytearray(2)
        self.conf = list()
        self.set_conf(**kwargs)

    def set_conf(self, **kwargs) -> None:
        self._mux  = kwargs.get('channel', self._mux)
        self._pga  = kwargs.get('gain', self._pga)
        self._rate = kwargs.get('rate', self._rate)
        self._comp = kwargs.get('comp', self._comp)
        self._gain = _GAINS_V[self._pga]
        self.conf  = list()
        for i in range(len(self._mux)):
            self.conf[i] = (_OS_SINGLE|_MODE_SINGLE|_MUX_CONF[self._mux[i]]|
                            _PGA_CONF[self._pga]|_DR_CONF[self._rate]|self._comp)

    def start_conv(self, idx: int = 0) -> None:
        self._buff[0], self._buff[1] = self.conf[idx] >> 8, self.conf[idx] & 0xff
        self.i2c.writeto_mem(self.addr, _REGISTER_CONFIG, self._buff)

    def read_conv(self, raw: bool = False) -> None|int|float:
        self.i2c.readfrom_mem_into(self.addr, _REGISTER_CONFIG, self._buff)
        if (self._buff[0] << 8) & _OS_BUSY: return None
        self.i2c.readfrom_mem_into(self.addr, _REGISTER_CONVERS, self._buff)
        res = (self._buff[0] << 8) | self._buff[1]
        if res & (1 << 15): res -= (1 << 16)
        return res if raw else res * self._gain / (1 << 15)