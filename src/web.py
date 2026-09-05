import logging
import re
from datetime import datetime
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class NewsDigesterError(RuntimeError):
    """Base error for scraper-related failures."""


class ArticleFetchError(NewsDigesterError):
    """Raised when an article page cannot be fetched or validated."""


class ArticleParseError(NewsDigesterError):
    """Raised when an article page is fetched but expected content cannot be parsed."""


def extract_data_onet_pl(url: str, timeout=10) -> dict:
    if not url or not url.strip():
        raise ValueError("Article URL is empty.")

    try:
        response = requests.get(
            url, timeout=timeout, headers={"User-Agent": "News_digester/0.1"}
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ArticleFetchError(
            f"Failed to fetch article '{url}' within {timeout}s. "
            f"HTTP request error: {exc}"
        ) from exc

    try:
        soup = BeautifulSoup(response.text, "html.parser")

        article_title = soup.find("h1")
        title = article_title.text.strip() if article_title else "title not found"
        if not article_title:
            logger.warning("Could not locate <h1> title for article '%s'.", url)

        element_time = soup.find("time")
        date_pub = element_time.text.strip() if element_time else "date not found"
        if not element_time:
            logger.warning("Could not locate <time> element for article '%s'.", url)

        paragraphs = soup.find_all("p", class_=lambda x: x and "detailParagraph" in x)
        if not paragraphs:
            main_content = soup.find("div", id="mainArticle") or soup.find("article")
            if main_content:
                paragraphs = main_content.find_all("p")

        article_text = "\n\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
        if not article_text:
            logger.warning("Could not extract article text for '%s'.", url)
    except Exception as exc:
        raise ArticleParseError(
            f"Failed to parse article content for '{url}'. "
            f"The page loaded, but the expected structure was missing or unreadable: {exc}"
        ) from exc

    extracted_data = {
        "title": title,
        "date": date_pub,
        "text": article_text if article_text else "Was not possible to extract text.",
    }

    return extracted_data


def gather_articles(base_url: str, timeout=10) -> list[str]:
    if not base_url or not base_url.strip():
        raise ValueError("Base URL is empty.")

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_articles = []
    seen_links = set()

    page = 1
    keep_fetching = True

    while keep_fetching:
        url = base_url if page == 1 else f"{base_url}?strona={page}"
        print(f"\n--- Fetching Page {page}: {url} ---")

        try:
            response = requests.get(
                url, timeout=timeout, headers={"User-Agent": "News_digester/0.1"}
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ArticleFetchError(
                f"Failed to fetch source list page '{url}' while gathering articles "
                f"from '{base_url}' (timeout={timeout}s). Error: {exc}"
            ) from exc

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)

            page_links_dict = {}
            for a_tag in links:
                raw_href = a_tag["href"]
                full_url = urljoin(url, str(raw_href))
                clean_url = full_url.split("?")[0]

                if clean_url.startswith(base_url) and clean_url not in seen_links:
                    page_links_dict[clean_url] = True
                    seen_links.add(clean_url)

            page_links = list(page_links_dict.keys())
        except Exception as exc:
            raise ArticleParseError(
                f"Failed to parse article index page '{url}'. The response was received, "
                f"but the page structure did not match expectations: {exc}"
            ) from exc

        if not page_links:
            print("No relevant new links found on this page. Stopping.")
            keep_fetching = False
            continue

        print(
            f"Found {len(page_links)} new potential articles on page {page}. Verifying..."
        )

        hit_old_article = False

        for link in page_links:
            try:
                article_resp = requests.get(
                    link, headers={"User-Agent": "News_digester/0.1"}, timeout=timeout
                )
                article_resp.raise_for_status()
                match = re.search(r'"datePublished"\s*:\s*"([^"]+)"', article_resp.text)

                if match:
                    pub_date = match.group(1)
                    if pub_date.startswith(today_str):
                        today_articles.append(link)
                        print(f"[TODAY] {link}")
                    else:
                        print(f"[OLDER] {link}")
                        hit_old_article = True
                        break
                else:
                    logger.warning("No publication date metadata found for article '%s'.", link)
            except requests.RequestException as exc:
                logger.warning(
                    "Skipping article '%s' because it could not be fetched or validated: %s",
                    link,
                    exc,
                )
                continue
            except Exception as exc:
                logger.warning(
                    "Skipping article '%s' because parsing raised an unexpected error: %s",
                    link,
                    exc,
                )
                continue

        if hit_old_article:
            print(f"Reached yesterday's news on page {page}. Stopping pagination.")
            keep_fetching = False
        else:
            page += 1
    print(
        f"\nFinished! Verified a total of {len(today_articles)} articles posted today."
    )
    return today_articles


def extract_articles_data_async(
    urls: list[str], timeout: int = 10, max_workers: int = 8
) -> list[dict]:
    if not urls:
        return []

    results = []
    workers = min(max_workers, len(urls))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(extract_data_onet_pl, url, timeout) for url in urls]
        for future in futures:
            try:
                results.append(future.result())
            except (ArticleFetchError, ArticleParseError, ValueError) as exc:
                logger.error("Skipping article extraction because the page could not be processed: %s", exc)
            except Exception as exc:
                logger.exception("Unexpected error while extracting article data: %s", exc)

    return results
