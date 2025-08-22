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
BASE_URL = "https://forums.beyondblue.org.au/t5/anxiety/bd-p/c1-sc2-b1"
OUTPUT_CSV = "beyondblue_anxiety_threads_all.csv"

# ——— SET UP SELENIUM ———
options = Options()
# options.add_argument("--headless")  # uncomment to run headlessly
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

threads = []
driver.get(BASE_URL)
page_counter = 1

while True:
    print(f"🔄 Processing page {page_counter}...")

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[title]"))
        )
    except Exception as e:
        print(f"⚠️ Could not find threads on page {page_counter}: {e}")
        break

    soup = BeautifulSoup(driver.page_source, "html.parser")
    link_elems = soup.select("a[title]")

    for a in link_elems:
        href = a.get("href", "")
        # only threads in the anxiety section
        if href.startswith("/t5/anxiety/"):
            title = a.get_text(strip=True)
            url = href if href.startswith("http") else "https://forums.beyondblue.org.au" + href
            threads.append({"title": title, "link": url})

    # pagination: look for “Next Page”
    next_btn = soup.select_one('a[aria-label="Next Page"]')
    if next_btn:
        next_href = next_btn.get("href", "")
        if next_href:
            # fix for relative vs absolute URLs
            if next_href.startswith("http"):
                next_url = next_href
            else:
                next_url = "https://forums.beyondblue.org.au" + next_href

            print(f"➡️ Going to: {next_url}")
            driver.get(next_url)
            page_counter += 1
            time.sleep(2)
            continue

    print("✅ No more pages. Scraping complete.")
    break

driver.quit()

# dedupe and save
df = pd.DataFrame(threads).drop_duplicates(subset=["link"])
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"✅ Scraped {len(df)} unique threads. Saved to '{OUTPUT_CSV}'.")
