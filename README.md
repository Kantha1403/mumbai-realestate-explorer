# Mumbai & Navi Mumbai Real Estate Explorer

An end-to-end data analysis project that scrapes live apartment listings from MagicBricks, analyzes pricing across localities, and serves an interactive dashboard for homebuyers.

## What This Project Does

- Scrapes 1,859 real apartment listings across Mumbai and Navi Mumbai from MagicBricks
- Extracts price, BHK type, locality, area, developer, possession date, and nearby facilities
- Cleans and analyzes data to calculate price per sq ft by locality
- Serves an interactive Streamlit dashboard where users can filter by city, locality, and BHK type

## Key Findings

- Taloja and New Panvel are the most affordable areas in Navi Mumbai at Rs 8,000-9,000 per sq ft
- Panvel offers the best value among well-connected areas at Rs 10,243 per sq ft (median)
- Kharghar sits at Rs 13,325 per sq ft — premium but with strong infrastructure
- Vashi and Seawoods are the most expensive at Rs 31,000+ per sq ft

## Tech Stack

- Scraping: Python, requests, BeautifulSoup, re (regex)
- Analysis: pandas, numpy
- Visualization: matplotlib, seaborn
- App: Streamlit

## Project Structure

- app.py — Streamlit dashboard
- real_estate_project_clean.ipynb — Full analysis notebook
- mumbai_realestate_master.csv — Scraped dataset (1,859 listings)
- requirements.txt — Python dependencies

## How to Run Locally

1. Clone the repository
2. Install dependencies
3. Run the app

git clone https://github.com/Kantha1403/mumbai-realestate-explorer.git
cd mumbai-realestate-explorer
pip install -r requirements.txt
streamlit run app.py

## Dashboard Features

- Filter by city (Mumbai / Navi Mumbai / Both)
- Filter by locality and BHK type
- Key metrics: total listings, median price, cheapest, most expensive
- Price by BHK chart and price distribution chart
- Price per sq ft comparison table across localities
- Nearby railway stations, hospitals, and supermarkets
- Top developers and full listings table

## Data Source

Live listings scraped from MagicBricks — 50 pages each for Mumbai and Navi Mumbai (100 pages total, approximately 2,250 raw listings, 1,859 after cleaning and deduplication).

## Author

Kantha — built as a portfolio project to learn Python data analysis and for personal homebuying research in Navi Mumbai.
