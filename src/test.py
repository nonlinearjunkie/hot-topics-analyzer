
from gather_news import TopicsExtractor

t = TopicsExtractor("Kathmandu", 20, 30)


topics = t.get_top_5_trending_topics()
print(topics)



