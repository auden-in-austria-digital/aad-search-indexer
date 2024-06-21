import json
import os
import glob
import shutil
from tqdm import tqdm
from typesense.api_call import ObjectNotFound
from acdh_cfts_pyutils import TYPESENSE_CLIENT as client
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import extract_fulltext


DATA_DIR = "./data/editions"

TS_INDEX_NAME = "acdh_index"

BLACKLIST = [
    "{http://www.tei-c.org/ns/1.0}orig",
    "{http://www.tei-c.org/ns/1.0}del",
]

CURRENT_SCHEMA = {
    "name": TS_INDEX_NAME,
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "rec_id", "type": "string"},
        {"name": "title", "type": "string"},
        {"name": "full_text", "type": "string"},
        {"name": "date", "type": "int32", "sort": True},
        {"name": "edition", "type": "string[]", "facet": True, "optional": True},
        {"name": "places", "type": "string[]", "facet": True, "optional": True},
    ],
}

XPATHS = {
    "id": ".//tei:TEI/@xml:id",
    "rec_id": ".//tei:TEI/@xml:id",
    "title": ".//tei:titleStmt/tei:title[1]",
    "full_text": ".//tei:text//tei:p|.//tei:text//tei:lg|.//tei:text//tei:head|.//tei:text//tei:titlePage",
    "date": ".//tei:publicationStmt/tei:date/@when",
    "edition": ".//tei:editionStmt/tei:edition",
    "places": ".//tei:placeName",
}


def create_dirs(output_dir: str) -> None:
    output_dir = os.path.join(output_dir, "verticals")
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)


def load_xml_files(input_dir: str) -> list:
    return glob.glob(os.path.join(input_dir, "*.xml"))


def extract_structure(doc: TeiReader, structure: str) -> list:
    return doc.any_xpath(structure)


def extract_text(structure: list, blacklist: list):
    return extract_fulltext(structure, blacklist)


def create_index_record(doc: TeiReader, blacklist: list) -> dict:
    record = {}
    for key, value in XPATHS.items():
        items = extract_structure(doc, value)
        match key:
            case "date":
                record[key] = int("".join(items))
            case "places":
                record[key] = [extract_text(place, blacklist) for place in items]
            case "edition":
                record[key] = [extract_text(edition, blacklist) for edition in items]
            case _:
                record[key] = " ".join([extract_text(text, blacklist) for text in items])
    return record


def process_fils(files: str, blacklist: list) -> list:
    records = []
    for file in tqdm(files, total=len(files)):
        doc = TeiReader(file)
        records.append(create_index_record(doc, blacklist))
    return (records, len(records))


if __name__ == "__main__":
    debug = True
    data_dir = DATA_DIR
    records, counter = process_fils(load_xml_files(data_dir), BLACKLIST)
    if debug:
        with open("data/index.json", "w") as f:
            json.dump(records, f, indent=4)
    try:
        client.collections[TS_INDEX_NAME].delete()
    except ObjectNotFound:
        pass
    try:
        client.collections[TS_INDEX_NAME].delete()
    except Exception as e:
        print(e)
    client.collections.create(CURRENT_SCHEMA)
    make_index = client.collections[TS_INDEX_NAME].documents.import_(records)
    print(make_index)
    print(f"done with indexing of {counter} documents in {TS_INDEX_NAME}")
