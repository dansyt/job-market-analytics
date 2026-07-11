import csv
import time
import json
import re
import datetime
import argparse
import requests
from bs4 import BeautifulSoup

def format_salary(job):
    """
    Mengambil data salary dari JSON terstruktur (Next.js data).
    Lebih andal dibanding parsing teks HTML karena datanya bersumber dari API.
    """
    salary_shown = job.get("salaryShown", False)
    base_salary = job.get("baseSalary")
    max_salary = job.get("maximumSalary")
    # Selalu gunakan IDR untuk Indonesia, abaikan PHP atau currency lain
    currency = "IDR"
    interval = job.get("salaryInterval", "month")

    if not salary_shown or not base_salary:
        return "Gaji Tidak Diumumkan"

    # Format angka menjadi gaya Indonesia (misal: 5.000.000)
    def fmt(n):
        return f"{int(n):,}".replace(",", ".")

    if max_salary and max_salary != base_salary:
        return f"{currency} {fmt(base_salary)} - {fmt(max_salary)} / {interval}"
    else:
        return f"{currency} {fmt(base_salary)} / {interval}"


def extract_jobs_from_page(html):
    """
    Mengekstrak data jobs langsung dari JSON terstruktur Next.js
    yang disematkan di dalam tag <script> pada halaman.
    Cara ini tidak terpengaruh oleh lokasi server (Indonesia vs Amerika).
    """
    script_tags = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    next_data_script = None
    for tag in script_tags:
        if '"baseSalary"' in tag or '"salaryShown"' in tag:
            next_data_script = tag
            break

    if not next_data_script:
        return []

    try:
        data = json.loads(next_data_script)
        jobs = data.get("props", {}).get("pageProps", {}).get("jobs", [])
        return jobs
    except (json.JSONDecodeError, KeyError):
        return []


