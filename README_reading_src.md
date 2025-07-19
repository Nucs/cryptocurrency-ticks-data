# Cryptocurrency Tick Data Reader

A comprehensive Python module for loading and analyzing cryptocurrency tick data from ZIP archives containing CSV files. This module provides easy access to historical trade tick data for various cryptocurrency pairs with pandas DataFrame support and flexible date range filtering.

## 📊 Data Overview

This repository contains **590+ days** of cryptocurrency trade tick data spanning from **April 2018 to November 2019**:

- **7 Available Tickers**: BCCUSDT, BNBUSDT, BTCUSDT, ETHBTC, LTCBTC, NEOUSDT, QTUMUSDT
- **Date Range**: 2018-04-07 to 2019-11-18
- **Data Format**: Daily ZIP files containing CSV trade data
- **Total Size**: ~5.1GB of compressed tick data

### Data Structure

Each trade record contains the following fields:
1. `Id` - id provided by the exchange
2. `time` - epoch time, UTC. There might be a 1-3h (consistent) offset accidentally added by C# automatic localization of DateTime. I have no way to verify if this is true.
3. `Price` - The price in the rhs symbol (e.g. BTCUSDT means price is in USDT)
4. `Quantity` - Quantity of the lhs symbol (e.g. BTCUSDT means quantity in BTC)
5. `IsBuyerMaker` - was the trade completed by the buyer (true) or by the seller (false). 
   when it is true, it means that the seller has placed a ask for his holdings and a buyer came along later on and completed the trade.
   when it is false, it means that the buyer has placed a bid for his curreny and a seller came along later on and completed the trade.
6. `BuyerOrderId` - Order id of the buyer
7. `SellerOrderId` - Order id of the seller
8. `IsBestPriceMatch` - Has the Maker (buyermaker or sellermaker) accomplished the trade by a market order as opposed to a trade accomplished by a limit order which waits for an opposite trade pair (I might be wrong tho, this need verification).

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Nucs/cryptocurrency-ticks-data.git
cd cryptocurrency-ticks-data

# Install required dependencies
pip install pandas
```

### Basic Usage

```python
from reading_src import TickerDataLoader

# Initialize the data loader
loader = TickerDataLoader()

# Load one day of BTCUSDT data
btc_data = loader.load_ticker_data("BTCUSDT", "2018-04-07", "2018-04-07")
print(f"Loaded {len(btc_data)} trades")
print(f"Price range: ${btc_data['Price'].min():.2f} - ${btc_data['Price'].max():.2f}")
```

## 📚 Comprehensive API Reference

### TickerDataLoader Class

#### Initialization

```python
from reading_src import TickerDataLoader

# Use default data path
loader = TickerDataLoader()

# Use custom data path
loader = TickerDataLoader(data_path="/path/to/your/data")
```

#### Core Methods

##### `get_available_tickers() -> List[str]`

Get a list of all available ticker symbols.

```python
tickers = loader.get_available_tickers()
print(f"Available tickers: {tickers}")
# Output: ['BCCUSDT', 'BNBUSDT', 'BTCUSDT', 'ETHBTC', 'LTCBTC', 'NEOUSDT', 'QTUMUSDT']
```

##### `get_date_range(ticker: str) -> Tuple[datetime, datetime]`

Get the available date range for a specific ticker.

```python
start_date, end_date = loader.get_date_range("BTCUSDT")
print(f"BTCUSDT data available from {start_date.date()} to {end_date.date()}")
# Output: BTCUSDT data available from 2018-04-07 to 2019-11-18
```

##### `load_ticker_data(ticker, start_date=None, end_date=None) -> pd.DataFrame`

Load ticker data with optional date range filtering.

```python
# Load single day
df = loader.load_ticker_data("BTCUSDT", "2018-04-07", "2018-04-07")

# Load date range
df = loader.load_ticker_data("ETHBTC", "2018-04-07", "2018-04-10")

# Load all available data
df = loader.load_ticker_data("NEOUSDT")
```

##### `load_all_data(ticker: str) -> pd.DataFrame`

Load all available data for a ticker (equivalent to `load_ticker_data` without date parameters).

```python
all_btc_data = loader.load_all_data("BTCUSDT")
print(f"Total trades: {len(all_btc_data)}")
```

### Utility Functions

#### `list_available_tickers(data_path="data") -> List[str]`

Convenience function to quickly list available tickers.

```python
from reading_src import list_available_tickers

