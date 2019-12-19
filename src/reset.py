import sys

import constants
import machine
import network
import utime


class ResetDevice:
    def __init__(self, reason):
        print('Reset reason: %r' % reason)

        self.reason = reason

        from rtc import update_rtc_dict
        # Save reason in RTC RAM:
        update_rtc_dict(data={constants.RTC_KEY_RESET_REASON: reason})

    def reset(self, timer=None):
        print('Reset device: %r' % self.reason)
        utime.sleep(1)
        # deactivate WiFi: So a change DHCP hostname will be used after reboot
        network.WLAN(network.STA_IF).disconnect()
        utime.sleep(1)
        machine.reset()
        utime.sleep(1)
        sys.exit()

    def schedule(self, period=2000):
        timer = machine.Timer(-1)
        timer.init(
            mode=machine.Timer.ONE_SHOT,
            period=period,
            callback=self.reset
        )
        print('Reset scheduled in %i sec.' % (period / 1000))
