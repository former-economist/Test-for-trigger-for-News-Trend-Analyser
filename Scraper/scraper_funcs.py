from textblob import TextBlob
from gnews import GNews

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