import unittest
from unittest.mock import patch, MagicMock

from src.gather_discussions import GatherDiscussions


class TestGatherDiscussions(unittest.TestCase):

    @patch('src.gather_discussions.praw.Reddit')
    @patch('src.utils.llm.LLM')
    def setUp(self, mock_reddit, mock_llm):
    
        self.mock_reddit = mock_reddit
        self.mock_llm = mock_llm

        # Instantiate the class with the mocked dependencies
        self.gatherer = GatherDiscussions()
        self.gatherer.reddit=mock_reddit
        


    def test_build_comment_chain(self):
      
        comment = MagicMock()
        comment.body = "Test comment"
        comment.author = MagicMock()
        comment.is_root = True

        result = self.gatherer.build_comment_chain(comment)
        self.assertEqual(result, ["Test comment"])


    @patch('src.gather_discussions.GatherDiscussions.build_comment_chain')
    def test_get_all_comment_chains(self, mock_build_comment_chain):

        submission = MagicMock()
        submission.comments.list.return_value = [MagicMock()]

        mock_build_comment_chain.return_value = ["Test comment"]

        result = self.gatherer.get_all_comment_chains(submission)
        self.assertEqual(result, [["Test comment"]])


    
    @patch('src.gather_discussions.GatherDiscussions.get_all_comment_chains')
    @patch('src.utils.llm.LLM.get_chat_completion')
    def test_gather_discussions(self, mock_get_chat_completion, mock_get_all_comment_chains):
        
        mock_get_all_comment_chains.return_value = [["Comment 1", "Comment 2"]]
        mock_get_chat_completion.return_value = "Test Response"

        mock_submission = MagicMock()
        mock_submission.title = "Test Title"
        mock_submission.selftext = "Test Content"
        self.gatherer.reddit.subreddit.return_value.search.return_value = [mock_submission]

        result = self.gatherer.gather_discussions("keyword")
        self.assertEqual(len(result), 1)
        self.assertIn("Test Response", result[0]["discussion_points"])
        


if __name__ == '__main__':
    unittest.main()

