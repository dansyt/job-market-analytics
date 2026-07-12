Job Market Analytics - Kalibrr Job Scraper
A lightweight Python scraper that uses requests and BeautifulSoup to collect job listings from Kalibrr. The extracted data is organized into dynamic timestamped CSV files and automatically uploaded to a Supabase database for visualization using Metabase (Docker).
---
📁 Project Structure
```text
JOB-MARKET-ANALYTICS/
│
├── .github/workflows/
│   └── scrape.yml             # GitHub Actions CI/CD pipeline configured for manual workflow execution
├── result_csv/                # Target directory where the scraper dumps raw, timestamped CSV files (Git-ignored)
│   └── kalibrr_jobs_*.csv     # Dynamic data outputs containing extracted job details (titles, salaries, roles, etc.)
├── .env                       # Local configuration file containing sensitive database tokens and API access keys
├── .gitignore                 # Specifies intentionally untracked files (e.g., .env, result_csv/, caches) to prevent security leaks
├── README.md                  # Comprehensive project documentation, setup guides, and operational workflows
├── requirements.txt           # Package manifest listing necessary Python libraries (e.g., requests, supabase, pandas)
├── scraper.py                 # Core scraping engine that targets the Kalibrr platform, extracts job nodes, and handles pagination
└── upload_to_supabase.py      # Data pipeline script that formats column schemas, handles missing values, and upserts data to Supabase
```
---
📊 Extracted Data Schema
The following table fields are parsed by `scraper.py` and sanitized into a lowercase `snake_case` schema before being pushed to Supabase:
Field	Description
`title`	The official job position/title.
`company`	The name of the hiring organization.
`location`	The corporate office address or geographic location.
`work_experience`	The required minimum years of experience.
`salary`	Estimated compensation package (Sanitized into IDR, with automated handling for PHP foreign exchange).
`skills`	Core technical competencies and tags required for the role.
`job_description`	Detailed responsibilities and day-to-day duties.
`qualification`	Educational requirements and background prerequisites.
`posted_at`	The original publication date of the listing on Kalibrr.
`scraped_at`	Precision metadata timestamp marking when the data entry was gathered.
---
