import gc

import constants
import machine
import uerrno as errno
import usocket as socket
import utime as time
from utils import ResetDevice

WATCHDOG_TIMEOUT = const(30)

_CHECK_PERIOD = const(50 * 1000)  # 50 sec
_MIN_FREE = const(2 * 1024)


def reset(rtc, reason):
    print('Watchdog reset reason: %s' % reason)
    rtc.incr_rtc_count(key=constants.RTC_KEY_WATCHDOG_COUNT)
    ResetDevice(rtc=rtc, reason=reason).reset()


def can_bind_web_server_port():
    server_address = (constants.WEBSERVER_HOST, constants.WEBSERVER_PORT)
    sock = socket.socket()
    try:
        sock.settimeout(1)
        try:
            sock.bind(server_address)
        except OSError as e:
            # If webserver is running:
            # [Errno 98] EADDRINUSE
            if e.args[0] == errno.EADDRINUSE:
                return False
        else:
            print('ERROR: Web server not running! (Can bind to %s:%i)' % server_address)
            return True
    finally:
        sock.close()


class Watchdog:
    last_feed = 0
    last_check = 0
    check_count = 0

    timer = machine.Timer(-1)

    def __init__(self, wifi, rtc):
        self.wifi = wifi
        self.rtc = rtc

        print('Start Watchdog period timer')
        self.timer.deinit()
        self.timer.init(
            period=_CHECK_PERIOD,
            mode=machine.Timer.PERIODIC,
            callback=self._timer_callback
        )

    def _timer_callback(self, timer):
        gc.collect()

        if gc.mem_free() < _MIN_FREE:
            reset(rtc=self.rtc, reason='RAM full')

        if not self.wifi.is_connected:
            self.wifi.ensure_connection()

        last_connection = time.time() - self.wifi.connected_time
        if last_connection > constants.WIFI_TIMEOUT:
            reset(rtc=self.rtc, reason='WiFi timeout')

        if can_bind_web_server_port():
            reset(rtc=self.rtc, reason='Web Server down')

        if time.time() - self.last_feed > WATCHDOG_TIMEOUT:
            reset(rtc=self.rtc, reason='Feed timeout')

        self.check_count += 1
        self.last_check = self.rtc.isoformat()

    def deinit(self):
        self.timer.deinit()

    def feed(self):
        self.last_feed = time.time()

    def __str__(self):
        # get reset info form RTC RAM:
        reset_count = self.rtc.d.get(constants.RTC_KEY_WATCHDOG_COUNT, 0)
        reset_reason = self.rtc.d.get(constants.RTC_KEY_RESET_REASON)
        return (
            'Watchdog -'
            ' last check: %s,'
            ' check count: %s,'
            ' feed since: %i,'
            ' reset count: %s,'
            ' last reset reason: %s'
        ) % (
            self.last_check, self.check_count,
            (time.time() - self.last_feed),
            reset_count, reset_reason,
        )
