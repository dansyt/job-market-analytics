import os
import csv
import time
import json
import re
import datetime
import argparse
import requests

def format_salary(job):
    """
    Mengambil data salary dari JSON terstruktur dan menghitung rata-ratanya.
    Menangani kasus jika hanya ada base_salary, hanya ada max_salary, atau keduanya.
    """
    salary_shown = job.get("salaryShown", False)
    base_salary = job.get("baseSalary")
    max_salary = job.get("maximumSalary")

    if not salary_shown:
        return None

    base = float(base_salary) if base_salary else None
    maximum = float(max_salary) if max_salary else None

    # Kasus 1: Dua-duanya ada nilainya -> Hitung Rata-rata
    if base is not None and maximum is not None:
        if base == maximum:
            return base
        return (base + maximum) / 2

    # Kasus 2: Hanya ada base_salary -> Ambil base_salary
    elif base is not None:
        return base

    # Kasus 3: Hanya ada maximumSalary -> Ambil maximumSalary
    elif maximum is not None:
        return maximum

    return None


def get_specialization(job):
    """
    Mengambil data spesialisasi dari key 'function' di JSON Kalibrr.
    Langsung mengembalikan string nama bidang kerja (misal: 'IT and Software').
    """
    spec = job.get("function")
    if spec:
        return str(spec)
    return " "


def map_education_level(job):
    """
    Mengubah kode angka educationLevel dari JSON menjadi label teks Bahasa Indonesia.
    """
    edu_code = job.get("educationLevel")
    if edu_code is None:
        return " "
    
    # Konversi ke integer jika dikirim dalam bentuk string angka
    try:
        edu_code = int(edu_code)
    except ValueError:
        return " "

    mapping = {
        200: "Graduated from high school",
        350: "Complete vocational course",
        450: "Completed associate's degree",
        550: "Bachelor's degree graduate",
        650: "Master's degree graduate"
    }
    
    return mapping.get(edu_code, " ")


def map_work_experience(job):
    """
    Mengubah kode angka experienceLevel dari JSON menjadi label tingkat jabatan.
    """
    # 🛠️ PERBAIKAN: Menembak langsung key 'experienceLevel' sesuai struktur asli JSON Kalibrr
    exp_code = job.get("workExperience")
    if exp_code is None:
        return " "
        
    try:
        exp_code = int(exp_code)
    except ValueError:
        return " "

    mapping = {
        100: "Internship",
        200: "Entry Level",
        300: "Supervisor",
        400: "Mid-Senior Level",
        500: "Director"
    }
    
    return mapping.get(exp_code, " ")


