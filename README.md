# Job Market Analytics - Kalibrr Job Scraper

A lightweight Python scraper that uses **requests** and **BeautifulSoup** to collect job listings from Kalibrr. The extracted data is organized into dynamic timestamped CSV files and automatically uploaded to a **Supabase** database for visualization using **Metabase** (Docker).

---

## 📁 Project Structure

```text
JOB-MARKET-ANALYTICS/
│
├── .github/workflows/
│   └── scrape.yml             # GitHub Actions workflow (Manual execution only)
├── result_csv/                # Folder for scraped outputs (Ignored by Git via .gitignore)
│   └── kalibrr_jobs_*.csv     # Dynamic timestamped CSV files
├── .env                       # Secret environment credentials (Supabase API & PostgreSQL)
├── .gitignore                 # Excludes generated CSV files, caches, and the .env file
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── scraper.py                 # Main Kalibrr scraping script
└── upload_to_supabase.py      # Script to clean and upload CSV data to Supabase