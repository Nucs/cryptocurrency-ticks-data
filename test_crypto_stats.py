#!/usr/bin/env python3
"""
Test script for crypto_stats.py functionality.
"""

import subprocess
import sys
import os

def test_single_ticker():
    """Test analysis of a single ticker."""
    print("Testing single ticker analysis...")
    result = subprocess.run([
        sys.executable, 'crypto_stats.py', 'BTCUSDT', 
        '--start-date', '2018-04-07', '--end-date', '2018-04-07'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Single ticker test passed")
        print("Sample output:")
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        return True
    else:
        print(f"✗ Single ticker test failed: {result.stderr}")
        return False

def test_multiple_tickers():
    """Test analysis of multiple tickers."""
    print("Testing multiple ticker analysis...")
    result = subprocess.run([
        sys.executable, 'crypto_stats.py', 'BTCUSDT,ETHBTC', 
        '--start-date', '2018-04-07', '--end-date', '2018-04-07'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Multiple ticker test passed")
        return True
    else:
        print(f"✗ Multiple ticker test failed: {result.stderr}")
        return False

def test_invalid_ticker():
    """Test error handling for invalid ticker."""
    print("Testing invalid ticker handling...")
    result = subprocess.run([
        sys.executable, 'crypto_stats.py', 'INVALID'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("✓ Invalid ticker test passed (correctly failed)")
        return True
    else:
        print("✗ Invalid ticker test failed (should have failed)")
        return False

def test_date_range():
    """Test date range functionality."""
    print("Testing date range functionality...")
    result = subprocess.run([
        sys.executable, 'crypto_stats.py', 'BTCUSDT', 
        '--start-date', '2018-04-07', '--end-date', '2018-04-09'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Date range test passed")
        return True
    else:
        print(f"✗ Date range test failed: {result.stderr}")
        return False

def test_no_date_range():
    """Test analysis without date range (should use all available data)."""
    print("Testing analysis without date range...")
    result = subprocess.run([
        sys.executable, 'crypto_stats.py', 'NEOUSDT'
    ], capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("✓ No date range test passed")
        return True
    else:
        print(f"✗ No date range test failed: {result.stderr}")
        return False

def main():
    """Run all tests."""
    print("Running crypto_stats.py tests...")
    print("=" * 50)
    
    tests = [
        test_single_ticker, 
        test_multiple_tickers, 
        test_invalid_ticker,
        test_date_range,
        test_no_date_range
    ]
    passed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
        print()
    
    print(f"Tests passed: {passed}/{len(tests)}")
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
