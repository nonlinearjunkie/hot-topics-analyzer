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
    

    def make_discussion_sentiment_summary_prompt(
        self, topic_name, discussion_title, discussion_string
    ):

        prompt = f"""
            I have collected discussion points from various individuals on the topic {topic_name}. The discussion points refer to the content of a post with the title
            {discussion_title} on social media and comments made on the given post. The discussion points are listed below inside double-back ticks.
            ``
            {discussion_string}
            ``
            I want you to generate a report that contains information about what percentage of discussion points have positive sentiment for the topic {topic_name}, 
            what percentage of discussion points have negative sentiment for the topic {topic_name}, and what percentage of discussion points have neutral sentiment for the topic {topic_name}.]
            The output response must strictly adhere to the following JSON schema inside triple backticks.
            ```
            {{
                "positive_percentage":pos_percentage, 
                "negative_percentage":neg_percentage,
                "neutral_percentage":neut_percentage
            }}
            ```

            In the output response JSON schema, pos_percentage represents the percentage of discussion points having positive sentiment, neg_percentage represents the percentage of discussion points having negative sentiment,
            and neut_percentage represents the percentage of discussion points having neutral sentiment. Also try to make sure each percentage is rounded to
            nearest integer. The output response must only contain JSON document so that it can be used directly by other piece of code.
        """

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
            


