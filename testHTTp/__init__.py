import logging
import os
from sqlalchemy.orm import Session


from . import models
import azure.functions as func
from datetime import date
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

def create_search_string(topic: str, blocked_words: list):
    """Funcition to create the search from http request.

    Args:
        topic (str): The user searched topic.
        blocked_words (list): A list of words to that show not occur in returned results

    Returns:
        str: A string containing search topic, and excluded terms prefixed by a dash.
    """
    primary_search = topic
    excluded_terms = blocked_words
    for word in excluded_terms:
        dash = ' -'
        dash += word
        primary_search += dash

    return primary_search

def create_instance():
    """A function that creates an instance object of a GNews

    Returns:
        GNews: A google news class object that will be used to carry out searches.
    """
    google_object = GNews()
    return google_object

def create_dated_instance(start_date: list, end_date: list):
    """
    A function that creates an instance of GNews that is restricted to searching
    input dates.


    Args:
        start_date (list): Return articles begining from this date
        end_date (list): Return article before this date inclusive

    Returns:
        GNews: A GNews object instance restricted to search articles to the input
        search dates. 
    """
    google_object = GNews()
    google_object.start_date = tuple(start_date)
    google_object.end_date = tuple(end_date)
    return google_object

def search(topic: str, google_object:GNews):
    """A function that is used to search for article of the topics.

    Args:
        topic (str): The search topic including terms for exlcusion
        google_object (GNews): The object instance of GNews.

    Returns:
        list: A list of JSON objects containing 
    """
    make_string = str(topic)
    results= google_object.get_news(make_string) 
    return results

def articles(search_results, google_object):
    dic = {}
    key = 0
    for index, value in enumerate(search_results):
        if key <=2:
            article = google_object.get_full_article(value['url'])
            dic[index] = article.text
            key +=1
    return dic

def analysis_sentiment(search_results: list):
    """
    A function that finds the sentiment values of each found article
    and add the sentiment value to the article json.

    Args:
        search_results (_type_): _description_
    """
    for article in search_results:
        string = article['title']
        string += " "
        string += article['description']
        blob = TextBlob(string)
        sentiment = blob.sentiment.polarity
        article['sentiment'] = sentiment
    
    

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

    result_query = topic
    
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
        engine = sqlalchemy.create(connection_string, connect_args=connection_args, echo=False, future=True)
    
    


    if found_articles:
        models.Base.metadata.create_all(engine)
        session = Session(engine)

        statement = sqlalchemy.select(models.Query).where(models.Query.query == topic)
        query = session.execute(statement).first()

        if query is None:
            query = models.Query(topic)
        
        # Extract article details from json and assign to variables.
        for article in found_articles:
            article_query = query
            article_publisher = article['publisher']
            article_headline = article['headline']
            article_desc = article['desc']
            article_url = article['url']
            article_date = article['published date']
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

        return func.HttpResponse(f"{found_articles}", status_code=201)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
