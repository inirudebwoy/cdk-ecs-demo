import os

import boto3
from fastapi import FastAPI

app = FastAPI()

DB_CLUSTER_IDENTIFIER = os.environ["DB_CLUSTER_IDENTIFIER"]


@app.get("/")
def read_root():
    rds = boto3.client("rds")
    return rds.describe_db_clusters(DBClusterIdentifier=DB_CLUSTER_IDENTIFIER)
