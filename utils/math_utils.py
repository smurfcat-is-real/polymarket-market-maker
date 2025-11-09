"""Mathematical utility functions"""
import math
from decimal import Decimal, ROUND_DOWN, ROUND_UP


def round_down(value: float, decimals: int) -> float:
    """Round down to specified decimal places"""
    if decimals < 0:
        raise ValueError("Decimals must be non-negative")
    
    multiplier = 10 ** decimals
    return math.floor(value * multiplier) / multiplier


def round_up(value: float, decimals: int) -> float:
    """Round up to specified decimal places"""
    if decimals < 0:
        raise ValueError("Decimals must be non-negative")
    
    multiplier = 10 ** decimals
    return math.ceil(value * multiplier) / multiplier


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide, returning default on division by zero"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (ZeroDivisionError, TypeError):
        return default


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value between min and max"""
    return max(min_value, min(max_value, value))


def calculate_mid_price(bid: float, ask: float) -> float:
    """Calculate mid price from bid and ask"""
    return (bid + ask) / 2


def calculate_spread(bid: float, ask: float) -> float:
    """Calculate spread between bid and ask"""
    return abs(ask - bid)


def calculate_spread_pct(bid: float, ask: float) -> float:
    """Calculate spread as percentage of mid price"""
    mid = calculate_mid_price(bid, ask)
    if mid == 0:
        return 0.0
    return (calculate_spread(bid, ask) / mid) * 100


def calculate_pnl_pct(entry_price: float, current_price: float) -> float:
    """Calculate P&L percentage"""
    if entry_price == 0:
        return 0.0
    return ((current_price - entry_price) / entry_price) * 100