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
    *(Note : L'application nécessite soit `openpyxl` soit `xlsxwriter` pour l'export Excel. Le `requirements.txt` inclut les deux, mais Python installera ceux qui lui sont nécessaires.)*

