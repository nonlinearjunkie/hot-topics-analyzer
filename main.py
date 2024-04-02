import json
import os
import uuid
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Union

from src.topics_extractor import TopicsExtractor
from src.gather_discussions import GatherDiscussions
from src.information_analyzer import InformationAnalyzer

CACHE_STORAGE_PATH="data/cache_storage.json"
DISCUSSIONS_TMP_STORAGE_DIR = "data/tmp/discussions"
RESULTS_DIR = "data/results"

app = FastAPI()

origins = [
   "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins to make requests
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class CityNotFoundError(Exception):
    def __init__(self):
        super().__init__("The city for which you are trying to fetch report does not exist in cache.")


def get_city_uuid(city_name):

    with open(CACHE_STORAGE_PATH) as fp:
        all_cities_info = json.load(fp)

    if city_name not in all_cities_info:
        raise CityNotFoundError
    
    city_uuid = all_cities_info.get(city_name).get("id")

    return city_uuid


def get_topics(city_name):

    city_name=city_name.lower()

    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(CACHE_STORAGE_PATH):
        with open(CACHE_STORAGE_PATH, 'a') as file:
            file.write('{}')

    with open(CACHE_STORAGE_PATH) as fp:
        all_cities_info = json.load(fp) 

    if city_name not in all_cities_info:
        analyze_discussions(city_name)
        with open(CACHE_STORAGE_PATH) as fp:
            all_cities_info = json.load(fp) 
    else:
        if(int(time.time())- all_cities_info[city_name].get("ts") > 604800):
            analyze_discussions(city_name)
            with open(CACHE_STORAGE_PATH) as fp:
                all_cities_info = json.load(fp) 
  
         
    return all_cities_info.get(city_name).get("topics")
        


def analyze_discussions(city_name):

    if not os.path.exists(DISCUSSIONS_TMP_STORAGE_DIR):
        os.makedirs(DISCUSSIONS_TMP_STORAGE_DIR)

    city_uuid = str(uuid.uuid4()) 

    print("Extracting top 5 trending topics......")   

    te = TopicsExtractor(city_name=city_name, news_number=20, radius_in_km=30)
    topics = te.get_top_5_trending_topics() 

    print("Trending topics extraction completed......")   

    for topic in topics:

        # append city name to topic to extract relevant topics for a city
        topic_with_location = f"{city_name} {topic}"

        # Construct the full file path
        file_path = os.path.join(DISCUSSIONS_TMP_STORAGE_DIR, f"{topic}.json")

        print(f"Gathering discussions for topic: {topic}")

        gd = GatherDiscussions()
        discussions = gd.gather_discussions(topic)
        with open(file_path, "w") as outfile: 
            json.dump(discussions, outfile)


        print("Generating reports for discussions in {topic} topic........")
        ia= InformationAnalyzer()
        topic_report=ia.generate_topic_analysis_report(file_path)
        print("Topic report:")
        print(topic_report)

        topic_dir=os.path.join(RESULTS_DIR, city_uuid, "topics", topic)
        if not os.path.exists(topic_dir):
            os.makedirs(topic_dir)
        topic_file_path=os.path.join(topic_dir, "topic_report.json")
        with open(topic_file_path, "w") as outfile: 
            json.dump(topic_report, outfile)

        discussions_dir = os.path.join(topic_dir, "discussions")  
        if not os.path.exists(discussions_dir):
            os.makedirs(discussions_dir) 


        discussion_report=ia.generate_discussion_analysis_report(file_path)
        for dis_title, dis_info in discussion_report.items():
            dis_file_path = os.path.join(discussions_dir, f"{dis_title}.json")
            with open(dis_file_path, "w") as outfile: 
                json.dump(dis_info, outfile)


    with open(CACHE_STORAGE_PATH) as fp:
        all_cities_info = json.load(fp) 

    all_cities_info[city_name]={
        "id":city_uuid,
        "ts":int(time.time()),
        "topics":topics
    } 

    with open(CACHE_STORAGE_PATH, "w") as outfile: 
        json.dump(all_cities_info, outfile)      
        

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get-topics/{city_name}")
def get_topics_by_city(city_name:str):

    city_name=city_name.lower()
    trending_topics=get_topics(city_name)

    return {"city_name":city_name,"trending_topics":trending_topics}


@app.get("/get-topic-report/{city_name}")
def get_topic_report(city_name:str, topic_name: Union[str, None] = None):

    city_name=city_name.lower()

    try:
        city_uuid = get_city_uuid(city_name)
        topic_report_path = os.path.join(RESULTS_DIR,city_uuid, "topics", topic_name, "topic_report.json")

        try:
            with open(topic_report_path, "r") as fp:
                topic_report = json.load(fp)
        except:
            raise HTTPException(status_code=404, detail=f"No topic report found for {city_name} city with topic {topic_name}.")

    except CityNotFoundError:
        raise HTTPException(status_code=404, detail=f"No record found for {city_name} city.")
    except:
        raise HTTPException(status_code=500, detail=f"Internal server error.")
    
    return {"city_name":city_name, "topic_name":topic_name,"topic_report":topic_report}



@app.get("/get-discussion-report/{city_name}")
def get_discussion_report(city_name:str, topic_name: Union[str, None] = None, discussion_title: Union[str, None] = None):

    city_name=city_name.lower()
    try:
        city_uuid = get_city_uuid(city_name)
        discussion_report_path = os.path.join(RESULTS_DIR,city_uuid, "topics", topic_name, "discussions", f"{discussion_title}.json")

        try:
            with open(discussion_report_path, "r") as fp:
                discussion_report = json.load(fp)
        except:
            raise HTTPException(status_code=404, detail=f"No discssion report found for {city_name} city with discussion titled {discussion_title}.")

    except CityNotFoundError:
        raise HTTPException(status_code=404, detail=f"No record found for {city_name} city.")
    except:
        raise HTTPException(status_code=500, detail=f"Internal server error.")
    

    return {"city_name":city_name,"topic_name":topic_name, "discussion_title":discussion_title, "discussion_report":discussion_report}


  





