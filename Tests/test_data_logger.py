from urllib import response
import azure.functions as func
import unittest
import Data_Logger
import json
from sqlalchemy import create_engine


class TestDataLogger(unittest.TestCase):

    def setUp(cls) -> None:
        Data_Logger.__test_db_engine__=create_engine("sqlite+pysqlite:///:memory:", echo=True, future=False)

    def test_data_logger(self):
        request = func.HttpRequest(
            method="GET",
            body= json.dumps(
                {
                'topic': 'boris',
                'blocked-words': ["partygate", "brexit"]
                }
            ).encode('utf8'), 
            headers={"Accept": "application/json"},
            url="/"
        )
        response=Data_Logger.main(request)
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()