from typing import Union

Number = Union[int, float]


def format_currency(value: Number, decimals: int = 2) -> str:
    """Format numeric value as USD currency, e.g. $2,261,536.97"""
    if value is None:
        return "$0.00"
    return f"${value:,.{decimals}f}"


def format_number(value: Number) -> str:
    """Format integer/number with thousands commas, e.g. 4,922"""
    if value is None:
        return "0"
    if isinstance(value, float) and value.is_integer():
        return f"{int(value):,}"
    if isinstance(value, int):
        return f"{value:,}"
    return f"{value:,.2f}"


def format_percentage(value: Number, decimals: int = 2) -> str:
    """Format value as percentage string, e.g. 9.96%"""
    if value is None:
        return "0.00%"
    return f"{value:.{decimals}f}%"


def format_days(value: Number, decimals: int = 2) -> str:
    """Format duration in days, e.g. 4.11 days"""
    if value is None:
        return "0.00 days"
    return f"{value:.{decimals}f} days"


def format_abbreviated_currency(value: Number) -> str:
    """Format numeric value in abbreviated form, e.g. $2.26M or $492.6k"""
    if value is None:
        return "$0"
    abs_val = abs(value)
    sign = "-" if value < 0 else ""
    if abs_val >= 1_000_000:
        return f"{sign}${abs_val / 1_000_000:.2f}M"
    elif abs_val >= 1_000:
        return f"{sign}${abs_val / 1_000:.1f}k"
    return f"{sign}${abs_val:.2f}"

