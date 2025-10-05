document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    const toolSelectionArea = document.getElementById('tool-selection-area');
    const toolResponseArea = document.getElementById('tool-response-area');
    const toolResponseBox = document.getElementById('tool-response-box');
    const loadingSpinner = document.querySelector('.loading-spinner');

    let extractedParams = {};

    // --- Core Functions ---

    // Function to render messages in the chat box
    const renderMessages = (messages) => {
        chatBox.innerHTML = '';
        messages.forEach(msg => {
            const messageType = msg.role === 'user' ? 'user-message' : 'assistant-message';
            chatBox.innerHTML += `
                <div class="chat-message ${messageType}">
                    <div class="card d-inline-block">
                        <div class="card-body">
                            ${msg.content}
                        </div>
                    </div>
                </div>
            `;
        });
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // Function to load chat history from the server
    const loadHistory = async () => {
        const response = await fetch('/history');
        const messages = await response.json();
        renderMessages(messages);
    };

    // Function to show/hide loading spinner
    const showLoading = (isLoading) => {
        loadingSpinner.style.display = isLoading ? 'block' : 'none';
        userInput.disabled = isLoading;
    };

    // --- Event Handlers ---

    // Handle chat form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const messageText = userInput.value.trim();
        if (!messageText) return;

        showLoading(true);
        toolSelectionArea.innerHTML = ''; // Clear old tools
        toolResponseArea.style.display = 'none';

        // Add user message to UI immediately
        const currentHistory = await (await fetch('/history')).json();
        renderMessages([...currentHistory, { role: 'user', content: messageText }]);
        userInput.value = '';

        try {
            const formData = new FormData();
            formData.append('userInput', messageText);

            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Network response was not ok.');
            
            const result = await response.json();
            extractedParams = result.extractedParameters;

            // Display classified tool buttons
            if (result.classifiedTools && result.classifiedTools.length > 0) {
                result.classifiedTools.forEach(toolName => {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-outline-success m-1';
                    btn.textContent = `Call ${toolName}`;
                    btn.dataset.toolName = toolName;
                    toolSelectionArea.appendChild(btn);
                });
            } else {
                toolSelectionArea.innerHTML = '<p class="text-muted">No relevant tools were identified.</p>';
            }

        } catch (error) {
            console.error('Error during chat processing:', error);
            toolSelectionArea.innerHTML = '<p class="text-danger">An error occurred. Please try again.</p>';
        } finally {
            showLoading(false);
            loadHistory(); // Reload history to include assistant's message
        }
    });

    // Handle clicking a tool button (event delegation)
    toolSelectionArea.addEventListener('click', async (e) => {
        if (e.target.tagName === 'BUTTON') {
            const toolName = e.target.dataset.toolName;
            const params = extractedParams[toolName];
            
            if (!params) {
                alert('Could not find parameters for this tool.');
                return;
            }

            try {
                const response = await fetch(`/call-tool/${toolName}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(params)
                });
                
                const result = await response.json();
                
                // Display the raw JSON response
                toolResponseBox.textContent = JSON.stringify(result, null, 2);
                toolResponseArea.style.display = 'block';

            } catch (error) {
                console.error('Error calling tool:', error);
                toolResponseBox.textContent = `Error: ${error.message}`;
                toolResponseArea.style.display = 'block';
            }
        }
    });

    // Handle clearing chat history
    clearChatBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear the entire conversation?')) {
            await fetch('/clear-chat', { method: 'POST' });
            renderMessages([]);
            toolSelectionArea.innerHTML = '';
            toolResponseArea.style.display = 'none';
        }
    });

    // --- Initial Load ---
    loadHistory();
});
