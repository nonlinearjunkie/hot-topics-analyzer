import praw
from src.utils import utils
from src.utils.llm import LLM

CONFIG_JSON_FILE_PATH = "config.json"
config_dict = utils.read_json(CONFIG_JSON_FILE_PATH)

OPENAI_MODEL_NAME = config_dict.get("openai").get("model_name")
OPENAI_API_KEY = config_dict.get("openai").get("API-KEY")

reddit_configs = config_dict.get("reddit")


class GatherDiscussionException(Exception):
    def __init__(self):
        super().__init__("An error occured while gathering discussions for a topic.")


class GatherDiscussions:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=reddit_configs.get("client_id"),
            client_secret=reddit_configs.get("client_secret"),
            username=reddit_configs.get("username"),
            password=reddit_configs.get("password"),
            user_agent=reddit_configs.get("user_agent"),
        )

        self.openai_client = LLM(OPENAI_MODEL_NAME, OPENAI_API_KEY)

    def build_comment_chain(self, comment, chain=None):
        """Build a chain of comments from the comment to its top-level ancestor. If any comment in the chain is deleted, return None."""
        if chain is None:
            chain = []

        # Check if the comment or its author is deleted
        if (
            comment.author is None
            or comment.body == "[deleted]"
            or comment.body == "[removed]"
        ):
            return None

        # Prepend current comment to maintain order from root to leaf in the final output
        chain.insert(0, f"{comment.body}")
        if not comment.is_root:
            parent = comment.parent()
            return self.build_comment_chain(parent, chain)

        return chain
    
    def get_summarize_prompt(self, text):
        return f'''
        Summarize the text enclosed in double back ticks below. 
        ``
        {text}
        ``
        The summarized output response should have 40 words at maximum.
        '''

    def get_all_comment_chains(self, submission):
        """Get all comment chains for a submission, ignoring chains with deleted comments."""
        submission.comments.replace_more(limit=None)  # Load all comments
        all_chains = []
        for comment in submission.comments.list():
            # collect a maximmum of 10 comments from each submission
            if len(all_chains) > 10:
                break
            if isinstance(comment, praw.models.MoreComments):
                continue
            chain = self.build_comment_chain(comment)
            if chain is not None:
                all_chains.append(chain)
        return all_chains

    def generate_comment_prompt(self, post_title, post_content, comment_chain):

        comment_chain_hierarchy = ""
        for i, comment in enumerate(comment_chain, start=1):
            comment_chain_hierarchy += f"{i}. {comment} \n"

        prompt = f""""
        I have fetched all the comments from a submission in reddit. The comments
        have hierarchial structure meaning, there is a root comment on the submission and there can be a reply to a comment.
        I will provide you a comment chain where comment at the top or number 1 represents the comment directly done on the 
        submission. if there is a comment indexed with number 2, it represents a reply to comment on the number 1 and so on.
        All the replies to a comment are followed by it.

        Title of the submission : {post_title}
        Text content of the submission is wrapped in triple back quotes: 
        ```
        {post_content}
        ```
        Comment chain is the piece of text warpped inside double back quotes:
        ``
        {comment_chain_hierarchy}
        ``

        I want you to generate me a sentence that represents viewpoint of last comment in the comment chain. The viewpoint must be generated using 
        all the comments preceding the last comment in comment chain and the post content for maintaining the context of the last comment. 
        Please ignore the phrases like 'Based on the comments provided, it seems like', 'The viewpoint of the last comment in the comment chain is', etc. in the response.
        I want the sentence representing viewpoint only in the response. I will be using the viewpoint for further analysis, so please ignore unnecessary phrases in the response.
        Restrict the length of response to 20 words.

        """

        return prompt

    def gather_discussions(self, keyword, limit=5):
        discussions = []
        submission_count=0
        for submission in self.reddit.subreddit("all").search(keyword, limit=10):

            if(submission_count)>limit:
                break

            if submission.selftext:
                submission_details = {}

                submission_details["title"] = submission.title
                submission_details["discussion_points"] = []
                if (len(submission.selftext)>500):
                    post_summarizer_prompt = self.get_summarize_prompt(submission.selftext)
                    try:
                        post_content = self.openai_client.get_chat_completion(post_summarizer_prompt)
                    except:
                        raise GatherDiscussionException()
                else:
                    post_content=  submission.selftext 

                submission_details["discussion_points"].append(post_content)

                comment_chains = self.get_all_comment_chains(submission)
                for comment_chain in comment_chains:
        
                    prompt = self.generate_comment_prompt(
                        submission.title, submission.selftext, comment_chain
                    )
                    try:
                        openai_resp = self.openai_client.get_chat_completion(prompt)
                    except:
                        raise GatherDiscussionException()

                    submission_details["discussion_points"].append(openai_resp)

                discussions.append(submission_details)

                submission_count+=1

        return discussions
