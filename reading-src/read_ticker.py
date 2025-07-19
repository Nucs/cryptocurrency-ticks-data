#!/usr/bin/env python3
"""
Cryptocurrency Tick Data Reader

This module provides functionality to load and analyze cryptocurrency tick data
from the cryptocurrency-ticks-data repository. The data consists of trade ticks
for various cryptocurrency pairs stored as CSV files within ZIP archives.

Data Structure:
- Id: Trade ID provided by the exchange
- time: Epoch timestamp in UTC (may have 1-3h offset)
- Price: Price in the quote currency (e.g., USDT for BTCUSDT)
- Quantity: Quantity in the base currency (e.g., BTC for BTCUSDT)
- IsBuyerMaker: True if buyer initiated, False if seller initiated
- BuyerOrderId: Order ID of the buyer
- SellerOrderId: Order ID of the seller
- IsBestPriceMatch: Whether trade was executed via market order

Available tickers: BCCUSDT, BNBUSDT, BTCUSDT, ETHBTC, LTCBTC, NEOUSDT, QTUMUSDT
Date range: 2018-04-07 to 2019-11-18
"""

import os
import zipfile
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import glob
from pathlib import Path


class TickerDataLoader:
    """
    A class to load and manage cryptocurrency tick data from ZIP archives.
    
    The data is organized in directories by ticker symbol, with daily ZIP files
    containing CSV data for each trading day.
    """
    
    def __init__(self, data_path: str = "data"):
        """
        Initialize the TickerDataLoader.
        
        Args:
            data_path: Path to the data directory containing ticker folders
        """
        self.data_path = Path(data_path)
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data path {data_path} does not exist")
    
    def get_available_tickers(self) -> List[str]:
        """
        Get a list of all available ticker symbols.
        
        Returns:
            List of ticker symbols (e.g., ['BTCUSDT', 'ETHBTC', ...])
        """
        tickers = []
        for item in self.data_path.iterdir():
            if item.is_dir():
                tickers.append(item.name)
        return sorted(tickers)
    
    def get_date_range(self, ticker: str) -> Tuple[datetime, datetime]:
        """
        Get the available date range for a specific ticker.
        
        Args:
            ticker: Ticker symbol (e.g., 'BTCUSDT')
            
        Returns:
            Tuple of (start_date, end_date) as datetime objects
            
        Raises:
            ValueError: If ticker is not found
        """
        ticker_path = self.data_path / ticker
        if not ticker_path.exists():
            raise ValueError(f"Ticker {ticker} not found. Available tickers: {self.get_available_tickers()}")
        
        zip_files = list(ticker_path.glob("*.zip"))
        if not zip_files:
            raise ValueError(f"No data files found for ticker {ticker}")
        
        dates = []
        for zip_file in zip_files:
            date_str = zip_file.stem.split('.')[-2]
            dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
        
        return min(dates), max(dates)
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string in YYYY-MM-DD format."""
        return datetime.strptime(date_str, "%Y-%m-%d")
    
    def _get_file_path(self, ticker: str, date: datetime) -> Path:
        """Get the file path for a specific ticker and date."""
        date_str = date.strftime("%Y-%m-%d")
        filename = f"{ticker}.{date_str}.csv.zip"
        return self.data_path / ticker / filename
    
    def _load_single_day(self, ticker: str, date: datetime) -> pd.DataFrame:
        """
        Load data for a single day.
        
        Args:
            ticker: Ticker symbol
            date: Date to load
            
        Returns:
            DataFrame with tick data for the specified day
        """
        file_path = self._get_file_path(ticker, date)
        
        if not file_path.exists():
            return pd.DataFrame()
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                csv_filename = f"{ticker}.{date.strftime('%Y-%m-%d')}.csv"
                with zip_ref.open(csv_filename) as csv_file:
                    df = pd.read_csv(csv_file)
                    
                    df['datetime'] = pd.to_datetime(df['time'], unit='s')
                    df['date'] = date.strftime('%Y-%m-%d')
                    
                    return df
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return pd.DataFrame()
    
    def load_ticker_data(self, ticker: str, start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Load ticker data with optional date range filtering.
        
        Args:
            ticker: Ticker symbol (e.g., 'BTCUSDT')
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (inclusive)
            
        Returns:
            DataFrame with columns: Id, time, Price, Quantity, IsBuyerMaker,
            BuyerOrderId, SellerOrderId, IsBestPriceMatch, datetime, date
            
        Raises:
            ValueError: If ticker is not found or date format is invalid
        """
        if ticker not in self.get_available_tickers():
            raise ValueError(f"Ticker {ticker} not found. Available tickers: {self.get_available_tickers()}")
        
        available_start, available_end = self.get_date_range(ticker)
        
        if start_date:
            start_dt = self._parse_date(start_date)
            start_dt = max(start_dt, available_start)
        else:
            start_dt = available_start
            
        if end_date:
            end_dt = self._parse_date(end_date)
            end_dt = min(end_dt, available_end)
        else:
            end_dt = available_end
        
        if start_dt > end_dt:
            raise ValueError(f"Start date {start_dt.date()} is after end date {end_dt.date()}")
        
        dataframes = []
        current_date = start_dt
        
        while current_date <= end_dt:
            daily_df = self._load_single_day(ticker, current_date)
            if not daily_df.empty:
                dataframes.append(daily_df)
            current_date += timedelta(days=1)
        
        if not dataframes:
            return pd.DataFrame()
        
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df = combined_df.sort_values('time').reset_index(drop=True)
        
        return combined_df
    
    def load_all_data(self, ticker: str) -> pd.DataFrame:
        """
        Load all available data for a ticker.
        
        Args:
            ticker: Ticker symbol (e.g., 'BTCUSDT')
            
        Returns:
            DataFrame with all available tick data for the ticker
        """
        return self.load_ticker_data(ticker)


