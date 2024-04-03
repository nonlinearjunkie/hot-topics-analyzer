# hot-topics-analyzer

This project aims to list trending topics in a given city. For each of the topics, we will then gather the discussions happening around in various social media platforms. The discussions will be then grouped in three major categories:
1. Discussions that have positive sentiment for a given topic
2. Discussions that have neutral sentiment for a given topic
3. Discussions that have negative sentiment for a given topic

For each of the discussion groups(positive, negative and neutral), we will then form a multiple clusters of discussions sharing a common viewpoint and represent the cluster with a viewpoint that gives holistic idea about the cluster.

Finally, we will develop a dashboard to view the analysis done above.

## Approach:

### Task-1 (Topics Extraction):
I have used following steps to extract top 5 trending topics in a city:

1. Geolocation Fetching: Converts the city name into geographical coordinates (latitude and longitude) by making an API request to a geolocation endpoint provided by WorldNews API. This is critical for ensuring that the news fetched is geographically relevant.

2. News Gathering: Fetches news headlines based on the city's geolocation and predefined criteria such as the number of news items, language, and the radius from the city center. 

3. Trending Topics Extraction Using LLM: We generate a prompt for the OpenAI model by listing the fetched news headlines. This prompt is designed to guide the AI in identifying the most relevant topics from the headlines. We then submit the constructed prompt to the OpenAI model and then process the response from Open AI model to extract a list of the top 5 trending topics. 

### Task-2 (Gather relevant discussions):

Here, we gather relevant discussions happening on trending topics extracted in task-1 from social media. 

Steps Involved:

1. Discussion Gathering: Fetches Reddit submissions based on a search keyword. We store title, content and comment of each reedit submission for futher analysis. While fetching comments, we build a comment chain for each comment that includes all the parent comments for a comment, to maintain the context of each comment. 
2. Content Summarization: For lengthy submission texts, a summarization prompt is created and sent to OpenAI's model to obtain a concise version of the submission content, making it easier to analyze and understand.
3. Viewpoint Generation: For each comment chain, a prompt is constructed that includes the submission's title and content along with the hierarchical comments. This prompt is used to generate a sentence representing the viewpoint of the last comment in the chain, considering the context provided by the submission and preceding comments.

### Task-3 (Analyze gathered information)

It analyzes all the gathered information. i have done three major analysis of the gathered information:
1. Summarization: Summarized the information in all the discussion gathered for a specific topic, also summarized information
gathered in each discussion.

2. Sentiment analysis of discussion points: For each discussion gathered for a topic, I have summarized sentiment information indicating what percentage of discussions have positive, negative and neutral sentiment. The information is presented in the frontend using a pie chart.

3. Organizing discussion points with similar viewpoints and getting count of discussion points in each cluster. The information is presented in the frontend using a bar chart.

### Task-4(Build a small front-end to display your analyzed information)

For this I have built a frontend using HTML, CSS and JavaScript which takes the city name as input and sends a request to
backend server made using FastAPI to fetch the required information.

To minimize redundant data processing,the system uses JSON files stored in a data directory for caching information about cities, topics, and discussions. When a request for topics in a city is received, the system checks if the data is already cached. If not, or if the data is outdated (older than a week), it triggers the data gathering and analysis process.

## Installation

Before you begin, make sure you have `Python 3.8+` installed on your system

To install the project, follow these steps:

1. Clone the repository

First, clone the repository to your local machine:

```bash

git clone https://github.com/nonlinearjunkie/hot-topics-analyzer.git
cd hot-topics-analyzer
```

2. Set up a virtual environment

```bash
Copy code
python3 -m venv .venv
```

3. Activate the virtual environment:

On Windows:

```

.\.venv\Scripts\activate
```

On Unix or MacOS:

```bash

source .venv/bin/activate
```


4.Install dependencies

With your virtual environment activated, install the project dependencies by running:

```bash

pip install -r requirements.txt
```


## Running the Application
After setting up the project, you can start the FastAPI server by executing:

```bash
uvicorn main:app --port 8000
```

This will start a FastAPI server on port `8000` that will serve requests made by the frontend.

To start the frontend, open the file `fe/index.html` on your browser.
Then you can interact with the application using the frontend.