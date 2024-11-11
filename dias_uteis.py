import datetime
from functools import partial
from typing import List, Optional, Callable
import warnings


__all__ = [
    'is_du',
    'delta_du',
    'last_du',
    'next_du',
    'range_du',
    'year_dus',
    'year_holidays',
    'diff_du',
]
import pdb


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
                raise ValueError("'func' is required if 'month' and 'day' are both None")
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

    def _find_bd(
        self,
        start_date: datetime.date,
        direction: int,
    ) -> datetime.date:
        date = start_date
        while not self.is_bd(date):
            date += datetime.timedelta(days=direction)
        return date

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
        start_calendar_date = date + datetime.timedelta(days=-delta_days * 4)
        end_calendar_date = date + datetime.timedelta(days=delta_days * 4)
        years = _get_years_between_two_dates(start_calendar_date, end_calendar_date)
        all_bdays = self._get_all_bdays_for_years(years)

        date_position = all_bdays.index(date)
        return all_bdays[date_position + delta_days]

    def next_bd(
        self,
        date: Optional[datetime.date] = None,
        raise_error_not_bd: bool = True,
    ) -> datetime.date:
        """
        Finds the next business day relative to today.

        Returns
        -------
        datetime.date
            The date of the next business day.
        """
        if not date:
            date = datetime.date.today()

        if not self.is_bd(date):
            date = self._find_bd(date, -1)  # find last bday

        return self.delta_bd(date, 1)

    def last_bd(
        self,
        date: Optional[datetime.date] = None,
        raise_error_not_bd: bool = True,
    ) -> datetime.date:
        """
        Finds the last business day relative to today.

        Returns
        -------
        datetime.date
            The date of the last business day.
        """
        if not date:
            date = datetime.date.today()

        if not self.is_bd(date):
            date = self._find_bd(date, 1)  # find next bday

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
            return [bday for bday in all_bdays if bday >= start_date and bday <= end_date]
        else:
            return [bday for bday in all_bdays if bday >= start_date and bday < end_date]

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
        return self.range_bd(datetime.date(year, 1, 1), datetime.date(year, 12, 31), True)

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

    # def diff(self, a: datetime.date, b: datetime.date) -> int:
    #     years = list(set([a.year, b.year]))
    #     all_bdays = self._get_all_bdays_for_years(years)
    #     bdays = []
    #     b_gt_a = b > a
    #     _min_date = a if b_gt_a else b
    #     _max_date = b if b_gt_a else a
    #     _date = _min_date
    #     while True:
    #         if _date in all_bdays:
    #             bdays.append(_date)
    #         _date += datetime.timedelta(days=1)
    #         if _date > _max_date:
    #             break
    #     i = 1 if b_gt_a else -1
    #     return (len(bdays) - 1) * i

    def diff(self, a: datetime.date, b: datetime.date) -> int:
        _years = {a.year, b.year}
        years = list(range(min(_years), max(_years) + 1))
        all_bdays = self._get_all_bdays_for_years(years)
        _min_date, _max_date = sorted((a, b))
        bdays = [_date for _date in all_bdays if _min_date <= _date <= _max_date]
        return (len(bdays) - 1) * (1 if b > a else -1)


def _get_year_holidays(year: int, holidays: List[Holiday]) -> List[datetime.date]:
    return [holiday.calc_for_year(year) for holiday in holidays]


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


def _get_years_between_two_dates(start_date: datetime.date, end_date: datetime.date) -> List[int]:
    if end_date > start_date:
        years = [year for year in range(start_date.year, end_date.year + 1)]
    else:
        years = [year for year in range(start_date.year, end_date.year - 1, -1)]
    return sorted(years)


# -------------------------------- dias uteis -------------------------------- #


