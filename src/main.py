import gc

import utime as time

for no in range(3, 0, -1):
    print('%i main.py wait...' % no)
    time.sleep(1)

import micropython

micropython.alloc_emergency_exception_buf(128)

from leds import power_led
from ntp import ntp_sync
from watchdog import watchdog
from webswitch import main
from wifi import wifi

print('wifi:', wifi)
print('ntp_sync:', ntp_sync)
print('power_led:', power_led)
print('watchdog:', watchdog)


print('gc.collect()')
gc.collect()


main()
