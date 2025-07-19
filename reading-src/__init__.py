"""
Reading source package for cryptocurrency tick data.

This package provides functionality to load and analyze cryptocurrency tick data
from ZIP archives containing CSV files.
"""

from .read_ticker import TickerDataLoader, list_available_tickers, quick_load

__all__ = ['TickerDataLoader', 'list_available_tickers', 'quick_load']
