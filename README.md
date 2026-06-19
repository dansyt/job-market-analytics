# Kalibrr Job Scraper

A lightweight Python scraper that uses **requests** and **BeautifulSoup** to collect job listings from Kalibrr.

## How to Run Locally
```
python scraper.py --pages 3 --output kalibrr_jobs.csv
```

## GitHub Actions Workflow
The workflow defined in `.github/workflows/scrape.yml` runs on every push to `main` **and** daily at 00:00 UTC, executing the scraper and uploading the generated `kalibrr_jobs.csv` as an artifact.

## Project Structure
- `scraper.py` – main scraping script.
- `.github/workflows/scrape.yml` – CI workflow.
- `requirements.txt` – Python dependencies.
- `.gitignore` – excludes generated CSV files, caches, and OS‑specific artefacts.

