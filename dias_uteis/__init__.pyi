import datetime
from typing import List, Optional

def is_du(date: datetime.date) -> bool: ...
def is_holiday(date: datetime.date) -> bool: ...
def delta_du(from_date: datetime.date, days_delta: int) -> datetime.date: ...
def last_du(date: Optional[datetime.date] = None) -> datetime.date: ...
def next_du(date: Optional[datetime.date] = None) -> datetime.date: ...
def range_du(
    start: datetime.date,
    end: datetime.date,
    include_end: bool = False,
) -> List[datetime.date]: ...
def year_dus(year: int) -> List[datetime.date]: ...
def year_holidays(year: int) -> List[datetime.date]: ...
def diff_du(a: datetime.date, b: datetime.date) -> int: ...
