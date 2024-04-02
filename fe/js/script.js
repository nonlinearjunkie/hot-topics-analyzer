document.getElementById('fetchButton').addEventListener('click', async function() {
    const city = document.getElementById('cityInput').value;
    const dropdown = document.getElementById('trendingTopicsDropdown');
    const dropdownContainer = document.getElementById('dropdownContainer');
    const noTopicsMessage = document.getElementById('noTopicsMessage'); // New line

    try {
        const response = await fetch(`http://127.0.0.1:8000/get-topics/${city}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (data.trending_topics && data.trending_topics.length > 0) {
            dropdown.length = 1; 
            data.trending_topics.forEach(topic => {
                const option = new Option(topic, topic);
                dropdown.add(option);
            });
            dropdownContainer.classList.remove('hidden'); 
            noTopicsMessage.classList.add('hidden'); 
        } else {
            dropdownContainer.classList.add('hidden'); 
            noTopicsMessage.classList.remove('hidden'); 
        }
    } catch (error) {
        console.error('Error fetching topics:', error);
        dropdownContainer.classList.add('hidden');
        
        noTopicsMessage.classList.remove('hidden'); 
        noTopicsMessage.textContent = 'Error fetching topics.'; 
    }
});

document.getElementById('fetchButton').addEventListener('click', fetchTopics);

async function fetchTopics() {
    const city = document.getElementById('cityInput').value;
    const dropdown = document.getElementById('trendingTopicsDropdown');
    const dropdownContainer = document.getElementById('dropdownContainer');
    const noTopicsMessage = document.getElementById('noTopicsMessage');
    const detailsButton = document.getElementById('detailsButton');
    const topicDetailsDiv = document.getElementById('topicDetails');

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
            dropdownContainer.classList.remove('hidden'); // Unhide dropdown
            noTopicsMessage.classList.add('hidden'); // Ensure no topics message is hidden
            topicDetailsDiv.classList.add("hidden")
        } else {
            dropdownContainer.classList.add('hidden'); // Hide dropdown
            noTopicsMessage.classList.remove('hidden'); // Display no topics message
            topicDetailsDiv.classList.add("hidden");
        }
    } catch (error) {
        console.error('Error fetching topics:', error);
        dropdownContainer.classList.add('hidden');
        noTopicsMessage.classList.remove('hidden'); // Display no topics message in case of error as well
        topicDetailsDiv.classList.add("hidden");
        noTopicsMessage.textContent = 'Error fetching topics.'; // Custom error message
    }
}

// Event listener for when a topic is selected from the dropdown
document.getElementById('trendingTopicsDropdown').addEventListener('change', function() {
    const detailsButton = document.getElementById('detailsButton');
    const topicDetailsDiv = document.getElementById('topicDetails');
    if (this.value !== "Select a topic") {
        detailsButton.classList.remove('hidden');
        topicDetailsDiv.classList.add("hidden")
    } else {
        detailsButton.classList.add('hidden');
        topicDetailsDiv.classList.add("hidden")
    }
});

// Event listener for the 'Show Topic Details' button
document.getElementById('detailsButton').addEventListener('click', function() {
    const topicName = document.getElementById('trendingTopicsDropdown').value;
    const city = document.getElementById('cityInput').value;
    getTopicDetails(city, topicName);
});

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

    // Clear previous discussions
    const discussionsContainer = document.getElementById('discussionsContainer');
    discussionsContainer.innerHTML = '';

    // Loop through each discussion in the topicDetails
    topicReport.discussions.forEach((discussion, index) => {
        // Create discussion container
        const discussionDiv = document.createElement('div');
        discussionDiv.classList.add('discussion');

        // Create title
        const titleDiv = document.createElement('div');
        titleDiv.classList.add('title');
        titleDiv.textContent = discussion.title;
        discussionDiv.appendChild(titleDiv);

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