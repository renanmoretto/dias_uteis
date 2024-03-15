import datetime
from typing import Callable, List, Optional


class Holiday:
    """
    A class representing a holiday.

    Parameters
    ----------
    month : int, optional
        The month when the holiday occurs if it's a fixed date, default None.
    day : int, optional
        The day of the month when the holiday occurs if it's a fixed date, default None.
    func : Callable[[int], datetime.date], optional
        A function that takes a year as an argument and returns the date of the holiday for
        that year if it's a dynamic date, default None.

    Methods
    -------
    calc_for_year(year: int) -> datetime.date
        Calculate the date of the holiday for the given year.

    Notes
    -----
        'func' will be ignored if 'day' and 'month' are provided. The holiday's
        type in this case will be 'fixed'.

        If 'func' is provided and 'day' or 'month' is None, the holiday's type
        will be 'dynamic'.
    """

    def __init__(
        self,
        month: Optional[int] = None,
        day: Optional[int] = None,
        func: Optional[Callable[[int], datetime.date]] = None,
    ):
        _month_day_passed = month is not None and day is not None
        if _month_day_passed:
            if not isinstance(month, int) or not isinstance(day, int):
                raise TypeError("'month' and 'day' types must be int")

            # Validating month/day values
            _year_for_validation = datetime.date.today().year
            datetime.date(_year_for_validation, month, day)

            _type = 'fixed'
        else:
            if func is None:
                raise ValueError(
                    "'func' is required if 'month' and 'day' are both None"
                )
            if not callable(func):
                raise TypeError("'func' must be a callable")
            _type = 'dynamic'

        self.month = month
        self.day = day
        self.func = func
        self._type = _type

    def calc_for_year(self, year: int) -> datetime.date:
        """
        Calculate the exact date of the holiday for the specified year.

        Parameters
        ----------
        year : int
            The year to calculate the holiday's date.

        Returns
        -------
        datetime.date
            The date of the holiday for the specified year.
        """
        # Just to validate the year value.
        # Values like -5 or 60000 are invalid.
        datetime.date(year, 1, 1)

        if self._type == 'fixed':
            return datetime.date(year, self.month, self.day)  # type: ignore
        else:
            func_response = self.func(year)  # type: ignore
            if not isinstance(func_response, datetime.date):
                raise TypeError("'func' must return a datetime.date")
            return func_response