tickers = list_available_tickers()
print(f"Found {len(tickers)} tickers")
```

#### `quick_load(ticker, days=1, data_path="data") -> pd.DataFrame`

Quick load function for recent data.

```python
from reading_src import quick_load

# Load last day of data
recent_data = quick_load("BTCUSDT", days=1)

# Load last week of data
week_data = quick_load("ETHBTC", days=7)
```

## 🎯 Usage Examples & Showcase

### Example 1: Basic Data Exploration

```python
from reading_src import TickerDataLoader
import pandas as pd

loader = TickerDataLoader()

# Load first day of BTCUSDT data
btc_data = loader.load_ticker_data("BTCUSDT", "2018-04-07", "2018-04-07")

print("=== BTCUSDT Data Overview ===")
print(f"Total trades: {len(btc_data):,}")
print(f"Date: {btc_data['date'].iloc[0]}")
print(f"Time range: {btc_data['datetime'].min()} to {btc_data['datetime'].max()}")
print(f"Price range: ${btc_data['Price'].min():.2f} - ${btc_data['Price'].max():.2f}")
print(f"Total volume: {btc_data['Quantity'].sum():.8f} BTC")
print(f"Average trade size: {btc_data['Quantity'].mean():.8f} BTC")

# Sample output:
# === BTCUSDT Data Overview ===
# Total trades: 85,141
# Date: 2018-04-07
# Time range: 2018-04-07 00:00:37.617000 to 2018-04-07 23:59:59.815000
# Price range: $6589.98 - $7041.99
# Total volume: 1,234.56789012 BTC
# Average trade size: 0.01450123 BTC
```

### Example 2: Multi-Day Analysis

```python
# Load a week of ETHBTC data
eth_week = loader.load_ticker_data("ETHBTC", "2018-04-07", "2018-04-13")

print("=== ETHBTC Weekly Analysis ===")
print(f"Total trades: {len(eth_week):,}")
print(f"Unique dates: {len(eth_week['date'].unique())}")

# Daily trade counts
daily_counts = eth_week.groupby('date').size()
print("\nDaily trade counts:")
for date, count in daily_counts.items():
    print(f"  {date}: {count:,} trades")

# Price statistics by day
daily_stats = eth_week.groupby('date')['Price'].agg(['min', 'max', 'mean', 'std'])
print("\nDaily price statistics:")
print(daily_stats.round(8))
```

### Example 3: Market Microstructure Analysis

```python
# Analyze buyer vs seller initiated trades
btc_sample = loader.load_ticker_data("BTCUSDT", "2018-04-07", "2018-04-07")

print("=== Market Microstructure Analysis ===")

# Buyer vs Seller initiated trades
buyer_initiated = btc_sample[btc_sample['IsBuyerMaker'] == True]
seller_initiated = btc_sample[btc_sample['IsBuyerMaker'] == False]

print(f"Buyer initiated trades: {len(buyer_initiated):,} ({len(buyer_initiated)/len(btc_sample)*100:.1f}%)")
print(f"Seller initiated trades: {len(seller_initiated):,} ({len(seller_initiated)/len(btc_sample)*100:.1f}%)")

# Volume analysis
buyer_volume = buyer_initiated['Quantity'].sum()
seller_volume = seller_initiated['Quantity'].sum()
total_volume = btc_sample['Quantity'].sum()

print(f"\nVolume breakdown:")
print(f"Buyer volume: {buyer_volume:.8f} BTC ({buyer_volume/total_volume*100:.1f}%)")
print(f"Seller volume: {seller_volume:.8f} BTC ({seller_volume/total_volume*100:.1f}%)")

# Best price match analysis
best_price_trades = btc_sample[btc_sample['IsBestPriceMatch'] == True]
print(f"\nBest price match trades: {len(best_price_trades):,} ({len(best_price_trades)/len(btc_sample)*100:.1f}%)")
```

### Example 4: Time Series Analysis

```python
import matplotlib.pyplot as plt

# Load data for time series analysis
data = loader.load_ticker_data("BTCUSDT", "2018-04-07", "2018-04-09")

# Convert to time series with 1-minute intervals
data['minute'] = data['datetime'].dt.floor('T')
minute_data = data.groupby('minute').agg({
    'Price': ['first', 'max', 'min', 'last'],
    'Quantity': 'sum',
    'Id': 'count'
}).round(8)

