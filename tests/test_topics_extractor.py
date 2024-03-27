import unittest
from src.topics_extractor import TopicsExtractor


class TestTopicsExtractor(unittest.TestCase):

    def setUp(self):
        self.te = TopicsExtractor("Mumbai", 20, 30)

    def test_get_lat_long(self):
        self.assertEqual(self.te.get_latitude_longitude(), (19.0759837,72.8776559)) 

    def test_gather_news(self):
        self.assertEqual(len(self.te.gather_news()), self.te.news_number) 

    def test_get_top_5_trending_topics(self):
        self.assertEqual(len(self.te.get_top_5_trending_topics()), 5)          



if __name__ == '__main__':
    unittest.main()


