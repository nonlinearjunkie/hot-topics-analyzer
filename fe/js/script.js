document.getElementById('fetchButton').addEventListener('click', fetchTopics);

async function fetchTopics() {
    console.log("Request sent to backend")
    // Get the Fetch Topics button and disable it
    const fetchButton = document.getElementById('fetchButton');
    fetchButton.disabled = true;

    const city = document.getElementById('cityInput').value;
    const dropdown = document.getElementById('trendingTopicsDropdown');
    const dropdownContainer = document.getElementById('dropdownContainer');
    const noTopicsMessage = document.getElementById('noTopicsMessage');
    const detailsButton = document.getElementById('detailsButton');
    const topicDetailsDiv = document.getElementById('topicDetails');
    const discussionDetailsDiv = document.getElementById('discussionDetails');

    detailsButton.classList.add('hidden');

    try {
        const response = await fetch(`http://127.0.0.1:8000/get-topics/${city}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (data.trending_topics && data.trending_topics.length > 0) {
            dropdown.length = 1; // Clear current options except the first
            data.trending_topics.forEach(topic => {
                const option = new Option(topic, topic);
                dropdown.add(option);
            });
            dropdownContainer.classList.remove('hidden'); 
            noTopicsMessage.classList.add('hidden'); 
            topicDetailsDiv.classList.add("hidden");
            discussionDetailsDiv.classList.add("hidden");
        } else {
            dropdownContainer.classList.add('hidden'); 
            noTopicsMessage.classList.remove('hidden'); 
            topicDetailsDiv.classList.add("hidden");
            discussionDetailsDiv.classList.add("hidden");
        }
    } catch (error) {
        console.error('Error fetching topics:', error);
        dropdownContainer.classList.add('hidden');
        noTopicsMessage.classList.remove('hidden'); 
        topicDetailsDiv.classList.add("hidden");
        discussionDetailsDiv.classList.add("hidden");
        noTopicsMessage.textContent = 'Error fetching topics.';
    } finally {
        // Re-enable the Fetch Topics button whether the fetch was successful or failed
        fetchButton.disabled = false;
    }
}

// Event listener for when a topic is selected from the dropdown
document.getElementById('trendingTopicsDropdown').addEventListener('change', function() {
    const detailsButton = document.getElementById('detailsButton');
    const topicDetailsDiv = document.getElementById('topicDetails');
    const discussionDetailsDiv = document.getElementById('discussionDetails');
    if (this.value !== "Select a topic") {
        detailsButton.classList.remove('hidden');
        topicDetailsDiv.classList.add("hidden");
        discussionDetailsDiv.classList.add("hidden");
    } else {
        detailsButton.classList.add('hidden');
        topicDetailsDiv.classList.add("hidden");
        discussionDetailsDiv.classList.add("hidden");
    }
});

// Event listener for the 'Show Topic Details' button
document.getElementById('detailsButton').addEventListener('click', function() {
    const topicName = document.getElementById('trendingTopicsDropdown').value;
    const city = document.getElementById('cityInput').value;
    getTopicDetails(city, topicName);
});


// Function to handle click on discussion title
async function handleDiscussionTitleClick(city, topicName, discussionTitle) {
    try {
        // Encode the URI components to ensure the URL is properly formatted
        const response = await fetch(`http://127.0.0.1:8000/get-discussion-report/${encodeURIComponent(city)}?topic_name=${encodeURIComponent(topicName)}&discussion_title=${encodeURIComponent(discussionTitle)}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Call displayDiscussionDetails with the response data
        displayDiscussionDetails(data);
    } catch (error) {
        console.error('Error fetching discussion report:', error);
    }
}


// Function to get the details of a topic
async function getTopicDetails(city, topicName) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/get-topic-report/${city}?topic_name=${encodeURIComponent(topicName)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const topicDetails = await response.json();
        var topicReport = topicDetails.topic_report;
        console.log(topicDetails); 
        console.log(topicReport)
    } catch (error) {
        console.error('Error fetching topic details:', error);
    }

    document.getElementById('topicTitle').textContent = topicReport.title;
    document.getElementById('topicSummary').textContent = topicReport.summary;
    document.getElementById('topicSummary').style.textAlign = 'left';

    // Clear previous discussions
    const discussionsContainer = document.getElementById('discussionsContainer');
    discussionsContainer.innerHTML = '';

    // Loop through each discussion in the topicDetails
    topicReport.discussions.forEach((discussion, index) => {
        // Create discussion container
        const discussionDiv = document.createElement('div');
        discussionDiv.classList.add('discussion');

         // Create clickable title element (button)
         const titleButton = document.createElement('button');
         titleButton.classList.add('title');
         titleButton.textContent = discussion.title;
         
         // Add click event listener to the titleButton
         titleButton.addEventListener('click', () => handleDiscussionTitleClick(city, topicName, discussion.title));

         discussionDiv.appendChild(titleButton);


        const canvas = document.createElement('canvas');
        canvas.id = `chart${index}`; // Assign a unique ID for each canvas
        const chartContainer = document.createElement('div');
        chartContainer.classList.add('chart-container');
        chartContainer.appendChild(canvas); // Append the canvas to the chart container
        discussionDiv.appendChild(chartContainer);


        // Append discussion to container
        discussionsContainer.appendChild(discussionDiv);

        // Generate pie chart after adding to DOM
        generatePieChart(canvas.id, discussion.sentiment_stats);
    });

    // Unhide topic details container
    document.getElementById('topicDetails').classList.remove('hidden');
}


