WATCHDOG_CHECK_PERIOD = const(50 * 1000)  # 50 sec
WATCHDOG_TIMEOUT = const(40 * 1000) # 40 sec

WIFI_TIMER = const(30 * 1000)  # 30 sec
NTP_TIMER = const(15 * 60 * 1000)  # 15 min

assert WATCHDOG_TIMEOUT > WIFI_TIMER
assert WATCHDOG_CHECK_PERIOD > WATCHDOG_TIMEOUT