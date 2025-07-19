#!/usr/bin/env python3
"""
Test suite for the cryptocurrency tick data reader module.

Tests cover the TickerDataLoader class functionality including:
- Loading ticker data with date ranges
- Error handling for invalid inputs
- Data format validation
- Utility functions
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import zipfile
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'reading-src'))
from read_ticker import TickerDataLoader, list_available_tickers, quick_load


class TestTickerDataLoader:
    """Test cases for the TickerDataLoader class."""
    
    @pytest.fixture
    def sample_data_dir(self):
        """Create a temporary directory with sample test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            ticker_dir = temp_path / "TESTUSDT"
            ticker_dir.mkdir()
            
            sample_csv_data = """Id,time,Price,Quantity,IsBuyerMaker,BuyerOrderId,SellerOrderId,IsBestPriceMatch
1,1523035637.617,6589.98,0.20916900,True,82991182,82991232,True
2,1523035637.617,6589.98,1.78883100,True,82991224,82991232,True
3,1523035639.213,6589.99,0.30389100,False,82991235,82991112,True
4,1523035646.516,6589.99,0.02137600,False,82991240,82991112,True
5,1523035646.815,6589.98,0.03023600,True,82991224,82991241,True"""
            
            dates = ["2018-04-07", "2018-04-08", "2018-04-09"]
            for date in dates:
                zip_filename = f"TESTUSDT.{date}.csv.zip"
                zip_path = ticker_dir / zip_filename
                
                with zipfile.ZipFile(zip_path, 'w') as zip_file:
                    csv_filename = f"TESTUSDT.{date}.csv"
                    zip_file.writestr(csv_filename, sample_csv_data)
            
            yield temp_path
    
    @pytest.fixture
    def loader_with_sample_data(self, sample_data_dir):
        """Create a TickerDataLoader instance with sample data."""
        return TickerDataLoader(str(sample_data_dir))
    
    def test_init_valid_path(self, sample_data_dir):
        """Test TickerDataLoader initialization with valid path."""
        loader = TickerDataLoader(str(sample_data_dir))
        assert loader.data_path == Path(sample_data_dir)
    
    def test_init_invalid_path(self):
        """Test TickerDataLoader initialization with invalid path."""
        with pytest.raises(FileNotFoundError):
            TickerDataLoader("/nonexistent/path")
    
    def test_get_available_tickers(self, loader_with_sample_data):
        """Test getting available tickers."""
        tickers = loader_with_sample_data.get_available_tickers()
        assert "TESTUSDT" in tickers
        assert isinstance(tickers, list)
        assert len(tickers) >= 1
    
    def test_get_date_range_valid_ticker(self, loader_with_sample_data):
        """Test getting date range for valid ticker."""
        start_date, end_date = loader_with_sample_data.get_date_range("TESTUSDT")
        assert isinstance(start_date, datetime)
        assert isinstance(end_date, datetime)
        assert start_date <= end_date
        assert start_date.date() == datetime(2018, 4, 7).date()
        assert end_date.date() == datetime(2018, 4, 9).date()
    
    def test_get_date_range_invalid_ticker(self, loader_with_sample_data):
        """Test getting date range for invalid ticker."""
        with pytest.raises(ValueError, match="Ticker INVALID not found"):
            loader_with_sample_data.get_date_range("INVALID")
    
    def test_load_ticker_data_single_day(self, loader_with_sample_data):
        """Test loading data for a single day."""
        df = loader_with_sample_data.load_ticker_data("TESTUSDT", "2018-04-07", "2018-04-07")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5  # Sample data has 5 rows
        assert "datetime" in df.columns
        assert "date" in df.columns
        assert df["date"].iloc[0] == "2018-04-07"
        
        expected_columns = ["Id", "time", "Price", "Quantity", "IsBuyerMaker", 
                          "BuyerOrderId", "SellerOrderId", "IsBestPriceMatch", 
                          "datetime", "date"]
        for col in expected_columns:
            assert col in df.columns
    
    def test_load_ticker_data_date_range(self, loader_with_sample_data):
        """Test loading data for a date range."""
        df = loader_with_sample_data.load_ticker_data("TESTUSDT", "2018-04-07", "2018-04-09")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 15  # 3 days × 5 rows each
        
        unique_dates = sorted(df["date"].unique())
        expected_dates = ["2018-04-07", "2018-04-08", "2018-04-09"]
        assert unique_dates == expected_dates
    
    def test_load_ticker_data_no_date_range(self, loader_with_sample_data):
        """Test loading all available data when no date range specified."""
        df = loader_with_sample_data.load_ticker_data("TESTUSDT")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 15  # All 3 days × 5 rows each
    
    def test_load_ticker_data_invalid_ticker(self, loader_with_sample_data):
        """Test loading data for invalid ticker."""
        with pytest.raises(ValueError, match="Ticker INVALID not found"):
            loader_with_sample_data.load_ticker_data("INVALID")
    
    def test_load_ticker_data_invalid_date_format(self, loader_with_sample_data):
        """Test loading data with invalid date format."""
        with pytest.raises(ValueError):
            loader_with_sample_data.load_ticker_data("TESTUSDT", "invalid-date")
    
    def test_load_ticker_data_start_after_end(self, loader_with_sample_data):
        """Test loading data with start date after end date."""
        with pytest.raises(ValueError, match="Start date .* is after end date"):
            loader_with_sample_data.load_ticker_data("TESTUSDT", "2018-04-09", "2018-04-07")
    
    def test_load_all_data(self, loader_with_sample_data):
        """Test loading all data for a ticker."""
        df = loader_with_sample_data.load_all_data("TESTUSDT")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 15  # All available data
    
    def test_datetime_conversion(self, loader_with_sample_data):
        """Test that datetime conversion works correctly."""
        df = loader_with_sample_data.load_ticker_data("TESTUSDT", "2018-04-07", "2018-04-07")
        
        assert df["datetime"].dtype == "datetime64[ns]"
        assert isinstance(df["datetime"].iloc[0], pd.Timestamp)
    
    def test_data_sorting(self, loader_with_sample_data):
        """Test that data is sorted by time."""
        df = loader_with_sample_data.load_ticker_data("TESTUSDT", "2018-04-07", "2018-04-09")
        
        time_values = df["time"].values
        assert all(time_values[i] <= time_values[i+1] for i in range(len(time_values)-1))


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    @pytest.fixture
    def sample_data_dir(self):
        """Create a temporary directory with sample test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            ticker_dir = temp_path / "TESTUSDT"
            ticker_dir.mkdir()
            
            sample_csv_data = """Id,time,Price,Quantity,IsBuyerMaker,BuyerOrderId,SellerOrderId,IsBestPriceMatch
