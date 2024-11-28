# Exchange Rate Data Export

## Introduction

Finding reliable and easy-to-use sources for historical exchange rate data in CSV format can be a real challenge. Most websites either require paid subscriptions, have limited data availability, or provide data in inconvenient formats. To solve this problem, I've developed (with the assistance of Claude Sonnet from Anthropic) this command-line tool that makes it simple to export historical exchange rate data to CSV files.

The tool uses Yahoo Finance's API to fetch exchange rates, supports multiple currencies including Bitcoin, and handles missing data through interpolation. All data is neatly organized in a dedicated folder for easy access and management.

## Features

- Support for major currencies and Bitcoin
- Interactive mode for easy currency and timeframe selection
- Command-line arguments for scripting and automation
- Automatic handling of missing dates through interpolation
- Basic statistical analysis of the exchange rates
- Organized output in a dedicated folder
- Support for custom date ranges

## Supported Currencies

1. USD (US Dollar)
2. GBP (British Pound)
3. JPY (Japanese Yen)
4. CHF (Swiss Franc)
5. AUD (Australian Dollar)
6. CAD (Canadian Dollar)
7. CNY (Chinese Yuan)
8. HKD (Hong Kong Dollar)
9. NZD (New Zealand Dollar)
10. SEK (Swedish Krona)
11. BTC (Bitcoin)

## Setup

### Requirements

- Python 3.8 or higher
- pip3 (Python package installer)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/Asi0Flammeus/exchange-rate-exporter.git
cd exchange-rate-exporter
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv env
# On Windows:
env\Scripts\activate
# On Unix or MacOS:
source env/bin/activate
```

3. Install required packages:

```bash
pip3 install -r requirements.txt
```

## Usage

### Interactive Mode

Simply run the script without arguments:

```bash
python exchange_rates.py
```

Follow the prompts to:

1. Select a currency
2. Choose a timeframe:
   - Last year (365 days)
   - Current year (from January 1st)
   - Custom dates

### Command Line Mode

Use arguments to fetch specific data:

```bash
python exchange_rates.py BTC --start_date 2023-01-01 --end_date 2024-01-01
```

Available arguments:

- `quote_currency`: Currency code (e.g., CHF, BTC)
- `--start_date`: Start date in YYYY-MM-DD format
- `--end_date`: End date in YYYY-MM-DD format

### Output

- All CSV files are saved in the `exchange_rates_data` folder
- File naming format: `EUR_[CURRENCY]_exchange_rate_[START_DATE]_to_[END_DATE].csv`
- Data format:
  ```
  Date,EUR/[CURRENCY]
  2023-01-01,1.2345
  2023-01-02,1.2346
  ...
  ```

### Statistical Information

The tool provides basic statistics for each export:

- Average rate
- Minimum rate
- Maximum rate

## Data Handling

- Missing dates are automatically detected and filled using linear interpolation
- The script notifies you when dates are interpolated and shows the calculated values
- All dates use `YYYY-MM-DD` format
- Exchange rates maintain full precision from the source

## Error Handling

- Invalid dates are caught and reported
- Network issues are handled gracefully
- Missing data is interpolated and reported
- Timezone mismatches are automatically resolved

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Claude Sonnet (Anthropic) for assistance in development
- Yahoo Finance for providing the exchange rate data
- The open-source community for the excellent Python libraries used in this project
