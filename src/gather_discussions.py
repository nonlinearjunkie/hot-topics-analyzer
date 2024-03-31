import praw
# The keyword you want to search for
keyword = "Python programming"


class GatherDiscussions:

    def __init__(self):
        self.reddit =praw.Reddit(client_id="xnpLhyYbMDQsTTqfcxc05g",
                    client_secret="7Dbr8vDPD70NdFPDv8AmTltG8_hHqw",
                    username="lamb_of_god_666",
                    password="k*VSdSEfE6HM7bi",
                    user_agent="topicsanalyzer:v1.0.0 (by u/lamb_of_god_666)"
                    )


    def build_comment_chain(self,comment, chain=None):
        """Build a chain of comments from the comment to its top-level ancestor. If any comment in the chain is deleted, return None."""
        if chain is None:
            chain = []

        # Check if the comment or its author is deleted
        if comment.author is None or comment.body == '[deleted]' or comment.body == '[removed]':
            return None  

        # Prepend current comment to maintain order from root to leaf in the final output
        chain.insert(0, f"{comment.body}")
        if not comment.is_root:
            parent = comment.parent()  
            return self.build_comment_chain(parent, chain)  

        return chain
    

    def get_all_comment_chains(self,submission):
        """Get all comment chains for a submission, ignoring chains with deleted comments."""
        submission.comments.replace_more(limit=None)  # Load all comments
        all_chains = []
        for comment in submission.comments.list():
            if isinstance(comment, praw.models.MoreComments):
                continue  
            chain = self.build_comment_chain(comment)
            if chain is not None:  
                all_chains.append(chain)
        return all_chains
    

    def gather_discussions(self,keyword):
        for submission in self.reddit.subreddit('all').search(keyword, limit=10):
            if(submission.selftext):
                print(f"Title: {submission.title}")
                print(f"Content:{submission.selftext}")

                print("Comments:")
                comment_chains = self.get_all_comment_chains(submission)
                for comment_chain in comment_chains:
                    print(comment_chain)
    