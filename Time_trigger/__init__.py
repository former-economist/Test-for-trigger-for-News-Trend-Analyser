# import logging
# import os
# import dateparser
# import gnews
# from sqlalchemy.orm import Session
# import datetime

# from .scraper_funcs import create_instance_for_day, search, analysis_sentiment
# import json
# from . import models
# import azure.functions as func
# from datetime import date
# import sqlalchemy
# from textblob import TextBlob
# from gnews import GNews

# __test_db_engine__ = None

# def database_uri():

#     url = os.environ.get("DB_CONNECTION_STRING", default="")
#     if len(url) != 0:
#         return url
    
#     url = sqlalchemy.engine.url.URL.create(
#         drivername = "mariadb+mariadbconnector",
#         username = os.environ.get("DB_USER", default="none"),
#         password = os.environ.get("DB_PASSWORD", default="none"),
#         host = os.environ.get("DB_SERVER", default="127.0.0.1"),
#         port = os.environ.get("DB_PORT", default="3306"),
#         database = os.environ.get("DB_NAME", default="mydb"))
#     return str(url)



# def main(mytimer: func.TimerRequest) -> None:
#     utc_timestamp = datetime.datetime.utcnow().replace(
#         tzinfo=datetime.timezone.utc).isoformat()
    
#     #Get or create and engine
#     if __test_db_engine__ is not None:
#         engine = __test_db_engine__
#     else:
#         # Get the connection variable andd SSl certificate if it has been provided.
#         connection_string = database_uri()
#         ssl_cert = os.environ.get("DB_SSL_CERT", default=None)
#         connection_args = {}
#         if ssl_cert is not None:
#             connection_args["ssl_ca"] = ssl_cert
#         engine = sqlalchemy.create_engine(connection_string, connect_args=connection_args, echo=False, future=True)
    
#     models.Base.metadata.create_all(engine)
#     session = Session(engine)

#     statement = sqlalchemy.select(models.Query.query)
#     queries = session.execute(statement)

#     todays_news = create_instance_for_day()

#     query_results = {}
    
#     for query in queries.scalars():
#         found_articles = search(query, todays_news)
#         analysis_sentiment(found_articles)
#         query_results[query] = found_articles
    
#     for article_query, articles in query_results.values():
#         for article in articles:
#             article_query = article_query
#             article_publisher = article['publisher']['title']
#             article_headline = article['title']
#             article_desc = article['description']
#             article_url = article['url']
#             article_date = dateparser.parse(article['published date'])
#             article_sentiment = article['sentiment']

#             result = models.QueryResult(
#                 article_query,
#                 article_publisher,
#                 article_headline,
#                 article_desc,
#                 article_url,
#                 article_date,
#                 article_sentiment
#             )

#             session.add(result)
#             session.commit()
#     session.close()
