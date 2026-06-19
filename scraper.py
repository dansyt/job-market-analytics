import csv
import time
import argparse
import requests
from bs4 import BeautifulSoup

def scrape_kalibrr(keyword=None, max_pages=3, output_file="kalibrr_jobs.csv"):
    """
    Scraper untuk mengambil data lowongan pekerjaan dari Kalibrr secara umum atau berdasarkan keyword
    menggunakan requests dan BeautifulSoup (tanpa Playwright, ramah untuk GitHub Actions).
    """
    if keyword:
        formatted_keyword = keyword.strip().replace(" ", "-")
        base_url = f"https://www.kalibrr.com/id-ID/home/te/{formatted_keyword}"
    else:
        base_url = "https://www.kalibrr.com/id-ID/job-board"

    jobs_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    print(f"=== Memulai Scraping Kalibrr (Menggunakan Requests + BS4) ===")
    print(f"Target: {'Umum (Semua Bidang)' if not keyword else f'Keyword: {keyword}'}")
    print(f"Jumlah Halaman Maksimal: {max_pages}")
    print(f"File Output: {output_file}\n")

    session = requests.Session()

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

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Temukan semua link judul pekerjaan
        job_links = soup.select('a.k-text-black[href*="/jobs/"]')
        count = len(job_links)
        print(f"   Ditemukan {count} kartu lowongan kerja di halaman ini.")

        if count == 0:
            print("   Selesai (tidak ada lowongan baru atau halaman kosong).")
            break

        for idx, link in enumerate(job_links):
            try:
                title = link.get_text().strip()
                href = link.get("href")
                full_url = f"https://www.kalibrr.com{href}" if href else ""

                # Naik 4 tingkat untuk mencari kontainer kartu (Parent 4)
                card = link.parent.parent.parent.parent
                
                # Mengambil baris teks di dalam kartu
                card_text = card.get_text(separator="\n")
                lines = [line.strip() for line in card_text.split("\n") if line.strip()]

                # Inisialisasi field default
                company = ""
                location = ""
                salary = "Gaji Tidak Diumumkan"
                job_type = ""
                recruiter_status = ""
                experience_level = ""
                deadline = ""

                if len(lines) > 1:
                    company = lines[1]
                if len(lines) > 2:
                    location = lines[2]

                # Parsing dinamis untuk detail baris lainnya
                for line in lines[3:]:
                    if "gaji" in line.lower() or "idr" in line.lower() or "rp" in line.lower() or "tidak diumumkan" in line.lower():
                        salary = line
                    elif "penuh waktu" in line.lower() or "paruh waktu" in line.lower() or "magang" in line.lower() or "kontrak" in line.lower() or "full-time" in line.lower() or "internship" in line.lower():
                        job_type = line
                    elif "rekruter terakhir aktif" in line.lower() or "aktif" in line.lower():
                        recruiter_status = line
                    elif "lulusan baru" in line.lower() or "junior" in line.lower() or "senior" in line.lower() or "tahun" in line.lower() or "pengalaman" in line.lower():
                        experience_level = line
                    elif "apply before" in line.lower() or "lamar sebelum" in line.lower():
                        deadline = line

                jobs_data.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Salary": salary,
                    "Job Type": job_type,
                    "Experience Level": experience_level,
                    "Recruiter Status": recruiter_status,
                    "Deadline": deadline,
                    "URL": full_url
                })

            except Exception as card_err:
                print(f"   [Peringatan] Gagal memproses kartu ke-{idx+1}: {card_err}")

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
    parser = argparse.ArgumentParser(description="Kalibrr Job Board Scraper menggunakan Requests + BeautifulSoup")
    parser.add_argument("--keyword", type=str, default=None, help="Kata kunci pencarian (misal: 'Data Analyst'). Kosongkan untuk pencarian umum.")
    parser.add_argument("--pages", type=int, default=1, help="Jumlah halaman yang ingin di-scrape (default: 1)")
    parser.add_argument("--output", type=str, default="kalibrr_jobs.csv", help="Nama file output CSV (default: 'kalibrr_jobs.csv')")
    
    args = parser.parse_args()
    
    scrape_kalibrr(keyword=args.keyword, max_pages=args.pages, output_file=args.output)
