from typing import Optional, Dict, Tuple
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, date
import argparse
import sys
import os
from pathlib import Path

AVAILABLE_CURRENCIES: Dict[str, Tuple[str, str]] = {
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

def ensure_output_dir() -> str:
    """Creates and returns the path to the output directory."""
    output_dir = Path("exchange_rates_data")
    output_dir.mkdir(exist_ok=True)
    return str(output_dir)

def fill_missing_dates(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """Fill missing dates with interpolated values."""
    # Convert dates to timezone-naive datetime
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    
    # Create complete date range
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create a complete DataFrame with all dates
    complete_df = pd.DataFrame({'Date': date_range})
    
    # Merge with existing data
    merged_df = pd.merge(complete_df, df, on='Date', how='left')
    
    # Interpolate missing values
    rate_column = merged_df.columns[1]  # The rate column is always the second column
    merged_df[rate_column] = merged_df[rate_column].interpolate(method='linear')
    
    # Convert dates back to date objects
    merged_df['Date'] = merged_df['Date'].dt.date
    
    # Check if any dates were added
    missing_dates = set(date_range.date) - set(pd.to_datetime(df['Date']).dt.date)
    if missing_dates:
        print("\nMissing dates filled with interpolated values:")
        for missing_date in sorted(missing_dates):
            rate = merged_df.loc[merged_df['Date'] == missing_date, rate_column].iloc[0]
            print(f"{missing_date}: {rate:.4f}")
    
    return merged_df

def get_exchange_rate(base_currency: str, quote_currency: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """Fetches historical exchange rates from Yahoo Finance and returns a DataFrame with daily rates."""
    symbol = f"BTC-EUR" if quote_currency.upper() == "BTC" else f"{base_currency}{quote_currency}=X"
    
    try:
        # Fetch data
        df = yf.Ticker(symbol).history(start=start_date, end=end_date)
        df = df[['Close']].reset_index()
        df.columns = ['Date', f'{base_currency}/{quote_currency}']
        
        # Fill missing dates with interpolated values
        df = fill_missing_dates(df, start_date, end_date)
        
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def select_currency() -> str:
    """Displays available currencies and returns the selected currency code."""
    print("\nAvailable currencies:")
    for key, (code, name) in AVAILABLE_CURRENCIES.items():
        print(f"{key}. {code} - {name}")
    
    while True:
        choice = input("\nSelect a currency (1-11): ")
        if choice in AVAILABLE_CURRENCIES:
            return AVAILABLE_CURRENCIES[choice][0]
        print("Invalid choice. Please try again.")

def select_timeframe() -> Tuple[str, str]:
    """Prompts user for timeframe selection and returns start and end dates."""
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
    """Processes command line arguments or provides interactive selection for exchange rate data export."""
    parser = argparse.ArgumentParser(description='Fetch exchange rate data from Yahoo Finance')
    parser.add_argument('quote_currency', nargs='?', type=str, help='Quote currency (e.g., CHF, BTC)')
    parser.add_argument('--start_date', type=str, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end_date', type=str, help='End date in YYYY-MM-DD format')
    
    args = parser.parse_args()
    base_currency = "EUR"
    
    # Ensure output directory exists
    output_dir = ensure_output_dir()
    
    if len(sys.argv) == 1:
        quote_currency = select_currency()
        start_date, end_date = select_timeframe()
    else:
        quote_currency = args.quote_currency.upper()
        start_date = args.start_date or (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        end_date = args.end_date or datetime.now().strftime('%Y-%m-%d')
    
    print(f"\nFetching exchange rate data for {base_currency}/{quote_currency}...")
    print(f"From {start_date} to {end_date}")
    
    df = get_exchange_rate(base_currency, quote_currency, start_date, end_date)
    
    if df is not None:
        # Create filename with full path
        output_filename = os.path.join(
            output_dir, 
            f"EUR_{quote_currency}_exchange_rate_{start_date}_to_{end_date}.csv"
        )
        
        df.to_csv(output_filename, index=False, date_format='%Y-%m-%d')
        print(f"\nData exported successfully to {output_filename}")
        
        print("\nFirst few rows of the data:")
        print(df.head().to_string())
        
        rate_column = f"EUR/{quote_currency}"
        print("\nBasic statistics:")
        print(f"Average rate: {df[rate_column].mean():.2f}")
        print(f"Minimum rate: {df[rate_column].min():.2f}")
        print(f"Maximum rate: {df[rate_column].max():.2f}")
    else:
        print("Failed to fetch exchange rate data")

if __name__ == "__main__":
    main()
