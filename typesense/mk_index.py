import json
import os
import glob
import shutil
from collections import deque
from tqdm import tqdm
from typesense.api_call import ObjectNotFound
from acdh_cfts_pyutils import TYPESENSE_CLIENT as client
from acdh_cfts_pyutils import CFTS_COLLECTION
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import extract_fulltext


DATA_DIR = "./data/preprocessed"

TS_INDEX_NAME = "amp"

BLACKLIST = [
    "{http://www.tei-c.org/ns/1.0}del",
]

CURRENT_SCHEMA = {
    'name': TS_INDEX_NAME,
    'fields': [
        {
            'name': 'id',
            'type': 'string'
        },
        {
            'name': 'rec_id',
            'type': 'string'
        },
        {
            'name': 'title',
            'type': 'string',
        },
        {
            'name': 'full_text',
            'type': 'string',
        },
        {
            'name': 'year',
            'type': 'int32',
            'optional': True,
            'facet': True,
        },
        {
            'name': 'date',
            'type': 'string',
            'facet': True,
            'sort': True
        },
        {
            'name': 'persons',
            'type': 'string[]',
            'facet': True,
            'optional': True
        },
        {
            'name': 'places',
            'type': 'string[]',
            'facet': True,
            'optional': True
        },
        {
            'name': 'orgs',
            'type': 'string[]',
            'facet': True,
            'optional': True
        },
        {
            'name': 'works',
            'type': 'string[]',
            'facet': True,
            'optional': True
        },
        {
            'name': 'events',
            'type': 'string[]',
            'facet': True,
            'optional': True
        },
        {
            'name': 'document_type',
            'type': 'string[]',
            'optional': True,
            'facet': True,
        },
        {
            'name': 'image',
            'type': 'string',
        },
        {"name": "page_int", "type": "int32", "sort": True},
        {"name": "page_str", "type": "string"},
        {"name": "comments_count", "type": "int32"},
        {"name": "comments_bool", "type": "bool", "facet": True},
        {"name": "poem_bool", "type": "bool", "facet": True},
        {"name": "poem_count", "type": "int32"}
    ]
}

CFTS_SCHEMA = {
    "project": "string",
    "id": "string",
    "rec_id": "string",
    "resolver": "string",
    "title": "string",
    "full_text": "string",
    "year": "int32",
    "persons": "string[]",
    "places": "string[]",
    "orgs": "string[]",
    "works": "string[]",
    "events": "string[]",
}

XPATHS = {
    "image": "@facs",
    "page_str": "@ed",
    "id": "//tei:TEI/@xml:id",
    "rec_id": "//tei:TEI/@xml:id",
    "title": ".//tei:titleStmt/tei:title[@level='a']",
    "full_text": """.//tei:p|
                    .//tei:lg|
                    .//tei:head|
                    .//tei:ab|
                    .//tei:div[not(@type)]|
                    .//tei:quote|
                    .//tei:fw""",
    "date": ".//tei:origin/tei:origDate/@notBefore-iso|.//tei:origin/tei:origDate/text()",
    "document_type": ".//tei:text/@type"
}


def get_context(xpath, page):
    comments = False
    comments_len = 0
    for p in page:
        try:
            ent = p.xpath(xpath, namespaces={'tei': "http://www.tei-c.org/ns/1.0"})
        except AttributeError:
            ent = []
        if len(ent) > 0:
            comments = True
            comments_len += len(ent)
    return (comments, comments_len)


def get_entities(ent_type, ent_node, ent_name, page, doc):
    entities = []
    e_path = f'.//tei:rs[@type="{ent_type}"]/@ref'
    for p in page:
        try:
            ent = p.xpath(e_path, namespaces={'tei': "http://www.tei-c.org/ns/1.0"})
        except AttributeError:
            ent = []
        ref = [ref.replace("#", "") for e in ent if len(ent) > 0 for ref in e.split()]
        if len(ref) > 0:
            for r in ref:
                p_path = f'.//tei:{ent_node}[@xml:id="{r}"]//tei:{ent_name}[1]'
                en = doc.any_xpath(p_path)
                if en:
                    entity = " ".join(" ".join(en[0].xpath(".//text()")).split())
                    if len(entity) != 0:
                        entities.append(entity)
    return [ent for ent in sorted(set(entities))]


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


def exhaust(items):
    return deque(items)


