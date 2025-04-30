# Module: utils_dates.py
# Utilitários de data/hora: parsing, fusos, dias úteis, etc.

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
import calendar
from typing import Union

def to_timezone(dt: datetime, tz: str) -> datetime:
    """
    Converte um objeto datetime para o fuso-horário especificado.
    """
    target_tz = pytz.timezone(tz)
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(target_tz)

def is_business_day(dt: datetime) -> bool:
    """
    Verifica se uma data é um dia útil (não é sábado nem domingo).
    """
    return dt.weekday() < 5

def next_business_day(dt: datetime) -> datetime:
    """
    Retorna a próxima data útil a partir da data informada.
    """
    next_day = dt
    while not is_business_day(next_day):
        next_day += timedelta(days=1)
    return next_day

def previous_business_day(dt: datetime) -> datetime:
    """
    Retorna o dia útil anterior à data informada.
    """
    prev_day = dt
    while not is_business_day(prev_day):
        prev_day -= timedelta(days=1)
    return prev_day

def adjust_to_first_business_day_of_month(dt: datetime) -> datetime:
    """
    Ajusta a data para o primeiro dia útil do mês correspondente.
    """
    first = dt.replace(day=1)
    return next_business_day(first)

def adjust_to_first_business_day_of_week(dt: datetime) -> datetime:
    """
    Ajusta a data para o primeiro dia útil da semana (segunda-feira).
    """
    start = dt - timedelta(days=dt.weekday())
    return next_business_day(start)

def parse_frequency(freq: str) -> relativedelta:
    """
    Converte uma string de frequência em um objeto relativedelta.
    """
    import re
    m = re.match(r"^(\d+)([dwmy])$", freq)
    if not m:
        raise ValueError(f"Frequência inválida: {freq}")
    value, unit = m.groups()
    value = int(value)
    if unit == 'd':
        return relativedelta(days=value)
    elif unit == 'w':
        return relativedelta(weeks=value)
    elif unit == 'm':
        return relativedelta(months=value)
    elif unit == 'y':
        return relativedelta(years=value)
    else:
        raise ValueError(f"Unidade de frequência não suportada: {unit}")

def shift_date_by_frequency(dt: datetime, freq: str, reverse: bool = False) -> datetime:
    """
    Desloca uma data pelo intervalo especificado por freq.
    """
    delta = parse_frequency(freq)
    return dt - delta if reverse else dt + delta