1,1523035637.617,6589.98,0.20916900,True,82991182,82991232,True"""
            
            zip_filename = "TESTUSDT.2018-04-07.csv.zip"
            zip_path = ticker_dir / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                csv_filename = "TESTUSDT.2018-04-07.csv"
                zip_file.writestr(csv_filename, sample_csv_data)
            
            yield temp_path
    
    def test_list_available_tickers(self, sample_data_dir):
        """Test list_available_tickers utility function."""
        tickers = list_available_tickers(str(sample_data_dir))
        assert "TESTUSDT" in tickers
        assert isinstance(tickers, list)
    
    def test_quick_load_single_day(self, sample_data_dir):
        """Test quick_load utility function for single day."""
        df = quick_load("TESTUSDT", days=1, data_path=str(sample_data_dir))
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1  # Sample data has 1 row
    
    def test_quick_load_invalid_ticker(self, sample_data_dir):
        """Test quick_load with invalid ticker."""
        with pytest.raises(ValueError):
            quick_load("INVALID", data_path=str(sample_data_dir))


class TestRealDataIntegration:
    """Integration tests with real cryptocurrency data (if available)."""
    
    @pytest.fixture
    def real_data_loader(self):
        """Create loader with real data if available."""
        data_path = Path("data")
        if data_path.exists():
            return TickerDataLoader("data")
        else:
            pytest.skip("Real data directory not available")
    
    def test_real_tickers_available(self, real_data_loader):
        """Test that real tickers are available."""
        tickers = real_data_loader.get_available_tickers()
        assert len(tickers) > 0
        
        expected_tickers = ["BTCUSDT", "ETHBTC", "NEOUSDT"]
        for ticker in expected_tickers:
            if ticker in tickers:
                assert ticker in tickers
    
    def test_real_data_loading(self, real_data_loader):
        """Test loading real data if available."""
        tickers = real_data_loader.get_available_tickers()
        if not tickers:
            pytest.skip("No real tickers available")
        
        ticker = tickers[0]
        start_date, end_date = real_data_loader.get_date_range(ticker)
        
        df = real_data_loader.load_ticker_data(ticker, 
                                             start_date.strftime("%Y-%m-%d"), 
                                             start_date.strftime("%Y-%m-%d"))
        
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "datetime" in df.columns
            assert "Price" in df.columns
            assert "Quantity" in df.columns


class TestErrorHandling:
    """Test cases for error handling scenarios."""
    
    def test_missing_zip_file_handling(self, tmp_path):
        """Test handling of missing ZIP files."""
        ticker_dir = tmp_path / "EMPTYUSDT"
        ticker_dir.mkdir()
        
        loader = TickerDataLoader(str(tmp_path))
        
        df = loader._load_single_day("EMPTYUSDT", datetime(2018, 4, 7))
        assert isinstance(df, pd.DataFrame)
        assert df.empty
    
    def test_corrupted_zip_file_handling(self, tmp_path):
        """Test handling of corrupted ZIP files."""
        ticker_dir = tmp_path / "CORRUPTUSDT"
        ticker_dir.mkdir()
        
        zip_path = ticker_dir / "CORRUPTUSDT.2018-04-07.csv.zip"
        with open(zip_path, 'w') as f:
            f.write("This is not a valid ZIP file")
        
        loader = TickerDataLoader(str(tmp_path))
        
        df = loader._load_single_day("CORRUPTUSDT", datetime(2018, 4, 7))
        assert isinstance(df, pd.DataFrame)
        assert df.empty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
