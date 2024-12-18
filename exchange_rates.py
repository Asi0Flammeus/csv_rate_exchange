from typing import Optional, Dict, Tuple, List
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, date
import argparse
import sys
import os
from pathlib import Path

AVAILABLE_CURRENCIES: Dict[str, Tuple[str, str]] = {
    "0": ("EUR", "Euros"),
    "1": ("USD", "US Dollar"),
    "2": ("GBP", "British Pound"),
    "3": ("JPY", "Japanese Yen"),
    "4": ("CHF", "Swiss Franc"),
    "5": ("AUD", "Australian Dollar"),
    "6": ("CAD", "Canadian Dollar"),
    "7": ("CNY", "Chinese Yuan"),
    "8": ("HKD", "Hong Kong Dollar"),
    "9": ("NZD", "New Zealand Dollar"),
    "10": ("SEK", "Swedish Krona"),
    "11": ("BTC", "Bitcoin")
}

def ensure_output_dir() -> Path:
    """Creates and returns the path to the output directory."""
    output_dir = Path("exchange_rates_data")
    output_dir.mkdir(exist_ok=True)
    return output_dir

def fill_missing_dates(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fill missing dates in the DataFrame with interpolated values.
    
    Args:
        df: DataFrame containing exchange rate data
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        DataFrame with complete date range and interpolated values
    """
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    complete_df = pd.DataFrame({'Date': date_range})
    merged_df = pd.merge(complete_df, df, on='Date', how='left')
    rate_column = merged_df.columns[1]
    merged_df[rate_column] = merged_df[rate_column].interpolate(method='linear')
    merged_df['Date'] = merged_df['Date'].dt.date
    
    missing_dates = set(date_range.date) - set(pd.to_datetime(df['Date']).dt.date)
    if missing_dates:
        print("\nMissing dates filled with interpolated values:")
        for missing_date in sorted(missing_dates):
            rate = merged_df.loc[merged_df['Date'] == missing_date, rate_column].iloc[0]
            print(f"{missing_date}: {rate:.4f}")
    
    return merged_df

def get_exchange_rate(base_currency: str, quote_currency: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """
    Fetch historical exchange rates from Yahoo Finance.
    
    Args:
        base_currency: Base currency code
        quote_currency: Quote currency code
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        DataFrame with daily rates or None if fetch fails
    """
    symbol = f"BTC-{base_currency}" if quote_currency.upper() == "BTC" else f"{base_currency}{quote_currency}=X"
    
    try:
        df = yf.Ticker(symbol).history(start=start_date, end=end_date)
        df = df[['Close']].reset_index()
        df.columns = ['Date', f'{base_currency}/{quote_currency}']
        return fill_missing_dates(df, start_date, end_date)
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def select_currency(prompt: str) -> str:
    """
    Display available currencies and get user selection.
    
    Args:
        prompt: Message to display when asking for currency selection
    
    Returns:
        Selected currency code
    """
    print(f"\n{prompt}")
    for key, (code, name) in AVAILABLE_CURRENCIES.items():
        print(f"{key}. {code} - {name}")
    
    while True:
        choice = input("\nSelect a currency (0-11): ")
        if choice in AVAILABLE_CURRENCIES:
            return AVAILABLE_CURRENCIES[choice][0]
        print("Invalid choice. Please try again.")

def select_timeframe() -> Tuple[str, str]:
    """
    Get user-selected time period for data retrieval.
    
    Returns:
        Tuple containing start and end dates in YYYY-MM-DD format
    """
    print("\nTimeframe options:")
    print("1. Last year (365 days)")
    print("2. Current year (from January 1st)")
    print("3. Custom dates")
    
    while True:
        choice = input("\nSelect timeframe option (1-3): ")
        
        if choice == "1":
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            return start_date, end_date
            
        elif choice == "2":
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = f"{datetime.now().year}-01-01"
            return start_date, end_date
            
        elif choice == "3":
            while True:
                try:
                    start_date = input("Enter start date (YYYY-MM-DD): ")
                    end_date = input("Enter end date (YYYY-MM-DD): ")
                    datetime.strptime(start_date, '%Y-%m-%d')
                    datetime.strptime(end_date, '%Y-%m-%d')
                    return start_date, end_date
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD format.")
        
        print("Invalid choice. Please try again.")

def main() -> None:
    """Process command line arguments or provide interactive selection for exchange rate data export."""
    parser = argparse.ArgumentParser(description='Fetch exchange rate data from Yahoo Finance')
    parser.add_argument('base_currency', nargs='?', type=str, help='Base currency (e.g., USD, EUR)')
    parser.add_argument('quote_currency', nargs='?', type=str, help='Quote currency (e.g., CHF, BTC)')
    parser.add_argument('--start_date', type=str, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end_date', type=str, help='End date in YYYY-MM-DD format')
    
    args = parser.parse_args()
    output_dir = ensure_output_dir()
    
    if len(sys.argv) == 1:
        base_currency = select_currency("Select base currency:")
        quote_currency = select_currency("Select quote currency:")
        start_date, end_date = select_timeframe()
    else:
        base_currency = args.base_currency.upper()
        quote_currency = args.quote_currency.upper()
        start_date = args.start_date or (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        end_date = args.end_date or datetime.now().strftime('%Y-%m-%d')
    
    print(f"\nFetching exchange rate data for {base_currency}/{quote_currency}...")
    print(f"From {start_date} to {end_date}")
    
    df = get_exchange_rate(base_currency, quote_currency, start_date, end_date)
    
    if df is not None:
        output_filename = output_dir / f"{base_currency}_{quote_currency}_exchange_rate_{start_date}_to_{end_date}.csv"
        df.to_csv(output_filename, index=False, date_format='%Y-%m-%d')
        print(f"\nData exported successfully to {output_filename}")
        
        print("\nFirst few rows of the data:")
        print(df.head().to_string())
        
        rate_column = f"{base_currency}/{quote_currency}"
        print("\nBasic statistics:")
        print(f"Average rate: {df[rate_column].mean():.2f}")
        print(f"Minimum rate: {df[rate_column].min():.2f}")
        print(f"Maximum rate: {df[rate_column].max():.2f}")
    else:
        print("Failed to fetch exchange rate data")

if __name__ == "__main__":
    main()
