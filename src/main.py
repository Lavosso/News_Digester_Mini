import json
import logging
from src import web

logger = logging.getLogger(__name__)
SOURCE_LIST_DIR = "source_list.json"

def write_data_in_markdown(data: list[dict[str, str]], title: str) -> None:
    md_text = f"# General Report: {title}\n"
    for article in data:
        md_text += f"## {article['title']}:\n"
        md_text += f"**{article['date']}**\n\n"
        md_text += article['text'] + f"\n\n"
    with open(f"sumup_{title}.md", "w", encoding="utf-8") as f:
        f.write(md_text)

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    with open(SOURCE_LIST_DIR, "r") as json_source_list:
        source_list = json.loads(json_source_list.read())
        logger.info(f"loaded source list: {source_list}")

    for source_id, source in source_list.items():
        found_articles = web.gather_articles(source)
        source_articles = []
        for article_url in found_articles:
            article_data = web.extract_data_onet_pl(article_url)
            source_articles.append(article_data)
            write_data_in_markdown(source_articles, source_id)


if __name__ == "__main__":
    main()
