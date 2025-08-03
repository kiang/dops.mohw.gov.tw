# Taiwan MOHW Open Data Crawler

A Python crawler for fetching and converting ODS files from Taiwan's Ministry of Health and Welfare (MOHW) open data platform.

## Overview

This crawler fetches ODS (OpenDocument Spreadsheet) files from specific MOHW datasets and converts them to CSV format using LibreOffice headless mode for better performance.

### Supported Datasets

- **157217**: 家庭暴力資料集 (Family Violence Dataset)
- **152223**: 性侵害案件資料集 (Sexual Assault Cases Dataset)
- **156470**: 兒童及少年保護案件資料集 (Child and Youth Protection Cases Dataset)

## Features

- Fetches dataset metadata via Taiwan Open Data API
- Downloads ODS files for years 2019-2023 (Taiwan years 108-112)
- Converts ODS to CSV using LibreOffice headless mode
- Organizes output in `raw/{dataset_id}/{year}.csv` structure
- Handles Taiwan year (ROC) to Western year conversion
- Skips downloading if target CSV file already exists (incremental updates)

## Requirements

- Python 3.6+
- LibreOffice (for ODS to CSV conversion)
- Python packages: `requests`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dops.mohw.gov.tw.git
cd dops.mohw.gov.tw
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure LibreOffice is installed:
```bash
# Ubuntu/Debian
sudo apt-get install libreoffice

# macOS
brew install --cask libreoffice
```

## Usage

Run the crawler to fetch and convert all datasets:

```bash
python3 crawler.py
```

To test with a single dataset:

```bash
python3 test_single.py
```

## Output Structure

```
raw/
├── 152223/          # Sexual assault cases
│   ├── 2019.csv
│   ├── 2020.csv
│   ├── 2021.csv
│   ├── 2022.csv
│   └── 2023.csv
├── 156470/          # Child and youth protection
│   ├── 2019.csv
│   ├── 2020.csv
│   ├── 2021.csv
│   ├── 2022.csv
│   └── 2023.csv
└── 157217/          # Family violence
    ├── 2019.csv
    ├── 2020.csv
    ├── 2021.csv
    ├── 2022.csv
    └── 2023.csv
```

## How It Works

1. **API Query**: Fetches dataset metadata from `https://data.gov.tw/api/v2/rest/dataset/{dataset_id}`
2. **Year Extraction**: Extracts year from ODS filename (first 3 digits) and converts Taiwan year to Western year
3. **Download**: Downloads ODS files with proper headers to avoid 406 errors
4. **Conversion**: Uses LibreOffice headless mode for fast ODS to CSV conversion
5. **Cleanup**: Removes temporary ODS files after successful conversion

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Finjon Kiang

## Acknowledgments

- Data source: [Taiwan Government Open Data Platform](https://data.gov.tw)
- Ministry of Health and Welfare, Taiwan