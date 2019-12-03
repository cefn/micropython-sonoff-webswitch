import gc
import sys

import machine
import ujson as json


class Rtc:
    def __init__(self):
        self.rtc = machine.RTC()

        rtc = self.rtc.memory()  # Restore from RTC RAM
        if rtc:
            try:
                self.d = json.loads(rtc)
            except ValueError as e:
                sys.print_exception(e)
                print('RTC memory:', rtc)
                self.d = {}
        else:
            self.d = {}
        gc.collect()

    def save(self, data):
        self.d.update(data)
        self.rtc.memory(json.dumps(self.d))  # Save to RTC RAM
        gc.collect()

    def clear(self):
        self.rtc.memory(b'{}')
        self.d.clear()
        gc.collect()

    def incr_rtc_count(self, key):
        count = self.d.get(key, 0) + 1
        self.save(data={key: count})
        return count

    def isoformat(self, sep='T'):
        dt = self.rtc.datetime()
        return '%i-%02i-%02i%s%02i:%02i:%02i+00:00' % (dt[:3] + (sep,) + dt[4:7])

    def later(self, time):
        dt = self.rtc.datetime()
        return tuple(time) <= dt[4:6]

    def in_time_range(self, time1, time2):
        dt = self.rtc.datetime()
        return tuple(time1) <= dt[4:6] <= tuple(time2)

    def __str__(self):
        return '%r UTC: %s' % (self.d, self.isoformat())


if __name__ == '__main__':
    rtc = Rtc()
    print('RTC 1:', rtc)
    count = rtc.incr_rtc_count(key='test')
    print('RTC memory test call count:', count)
    print('RTC 2:', rtc)
    print(rtc.in_time_range((0, 0), (23, 59)))
    print(rtc.in_time_range((0, 0), (0, 1)))
