from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# ——— CONFIG ———
BASE_URL       = "https://forums.beyondblue.org.au/t5/anxiety/bd-p/c1-sc2-b1"
OUTPUT_THREADS = "beyondblue_social_anxiety_threads_all.csv"

# ——— SET UP SELENIUM ———
options = Options()
# options.add_argument("--headless")  # run invisibly
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

threads = []
driver.get(BASE_URL)
page = 1

while True:
    print(f"🔄 Processing page {page}…")
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[title]"))
        )
    except Exception as e:
        print(f"⚠️ No threads found on page {page}: {e}")
        break

    soup = BeautifulSoup(driver.page_source, "html.parser")
    for a in soup.select("a[title]"):
        href = a.get("href", "")
        # only include threads in the Social Anxiety sub‑topic
        if "/anxiety/social-anxiety/" in href:
            title = a.get_text(strip=True)
            url   = href if href.startswith("http") else "https://forums.beyondblue.org.au" + href
            threads.append({"title": title, "link": url})

    # pagination: look for “Next Page”
    nxt = soup.select_one('a[aria-label="Next Page"]')
    if nxt and nxt.get("href"):
        nh = nxt["href"]
        next_url = nh if nh.startswith("http") else "https://forums.beyondblue.org.au" + nh
        page += 1
        print(f"➡️ Going to: {next_url}")
        driver.get(next_url)
        time.sleep(2)
    else:
        break

driver.quit()

# dedupe & save
df_threads = pd.DataFrame(threads).drop_duplicates(subset=["link"])
df_threads.to_csv(OUTPUT_THREADS, index=False, encoding="utf-8")
print(f"✅ Scraped {len(df_threads)} unique Social Anxiety threads → {OUTPUT_THREADS}")
