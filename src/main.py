import json
import logging
from src import web

logger = logging.getLogger(__name__)
SOURCE_LIST_DIR = "source_list.json"


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

        for article_url in found_articles:
            article_data = web.extract_data_onet_pl(article_url)
            print(f"TITLE: {article_data['title']}")
            print(f"DATE: {article_data['date']}")
            print(f"TEXT: \n \n {article_data['text']} \n \n")
    

if __name__ == "__main__":
    main()
