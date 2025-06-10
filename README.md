# BI Pro CBD Shops – v3.4.1

## Description
This script, `rss_kilo2.py`, is a Business Intelligence (BI) tool designed for analyzing data from CBD shops. It provides various comparison tools and visualizations to help understand product diversity, publication volume, price distribution, and cannabinoid profiles across different shops.

## Key Features (v3.4.1 Updates)
*   **Reliable Multi-Shop Radar**: Utilizes `px.line_polar` for accurate multi-shop radar charts.
*   **Robust Average Rates Calculation**: Ensures the `avg_rates` variable is always defined and the related code executes only if `*_rate` columns are present.
*   **Consistent Dark Theme**: Implements `plotly_dark` template for improved readability on dark backgrounds, with legible axes.
*   **No Residual NameErrors**: Addresses and resolves any remaining `NameError` issues.

## Setup

### Prerequisites
*   Python 3.x
*   Required Python packages (listed in `requirements.txt`)

### Installation
1.  Clone this repository (if applicable) or ensure `rss_kilo2.py` is in your working directory.
2.  Install the necessary Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
This script is designed to be run as a Streamlit application.

To run the application:
```bash
streamlit run rss_kilo2.py
```

Once running, the application will open in your web browser, allowing you to interact with the BI dashboards and comparison tools.

## Configuration
Global configurations are defined within the script, including:
*   `USER_AGENT`: User agent string for requests.
*   `COLOR_SEQ_RADAR`: Color sequence for radar charts.
*   `EXPORT_EXCEL_ENGINE`: Engine for Excel exports.
*   `LOG_LEVEL`: Logging verbosity.
*   `RETRY_MAX`, `RETRY_BACKOFF`: Parameters for retrying failed requests.
*   `DEFAULT_DATE_RANGE_DAYS`: Default date range for data filtering.
*   `OUTLIER_IQR_FACTOR`: Factor for outlier detection.
*   `plotly_dark` template is set as default for all Plotly charts.

## Contact / Organization
For more information, you can refer to the GitHub organization mentioned in the `USER_AGENT`: `https://github.com/your-org` (Note: This is a placeholder and should be updated with the actual organization URL).
