const chat = document.getElementById('chat');
const form = document.getElementById('chat-form');
const input = document.getElementById('query');

// Generate a unique session ID for this browser session
const sessionId = 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();

function addMessage(text, isUser = false, source = null, type = '') {
    const div = document.createElement('div');
    div.className = `message ${isUser ? 'user' : 'bot'} ${type}`;
    div.textContent = text;

    if (source) {
        const sourceDiv = document.createElement('span');
        sourceDiv.className = 'source';
        sourceDiv.innerHTML = `Source: <a href="${source}" target="_blank">${source}</a>`;
        div.appendChild(sourceDiv);
    }

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

function askExample(btn) {
    input.value = btn.textContent;
    form.dispatchEvent(new Event('submit'));
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    addMessage(query, true);
    input.value = '';

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, session_id: sessionId }),
        });
        const data = await res.json();
        const type = data.type || '';
        const source = data.source || null;
        addMessage(data.answer || 'No answer returned.', false, source, type === 'refusal' ? 'refusal' : '');
    } catch (err) {
        addMessage('Sorry, something went wrong. Please try again.');
    }
});
