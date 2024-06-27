# bin/bash

# get editions

DATA_DIR=data/editions
REPO=amp-data
ORG=auden-musulin-papers
BRANCH=dev

echo "fetching transkriptions from data repo..."
mkdir ./data
rm -rf $DATA_DIR && mkdir $DATA_DIR
curl -LO https://github.com/$ORG/$REPO/archive/refs/heads/$BRANCH.zip
echo "data fetched"

echo "unzipping data..."
unzip $BRANCH

echo "moving data to $DATA_DIR..."

mv ./$REPO-$BRANCH/$DATA_DIR/*.xml ./$DATA_DIR

rm -rf $REPO-$BRANCH
rm $BRANCH.zip
echo "done"

# get Indexes

DATA_DIR=data/indexes
REPO=amp-entities
ORG=auden-musulin-papers
BRANCH=main

echo "fetching transkriptions from data repo..."
mkdir ./data
rm -rf $DATA_DIR && mkdir $DATA_DIR
curl -LO https://github.com/$ORG/$REPO/archive/refs/heads/$BRANCH.zip
echo "data fetched"

echo "unzipping data..."
unzip $BRANCH

echo "moving data to $DATA_DIR..."
mv ./$REPO-$BRANCH/out/*.xml ./$DATA_DIR

echo "removing zip and folder..."
rm -rf $REPO-$BRANCH
rm $BRANCH.zip
echo "done"