def scrape_kalibrr(keyword=None, max_pages=3, output_file="kalibrr_jobs.csv"):
    """
    Scraper untuk mengambil data lowongan pekerjaan dari Kalibrr.
    Menggunakan data JSON terstruktur (Next.js) untuk ekstraksi salary yang akurat,
    tidak bergantung pada lokasi server (Indonesia/Amerika/dll).
    """
    if keyword:
        formatted_keyword = keyword.strip().replace(" ", "-")
        base_url = f"https://www.kalibrr.com/id-ID/home/te/{formatted_keyword}"
    else:
        base_url = "https://www.kalibrr.com/id-ID/home/co/Indonesia"

    jobs_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    print(f"=== Memulai Scraping Kalibrr (Mode JSON Terstruktur) ===")
    print(f"Target: {'Umum (Semua Bidang)' if not keyword else f'Keyword: {keyword}'}")
    print(f"Jumlah Halaman Maksimal: {max_pages}")
    print(f"File Output: {output_file}\n")

    session = requests.Session()
    scraped_at = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
    
    proxies = {
        "http": "http://8.215.25.3:2080",
        "https": "https://8.215.25.3:2080"
    }
    session.proxies.update(proxies)

    for current_page in range(1, max_pages + 1):
        url = f"{base_url}?page={current_page}"
        print(f"-> Mengunduh halaman {current_page}: {url}")

        try:
            response = session.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"   [Gagal] Halaman mengembalikan status code: {response.status_code}")
                break
        except Exception as e:
            print(f"   [Gagal] Gagal menghubungi server: {e}")
            break

        # Ekstrak jobs dari JSON terstruktur Next.js
        jobs_json = extract_jobs_from_page(response.text)

        if not jobs_json:
            # Fallback ke BeautifulSoup jika JSON tidak ditemukan
            print("   [Info] JSON tidak ditemukan, beralih ke mode HTML parsing...")
            soup = BeautifulSoup(response.text, "html.parser")
            job_links = soup.select('a.k-text-black[href*="/jobs/"]')
            print(f"   Ditemukan {len(job_links)} kartu lowongan (mode HTML).")
            if not job_links:
                print("   Selesai (tidak ada lowongan baru atau halaman kosong).")
                break
            # Mode HTML fallback: ambil data dasar saja tanpa salary
            for link in job_links:
                title = link.get_text().strip()
                href = link.get("href", "")
                full_url = f"https://www.kalibrr.com{href}" if href else ""
                card = link.parent.parent.parent.parent
                lines = [l.strip() for l in card.get_text(separator="\n").split("\n") if l.strip()]
                company = lines[1] if len(lines) > 1 else ""
                location = lines[2] if len(lines) > 2 else ""
                jobs_data.append({
                    "Title": title, "Company": company, "Location": location,
                    "Salary": "Gaji Tidak Diumumkan", "Job Type": "", "Experience Level": "",
                    "Recruiter Status": "", "Deadline": "", "URL": full_url,
                    "Scraped At": scraped_at
                })
        else:
            print(f"   Ditemukan {len(jobs_json)} lowongan kerja di halaman ini.")
            if not jobs_json:
                print("   Selesai (tidak ada lowongan baru atau halaman kosong).")
                break

            for job in jobs_json:
                try:
                    # Ambil nama pekerjaan: bisa di field 'name' atau 'position'
                    title = job.get("name") or job.get("position", "")

                    # Data perusahaan
                    company_obj = job.get("company", {})
                    if isinstance(company_obj, dict):
                        company = company_obj.get("name", job.get("companyName", ""))
                    else:
                        company = job.get("companyName", "")

                    # Lokasi - ambil dari addressComponents
                    location_obj = job.get("googleLocation", {})
                    location = ""
                    if isinstance(location_obj, dict):
                        addr = location_obj.get("addressComponents", {})
                        if isinstance(addr, dict):
                            city = addr.get("city", "")
                            country = addr.get("country", "")
                            if city and country:
                                location = f"{city}, {country}"
                            elif city:
                                location = city

                    # Salary - dari data terstruktur, akurat di mana pun servernya
                    salary = format_salary(job)

                    # Tipe pekerjaan
                    tenure_map = {
                        "Full time": "Penuh waktu", "Part time": "Paruh waktu",
                        "Internship": "Magang", "Contract": "Kontrak"
                    }
                    job_type = tenure_map.get(job.get("tenure", ""), job.get("tenure", ""))

                    # Level pengalaman
                    work_exp = job.get("workExperience")
                    if job.get("isOpenToFreshGrads"):
                        experience_level = "Lulusan Baru / Junior"
                    elif work_exp:
                        experience_level = f"Min. {work_exp} bulan pengalaman"
                    else:
                        experience_level = ""

                    # Deadline
                    app_end = job.get("applicationEndDate", "")
                    if app_end:
                        try:
                            deadline_dt = datetime.datetime.fromisoformat(app_end.replace("Z", "+00:00"))
                            deadline = f"Apply before {deadline_dt.strftime('%-d %b')}"
                        except Exception:
                            deadline = app_end[:10]
                    else:
                        deadline = ""

                    # Status rekruter
                    recruiter_seen = job.get("esRecruiterLastSeen", "")
                    recruiter_status = f"Rekruter terakhir aktif {recruiter_seen}" if recruiter_seen else ""

                    # URL
                    slug = job.get("slug", "")
                    company_code = company_obj.get("code", "") if isinstance(company_obj, dict) else ""
                    full_url = f"https://www.kalibrr.com/id-ID/c/{company_code}/jobs/{job.get('id', '')}/{slug}" if slug else ""

                    jobs_data.append({
                        "Title": title,
                        "Company": company,
                        "Location": location,
                        "Salary": salary,
                        "Job Type": job_type,
                        "Experience Level": experience_level,
                        "Recruiter Status": recruiter_status,
                        "Deadline": deadline,
                        "URL": full_url,
                        "Scraped At": scraped_at
                    })

                except Exception as job_err:
                    print(f"   [Peringatan] Gagal memproses lowongan: {job_err}")

        # Jeda sopan
        time.sleep(1.5)

    # Simpan ke CSV
    if jobs_data:
        try:
            with open(output_file, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)
            print(f"\n[Sukses] Berhasil mengekstrak {len(jobs_data)} lowongan pekerjaan ke dalam file '{output_file}'!")
        except Exception as file_err:
            print(f"\n[Error] Gagal menulis data ke file CSV: {file_err}")
    else:
        print("\n[Selesai] Tidak ada data lowongan yang berhasil dikumpulkan.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kalibrr Job Board Scraper - Mode JSON Terstruktur")
    parser.add_argument("--keyword", type=str, default=None, help="Kata kunci pencarian (misal: 'Data Analyst'). Kosongkan untuk pencarian umum.")
    parser.add_argument("--pages", type=int, default=1, help="Jumlah halaman yang ingin di-scrape (default: 1)")
    parser.add_argument("--output", type=str, default="kalibrr_jobs.csv", help="Nama file output CSV (default: 'kalibrr_jobs.csv')")

    args = parser.parse_args()

    # If user kept default output name, inject a timestamp to avoid overwriting previous runs
    if args.output == "kalibrr_jobs.csv":
        ts = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%Y%m%d_%H%M%S")
        args.output = f"kalibrr_jobs_{ts}.csv"

    scrape_kalibrr(keyword=args.keyword, max_pages=args.pages, output_file=args.output)
