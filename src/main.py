import json
import logging
from src import web

logger = logging.getLogger(__name__)
SOURCE_LIST_DIR = "source_list.json"

def main() -> None:
    logging.basicConfig(level=logging.INFO)
    with open (SOURCE_LIST_DIR, "r") as json_source_list:
        source_list = json.loads(json_source_list.read())
        logger.info(f"loaded source list: {source_list}")
    for source_id, source in source_list.items():
        source_data = web.gather_data(source)
        logger.info(source_data)


if __name__ == "__main__":
    main()