"""
    Tests power timer on device
"""
from power_timer import PowerTimer


def test_power_timer():
    print('test not active...', end=' ')
    power_timer = PowerTimer()
    result = power_timer.info_text()
    assert result == 'Power timer is deactivated.', result
    result = str(power_timer)
    assert result == (
        'last_update=None, next_time=None, next_time_ms=None,'
        ' turn_on=None, active=None, today_active=None'
    ), result
    print('OK')

    print('test active...', end=' ')
    power_timer.active = True
    power_timer.today_active = True
    result = power_timer.info_text()
    assert result == 'No switch scheduled. (Last update: None)', result
    result = str(power_timer)
    assert result == (
        'last_update=None, next_time=None, next_time_ms=None,'
        ' turn_on=None, active=True, today_active=True'
    ), result
    print('OK')

    print('test schedule_next_switch()...', end=' ')
    power_timer.schedule_next_switch()
    power_timer.timer.deinit()
    power_timer.next_time = (21, 30)
    power_timer.next_time_ms = 0
    power_timer.last_update = 'Fake'
    result = power_timer.info_text()
    assert result == 'missed timer', result
    result = str(power_timer)
    assert result == (  # reset was called!
        "last_update='Fake', next_time=None, next_time_ms=None,"
        " turn_on=None, active=None, today_active=None"
    ), result
    print('OK')


if __name__ == '__main__':
    print('Run tests on device...')
    import sys
    sys.modules.clear()

    import gc
    gc.collect()

    test_power_timer()
    print('OK')
