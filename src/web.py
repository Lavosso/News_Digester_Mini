import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from urllib.parse import urljoin

def extract_data_onet_pl(url: str, timeout = 10) -> dict:
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "News_digester/0.1"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    article_title = soup.find("h1")
    title = article_title.text.strip() if article_title else "title not found"

    element_time = soup.find("time")
    date_pub = element_time.text.strip() if element_time else "date not found"

    paragraphs = soup.find_all("p", class_=lambda x: x and "detailParagraph" in x)
    if not paragraphs:
        main_content = soup.find("div", id="mainArticle") or soup.find("article")
        if main_content:
            paragraphs = main_content.find_all("p")

    article_text = "\n\n".join([p.text.strip() for p in paragraphs if p.text.strip()])

    extracted_data = {
        "title": title,
        "date": date_pub,
        "text": article_text if article_text else "Was not possible to extract text."}

    return extracted_data


def gather_articles(base_url: str, timeout=10) -> list[str]:
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_articles = []
    seen_links = set()

    page = 1
    keep_fetching = True

    while keep_fetching:
        # Construct the URL for pagination
        url = base_url if page == 1 else f"{base_url}?strona={page}"
        print(f"\n--- Fetching Page {page}: {url} ---")

        response = requests.get(url, timeout=timeout, headers={"User-Agent": "News_digester/0.1"})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        # Use a dictionary to maintain insertion order for THIS page's links
        page_links_dict = {}
        for a_tag in links:
            raw_href = a_tag['href']
            full_url = urljoin(url, str(raw_href))

            # Clean URL to prevent tracking tags from causing duplicate checks
            clean_url = full_url.split('?')[0]

            if clean_url.startswith('https://wiadomosci.onet.pl/kraj/'):
                if clean_url not in seen_links:
                    page_links_dict[clean_url] = True
                    seen_links.add(clean_url)

        page_links = list(page_links_dict.keys())

        if not page_links:
            print("No relevant new links found on this page. Stopping.")
            keep_fetching = False
            continue

        print(f"Found {len(page_links)} new potential articles on page {page}. Verifying...")

        # Assume we will go to the next page unless we hit an older article
        hit_old_article = False

        for link in page_links:
            try:
                article_resp = requests.get(link, headers={"User-Agent": "News_digester/0.1"})
                match = re.search(r'"datePublished"\s*:\s*"([^"]+)"', article_resp.text)

                if match:
                    pub_date = match.group(1)
                    if pub_date.startswith(today_str):
                        today_articles.append(link)
                        print(f"[TODAY] {link}")
                    else:
                        # We hit an article from yesterday. Stop checking this page.
                        print(f"[OLDER] {link}")
                        hit_old_article = True
                        break
            except Exception as e:
                print(f"[ERROR] Failed to read {link}: {e}")
                continue

        # If we encountered an old article, stop the while loop entirely
        if hit_old_article:
            print(f"Reached yesterday's news on page {page}. Stopping pagination.")
            keep_fetching = False
        else:
            # If every single article on this page was from today, load the next page
            page += 1
    print(f"\nFinished! Verified a total of {len(today_articles)} articles posted today.")
    return today_articles