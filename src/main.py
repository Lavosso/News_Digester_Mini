import json
import logging

from src import web

logger = logging.getLogger(__name__)
SOURCE_LIST_DIR = "src/source_list.json"


def write_data_in_markdown(data: list[dict[str, str]], title: str) -> None:
    md_text = f"# General Report: {title}\n"
    for article in data:
        md_text += f"## {article['title']}:\n"
        md_text += f"**{article['date']}**\n\n"
        md_text += article["text"] + "\n\n"
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
        try:
            found_articles = web.gather_articles(source)
            if not found_articles:
                logger.warning("No articles were found for source '%s' (%s).", source_id, source)
                continue

            source_articles = web.extract_articles_data_async(found_articles)
            write_data_in_markdown(source_articles, source_id)
        except (web.NewsDigesterError, ValueError) as exc:
            logger.error("Skipping source '%s' (%s) because it failed during scraping: %s", source_id, source, exc)
            continue
        except Exception as exc:
            logger.exception(
                "Unexpected error while processing source '%s' (%s). This source was skipped.",
                source_id,
                source,
            )
            continue


if __name__ == "__main__":
    main()
