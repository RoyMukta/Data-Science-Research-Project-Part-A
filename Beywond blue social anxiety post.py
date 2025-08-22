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
# point this at the file you actually have on disk:
INPUT_FILE  = "beyondblue_social_anxiety_threads_all.csv"
OUTPUT_FILE = "beyondblue_social_anxiety_posts_full.csv"

# then load it:
threads_df = pd.read_csv(INPUT_FILE)

# ——— SET UP SELENIUM ———
options = Options()
# options.add_argument("--headless")  # uncomment to run without opening a browser window
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

all_posts = []
print(f"🔄 Starting to scrape {len(threads_df)} Social Anxiety threads for main posts…")

for idx, row in threads_df.iterrows():
    url = row["link"]
    print(f"➡️ [{idx+1}/{len(threads_df)}] {url}")
    try:
        driver.get(url)
        # wait until the main post content is present
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.lia-message-body-content"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # derive post ID from URL
        post_id = url.rstrip("/").split("/")[-1]

        # title
        title_el = soup.select_one("h1")
        title_text = title_el.get_text(strip=True) if title_el else ""

        # main post content
        body_el = soup.select_one("div.lia-message-body-content")
        body_text = body_el.get_text(separator="\n", strip=True) if body_el else ""

        # author name
        auth_el = soup.select_one("a.lia-user-name-link span")
        author = auth_el.get_text(strip=True) if auth_el else "Unknown"

        # user ID from profile link
        user_id = ""
        ulink = soup.select_one("a.lia-user-name-link")
        if ulink and "href" in ulink.attrs and "user-id/" in ulink["href"]:
            user_id = ulink["href"].split("user-id/")[-1]

        # post date
        date_el = soup.select_one("span.local-date")
        date_text = date_el.get_text(strip=True) if date_el else ""

        all_posts.append({
            "Post ID":       post_id,
            "Thread URL":    url,
            "Post Title":    title_text,
            "Post Content":  body_text,
            "Post Author":   author,
            "User ID":       user_id,
            "Post Date":     date_text,
            "Post Category": "Social Anxiety"
        })

        print(f"✅ Scraped post: {title_text[:60]}")

    except Exception as e:
        print(f"⚠️ Error on {url}: {e}")

    time.sleep(1)  # polite delay

driver.quit()

# ——— SAVE RESULTS ———
df = pd.DataFrame(all_posts)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
print(f"\n✅ Finished! Saved {len(df)} posts to '{OUTPUT_FILE}'.")
