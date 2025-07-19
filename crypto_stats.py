#!/usr/bin/env python3
"""
Cryptocurrency Statistical Analysis Tool

Generate comprehensive statistical insights for cryptocurrency tickers.
Supports single ticker, multiple tickers, or all available tickers with optional date ranges.
"""

import argparse
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
except ImportError:
    PANDAS_TA_AVAILABLE = False
    print("Warning: pandas_ta not available, using manual technical indicator calculations", file=sys.stderr)
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'reading-src'))
from read_ticker import TickerDataLoader, list_available_tickers


class CryptoStatisticalAnalyzer:
    """Main class for cryptocurrency statistical analysis."""
    
    def __init__(self, data_path: str = "data"):
        self.loader = TickerDataLoader(data_path)
        self.available_tickers = self.loader.get_available_tickers()
    
    def calculate_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic statistical measures."""
        if df.empty:
            return {}
        
        price_stats = {
            'mean_price': df['Price'].mean(),
            'median_price': df['Price'].median(),
            'std_price': df['Price'].std(),
            'variance_price': df['Price'].var(),
            'skewness_price': df['Price'].skew(),
            'kurtosis_price': df['Price'].kurtosis(),
            'min_price': df['Price'].min(),
            'max_price': df['Price'].max(),
            'price_range': df['Price'].max() - df['Price'].min(),
        }
        
        df['returns'] = df['Price'].pct_change()
        df['log_returns'] = np.log(df['Price'] / df['Price'].shift(1))
        
        return_stats = {
            'mean_returns': df['returns'].mean(),
            'std_returns': df['returns'].std(),
            'skewness_returns': df['returns'].skew(),
            'kurtosis_returns': df['returns'].kurtosis(),
            'cumulative_return': (df['Price'].iloc[-1] / df['Price'].iloc[0]) - 1,
        }
        
        volume_stats = {
            'total_volume': df['Quantity'].sum(),
            'mean_volume': df['Quantity'].mean(),
            'median_volume': df['Quantity'].median(),
            'std_volume': df['Quantity'].std(),
            'total_trades': len(df),
        }
        
        return {**price_stats, **return_stats, **volume_stats}
    
    def calculate_sma(self, prices: pd.Series, window: int) -> pd.Series:
        """Calculate Simple Moving Average manually."""
        return prices.rolling(window=window).mean()
    
    def calculate_ema(self, prices: pd.Series, window: int) -> pd.Series:
        """Calculate Exponential Moving Average manually."""
        return prices.ewm(span=window).mean()
    
    def calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI manually."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, std_dev: float = 2.0):
        """Calculate Bollinger Bands manually."""
        sma = self.calculate_sma(prices, window)
        std = prices.rolling(window=window).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return lower_band, sma, upper_band
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD manually."""
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal)
        return macd_line, signal_line
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators."""
        if df.empty or len(df) < 50:
            return {}
        
        tech_stats = {}
        
        use_manual_calculations = not PANDAS_TA_AVAILABLE
        
        if PANDAS_TA_AVAILABLE:
            try:
                df['SMA_10'] = ta.sma(df['Price'], length=10)
                df['SMA_20'] = ta.sma(df['Price'], length=20)
                df['SMA_50'] = ta.sma(df['Price'], length=50)
                df['EMA_10'] = ta.ema(df['Price'], length=10)
                df['EMA_20'] = ta.ema(df['Price'], length=20)
                df['RSI'] = ta.rsi(df['Price'], length=14)
                
                macd_data = ta.macd(df['Price'])
                if macd_data is not None:
                    df = pd.concat([df, macd_data], axis=1)
                
                bb_data = ta.bbands(df['Price'], length=20)
                if bb_data is not None:
                    df = pd.concat([df, bb_data], axis=1)
            except Exception as e:
                print(f"Warning: pandas_ta failed, using manual calculations: {e}", file=sys.stderr)
                use_manual_calculations = True
        
        if use_manual_calculations:
            df['SMA_10'] = self.calculate_sma(df['Price'], 10)
            df['SMA_20'] = self.calculate_sma(df['Price'], 20)
            df['SMA_50'] = self.calculate_sma(df['Price'], 50)
            df['EMA_10'] = self.calculate_ema(df['Price'], 10)
            df['EMA_20'] = self.calculate_ema(df['Price'], 20)
            df['RSI'] = self.calculate_rsi(df['Price'], 14)
            
            bb_lower, bb_middle, bb_upper = self.calculate_bollinger_bands(df['Price'], 20)
            df['BBL_20_2.0'] = bb_lower
            df['BBM_20_2.0'] = bb_middle
            df['BBU_20_2.0'] = bb_upper
            
            macd_line, signal_line = self.calculate_macd(df['Price'])
            df['MACD_12_26_9'] = macd_line
            df['MACDs_12_26_9'] = signal_line
        
        if 'SMA_20' in df.columns and not pd.isna(df['SMA_20'].iloc[-1]):
            tech_stats['current_sma_20'] = df['SMA_20'].iloc[-1]
            tech_stats['price_vs_sma_20'] = (df['Price'].iloc[-1] / df['SMA_20'].iloc[-1] - 1) * 100
        
        if 'RSI' in df.columns and not pd.isna(df['RSI'].iloc[-1]):
            tech_stats['current_rsi'] = df['RSI'].iloc[-1]
            tech_stats['avg_rsi'] = df['RSI'].mean()
        
        if 'MACD_12_26_9' in df.columns and not pd.isna(df['MACD_12_26_9'].iloc[-1]):
            tech_stats['current_macd'] = df['MACD_12_26_9'].iloc[-1]
            if 'MACDs_12_26_9' in df.columns:
                tech_stats['current_macd_signal'] = df['MACDs_12_26_9'].iloc[-1]
        
        if 'BBL_20_2.0' in df.columns and 'BBU_20_2.0' in df.columns:
            if not pd.isna(df['BBL_20_2.0'].iloc[-1]) and not pd.isna(df['BBU_20_2.0'].iloc[-1]):
                tech_stats['bb_lower'] = df['BBL_20_2.0'].iloc[-1]
                tech_stats['bb_upper'] = df['BBU_20_2.0'].iloc[-1]
                tech_stats['bb_width'] = df['BBU_20_2.0'].iloc[-1] - df['BBL_20_2.0'].iloc[-1]
        
        return tech_stats
    
    def analyze_ticker(self, ticker: str, start_date: Optional[str] = None, 
                      end_date: Optional[str] = None) -> Dict[str, Any]:
        """Perform comprehensive analysis for a single ticker."""
        try:
            df = self.loader.load_ticker_data(ticker, start_date, end_date)
            
            if df.empty:
                return {
                    'ticker': ticker,
                    'error': 'No data available for specified date range',
                    'data_points': 0
                }
            
            basic_stats = self.calculate_basic_statistics(df.copy())
            tech_stats = self.calculate_technical_indicators(df.copy())
            
            date_info = {
                'start_date': df['date'].min(),
                'end_date': df['date'].max(),
                'data_points': len(df),
                'unique_days': df['date'].nunique()
            }
            
            return {
                'ticker': ticker,
                'date_info': date_info,
                'basic_statistics': basic_stats,
                'technical_indicators': tech_stats,
                'success': True
            }
            
        except Exception as e:
            return {
                'ticker': ticker,
                'error': str(e),
                'success': False
            }


def format_output(results: List[Dict[str, Any]]) -> str:
    """Format analysis results for display."""
    output = []
    output.append("=" * 80)
    output.append("CRYPTOCURRENCY STATISTICAL ANALYSIS REPORT")
    output.append("=" * 80)
    
    for result in results:
        ticker = result['ticker']
        output.append(f"\n{'='*20} {ticker} {'='*20}")
        
        if not result.get('success', False):
            output.append(f"ERROR: {result.get('error', 'Unknown error')}")
            continue
        
        date_info = result['date_info']
        output.append(f"Date Range: {date_info['start_date']} to {date_info['end_date']}")
        output.append(f"Data Points: {date_info['data_points']:,} trades across {date_info['unique_days']} days")
        
        basic = result['basic_statistics']
        if basic:
            output.append(f"\nBASIC STATISTICS:")
            output.append(f"  Price - Mean: ${basic['mean_price']:.4f}, Median: ${basic['median_price']:.4f}")
            output.append(f"  Price - Min: ${basic['min_price']:.4f}, Max: ${basic['max_price']:.4f}")
            output.append(f"  Price - Std Dev: ${basic['std_price']:.4f}, Variance: {basic['variance_price']:.4f}")
            output.append(f"  Price - Skewness: {basic['skewness_price']:.4f}, Kurtosis: {basic['kurtosis_price']:.4f}")
            output.append(f"  Returns - Mean: {basic['mean_returns']*100:.4f}%, Std: {basic['std_returns']*100:.4f}%")
            output.append(f"  Cumulative Return: {basic['cumulative_return']*100:.2f}%")
            output.append(f"  Volume - Total: {basic['total_volume']:.8f}, Mean: {basic['mean_volume']:.8f}")
            output.append(f"  Total Trades: {basic['total_trades']:,}")
        
        tech = result['technical_indicators']
        if tech:
            output.append(f"\nTECHNICAL INDICATORS:")
            if 'current_rsi' in tech:
                output.append(f"  RSI: {tech['current_rsi']:.2f} (Avg: {tech['avg_rsi']:.2f})")
            if 'current_sma_20' in tech:
                output.append(f"  SMA(20): ${tech['current_sma_20']:.4f}")
                output.append(f"  Price vs SMA(20): {tech['price_vs_sma_20']:.2f}%")
            if 'current_macd' in tech:
                output.append(f"  MACD: {tech['current_macd']:.6f}, Signal: {tech['current_macd_signal']:.6f}")
            if 'bb_lower' in tech and 'bb_upper' in tech:
                output.append(f"  Bollinger Bands: Lower ${tech['bb_lower']:.4f}, Upper ${tech['bb_upper']:.4f}")
                output.append(f"  Bollinger Band Width: ${tech['bb_width']:.4f}")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='Cryptocurrency Statistical Analysis Tool')
    parser.add_argument('tickers', help='Ticker symbol(s): single (BTCUSDT), multiple (BTCUSDT,ETHBTC), or "all"')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD format)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD format)')
    parser.add_argument('--data-path', default='data', help='Path to data directory')
    
    args = parser.parse_args()
    
    analyzer = CryptoStatisticalAnalyzer(args.data_path)
    
    if args.tickers.lower() == 'all':
        tickers_to_analyze = analyzer.available_tickers
    else:
        tickers_to_analyze = [t.strip().upper() for t in args.tickers.split(',')]
    
    invalid_tickers = [t for t in tickers_to_analyze if t not in analyzer.available_tickers]
    if invalid_tickers:
        print(f"Error: Invalid tickers: {invalid_tickers}")
        print(f"Available tickers: {analyzer.available_tickers}")
        sys.exit(1)
    
    results = []
    for ticker in tickers_to_analyze:
        print(f"Analyzing {ticker}...", file=sys.stderr)
        result = analyzer.analyze_ticker(ticker, args.start_date, args.end_date)
        results.append(result)
    
    print(format_output(results))


if __name__ == "__main__":
    main()
