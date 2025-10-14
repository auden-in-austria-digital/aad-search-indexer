# ACDH Search Indexer

This repository provides Python scripts to index data from TEI/XML sources into NoSketch Engine TSV Index files. It also contains a Dockerfile to build a NoSketch Engine Docker image with the ACDH Search Indexer scripts. Next to NoSketch it provides Python scripts to create an Index for Typesense Search.

## Fetch Data

Update `shellscripts/fetch_data.sh` to fetch the data you want to index. The script will be executed in the Github [Actions Workflow](./.githbub/workflows/index.yml).

## Create Noske Index

Update `noske/mk_verticals.py` constants to match your data. The script will be executed in the Github [Actions Workflow](./.githbub/workflows/index.yml). Or manually run:

```shell
pip install pipenv
pipenv install
pipenv run python noske/mk_verticals.py
```

## Create Typesense Index

Update `typesense/mk_index.py` constants to match your data. The script will be executed in the Github [Actions Workflow](./.githbub/workflows/index.yml). Or manually run:

```shell
pip install pipenv
pipenv install
pipenv run python typesense/mk_index.py
```

Make sure the returned data type matches the Schema. If not, you can adjust the `typesense/mk_index.py` script 
`match case` statements to your schema. For example, the following code snippet creates a record for the Typesense index:
    
```python
def create_index_record(doc: TeiReader, blacklist: list) -> dict:
    record = {}
    for key, value in XPATHS.items():
        items = extract_structure(doc, value)
        match key:
            case "date":
                # returns an integer of an attribute value
                record[key] = int("".join(items))
            case "places":
                # returns a list of strings from a list of elements
                record[key] = [extract_text(place, blacklist) for place in items]
            case "edition":
                # returns a list of strings from a list of elements
                record[key] = [extract_text(edition, blacklist) for edition in items]
            case _:
                # returns a string from a list of elements
                record[key] = " ".join([extract_text(text, blacklist) for text in items])
    return record
```

## Noske Docker

The Image uses [acdh-oeaw/noske-ubi9](https://github.com/acdh-oeaw/noske-ubi9) as base image.
Build the Docker image with the ACDH Search Indexer scripts:

```shell
docker build -f nosketchengine/Dockerfile -t acdh/noske .
```

Run Noske Docker Image:

```shell
docker run --rm -it -p 8080:8080 acdh/noske:latest
```