def list_available_tickers(data_path: str = "data") -> List[str]:
    """
    Convenience function to list all available tickers.
    
    Args:
        data_path: Path to the data directory
        
    Returns:
        List of available ticker symbols
    """
    loader = TickerDataLoader(data_path)
    return loader.get_available_tickers()


def quick_load(ticker: str, days: int = 1, data_path: str = "data") -> pd.DataFrame:
    """
    Quick load function for recent data.
    
    Args:
        ticker: Ticker symbol
        days: Number of recent days to load
        data_path: Path to the data directory
        
    Returns:
        DataFrame with recent tick data
    """
    loader = TickerDataLoader(data_path)
    start_date, end_date = loader.get_date_range(ticker)
    
    if days == 1:
        return loader.load_ticker_data(ticker, end_date.strftime("%Y-%m-%d"))
    else:
        start_recent = end_date - timedelta(days=days-1)
        return loader.load_ticker_data(ticker, 
                                     start_recent.strftime("%Y-%m-%d"),
                                     end_date.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    print("Cryptocurrency Tick Data Reader - Demo")
    print("=" * 50)
    
    loader = TickerDataLoader()
    
    print("\n1. Available Tickers:")
    tickers = loader.get_available_tickers()
    print(f"Found {len(tickers)} tickers: {', '.join(tickers)}")
    
    print("\n2. Date Ranges for Each Ticker:")
    for ticker in tickers:
        try:
            start_date, end_date = loader.get_date_range(ticker)
            print(f"{ticker}: {start_date.date()} to {end_date.date()}")
        except Exception as e:
            print(f"{ticker}: Error - {e}")
    
    print("\n3. Loading Sample Data (BTCUSDT - First Day):")
    try:
        btc_sample = loader.load_ticker_data("BTCUSDT", "2018-04-07", "2018-04-07")
        print(f"Loaded {len(btc_sample)} trades for BTCUSDT on 2018-04-07")
        print("\nFirst 5 trades:")
        print(btc_sample.head())
        print(f"\nColumns: {list(btc_sample.columns)}")
        print(f"Data types:\n{btc_sample.dtypes}")
        
        print(f"\nPrice range: ${btc_sample['Price'].min():.2f} - ${btc_sample['Price'].max():.2f}")
        print(f"Total volume: {btc_sample['Quantity'].sum():.8f} BTC")
        print(f"Time range: {btc_sample['datetime'].min()} to {btc_sample['datetime'].max()}")
        
    except Exception as e:
        print(f"Error loading BTCUSDT data: {e}")
    
    print("\n4. Loading Date Range (ETHBTC - First 3 Days):")
    try:
        eth_range = loader.load_ticker_data("ETHBTC", "2018-04-07", "2018-04-09")
        print(f"Loaded {len(eth_range)} trades for ETHBTC from 2018-04-07 to 2018-04-09")
        print(f"Unique dates: {sorted(eth_range['date'].unique())}")
        
    except Exception as e:
        print(f"Error loading ETHBTC range: {e}")
    
    print("\n5. Quick Load Demo (Last day of NEOUSDT):")
    try:
        neo_quick = quick_load("NEOUSDT", days=1)
        print(f"Quick loaded {len(neo_quick)} trades for NEOUSDT (last day)")
        if not neo_quick.empty:
            print(f"Date: {neo_quick['date'].iloc[0]}")
            print(f"Price range: {neo_quick['Price'].min():.8f} - {neo_quick['Price'].max():.8f} USDT")
        
    except Exception as e:
        print(f"Error with quick load: {e}")
    
    print("\n" + "=" * 50)
    print("Demo completed!")