function generatePieChart(containerId, sentimentStats) {
    const canvas = document.getElementById(containerId);
    const ctx = canvas.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Positive', 'Negative', 'Neutral'],
            datasets: [{
                label: 'Discussion Sentiment',
                data: [
                    sentimentStats.positive_percentage, 
                    sentimentStats.negative_percentage, 
                    sentimentStats.neutral_percentage
                ],
                backgroundColor: [
                    'rgba(10, 235, 10)', // Dark green
                    'rgba(235, 10, 10)',  // Dark red
                    'rgba(10, 10, 255)' // Dark blue
                ],
                borderColor: [
                    'rgba(10, 235, 10)', // Dark green
                    'rgba(235, 10, 10)',  // Dark red
                    'rgba(10, 10, 255)' // Dark blue
                ],
                borderWidth: 2 
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                position: 'bottom',
                labels: {
                    fontColor: '#333', // Dark font for legend labels
                    padding: 20,
                    boxWidth: 20
                }
            },
            
        }
    });
}

async function displayDiscussionDetails(responseData) {
    const discussionDetailsContainer = document.getElementById('discussionDetails');

    // Extract the discussion report from the response data
    const discussionReport = responseData.discussion_report;

    // Clear previous content
    discussionDetailsContainer.innerHTML = '';
  
    // Create and append the discussion title
    const titleElement = document.createElement('h2');
    titleElement.textContent = responseData.discussion_title;
    discussionDetailsContainer.appendChild(titleElement);
  
    // Create and append the discussion summary
    const summaryHeading = document.createElement('h3');
    summaryHeading.textContent = 'Discussion Summary';
    discussionDetailsContainer.appendChild(summaryHeading);
  
    const summaryElement = document.createElement('p');
    summaryElement.textContent = discussionReport.summary;
    summaryElement.style.textAlign="left";
    discussionDetailsContainer.appendChild(summaryElement);
  
    // Create and append the unique viewpoints heading
    const viewpointsHeading = document.createElement('h3');
    viewpointsHeading.textContent = 'Unique Viewpoints in the Discussion';
    discussionDetailsContainer.appendChild(viewpointsHeading);

    // Prepare data for the horizontal bar chart
    const labels = [];
    const dataPoints = [];
    Object.entries(discussionReport.clusters).forEach(([viewpointTitle, count]) => {
      labels.push(viewpointTitle);
      dataPoints.push(count);
    });

    // Unhide discussion details container
    discussionDetailsContainer.classList.remove('hidden');

    // Create a chart placeholder outside the loop, we will use one chart for all data
    const chartPlaceholder = document.createElement('div');
    chartPlaceholder.className = 'chart-container';
    chartPlaceholder.id = 'chart-placeholder';
    discussionDetailsContainer.appendChild(chartPlaceholder);

    // Render the bar charts inside the placeholder
    renderBarChart(labels, dataPoints);
}

function renderBarChart(labels, dataPoints) {
    // Get the chart container by id and clear any existing content
    const chartContainer = document.getElementById('chart-placeholder');
    chartContainer.innerHTML = '';

    // Create a canvas element for the bar chart
    const canvas = document.createElement('canvas');
    chartContainer.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    // Create the bar chart with Chart.js
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of discussion points supportting the viewpoint',
                data: dataPoints,
                backgroundColor: 'rgba(255, 88, 88)',
                borderColor: 'rgba(0, 0, 0)',
                borderWidth: 2,
                barThickness: 60,
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: Math.max(...dataPoints) * 1.1, // Ensure all bars use the same scale
                },
                y: {
                    ticks: {
                        autoSkip: false,
                        maxRotation: 0,
                        minRotation: 0,
                        mirror: true,
                        padding: -10,
                        font: {
                            size: 16,
                        },
                        callback: function(value) {
                            if (value.length > 25) {
                                return value.match(/.{1,25}(\s|$)/g);
                            }
                            return value;
                        }
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    enabled: true,
                },
            }
        }
    });
}
