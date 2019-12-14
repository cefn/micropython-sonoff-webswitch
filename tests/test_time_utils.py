

import machine
from src.times_utils import (get_next_timer, parse_timers, pformat_timers, restore_timers,
                             save_timers, validate_times)
from tests.base import MicropythonBaseTestCase
from tests.utils.mock_py_config import mock_py_config_context


class ParseTimesTestCase(MicropythonBaseTestCase):

    def test_parse_timers(self):
        assert tuple(parse_timers('''
            1:23 - 4:56
            19:00 - 20:00
        ''')) == (
            ((1, 23), (4, 56)),
            ((19, 0), (20, 0))
        )

    def test_parse_timers_emty_lines(self):
        assert tuple(parse_timers('''
            1:23 - 4:56

            19:00 - 20:00
        ''')) == (
            ((1, 23), (4, 56)),
            ((19, 0), (20, 0))
        )

    def test_parse_timers2(self):
        self.assertRaises(ValueError)
        assert tuple(parse_timers('''
            1:23 4:56
            Foo 19:00 X 20:00 Bar
        ''')) == (
            ((1, 23), (4, 56)),
            ((19, 0), (20, 0))
        )

    def test_parse_timers_error1(self):
        with self.assertRaises(ValueError) as cm:
            tuple(parse_timers('''
                1:23 - 4:56
                19:00 - :00
            '''))
        self.assertEqual(cm.exception.args[0], 'Wrong time in line 2')

    def test_parse_timers_error2(self):
        with self.assertRaises(ValueError) as cm:
            tuple(parse_timers('''
                1:23 - :56
                19:00 - 5:00
            '''))
        self.assertEqual(cm.exception.args[0], 'Wrong time in line 1')

    def test_pformat_timers(self):
        assert pformat_timers([
            ((1, 23), (4, 56)),
            ((19, 0), (20, 0))
        ]) == '01:23 - 04:56\n19:00 - 20:00'

    def test_validate_times(self):
        assert validate_times([
            ((1, 23), (4, 56)),
            ((19, 0), (20, 0))
        ]) is True

    def test_validate_times_wrong_order1(self):
        with self.assertRaises(ValueError) as cm:
            validate_times([((19, 1), (19, 0))])
        self.assertEqual(cm.exception.args[0], '19:00 is in wrong order')

    def test_validate_times_wrong_order2(self):
        with self.assertRaises(ValueError) as cm:
            validate_times([
                ((1, 23), (4, 56)),
                ((4, 55), (20, 0))
            ])
        self.assertEqual(cm.exception.args[0], '04:55 is in wrong order')

    def test_validate_times_hour_out_of_range1(self):
        with self.assertRaises(ValueError) as cm:
            validate_times([
                ((1, 23), (4, 56)),
                ((19, 0), (24, 0))
            ])
        self.assertEqual(cm.exception.args[0], '24:00 is not valid')

    def test_validate_times_hour_out_of_range2(self):
        with self.assertRaises(ValueError) as cm:
            validate_times([
                ((1, 23), (-4, 56)),
                ((19, 0), (23, 0))
            ])
        self.assertEqual(cm.exception.args[0], '-4:56 is not valid')

    def test_validate_times_minutes_out_of_range1(self):
        with self.assertRaises(ValueError) as cm:
            validate_times([
                ((1, 23), (4, 60)),
                ((19, 1), (20, 0))
            ])
        self.assertEqual(cm.exception.args[0], '04:60 is not valid')

    def test_validate_times_minutes_out_of_range2(self):
        with self.assertRaises(ValueError) as cm:
            validate_times([
                ((1, 23), (4, 56)),
                ((19, -1), (20, 0))
            ])
        self.assertEqual(cm.exception.args[0], '19:-1 is not valid')

    def test_restore_times_without_existing_file(self):
        assert restore_timers() == ()

    def test_get_next_timer(self):
        with mock_py_config_context():
            save_timers((
                ((1, 0), (2, 0)),
            ))
            rtc = machine.RTC()
            rtc.datetime((2000, 1, 1, 5, 0, 0, 0, 0))
            assert get_next_timer() == (True, 3600)

            rtc.datetime((2000, 1, 1, 5, 1, 30, 0, 0))
            assert get_next_timer() == (False, 7200)

    def test_get_next_timer_empty(self):
        with mock_py_config_context():
            assert get_next_timer() == (None, None)
