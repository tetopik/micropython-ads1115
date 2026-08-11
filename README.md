# micropython-ads1115

The most simplest and cleanest yet fully working `ads1115` 16-bit I2C ADC library ever.

---
- configurable `**kwargs`:
```    
channel
    0: Differential P=AIN0, N=AIN1 (default)
    1: Differential P=AIN0, N=AIN3
    2: Differential P=AIN1, N=AIN3
    3: Differential P=AIN2, N=AIN3
    4: Single-ended AIN0
    5: Single-ended AIN1
    6: Single-ended AIN2
    7: Single-ended AIN3
    
gain
    0: +/-6.144V range = Gain 2/3
    1: +/-4.096V range = Gain 1
    2: +/-2.048V range = Gain 2 (default),
    3: +/-1.024V range = Gain 4
    4: +/-0.512V range = Gain 8
    5: +/-0.256V range = Gain 16

rate
    0:   8 samples per second
    1:  16 samples per second
    2:  32 samples per second
    3:  64 samples per second
    4: 128 samples per second (default)
    5: 250 samples per second
    6: 475 samples per second
    7: 860 samples per Second
```

---
- main.py:
```py
import asyncio
from machine import I2C
from ads1115 import ADS1115

ads = ADS1115(i2I2C(0), channel=(4,5))


### single tight-loop ###

while True:
    for i in range(2):
        ads.start(i)
        res = None
        while res is None:
            res = ads.read()
        print(i, res)


### async polling ###

async def ads_poll():
    while True:
        for i in range(2):
            ads.start(i)
            res = ads.read()
            while res is None:
                await.asyncio.sleep(0)
                res = ads.read()
            print(i, res)

async def main():
    await asyncio.create_tast(ads_poll())

if __main__ == '__main__':
    asyncio.run(main())
```
