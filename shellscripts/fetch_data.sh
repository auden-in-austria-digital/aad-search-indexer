# bin/bash

DATA_DIR=data/editions
REPO=acdh-data
ORG=acdh-oeaw
BRANCH=main

echo "fetching transkriptions from data repo..."
rm -rf $DATA_DIR && mkdir $DATA_DIR
curl -LO https://github.com/$ORG/$REPO/archive/refs/heads/$BRANCH.zip
echo "data fetched"

echo "unzipping data..."
unzip $BRANCH

echo "moving data to $DATA_DIR..."
mkdir ./data
mkdir ./$DATA_DIR
mv ./$REPO-$BRANCH/$DATA_DIR/*.xml ./$DATA_DIR

rm -rf $REPO-$BRANCH
rm $BRANCH.zip
echo "done"