class BusinessDays:
    def __init__(self, holidays: Optional[List[Holiday]] = None):
        self.holidays = holidays

    def _get_year_business_days(self, year: int) -> List[datetime.date]:
        return _get_year_business_days(year, self.holidays)

    # def _find_bd(
    #     self, start_date: datetime.date, direction: int
    # ) -> datetime.date:
    #     date = start_date
    #     while not self.is_bd(date):
    #         date += datetime.timedelta(days=direction)
    #     return date

    def _get_all_bdays_for_years(self, years: List[int]) -> List[datetime.date]:
        all_bdays = []
        for year in years:
            all_bdays += self._get_year_business_days(year)
        return all_bdays

    def is_bd(self, date: datetime.date) -> bool:
        """
        Checks if a given date is a business day.

        Parameters
        ----------
        date : datetime.date
            The date to be checked.

        Returns
        -------
        bool
            Returns True if the date is a business day, False otherwise.
        """
        year_bdays = self._get_year_business_days(date.year)
        if date in year_bdays:
            return True
        return False

    def is_holiday(self, date: datetime.date) -> bool:
        """
        Checks if a given date is a holiday.

        Parameters
        ----------
        date : datetime.date
            The date to be checked.

        Returns
        -------
        bool
            Returns True if the date is a holiday, False otherwise.
        """
        # Fix self.holidays to be empty list if None
        self_holidays = [] if not self.holidays else self.holidays
        holidays = _get_year_holidays(date.year, self_holidays)
        if date in holidays:
            return True
        return False

    def delta_bd(self, date: datetime.date, delta_days: int) -> datetime.date:
        """
        Calculates the date a certain number of business days from a specified date.

        Parameters
        ----------
        from_date : datetime.date
            The starting date.
        days_delta : int
            The number of business days to be added to from_date.

        Returns
        -------
        datetime.date
            The calculated business day date.
        """
        if not self.is_bd(date):
            raise ValueError("'date' is not a business day")

        # delta_days*2 so the bday of the end year is always inside the list all_bdays
        end_calendar_date = date + datetime.timedelta(days=delta_days * 2)
        years = _get_years_between_two_dates(date, end_calendar_date)
        all_bdays = self._get_all_bdays_for_years(years)
        date_position = all_bdays.index(date)
        return all_bdays[date_position + delta_days]

    def next_bd(self, date: Optional[datetime.date] = None) -> datetime.date:
        """
        Finds the next business day relative to today.

        Returns
        -------
        datetime.date
            The date of the next business day.
        """
        if not date:
            date = datetime.date.today()
        return self.delta_bd(date, 1)

    def last_bd(self, date: Optional[datetime.date] = None) -> datetime.date:
        """
        Finds the last business day relative to today.

        Returns
        -------
        datetime.date
            The date of the last business day.
        """
        if not date:
            date = datetime.date.today()
        return self.delta_bd(date, -1)

    def range_bd(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        include_end: bool = False,
    ) -> List[datetime.date]:
        """
        Gets a list of business days within a specified range.

        Parameters
        ----------
        start : datetime.date
            The start date of the range.
        end : datetime.date
            The end date of the range.
        include_end : bool, optional
            If True, includes the end date in the range interval, default False.
            By default, Python's range() is closed on the start and open on the
            end of the interval, like [i, f[.

        Returns
        -------
        List[datetime.date]
            A list of business days within the specified range.
        """
        years = _get_years_between_two_dates(start_date, end_date)
        all_bdays = self._get_all_bdays_for_years(years)
        if include_end:
            return [
                bday
                for bday in all_bdays
                if bday >= start_date and bday <= end_date
            ]
        else:
            return [
                bday
                for bday in all_bdays
                if bday >= start_date and bday < end_date
            ]

    def year_bds(self, year: int) -> List[datetime.date]:
        """
        Returns a list of all business days for a given year.

        Parameters
        ----------
        year : int
            The year for which to calculate the business days.

        Returns
        -------
        List[datetime.date]
            A list containing all business days in the specified year.
        """
        return self.range_bd(
            datetime.date(year, 1, 1), datetime.date(year, 12, 31), True
        )

    def year_holidays(self, year: int) -> List[datetime.date]:
        """
        Returns a list of all holidays for a given year.

        If holidays are defined in the object, this method returns a list of those holidays
        for the specified year. If no holidays are defined, it returns an empty list.

        Parameters
        ----------
        year : int
            The year for which to retrieve the holidays.

        Returns
        -------
        List[datetime.date]
            A list containing all holidays for the specified year, or an empty list if
            no holidays are defined.
        """
        if self.holidays:
            return _get_year_holidays(year, self.holidays)
        else:
            return []

    def diff_bd(self, a: datetime.date, b: datetime.date) -> int:
        """
        Calculates the difference between two business days (b-a).

        Parameters
        ----------
        a : datetime.date
        b : datetime.date

        Returns
        -------
        int
            The difference between the business days 'a' and 'b'.
        """
        if not self.is_bd(a):
            raise ValueError("'a' must be business day")
        if not self.is_bd(b):
            raise ValueError("'b' must be business day")

        years = _get_years_between_two_dates(a, b)
        all_bdays = self._get_all_bdays_for_years(years)
        a_pos = all_bdays.index(a)
        b_pos = all_bdays.index(b)
        return b_pos - a_pos


def _get_year_holidays(
    year: int, holidays: List[Holiday]
) -> List[datetime.date]:
    return [holiday.calc_for_year(year) for holiday in holidays]


# Unused
# def _get_year_week_days(year: int) -> List[datetime.date]:
#     date = datetime.date(year, 1, 1)
#     last_date_of_year = datetime.date(year, 12, 31)
#     dates = []
#     while date <= last_date_of_year:
#         if date.weekday() < 5:
#             dates.append(date)
#         date += datetime.timedelta(days=1)
#     return dates


def _get_year_business_days(
    year: int, holidays: Optional[List[Holiday]] = None
) -> List[datetime.date]:
    if holidays:
        year_holidays = _get_year_holidays(year, holidays)
    else:
        year_holidays = []
    date = datetime.date(year, 1, 1)
    last_date_of_year = datetime.date(year, 12, 31)
    dates = []
    while date <= last_date_of_year:
        if date.weekday() < 5 and date not in year_holidays:
            dates.append(date)
        date += datetime.timedelta(days=1)
    return dates


def _get_years_between_two_dates(
    start_date: datetime.date, end_date: datetime.date
) -> List[int]:
    if end_date > start_date:
        years = [year for year in range(start_date.year, end_date.year + 1)]
    else:
        years = [year for year in range(start_date.year, end_date.year - 1, -1)]
    return sorted(years)
