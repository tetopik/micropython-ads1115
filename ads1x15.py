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

_CQUE_1CONV = const(0)  # Assert ALERT/RDY after one conversions
_CQUE_2CONV = const(1)  # Assert ALERT/RDY after two conversions
_CQUE_4CONV = const(2)  # Assert ALERT/RDY after four conversions
_CQUE_NONE  = const(3)  # Disable the comparator and put ALERT/RDY in high state (default)


class ADS1115:
    def __init__(self, i2c, addr=0x48, channel=(0,), gain=2, rate=4, comp=_CQUE_NONE):
        self.i2c  = i2c
        self.addr = addr
        self.mux  = channel
        self.gain = gain
        self.rate = rate
        self.comp = comp
        self.buff = bytearray(2)
        self.conf = list()
        self.set_conf()

    def _write_reg(self, reg, value):
        self.buff[0] = value >> 8
        self.buff[1] = value & 0xff
        self.i2c.writeto_mem(self.addr, reg, self.buff)

    def _read_reg(self, reg):
        self.i2c.readfrom_mem_into(self.addr, reg, self.buff)
        return (self.buff[0] << 8) | self.buff[1]

    def set_conf(self):
        for i in range(len(self.mux)):
            self.conf[i] = (_OS_SINGLE|_MODE_SINGLE|
                            _MUX_CONF[self.mux]|_PGA_CONF[self.gain]|
                            _DR_CONF[self.rate]|self.comp)

    def start_conv(self, idx=0):
        self._write_reg(_REGISTER_CONFIG, self.conf[idx])

    def read_conv(self, raw=False):
        if self._read_reg(_REGISTER_CONFIG) & _OS_BUSY:
            return None
        res = self._read_reg(_REGISTER_CONVERS)
        res -= 65536 if res >= 32768 else 0
        return res if raw else res * _GAINS_V[self.gain] / 32768

    # def set_conf(self, **kwargs):
    #     self.conf = (_OS_SINGLE |
    #                  kwargs.get('gain', _PGA_2_048V) |
    #
    #
    #                  mode|rate|cmode|cpol|clat|cque)
    #
    # def set_comp(self, mod=_CMODE_TRAD, pol=_CPOL_ACTVLO, lat=_CLAT_NONLAT, que=_CQUE_NONE):
    #     self.comp = mod|pol|lat|que


    # def raw_to_v(self, raw):
    #     v_p_b = _GAINS_V[self.gain] / 32768
    #     return raw * v_p_b
'''
    def set_conv(self, rate=4, channel1=0, channel2=None):
        """Set mode for read_rev"""
        self.mode = (_CQUE_NONE | _CLAT_NONLAT |
                     _CPOL_ACTVLOW | _CMODE_TRAD | _RATES[rate] |
                     _MODE_SINGLE | _OS_SINGLE | _GAINS[self.gain] |
                     _CHANNELS[(channel1, channel2)])

    def read(self, rate=4, channel1=0, channel2=None):
        """Read voltage between a channel and GND.
           Time depends on conversion rate."""
        self._write_register(_REGISTER_CONFIG, (_CQUE_NONE | _CLAT_NONLAT |
                             _CPOL_ACTVLOW | _CMODE_TRAD | _RATES[rate] |
                             _MODE_SINGLE | _OS_SINGLE | _GAINS[self.gain] |
                             _CHANNELS[(channel1, channel2)]))
        while not self._read_register(_REGISTER_CONFIG) & _OS_NOTBUSY:
            time.sleep_ms(1)
        res = self._read_register(_REGISTER_CONVERT)
        return res if res < 32768 else res - 65536

    def read_rev(self):
        """Read voltage between a channel and GND. and then start
           the next conversion."""
        res = self._read_register(_REGISTER_CONVERT)
        self._write_register(_REGISTER_CONFIG, self.mode)
        return res if res < 32768 else res - 65536

    def alert_start(self, rate=4, channel1=0, channel2=None,
                    threshold_high=0x4000, threshold_low=0, latched=False) :
        """Start continuous measurement, set ALERT pin on threshold."""
        self._write_register(_REGISTER_LOWTHRESH, threshold_low)
        self._write_register(_REGISTER_HITHRESH, threshold_high)
        self._write_register(_REGISTER_CONFIG, _CQUE_1CONV |
                             _CLAT_LATCH if latched else _CLAT_NONLAT |
                             _CPOL_ACTVLOW | _CMODE_TRAD | _RATES[rate] |
                             _MODE_CONTIN | _GAINS[self.gain] |
                             _CHANNELS[(channel1, channel2)])

    def conversion_start(self, rate=4, channel1=0, channel2=None):
        """Start continuous measurement, trigger on ALERT/RDY pin."""
        self._write_register(_REGISTER_LOWTHRESH, 0)
        self._write_register(_REGISTER_HITHRESH, 0x8000)
        self._write_register(_REGISTER_CONFIG, _CQUE_1CONV | _CLAT_NONLAT |
                             _CPOL_ACTVLOW | _CMODE_TRAD | _RATES[rate] |
                             _MODE_CONTIN | _GAINS[self.gain] |
                             _CHANNELS[(channel1, channel2)])

    def alert_read(self):
        """Get the last reading from the continuous measurement."""
        res = self._read_register(_REGISTER_CONVERT)
        return res if res < 32768 else res - 65536


class ADS1113(ADS1115):
    def __init__(self, i2c, address=0x48):
        super().__init__(i2c, address, 1)

    def raw_to_v(self, raw):
        return super().raw_to_v(raw)

    def read(self, rate=4):
        return super().read(rate, 0, 1)

    def alert_start(self, rate=4, threshold_high=0x4000, threshold_low=0, latched=False):
        return super().alert_start(rate, 0, 1, threshold_high, threshold_low, latched)

    def alert_read(self):
        return super().alert_read()


class ADS1114(ADS1115):
    def __init__(self, i2c, address=0x48, gain=1):
        super().__init__(i2c, address, gain)

    def raw_to_v(self, raw):
        return super().raw_to_v(raw)

    def read(self, rate=4):
        return super().read(rate, 0, 1)

    def alert_start(self, rate=4, threshold_high=0x4000, threshold_low=0, latched=False):
        return super().alert_start(rate, 0, 1, threshold_high,
            threshold_low, latched)

    def alert_read(self):
        return super().alert_read()


class ADS1015(ADS1115):
    def __init__(self, i2c, address=0x48, gain=1):
        super().__init__(i2c, address, gain)

    def raw_to_v(self, raw):
        return super().raw_to_v(raw << 4)

    def read(self, rate=4, channel1=0, channel2=None):
        return super().read(rate, channel1, channel2) >> 4

    def alert_start(self, rate=4, channel1=0, channel2=None, threshold_high=0x400,
        threshold_low=0, latched=False):
        return super().alert_start(rate, channel1, channel2, threshold_high << 4,
            threshold_low << 4, latched)

    def alert_read(self):
        return super().alert_read() >> 4
'''