minute_data.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Trades']

print("=== 1-Minute OHLC Data Sample ===")
print(minute_data.head(10))

# Calculate some basic statistics
print(f"\nTime series statistics:")
print(f"Total minutes: {len(minute_data)}")
print(f"Average trades per minute: {minute_data['Trades'].mean():.1f}")
print(f"Average volume per minute: {minute_data['Volume'].mean():.8f} BTC")
```

### Example 5: Cross-Ticker Comparison

```python
# Compare multiple tickers for the same date
date = "2018-04-07"
tickers = ["BTCUSDT", "ETHBTC", "NEOUSDT"]

print(f"=== Cross-Ticker Comparison for {date} ===")

comparison_data = {}
for ticker in tickers:
    try:
        data = loader.load_ticker_data(ticker, date, date)
        comparison_data[ticker] = {
            'trades': len(data),
            'volume': data['Quantity'].sum(),
            'price_min': data['Price'].min(),
            'price_max': data['Price'].max(),
            'price_avg': data['Price'].mean()
        }
    except Exception as e:
        print(f"Error loading {ticker}: {e}")

# Display comparison table
import pandas as pd
comparison_df = pd.DataFrame(comparison_data).T
print(comparison_df.round(8))
```

### Example 6: Memory-Efficient Large Data Processing

```python
# Process large datasets efficiently
def process_large_dataset(ticker, start_date, end_date, chunk_days=7):
    """Process large datasets in chunks to manage memory usage."""
    
    from datetime import datetime, timedelta
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    results = []
    current_date = start_dt
    
    while current_date <= end_dt:
        chunk_end = min(current_date + timedelta(days=chunk_days-1), end_dt)
        
        print(f"Processing {ticker} from {current_date.date()} to {chunk_end.date()}")
        
        chunk_data = loader.load_ticker_data(
            ticker, 
            current_date.strftime("%Y-%m-%d"), 
            chunk_end.strftime("%Y-%m-%d")
        )
        
        if not chunk_data.empty:
            # Process chunk (example: calculate daily statistics)
            daily_stats = chunk_data.groupby('date').agg({
                'Price': ['min', 'max', 'mean'],
                'Quantity': 'sum',
                'Id': 'count'
            })
            results.append(daily_stats)
        
        current_date = chunk_end + timedelta(days=1)
    
    return pd.concat(results) if results else pd.DataFrame()

# Example usage
monthly_stats = process_large_dataset("BTCUSDT", "2018-04-07", "2018-05-07")
print("Monthly statistics calculated efficiently!")
```

## 🔧 Advanced Features

### Error Handling

The module includes comprehensive error handling:

```python
try:
    # Invalid ticker
    data = loader.load_ticker_data("INVALID", "2018-04-07")
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Ticker INVALID not found. Available tickers: [...]

try:
    # Invalid date format
    data = loader.load_ticker_data("BTCUSDT", "invalid-date")
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: time data 'invalid-date' does not match format '%Y-%m-%d'

try:
    # Start date after end date
    data = loader.load_ticker_data("BTCUSDT", "2018-04-10", "2018-04-07")
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Start date 2018-04-10 is after end date 2018-04-07
```

### Data Validation

```python
# Validate loaded data
def validate_data(df, ticker):
    """Validate loaded cryptocurrency data."""
    
    required_columns = ['Id', 'time', 'Price', 'Quantity', 'IsBuyerMaker', 
                       'BuyerOrderId', 'SellerOrderId', 'IsBestPriceMatch', 
                       'datetime', 'date']
    
    print(f"=== Data Validation for {ticker} ===")
    
    # Check columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"❌ Missing columns: {missing_cols}")
    else:
        print("✅ All required columns present")
    
    # Check data types
    print(f"✅ DataFrame shape: {df.shape}")
    print(f"✅ Datetime column type: {df['datetime'].dtype}")
    print(f"✅ Price column type: {df['Price'].dtype}")
    
    # Check for missing values
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        print(f"⚠️  Null values found: {null_counts[null_counts > 0].to_dict()}")
    else:
        print("✅ No null values found")
    
    # Check time ordering
    if df['time'].is_monotonic_increasing:
        print("✅ Data is properly sorted by time")
    else:
        print("⚠️  Data may not be sorted by time")

