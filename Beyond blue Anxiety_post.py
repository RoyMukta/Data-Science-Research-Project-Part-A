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
INPUT_FILE   = "beyondblue_anxiety_threads_all.csv"
OUTPUT_FILE  = "beyondblue_anxiety_posts_full.csv"

# ——— LOAD THREAD LIST ———
threads_df = pd.read_csv(INPUT_FILE)

# ——— SET UP SELENIUM ———
options = Options()
# options.add_argument("--headless")   # uncomment to run without opening a browser window
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

all_posts = []
print(f"🔄 Starting to scrape {len(threads_df)} threads for their main post...")

for idx, row in threads_df.iterrows():
    url = row["link"]
    print(f"➡️ [{idx+1}/{len(threads_df)}] {url}")
    try:
        driver.get(url)
        # wait for the main post content to be present
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.lia-message-body-content"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # derive post ID from URL
        post_id = url.rstrip("/").split("/")[-1]

        # title
        title_elem = soup.select_one("h1")
        title_text = title_elem.get_text(strip=True) if title_elem else ""

        # main post content
        content_elem = soup.select_one("div.lia-message-body-content")
        content_text = content_elem.get_text(separator="\n", strip=True) if content_elem else ""

        # author name
        author_elem = soup.select_one("a.lia-link-navigation.lia-page-link.lia-user-name-link span")
        author_text = author_elem.get_text(strip=True) if author_elem else "Unknown"

        # user ID
        user_id = ""
        user_link = soup.select_one("a.lia-link-navigation.lia-page-link.lia-user-name-link")
        if user_link and "href" in user_link.attrs:
            href = user_link["href"]
            if "user-id/" in href:
                user_id = href.split("user-id/")[-1]

        # post date
        date_elem = soup.select_one("span.local-date")
        date_text = date_elem.get_text(strip=True) if date_elem else ""

        # assemble record
        all_posts.append({
            "Post ID": post_id,
            "Thread URL": url,
            "Post Title": title_text,
            "Post Content": content_text,
            "Post Author": author_text,
            "User ID": user_id,
            "Post Date": date_text,
            "Post Category": "Anxiety"
        })

        print(f"✅ Scraped post: {title_text[:50]}")

    except Exception as e:
        print(f"⚠️ Error on {url}: {e}")

    time.sleep(1)  # polite delay

driver.quit()

# ——— SAVE RESULTS ———
df = pd.DataFrame(all_posts)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
print(f"\n✅ Finished! Main posts saved to '{OUTPUT_FILE}' ({len(df)} records).")
