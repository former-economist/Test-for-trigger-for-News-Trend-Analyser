import logging

import azure.functions as func
from datetime import date
from textblob import TextBlob
from gnews import GNews
from flask import jsonify 

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

def create_dated_instance(date01, date02):
    d1 = date(date01)
    d2 = date(date02)
    num_days = d1 - d2
    days = str(num_days.days)
    days += 'd'
    google_obj = GNews()
    google_obj.period = days
    return google_obj

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
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == "GET":
        topic = req.params.get('topic')
        blocked_words = req.params.get('blocked-words')
        
        
    elif req.method == "POST":
        try:
            req_body = req.get_json()
        except ValueError:
            topic = None
            blocked_words = None
        else:
            topic = req_body.get('topic')
            blocked_words = req_body.get('blocked-words')
    
    search_instance = create_instance()
    search_string = create_search_string(topic, blocked_words)
    found = search(search_string, search_instance)
    analysis_sentiment(found)



    if topic:
        return func.HttpResponse(f"{found}")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
