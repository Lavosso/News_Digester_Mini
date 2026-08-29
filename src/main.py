import json


SOURCE_LIST_DIR = "source_list.json"

def main() -> None:
    with open (SOURCE_LIST_DIR, "r") as json_source_list:
        source_list = json.loads(json_source_list.read())

    for source in source_list:
