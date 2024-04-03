import json

from src.utils.rpc import RPC
from src.utils.llm import LLM
from src.utils import utils

CONFIG_JSON_FILE_PATH = "config.json"

config_dict = utils.read_json(CONFIG_JSON_FILE_PATH)
WORLD_NEWS_API_BASE_URL = config_dict.get("world-news-api").get("BASE_URL")
WORLD_NEWS_API_KEY = config_dict.get("world-news-api").get("API-KEY")
OPENAI_MODEL_NAME = config_dict.get("openai").get("model_name")
OPENAI_API_KEY = config_dict.get("openai").get("API-KEY")


class LatLongFetchError(Exception):
    def __init__(self, location):
        super().__init__(
            f"Unable to get latitude and longitude information of the location:{location}"
        )


class GatherNewsException(Exception):
    def __init__(self, location):
        super().__init__(f"Unable to gather news items of the location:{location}")


class ListTopicsException(Exception):
    def __init__(self, location):
        super().__init__(f"Unable to list trending topics of the location:{location}")


class TopicsExtractor:
    def __init__(self, city_name, news_number, radius_in_km):

        """
        city_name: city whose trending topics need to be determined
        news_number: number of news to be fetched to infer trending topics
        radius_in_km: Radius in km w.r.t. location from where news topics need to be fetched
        """
        self.city_name = city_name
        self.news_number = news_number
        self.radius_in_km = radius_in_km
        self.rpc = RPC(WORLD_NEWS_API_BASE_URL)
        self.openai_client = LLM(OPENAI_MODEL_NAME, OPENAI_API_KEY)

    def get_latitude_longitude(self):

        query_params = {
            "location": self.city_name,
            "api-key": WORLD_NEWS_API_KEY,
        }

        try:
            res = self.rpc.get("/geo-coordinates", {}, query_params=query_params)

        except:
            raise LatLongFetchError(self.city_name)

        return res.get("latitude"), res.get("longitude")

    def gather_news(self):

        titles = []

        try:
            lat, long = self.get_latitude_longitude()

        except:
            raise GatherNewsException(self.city_name)

        query_params = {
            "location-filter": f"{lat},{long},{self.radius_in_km}",
            "api-key": "b3a18d159b3a418999a1693f039d4f6f",
            "sort": "publish-time",
            "sort-direction": "DESC",
            "number": self.news_number,
            "language": "en",
            "entities": f"LOC:{self.city_name}",
        }

        try:
            res = self.rpc.get("/search-news", {}, query_params=query_params)
            all_news = res.get("news")
            for news in all_news:
                titles.append(news.get("title"))

        except:
            print("Could not fetch the response")
            raise GatherNewsException(self.city_name)

        return titles

    def make_prompt(self, list_news):

        all_news_ordered = ""
        for i, news in enumerate(list_news, start=1):
            all_news_ordered += f"{i}. {news} \n"

        prompt = f"""
            I have collected headlines of trending news in a city, and I want you to give me trending topics in that particular city based on the headlines.
            We have {len(list_news)} headlines for this case which are listed in the double-back quotes:
            ``{all_news_ordered}``
            Give me top 5 trending topics in the city inferred from the headlines. The output should be formatted a list of topics and restrict each topic's length to 
            maximmum of 5 words.
        """

        return prompt

    def get_top_5_trending_topics(self):

        topics = []

        news_titles = self.gather_news()

        prompt = self.make_prompt(news_titles)
        try:
            openai_resp = self.openai_client.get_chat_completion(prompt)
        except:
            raise ListTopicsException(self.city_name)

        lines = openai_resp.split("\n")
        for line in lines:
            line=line.replace("/","")
            topics.append(json.loads(line[3:]))

        return topics
