import logging
import os
from sqlalchemy.orm import Session
from .scraper_funcs import create_search_string, create_instance, create_dated_instance, search, analysis_sentiment

from . import models
import azure.functions as func
import dateparser
import sqlalchemy
from textblob import TextBlob
from gnews import GNews
from flask import jsonify

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

    # If GET request, get values and assign to variables.
    if req.method == "GET":
        topic = req.params.get('topic')
        blocked_words = req.params.get('blocked-words')
        is_dated = req.params.get('is-dated')
        
    #If POST request, get values from request and assign to varaibles.
    elif req.method == "POST":
        try:
            req_body = req.get_json()
        except ValueError:
            topic = None
            blocked_words = None
        else:
            topic = req_body.get('topic')
            blocked_words = req_body.get('blocked-words')
            is_dated = req_body.get('is-dated')
    
    #If GET request is date restricted, assign start and end dates to varaiables.
    #Create search instance depending on if date restericted. 
    if is_dated == True:
        start_date = req.params.get('start-date')
        end_date = req.params.get('end-date')
        search_instance = create_dated_instance(start_date, end_date)
    else:
        search_instance = create_instance()

    search_string = create_search_string(topic, blocked_words)
    found_articles = search(search_string, search_instance)
    analysis_sentiment(found_articles)

    
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
    
    


    if found_articles:
        models.Base.metadata.create_all(engine)
        session = Session(engine)

        statement = sqlalchemy.select(models.Query).where(models.Query.query == search_string)
        query = session.execute(statement).first()

        if query is None:
            query = models.Query(topic)
        
        # Extract article details from json and assign to variables.
        for article in found_articles:
            article_query = query
            article_publisher = article['publisher']['title']
            article_headline = article['title']
            article_desc = article['description']
            article_url = article['url']
            article_date = dateparser.parse(article['published date'])
            article_sentiment = article['sentiment']

            # Create new QueryResult
            result = models.QueryResult(
                article_query,
                article_publisher,
                article_headline,
                article_desc,
                article_url,
                article_date,
                article_sentiment
            )

            # Add to database
            session.add(result)
            session.commit()
        session.close()

        return func.HttpResponse('ok', status_code=201)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
