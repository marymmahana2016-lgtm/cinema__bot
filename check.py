import json
import os
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

URL = "https://cfc.scenecinemas.com/home"
TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FILE = "seen.json"

resp = requests.get(URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# href -> movie name
movies = {}
for a in soup.select('a[href*="/movie-details/"]'):
    name = a.get("title") or a.get_text(strip=True)
    if name:
        movies[a["href"]] = name

print("لقيت", len(movies), "فيلم")

if not movies:
    sys.exit("مفيش أفلام اتقرأت")

# First run: no seen file yet, so just save a baseline without notifying.
if os.path.exists(FILE):
    with open(FILE, encoding="utf-8") as f:
        seen = set(json.load(f))
else:
    seen = None

if seen is not None:
    for href in movies.keys() - seen:
        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            params={
                "chat_id": CHAT_ID,
                "text": f"فيلم جديد نزل: {movies[href]}\n{urljoin(URL, href)}",
            },
            timeout=20,
        )

with open(FILE, "w", encoding="utf-8") as f:
    json.dump(sorted((seen or set()) | set(movies)), f, ensure_ascii=False)
