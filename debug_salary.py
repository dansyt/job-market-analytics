import re, json, requests

url = 'https://www.kalibrr.com/id-ID/home/co/Indonesia?page=1'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
response = requests.get(url, headers=headers)
html = response.text

script_tags = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for tag in script_tags:
    if 'baseSalary' in tag:
        data = json.loads(tag)
        jobs = data['props']['pageProps']['jobs']
        # Print semua field lokasi dari 3 jobs pertama
        for i, j in enumerate(jobs[:3]):
            print(f"--- Job {i}: {j.get('name', j.get('position', ''))} ---")
            print("googleLocation:", j.get('googleLocation'))
            print("companyInfo:", j.get('companyInfo', {}).get('googleLocation') if isinstance(j.get('companyInfo'), dict) else 'no companyInfo')
            print()
        break
