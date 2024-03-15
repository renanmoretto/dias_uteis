import datetime
from functools import partial
from typing import List, Optional

from .business_days import BusinessDays, Holiday

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


def last_du(date: Optional[datetime.date] = None) -> datetime.date:
    """
    Encontra o último dia útil em relação a hoje.

    Retorna
    -------
    datetime.date
        A data do último dia útil.
    """
    return _business_days_default.last_bd(date=date)


def next_du(date: Optional[datetime.date] = None) -> datetime.date:
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
    return _business_days_default.diff_bd(a, b)
