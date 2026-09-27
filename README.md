# micropython-ads1115

The simplest and cleanest yet fully working `ads1115` 16-bit I2C ADC library.

Thanks to [robert-hh/ads1x15](https://github.com/robert-hh/ads1x15).

---
- some of the ADS1115 `**kwargs`:
```    
channels (tuple)
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
    2: +/-2.048V range = Gain 2 (default)
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
- constructor:
```py
from machine import I2C
from ads1115 import ADS1115

channels = (4, 5)  # 4: Single-ended AIN0, 5: Single-ended AIN1
ads = ADS1115(I2C(0), channels=channels)
results = [0] * len(channels)
```

---
- `read_blocking()`:
```py
while True:
    for i in range(len(results)):
        results[i] = ads.read_blocking(i)
    print(*results)
```
```py
from time import sleep_ms

num = len(channels)
i = 0

ads.start(i)
while True:
    sleep_ms(100)
    results[i] = ads.read(i)
    if results[i] is None:
        continue
    i = (i + 1) % num
    ads.start(i)
    if i == 0:
        print(*results)
```

---
- `read_async()`:
```py
import asyncio

async def poll_ads():
    global results
    while True:
        for i in range(len(results)):
            results[i] = await ads.read_async(i)
        print(*results)

async def main():
    asuncio.create_task(poll_ads())
    while True:
        await asyncio.sleep_ms(1000)

asyncio.run(main())
```
```py
import asyncio

async def poll_ads():
    global results

    num = len(channels)
    i = 0
    
    ads.start(i)
    while True:
        await asyncio.sleep_ms(100)
        results[i] = ads.read(i)
        if results[i] is None:
            continue
        i = (i + 1) % num
        ads.start(i)
        if i == 0:
            print(*results)

async def main():
    asuncio.create_task(poll_ads())
    while True:
        await asyncio.sleep_ms(1000)

asyncio.run(main())
```
