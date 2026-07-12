# Job Market Analytics - Kalibrr Job Scraper
 
A lightweight Python scraper that uses **requests** and **BeautifulSoup** to collect job listings from Kalibrr. The extracted data is organized into dynamic timestamped CSV files and automatically uploaded to a **Supabase** database for visualization using **Metabase** (Docker).

---
## 📁 Project Structure
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
### 📊 Extracted Data Schema

| Field | Description |
| :--- | :--- |
| `id` | Unique identifier for each job listing row. |
| `scraped_at` | Precision metadata timestamp marking when the data entry was gathered. |
| `title` | The official job position/title. |
| `company_name` | The name of the hiring organization. |
| `industry` | The sector or field of business the company operates in. |
| `specialization` | The specific functional area or domain of the job. |
| `education_level` | The minimum educational background required for applicants. |
| `job_level` | The career seniority level (e.g., Entry Level, Mid-Senior Level). |
| `city` | The primary city or region where the job is located. |
| `salary` | Estimated compensation package value. |
| `salary_interval` | The frequency of salary payments (e.g., Monthly, Yearly). |
| `job_type` | Employment type classification (e.g., Full-time, Part-time, Contract). |
| `is_hybrid` | Boolean flag indicating if the position supports a hybrid work arrangement. |
| `is_wfh` | Boolean flag indicating if the position allows fully working from home (Remote). |
| `is_fresh_grad` | Boolean flag indicating if the job welcomes entry-level or fresh graduates. |
| `url` | Direct web link to the specific job listing on Kalibrr. |
---