def create_index_records(doc: TeiReader, blacklist: list) -> list:
    record = []
    xbody = ".//tei:div[@type='page']"
    pages = doc.any_xpath(xbody)
    page_num = 1
    for page in pages:
        page_record = {}
        for key, value in XPATHS.items():
            items = page.xpath(value, namespaces={'tei': "http://www.tei-c.org/ns/1.0"})
            match key:
                case "full_text":
                    # get entities mentioned in the page
                    ent_type = "place"
                    ent_name = "placeName"
                    page_record["places"] = get_entities(ent_type=ent_type,
                                                         ent_node=ent_type,
                                                         ent_name=ent_name,
                                                         page=page,
                                                         doc=doc)
                    ent_type = "person"
                    ent_name = "persName"
                    page_record["persons"] = get_entities(ent_type=ent_type,
                                                          ent_node=ent_type,
                                                          ent_name=ent_name,
                                                          page=page,
                                                          doc=doc)
                    ent_type = "org"
                    ent_name = "orgName"
                    page_record["orgs"] = get_entities(ent_type=ent_type,
                                                       ent_node=ent_type,
                                                       ent_name=ent_name,
                                                       page=page,
                                                       doc=doc)
                    ent_type = "event"
                    ent_name = "label"
                    page_record["events"] = get_entities(ent_type=ent_type,
                                                         ent_node=ent_type,
                                                         ent_name=ent_name,
                                                         page=page,
                                                         doc=doc)
                    ent_type = "lit_work"
                    ent_name = "title"
                    ent_node = "bibl"
                    page_record["works"] = get_entities(ent_type=ent_type,
                                                        ent_node=ent_node,
                                                        ent_name=ent_name,
                                                        page=page,
                                                        doc=doc)
                    # get text of page
                    page_record[key] = " ".join([extract_text(text, blacklist) for text in items])
                    page_record['comments_bool'], page_record['comments_count'] = get_context('.//node()[@ana]', page)
                    page_record['poem_bool'], page_record['poem_count'] = get_context('.//tei:l', page)
                case "image":
                    page_record[key] = items[0].split("/")[-2]
                case "page_str":
                    page_record[key] = str(items[0])
                    page_record['page_int'] = int(page_num)
            items = extract_structure(doc, value)
            match key:
                case "id":
                    page_record[key] = items[0].replace('.xml', f'.html?tab={page_record["page_str"]}')
                case "rec_id":
                    page_record[key] = items[0]
                case "title":
                    page_record[key] = " ".join([extract_text(text, blacklist) for text in items])
                case "date":
                    page_record[key] = items[0]
                    page_record["year"] = int(items[0].split("-")[0])
                case "edition":
                    page_record[key] = items
        # print(page_record)
        page_num += 1
        if len(page_record["full_text"]) > 0:
            record.append(page_record)
    return record


def create_cfts_record(project_record: dict) -> dict:
    record = {}
    for key, value in CFTS_SCHEMA.items():
        match key:
            case "project":
                record[key] = "amp"
            case "resolver":
                record[key] = f'https://amp.acdh.oeaw.ac.at/{project_record["id"]}'
            case _:
                record[key] = project_record[key]
    return record


def create_index_record(doc: TeiReader, blacklist: list) -> dict:
    record = {}
    for key, value in XPATHS.items():
        items = extract_structure(doc, value)
        print(key, items)
        match key:
            case "date":
                record[key] = "".join(items[0])
            case "image":
                record[key] = [extract_text(place, blacklist) for place in items]
            case "places":
                record[key] = [extract_text(place, blacklist) for place in items]
            case "edition":
                record[key] = [extract_text(edition, blacklist) for edition in items]
            case _:
                record[key] = " ".join([extract_text(text, blacklist) for text in items])
    return record


def process_fils(files: str, blacklist: list, paginate: bool) -> list:
    records = []
    for file in tqdm(files, total=len(files)):
        doc = TeiReader(file)
        if paginate:
            rec_lists = create_index_records(doc, blacklist)
            for rec in rec_lists:
                records.append(rec)
        else:
            records.append(create_index_record(doc, blacklist))
    return (records, len(records))


if __name__ == "__main__":
    debug = False
    paginate = True
    cfts = True
    data_dir = DATA_DIR
    records, counter = process_fils(load_xml_files(data_dir), BLACKLIST, paginate)
    if cfts:
        cfts_records = []
        for x in records:
            cfts_record = create_cfts_record(x)
            cfts_records.append(cfts_record)
    if debug:
        with open("data/typesense_index.json", "w") as f:
            json.dump(records, f, indent=4)
        if cfts:
            with open("data/cfts_index.json", "w") as f:
                json.dump(cfts_records, f, indent=4)
    else:
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
        if cfts:
            make_cfts_index = CFTS_COLLECTION.documents.import_(cfts_records, {'action': 'upsert'})
            print(make_cfts_index)
            print(f"done with indexing of {len(cfts_records)} documents in CFTS_AMP_COLLECTION")
    print("done")