def _calc_pascoa(year: int) -> datetime.date:
    """Calcula a data da Páscoa usando o Algoritmo de Meeus/Jones/Butcher."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime.date(year, month, day)


def _delta_pascoa(year: int, delta: int) -> datetime.date:
    """
    Calcula a data relativa à páscoa no ano 'year'.

    Datas:
    Carnaval:
        Terça-feira de carnaval: 47 dias antes da páscoa.
        Segunda-feira de carnaval: 48 dias antes da páscoa.
    Sexta-feira Santa: 2 dias antes da páscoa.
    Corpus Christ: 60 dias depois da páscoa.
    """
    pascoa = _calc_pascoa(year)
    return pascoa + datetime.timedelta(days=delta)


_calc_segunda_feira_carnaval = partial(_delta_pascoa, delta=-48)
_calc_terca_feira_carnaval = partial(_delta_pascoa, delta=-47)
_calc_sexta_feira_santa = partial(_delta_pascoa, delta=-2)
_calc_corpus_christi = partial(_delta_pascoa, delta=60)

FERIADOS_NACIONAIS_BR = [
    Holiday(month=1, day=1),  # Ano novo
    Holiday(func=_calc_segunda_feira_carnaval),  # Segunda-feira de carnaval
    Holiday(func=_calc_terca_feira_carnaval),  # Terça-feira de carnaval
    Holiday(func=_calc_sexta_feira_santa),  # Sexta-feira Santa
    Holiday(month=4, day=21),  # Tiradentes
    Holiday(month=5, day=1),  # Dia do Trabalho
    Holiday(func=_calc_corpus_christi),  # Corpus Christi
    Holiday(month=9, day=7),  # Independência
    Holiday(month=10, day=12),  # Nossa Senhora Aparecida
    Holiday(month=11, day=2),  # Finados
    Holiday(month=11, day=15),  # Proclamação da República
    Holiday(month=11, day=20),  # Consciência Negra
    Holiday(month=12, day=25),  # Natal
]


# As próximas etapas são para facilitar o uso da API.

_business_days_default = BusinessDays(holidays=FERIADOS_NACIONAIS_BR)


def is_du(date: datetime.date) -> bool:
    """
    Verifica se uma data fornecida é um dia útil.

    Parâmetros
    ----------
    date : datetime.date
        A data a ser verificada.

    Retorna
    -------
    bool
        Retorna True se a data for um DU, False caso contrário.
    """
    return _business_days_default.is_bd(date)


def is_holiday(date: datetime.date) -> bool:
    """
    Verifica se uma data fornecida é um feriado.

    Parâmetros
    ----------
    date : datetime.date
        A data a ser verificada.

    Retorna
    -------
    bool
        Retorna True se a data for um feriado, False caso contrário.
    """
    return _business_days_default.is_holiday(date)


def delta_du(from_date: datetime.date, days_delta: int) -> datetime.date:
    """
    Calcula a data um determinado número de dias úteis a partir de uma data especificada.

    Parâmetros
    ----------
    from_date : datetime.date
        A data inicial.
    days_delta : int
        O número de dias úteis a serem adicionados à from_date.

    Retorna
    -------
    datetime.date
        A data calculada do dia útil.
    """
    return _business_days_default.delta_bd(from_date, days_delta)


def last_du(date: Optional[datetime.date] = None, raise_error_not_du: bool = True) -> datetime.date:
    """
    Encontra o último dia útil em relação a hoje.

    Retorna
    -------
    datetime.date
        A data do último dia útil.
    """
    return _business_days_default.last_bd(date=date)


def next_du(date: Optional[datetime.date] = None, raise_error_not_du: bool = True) -> datetime.date:
    """
    Encontra o próximo dia útil em relação a hoje.

    Retorna
    -------
    datetime.date
        A data do próximo dia útil.
    """
    return _business_days_default.next_bd(date=date)


def range_du(
    start: datetime.date,
    end: datetime.date,
    include_end: bool = False,
) -> List[datetime.date]:
    """
    Retorna uma lista de dias úteis dentro de um intervalo especificado.

    Parâmetros
    ----------
    start : datetime.date
        A data de início do intervalo.
    end : datetime.date
        A data de término do intervalo.
    include_end : bool, opcional
        Se True, inclui a data de término no range do intervalo, default False.
        Por padrão o range() do python é fechado no lado inicial e aberto no
        final do intervalo, como [i,f[.

    Retorna
    -------
    List[datetime.date]
        Uma lista de dias úteis dentro do intervalo especificado.
    """
    return _business_days_default.range_bd(start, end, include_end)


def year_dus(year: int) -> List[datetime.date]:
    """
    Retorna uma lista de todos os dias úteis para um determinado ano.

    Parâmetros
    ----------
    year : int
        Ano para o qual calcular os dias úteis.

    Retorna
    -------
    List[datetime.date]
        Uma lista contendo todos os dias úteis no ano especificado.
    """
    return _business_days_default.year_bds(year)


def year_holidays(year: int) -> List[datetime.date]:
    """
    Retorna uma lista de todos os feriados para um determinado ano.

    Se feriados estão definidos no objeto, este método retorna uma lista desses feriados
    para o ano especificado. Se nenhum feriado estiver definido, retorna uma lista vazia.

    Parâmetros
    ----------
    year : int
        Ano para o qual buscar os feriados.

    Retorna
    -------
    List[datetime.date]
        Uma lista contendo todos os feriados para o ano especificado, ou uma lista vazia se
        nenhum feriado estiver definido.
    """
    return _business_days_default.year_holidays(year)


def diff_du(a: datetime.date, b: datetime.date) -> int:
    """
    Calcula a diferença entre dois dias úteis (b-a).

    Parâmetros
    ----------
    a : datetime.date
    b : datetime.date

    Retorna
    -------
    int
        Diferença entre os dias úteis 'a' e 'b'.
    """
    warnings.warn(
        "O método 'diff_du' será removido em uma futura versão. Utilize o método 'diff' em vez dele.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _business_days_default.diff_bd(a, b)


def diff(a: datetime.date, b: datetime.date) -> int:
    """
    Calcula quantos dias úteis existem entre duas datas (b-a).

    Parâmetros
    ----------
    a : datetime.date
    b : datetime.date

    Retorna
    -------
    int
        Quantidade de dias úteis entre as datas 'a' e 'b'.
    """
    return _business_days_default.diff(a, b)
