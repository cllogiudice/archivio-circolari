import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import re
import email.utils
from datetime import datetime

json_filename = "circolari.json"
existing_links = set()
all_circolari = []

if os.path.exists(json_filename):
    try:
        with open(json_filename, "r", encoding="utf-8") as f:
            all_circolari = json.load(f)
            existing_links = {c["link"] for c in all_circolari}
    except Exception:
        pass

page = 1
print("Scaricamento feed RSS in corso...")

while page <= 97:
    url = f"https://balillaimbriani.edu.it/circolare/feed/?paged={page}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                break
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            items = root.findall("./channel/item")
            
            if not items:
                break
            
            for item in items:
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                pubDate = item.find("pubDate").text if item.find("pubDate") is not None else ""
                desc_raw = item.find("description").text if item.find("description") is not None else ""
                
                clean_desc = re.sub(r'<[^>]*>', '', desc_raw).replace('Leggi tutto', '').strip()
                
                if link not in existing_links:
                    all_circolari.append({
                        "title": title,
                        "link": link,
                        "pubDate": pubDate,
                        "description": clean_desc
                    })
                    existing_links.add(link)
            
            print(f"Elaborata pagina {page}...")
            page += 1
    except Exception as e:
        break

# Ordinamento cronologico reale (dal più recente al più vecchio)
all_circolari.sort(
    key=lambda x: email.utils.parsedate_to_datetime(x["pubDate"]) if x["pubDate"] else datetime.min, 
    reverse=True
)

with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(all_circolari, f, ensure_ascii=False, indent=4)

print(f"Completato! Totale circolari nel DB: {len(all_circolari)}")
