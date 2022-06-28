import logging
import os
from telnetlib import SE
from sqlalchemy.orm import Session

from . import models
import azure.functions as func
from datetime import date
import sqlalchemy
from textblob import TextBlob
from gnews import GNews
import json

__test_db_engine__ = None

def database_uri():

    url = os.environ.get("DB_CONNECTION_STRING", default="")
    if len(url) != 0:
        return url
    
    url = sqlalchemy.engine.url.URL.create(
        drivername = "mariadb+mariadbconnector",
        username = os.environ.get("DB_USER", default="none"),
        password = os.environ.get("DB_PASSWORD", default="none"),
        host = os.environ.get("DB_SERVER", default="127.0.0.1"),
        port = os.environ.get("DB_PORT", default="3306"),
        database = os.environ.get("DB_NAME", default="mydb"))
    return str(url)


def main(req: func.HttpRequest) -> func.HttpResponse:
    global __test_db_connection_string__

    logging.info('Python HTTP trigger function processed a request.')

    #Get or create and engine
    if __test_db_engine__ is not None:
        engine = __test_db_engine__
    else:
        # Get the connection variable andd SSl certificate if it has been provided.
        connection_string = database_uri()
        ssl_cert = os.environ.get("DB_SSL_CERT", default=None)
        connection_args = {}
        if ssl_cert is not None:
            connection_args["ssl_ca"] = ssl_cert
        engine = sqlalchemy.create_engine(connection_string, connect_args=connection_args, echo=False, future=True)

    models.Base.metadata.create_all(engine)
    session = Session(engine)
    
    statment = sqlalchemy.select(models.QueryResult)
    results = session.execute(statment)
    json_data = []
    for article in results.scalars():
        json_data.append({
            'publisher': article.publisher,
            'headline': article.headline,
            'desc': article.description,
            'url': article.url,
            'published date': article.publish_date,
            'sentiment': article.sentiment
        })

    return func.HttpResponse(json.dumps(json_data, default=str).encode("utf8"), status_code=201)
    