# Example usage
btc_data = loader.load_ticker_data("BTCUSDT", "2018-04-07", "2018-04-07")
validate_data(btc_data, "BTCUSDT")
```

## 🧪 Testing

The module includes a comprehensive test suite with 21 test cases:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_read_ticker.py::TestTickerDataLoader -v
python -m pytest tests/test_read_ticker.py::TestUtilityFunctions -v
python -m pytest tests/test_read_ticker.py::TestRealDataIntegration -v
python -m pytest tests/test_read_ticker.py::TestErrorHandling -v
```

### Test Coverage

- ✅ **Unit Tests**: Core functionality, data loading, date filtering
- ✅ **Integration Tests**: Real data loading with actual cryptocurrency files
- ✅ **Error Handling**: Invalid inputs, missing files, corrupted data
- ✅ **Edge Cases**: Boundary conditions, empty datasets, malformed dates
- ✅ **Data Validation**: DataFrame structure, timestamp conversion, sorting

## 📈 Performance Considerations

### Memory Usage

```python
# Monitor memory usage for large datasets
import psutil
import os

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

# Example: Load progressively larger datasets
datasets = [
    ("1 day", "2018-04-07", "2018-04-07"),
    ("1 week", "2018-04-07", "2018-04-13"),
    ("1 month", "2018-04-07", "2018-05-07")
]

for name, start, end in datasets:
    mem_before = get_memory_usage()
    data = loader.load_ticker_data("BTCUSDT", start, end)
    mem_after = get_memory_usage()
    
    print(f"{name}: {len(data):,} trades, "
          f"Memory: {mem_after - mem_before:.1f} MB, "
          f"DataFrame size: {data.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
```

### Loading Speed

```python
import time

def benchmark_loading(ticker, start_date, end_date):
    """Benchmark data loading speed."""
    
    start_time = time.time()
    data = loader.load_ticker_data(ticker, start_date, end_date)
    end_time = time.time()
    
    loading_time = end_time - start_time
    trades_per_second = len(data) / loading_time if loading_time > 0 else 0
    
    print(f"Loaded {len(data):,} trades in {loading_time:.2f}s "
          f"({trades_per_second:,.0f} trades/sec)")
    
    return data, loading_time

# Benchmark different dataset sizes
benchmark_loading("BTCUSDT", "2018-04-07", "2018-04-07")  # 1 day
benchmark_loading("BTCUSDT", "2018-04-07", "2018-04-13")  # 1 week
```

## 🔍 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure you're importing from the correct path
   ```python
   # Correct import
   from reading_src import TickerDataLoader
   
   # Alternative if path issues
   import sys
   sys.path.append('reading-src')
   from read_ticker import TickerDataLoader
   ```

2. **FileNotFoundError**: Check data directory path
   ```python
   # Check if data directory exists
   import os
   if not os.path.exists('data'):
       print("Data directory not found. Please ensure the data folder is present.")
   
   # Use custom path
   loader = TickerDataLoader(data_path="/path/to/your/data")
   ```

3. **Empty DataFrame**: Verify ticker and date range
   ```python
   # Check available tickers and date ranges
   print("Available tickers:", loader.get_available_tickers())
   for ticker in loader.get_available_tickers():
       start, end = loader.get_date_range(ticker)
       print(f"{ticker}: {start.date()} to {end.date()}")
   ```

4. **Memory Issues**: Use chunked processing for large datasets
   ```python
   # Process data in smaller chunks
   def load_in_chunks(ticker, start_date, end_date, chunk_days=7):
       # Implementation shown in Example 6 above
       pass
   ```

## 📝 Contributing

When contributing to this module:

1. **Run tests**: Ensure all tests pass before submitting changes
2. **Add tests**: Include tests for new functionality
3. **Follow conventions**: Use existing code style and naming patterns
4. **Update documentation**: Keep this README updated with new features

## 📄 License

This project follows the same license as the main repository. See the main README.md for license information.

## 🙏 Acknowledgments

- Data provided by the [cryptocurrency-ticks-data](https://github.com/Nucs/cryptocurrency-ticks-data) repository
- Built with [pandas](https://pandas.pydata.org/) for efficient data manipulation
- Tested with [pytest](https://pytest.org/) for reliable functionality

---

**Happy analyzing! 📊🚀**

For questions or issues, please open an issue in the main repository or refer to the comprehensive test suite for usage examples.
