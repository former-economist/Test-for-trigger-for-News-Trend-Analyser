from functions import scraper_functions
import unittest

class TestScraper(unittest.TestCase):

    def test_create_search_string(self):
        topic = 'boris'
        blocked_words = ['brexit', 'partygate']
        string = scraper_functions.create_search_string(topic, blocked_words)
        self.assertEqual(string, 'boris -brexit -partygate')