def extract_jobs_from_page(html):
    """
    Mengekstrak data jobs langsung dari JSON terstruktur Next.js
    yang disematkan di dalam tag <script> pada halaman HTML.
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


def scrape_kalibrr(keyword=None, max_pages=1, output_file="kalibrr_jobs.csv"):
    """
    Scraper utama Kalibrr yang menyimpan hasil ke folder result_csv.
    """
    if keyword:
        formatted_keyword = keyword.strip().replace(" ", "-")
        base_url = f"https://www.kalibrr.com/home/te/{formatted_keyword}"
    else:
        base_url = "https://www.kalibrr.com/home/co/Indonesia"

    jobs_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    print(f"=== Memulai Scraping Kalibrr (Final Clean Edition) ===")
    print(f"Target: {'Umum' if not keyword else f'Keyword: {keyword}'}")
    print(f"Jumlah Halaman Maksimal: {max_pages}")
    
    # 🛠️ 1. LOGIKA OTOMATIS MEMBUAT FOLDER result_csv
    target_dir = "result_csv"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"-> Folder '{target_dir}' belum ada. Berhasil dibuat otomatis.")
    
    # Gabungkan path folder dengan nama file
    final_output_path = os.path.join(target_dir, output_file)
    print(f"File Output: {final_output_path}\n")

    session = requests.Session()
    scraped_at = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")

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

        jobs_json = extract_jobs_from_page(response.text)

        if not jobs_json:
            print("   Selesai (Tidak ditemukan data JSON Next.js atau halaman kosong).")
            break

        print(f"   Ditemukan {len(jobs_json)} lowongan kerja di halaman ini.")

        for job in jobs_json:
            try:
                company_obj = job.get("company", {})
                if not isinstance(company_obj, dict):
                    company_obj = {"name": str(company_obj), "industry": "", "code": ""}

                location_obj = job.get("googleLocation", {})
                if not isinstance(location_obj, dict):
                    location_obj = {}
                
                addr_components = location_obj.get("addressComponents", {})
                if not isinstance(addr_components, dict):
                    addr_components = {}

                slug = job.get("slug", "")
                company_code = company_obj.get("code", "")
                job_id = job.get("id", "")
                full_url = f"https://www.kalibrr.com/c/{company_code}/jobs/{job_id}/{slug}" if slug else ""

                # Urutan append yang sudah kamu sesuaikan sebelumnya
                jobs_data.append({
                    "id": job_id,
                    "scraped_at": scraped_at,
                    "title": job.get("name") or job.get("position", ""),
                    "company_name": company_obj.get("name") or job.get("companyName", ""),
                    "industry": company_obj.get("industry", ""),
                    "specialization": get_specialization(job),
                    "education_level": map_education_level(job),
                    "job_level": map_work_experience(job),
                    "city": addr_components.get("city", ""),
                    "salary": format_salary(job),
                    "salary_interval": job.get("salaryInterval", "month"),
                    "job_type": job.get("tenure", ""),
                    "is_hybrid": job.get("isHybrid", False),
                    "is_wfh": job.get("workFromHome") or job.get("isRemote", False),
                    "is_fresh_grad": job.get("isOpenToFreshGrads", False),
                    "url": full_url
                })

            except Exception as job_err:
                print(f"   [Peringatan] Gagal memproses lowongan karena: {job_err}")

        time.sleep(1.5)

    # Simpan ke file CSV di dalam folder target_dir
    if jobs_data:
        try:
            with open(final_output_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)
            print(f"\n[Sukses] Berhasil mengekstrak {len(jobs_data)} data lowongan ke '{final_output_path}'!")
        except Exception as file_err:
            print(f"\n[Error] Gagal menulis data ke file CSV: {file_err}")
    else:
        print("\n[Selesai] Tidak ada data lowongan yang berhasil dikumpulkan.")

# ... (Kode penulisan CSV yang sudah ada sebelumnya) ...
        try:
            with open(final_output_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)
            print(f"\n[Sukses] Berhasil mengekstrak {len(jobs_data)} data lowongan ke '{final_output_path}'!")
            
            # 🛠️ OTOMATISASI UPLOAD KE SUPABASE DARI DALAM KODE
            print("\n[Info] Memulai otomatisasi upload ke Supabase...")
            import subprocess
            # Memanggil script upload_to_supabase.py secara programmatis
            result = subprocess.run(
                ["python", "upload_to_supabase.py", "--file", final_output_path],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print("[Sukses] Data berhasil terunggah ke database Supabase!")
            else:
                print(f"[Gagal] Gagal mengunggah ke Supabase. Error:\n{result.stderr}")

        except Exception as file_err:
            print(f"\n[Error] Gagal menulis data ke file CSV: {file_err}")    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kalibrr Job Board Scraper - Final Structured Edition")
    parser.add_argument("--keyword", type=str, default=None, help="Kata kunci pencarian.")
    parser.add_argument("--pages", type=int, default=1, help="Jumlah halaman yang ingin di-scrape.")
    parser.add_argument("--output", type=str, default="kalibrr_jobs.csv", help="Nama file output CSV.")

    args = parser.parse_args()

    if args.output == "kalibrr_jobs.csv":
        ts = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%Y%m%d_%H%M%S")
        args.output = f"kalibrr_jobs_{ts}.csv"

    scrape_kalibrr(keyword=args.keyword, max_pages=args.pages, output_file=args.output)