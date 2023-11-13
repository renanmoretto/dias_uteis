import datetime
import unittest

import dias_uteis as dus


class TestDiasUteis(unittest.TestCase):
    def test_is_du(self):
        du = datetime.date(2023, 11, 3)
        assert dus.is_du(du)

    def test_is_not_du(self):
        du = datetime.date(2023, 11, 2)  # Feriado 2/11
        du1 = datetime.date(2020, 2, 22)  # Terça de carnaval 2020
        assert not dus.is_du(du)
        assert not dus.is_du(du1)

    def test_is_holiday(self):
        holiday_example = datetime.date(2020, 6, 11)  # Corpus Christi 2020
        assert dus.is_holiday(holiday_example)

    def test_next_du(self):
        du = dus.next_du()
        assert isinstance(du, datetime.date)
        assert dus.is_du(du)

    def test_last_du(self):
        du = dus.next_du()
        assert isinstance(du, datetime.date)
        assert dus.is_du(du)

    def test_delta_du(self):
        date = datetime.date(2023, 11, 17)

        assert dus.delta_du(date, 5) == datetime.date(2023, 11, 24)
        assert dus.delta_du(date, -10) == datetime.date(2023, 11, 1)

    def test_range_du(self):
        range_dus = dus.range_du(datetime.date(2023, 11, 1), datetime.date(2023, 11, 30))

        nov2023_dus_sample = [
            datetime.date(2023, 11, 1),
            datetime.date(2023, 11, 3),
            datetime.date(2023, 11, 6),
            datetime.date(2023, 11, 7),
            datetime.date(2023, 11, 8),
            datetime.date(2023, 11, 9),
            datetime.date(2023, 11, 10),
            datetime.date(2023, 11, 13),
            datetime.date(2023, 11, 14),
            datetime.date(2023, 11, 16),
            datetime.date(2023, 11, 17),
            datetime.date(2023, 11, 20),
            datetime.date(2023, 11, 21),
            datetime.date(2023, 11, 22),
            datetime.date(2023, 11, 23),
            datetime.date(2023, 11, 24),
            datetime.date(2023, 11, 27),
            datetime.date(2023, 11, 28),
            datetime.date(2023, 11, 29),
        ]

        assert len(range_dus) == 19
        assert len(range_dus) == len(nov2023_dus_sample)

        for du, du_sample in zip(range_dus, nov2023_dus_sample):
            assert du == du_sample
            assert dus.is_du(du)

    def test_year_dus(self):
        year_dus = dus.year_dus(2023)
        for du in year_dus:
            assert dus.is_du(du)
        assert len(year_dus) == 249

    def test_year_holidays(self):
        year_holidays = dus.year_holidays(2023)
        holidays_2023_sample = [
            datetime.date(2023, 1, 1),
            datetime.date(2023, 2, 20),
            datetime.date(2023, 2, 21),
            datetime.date(2023, 4, 7),
            datetime.date(2023, 4, 21),
            datetime.date(2023, 5, 1),
            datetime.date(2023, 6, 8),
            datetime.date(2023, 9, 7),
            datetime.date(2023, 10, 12),
            datetime.date(2023, 11, 2),
            datetime.date(2023, 11, 15),
            datetime.date(2023, 12, 25),
        ]

        assert len(year_holidays) == len(holidays_2023_sample)
        assert len(year_holidays) == 12
        for holiday, holiday_sample in zip(year_holidays, holidays_2023_sample):
            assert holiday == holiday_sample
            assert not dus.is_du(holiday)

    def test_diff_du_positive(self):
        diff = dus.diff_du(datetime.date(2023, 11, 1), datetime.date(2023, 11, 30))
        assert diff == 19

    def test_diff_du_negative(self):
        diff = dus.diff_du(datetime.date(2025, 12, 11), datetime.date(2023, 10, 20))
        assert diff == -541
