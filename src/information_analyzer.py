import json
import re
from src.utils.llm import LLM
from src.utils import utils

config_path = "config.json"
config = utils.read_json(config_path)
openai_config = config.get("openai")


class TopicAnalysisException(Exception):
    def __init__(self, topic_name):
        super().__init__(
            f"Unable to generate analysis report for the topic:{topic_name}"
        )

class DiscussionAnalysisException(Exception):
    def __init__(self, discussion_title):
        super().__init__(
            f"Unable to generate analysis report for the discussion with title:{discussion_title}"
        )        

class OpenAIResponseFormatError(Exception):
    def __init__(self):
        super().__init__(
            f"The response from OpenAI is not in the specified format."
        )        


class InformationAnalyzer:
    def __init__(self):

        self.openai_client = LLM(
            model_name=openai_config.get("model_name"),
            model_key=openai_config.get("API-KEY"),
        )

    def extract_percentage_info_from_openai_response(self, openai_response):

        pattern = r'\{\s*"positive_percentage": \d+,\s*"negative_percentage": \d+,\s*"neutral_percentage": \d+\s*\}'

        # Search for the pattern in the string
        match = re.search(pattern, openai_response)

        if match:
            json_substring = match.group(0)
            json_data = json.loads(json_substring)  
    
        else:
            print(openai_response)
            raise OpenAIResponseFormatError

        return json_data    

    def make_topic_summarizer_prompt(self, topic_name, topic_information):

        prompt = f""" 
                    I have collected data on discussions happening on social media on a specific topic and stored it in a JSON file. 
                    The JSON file will be an array of objects where each discussion object in the array will represent a post made by someone (discussion) on social media.  
                    All the discussion objects will be on the same topic. Each discussion object will have two fields: title and discussion points. 
                    The title field value will represent the title of the post and discussion points will be an array where each element of the array represents the viewpoint of a specific user. 
                    I want you to summarize the information in not more than 100 words of the JSON file on the topic of {topic_name} whose content is given in the double back quotes below:

                    ``
                    {topic_information}

                    ``
                    Please do not include any other information besides summary like the json file contains....., and so on. The summary you generated 
                    will be shown as a summary directly to the stakeholders.
                """

        return prompt
    

    def make_discussion_summarizer_prompt(self, discussion_title, discussion_information):

        prompt = f""" 
                    I have collected data of discussions happening on social media. 
                    The discussion points, listed below inside double-back ticks, refer to the content of a post with the title {discussion_title} and comments made by various individuals in the post.
                    The discussion points are :
                    ``
                    {discussion_information}

                    ``
                    I want you to summarize the information in not more than 100 words of the discussion incluiding information from all discusion points.
                    Please do not include any other information besides summary like the json file contains....., and so on. The summary you generated 
                    will be shown as a summary directly to the stakeholders.
                """

        return prompt
    

    def make_discussion_sentiment_summary_prompt(
        self, topic_name, discussion_title, discussion_string
    ):


        prompt = f''' 
        You are an AI assistant to classify sentiment of discussion points from various individuals on the topic {topic_name} and then calculate percentage of
        discussion point with specific sentiment.
        I want you to generate a report that analyzes the sentiment of these discussion points regarding the topic **{topic_name}**. Classify the sentiment of each discussion point as either positive, negative, or neutral. 
        The discussion points refer to the content of a post with the title
            {discussion_title} on social media and comments made on the given post. The discussion points are listed below inside double-back ticks.
            ``
            {discussion_string}
            ``

        **Sentiment Classification Guidelines:**

        * **Positive:** The discussion point expresses a favorable opinion or view on the topic.
        * **Negative:** The discussion point expresses an unfavorable opinion or view on the topic.
        * **Neutral:** The discussion point does not express a clear opinion or view on the topic, or it presents both positive and negative aspects with equal weight.

        **Output Format:**

        The output response should be a JSON document adhering to the following schema:

        json
        {{
          "positive_percentage": *pos_percentage*,
          "negative_percentage": *neg_percentage*,
          "neutral_percentage": *neut_percentage*
        }}
         Also try to make sure each percentage is rounded to nearest integer.
        '''

        return prompt
    

    def make_discussion_cluster_summary_prompt(
        self,  discussion_title, discussion_string
    ):


        prompt = f''' 
        You are an AI assistant to group similair discussion points from various individuals into clusters on the post with title {discussion_title}, represent each cluster with a 
        description in single sentence that captures essence of all the discussion points in that cluster  and then determine number of discussion points in each cluster.
        
        I want you to generate a report that conatins a sentence that captures essence of all discussion points, grouped into a cluster, sharing a common viewpoint, 
        and count of discussion points in each cluster.
        The discussion points refer to the content of a post with the title
        {discussion_title} on social media and comments made on the given post. The discussion points are listed below inside double-back ticks.
            ``
            {discussion_string}
            ``

        **Cluster Formation guidelines:**

        * If two discussion points share common viewpoint, place them in same cluster.
        * Form a maximmum of 5 clusters of discussion points.
        * Represent each cluster with a sentence that represents common viewpoint of all the discussion points in the cluster.

        **Output Format:**

        The output response should be a JSON document adhering strictly to the following schema:

        json
        {{
          *sentence that represents common viewpoint of all the discussion points in a cluster*: *number of discussions in the cluster*
        }}
        The output json must contain number of elements equal to number of clusters, where each cluster represents each cluster.
        '''
        
        return prompt


    def generate_topic_analysis_report(self, topic_info_path):

        topic_report = {}

        topic_name = topic_info_path.split("/")[-1].split(".")[0]
        topic_information = utils.read_json(topic_info_path)
        prompt = self.make_topic_summarizer_prompt(topic_name, topic_information)
        try:
            openai_resp = self.openai_client.get_chat_completion(prompt)
        except:
            raise TopicAnalysisException(topic_name)

        topic_report["title"]=topic_name
        topic_report["summary"]=openai_resp
        topic_report["discussions"]=[]

        for discussion in topic_information:
            discussion_title = discussion.get("title")
            discussion_points = discussion.get("discussion_points")
            discussion_string = ''
            for i,discussion_point in enumerate(discussion_points, start=1):
                discussion_point = discussion_point.encode('utf-8', 'replace').decode()
                discussion_string+=f"{i}. {discussion_point} \n"
            sent_prompt = self.make_discussion_sentiment_summary_prompt(topic_name, discussion_title, discussion_string)
            try:
                openai_resp_sent = self.openai_client.get_chat_completion(sent_prompt)
                openai_resp_sent=self.extract_percentage_info_from_openai_response(openai_resp_sent)
            except:
                raise TopicAnalysisException(topic_name)
            
            discussion_report={}
            discussion_report["title"]=discussion_title
            discussion_report["sentiment_stats"]=openai_resp_sent
            topic_report["discussions"].append(discussion_report)
            
        return topic_report
    

    def generate_discussion_analysis_report(self, topic_info_path):

        discussion_report = {}
        topic_information = utils.read_json(topic_info_path)

        for discussion in topic_information:
            discussion_title = discussion.get("title")
            discussion_points = discussion.get("discussion_points")
            discussion_string = ''
            for i,discussion_point in enumerate(discussion_points, start=1):
                discussion_point = discussion_point.encode('utf-8', 'replace').decode()
                discussion_string+=f"{i}. {discussion_point} \n"
            discussion_summary_prompt = self.make_discussion_summarizer_prompt(discussion_title, discussion_string)
            try:
                discussion_summary = self.openai_client.get_chat_completion(discussion_summary_prompt)
            except:
                raise DiscussionAnalysisException(discussion_title)
            
            discussion_cluster_summary_prompt = self.make_discussion_cluster_summary_prompt(discussion_title, discussion_string)
            try:
                cluster_summary = self.openai_client.get_chat_completion(discussion_cluster_summary_prompt)
            except:
                raise DiscussionAnalysisException(discussion_title)
            
            discussion_report["summary"]=discussion_summary
            discussion_report["clusters"]=json.loads(cluster_summary)

            print(discussion_report)



            


