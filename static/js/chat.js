document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    const toolSelectionArea = document.getElementById('tool-selection-area');
    const toolResponseArea = document.getElementById('tool-response-area');
    const toolResponseBox = document.getElementById('tool-response-box');
    const loadingSpinner = document.querySelector('.loading-spinner');
    const stateDisplay = document.getElementById('state-display');
    let extractedParams = {};

    const renderMessages = (messages) => {
        chatBox.innerHTML = '';
        messages.forEach(msg => {
            const messageType = msg.role === 'user' ? 'user-message' : 'assistant-message';
            chatBox.innerHTML += `
                <div class="chat-message ${messageType}">
                    <div class="card d-inline-block">
                        <div class="card-body">${msg.content}</div>
                    </div>
                </div>`;
        });
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    const loadHistory = async () => {
        // FIX: Added { cache: 'no-store' } to prevent the browser from showing an old history
        const response = await fetch('/history', { cache: 'no-store' });
        renderMessages(await response.json());
    };

    const renderUserState = async () => {
        try {
            const response = await fetch('/state', { cache: 'no-store' });
            const state = await response.json();
            stateDisplay.innerHTML = `
                <span class="badge bg-secondary state-badge">Style: ${state.teaching_style}</span>
                <span class="badge bg-info text-dark state-badge">Emotion: ${state.emotional_state}</span>
                <span class="badge bg-success state-badge">Mastery: ${state.mastery_level.split(':')[0]}</span>`;
        } catch (error) { console.error('Error fetching user state:', error); }
    };

    const showLoading = (isLoading) => {
        loadingSpinner.style.display = isLoading ? 'block' : 'none';
        userInput.disabled = isLoading;
    };

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const messageText = userInput.value.trim();
        if (!messageText) return;
        showLoading(true);
        toolSelectionArea.innerHTML = '';
        toolResponseArea.style.display = 'none';
        const currentHistory = await (await fetch('/history', { cache: 'no-store' })).json();
        renderMessages([...currentHistory, { role: 'user', content: messageText }]);
        userInput.value = '';

        try {
            const formData = new FormData();
            formData.append('userInput', messageText);
            const response = await fetch('/chat', { method: 'POST', body: formData });
            if (!response.ok) throw new Error('Network response was not ok.');
            const result = await response.json();
            
            extractedParams = result.extractedParameters;
            if (result.clarification_question) {
                toolSelectionArea.innerHTML = '';
            } else if (result.classifiedTools && result.classifiedTools.length > 0) {
                result.classifiedTools.forEach(toolName => {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-outline-success m-1';
                    btn.textContent = `Call ${toolName.replace('Tool', '')}`;
                    btn.dataset.toolName = toolName;
                    toolSelectionArea.appendChild(btn);
                });
            } else {
                toolSelectionArea.innerHTML = '<p class="text-muted">No tools were identified for this request.</p>';
            }
        } catch (error) {
            console.error('Error during chat processing:', error);
            toolSelectionArea.innerHTML = '<p class="text-danger">An error occurred. Please try again.</p>';
        } finally {
            showLoading(false);
            await loadHistory();
            await renderUserState();
        }
    });

    toolSelectionArea.addEventListener('click', async (e) => {
        if (e.target.tagName === 'BUTTON') {
            const toolName = e.target.dataset.toolName;
            const params = extractedParams[toolName];
            if (!params) { alert('Could not find parameters for this tool.'); return; }
            try {
                const response = await fetch(`/call-tool/${toolName}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(params)
                });
                const result = await response.json();
                toolResponseBox.textContent = JSON.stringify(result, null, 2);
                toolResponseArea.style.display = 'block';
            } catch (error) {
                console.error('Error calling tool:', error);
                toolResponseBox.textContent = `Error: ${error.message}`;
                toolResponseArea.style.display = 'block';
            }
        }
    });

    clearChatBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear the entire conversation?')) {
            await fetch('/clear-chat', { method: 'POST' });
            renderMessages([]);
            toolSelectionArea.innerHTML = '';
            toolResponseArea.style.display = 'none';
        }
    });

    loadHistory();
    renderUserState();
});