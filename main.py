import json
import os
import uuid
import time

from src.topics_extractor import TopicsExtractor
from src.gather_discussions import GatherDiscussions
from src.information_analyzer import InformationAnalyzer

CACHE_STORAGE_PATH="data/cache_storage.json"
DISCUSSIONS_TMP_STORAGE_DIR = "data/tmp/discussions"
RESULTS_DIR = "data/results"


def get_topics(city_name):

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

    te = TopicsExtractor(city_name=city_name, news_number=20, radius_in_km=30)
    topics = te.get_top_5_trending_topics()    

    for topic in topics:

        # append city name to topic to extract relevant topics for a city
        topic_with_location = f"{city_name} {topic}"

        # Construct the full file path
        file_path = os.path.join(DISCUSSIONS_TMP_STORAGE_DIR, f"{topic}.json")

        gd = GatherDiscussions()
        discussions = gd.gather_discussions(topic)
        with open(file_path, "w") as outfile: 
            json.dump(discussions, outfile)


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
        

if __name__=="__main__":
    city_name="Hyderabad"
    topics = get_topics(city_name)  
    print(topics) 
  





