const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

let conversationHistory = [];

// Lightweight markdown renderer for the AI's responses
function renderMarkdown(text) {
    // Security: escape raw HTML first
    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Headers (## and ###)
    html = html.replace(/^### (.+)$/gm, '<strong style="font-size:1.05em;">$1</strong>');
    html = html.replace(/^## (.+)$/gm, '<strong style="font-size:1.1em;color:#c7f284;">$1</strong>');

    // Bold **text**
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Italic *text* (but not tool indicators with ⚙️ *)
    html = html.replace(/(?<!\⚙️ )\*([^*\n]+?)\*/g, '<em>$1</em>');

    // Inline code `code`
    html = html.replace(/`([^`]+)`/g, '<code style="background:rgba(199,242,132,0.12);color:#c7f284;padding:2px 6px;border-radius:4px;font-family:monospace;font-size:0.9em;">$1</code>');

    // Links [text](url)
    html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g,
        '<a href="$2" target="_blank" style="color:#c7f284;text-decoration:underline;">$1</a>');

    // Bare URLs (not already in an anchor)
    html = html.replace(/(?<!href="|">)(https?:\/\/[^\s<>"]+)/g,
        '<a href="$1" target="_blank" style="color:#c7f284;text-decoration:underline;">$1</a>');

    // Bullet points - item
    html = html.replace(/^- (.+)$/gm, '• $1');

    // Newlines to <br>
    html = html.replace(/\n/g, '<br>');

    return html;
}

function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-msg`;
    if (sender === 'bot') {
        const contentDiv = document.createElement('div');
        contentDiv.innerHTML = renderMarkdown(text);
        msgDiv.appendChild(contentDiv);
    } else {
        const pre = document.createElement('pre');
        pre.textContent = text;
        msgDiv.appendChild(pre);
    }
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-msg typing';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = '<span></span><span></span><span></span>';
    chatHistory.appendChild(typingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function removeTyping() {
    const typingDiv = document.getElementById('typing-indicator');
    if (typingDiv) typingDiv.remove();
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    userInput.value = '';
    conversationHistory.push({ role: 'user', content: text });
    showTyping();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, history: conversationHistory.slice(0, -1) })
        });

        removeTyping();

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            addMessage("Error: " + (data.error || "Failed to communicate with the Agent."), 'bot');
            return;
        }

        // Create live streaming bot message bubble
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-msg';
        const contentDiv = document.createElement('div');
        contentDiv.innerHTML = '';
        msgDiv.appendChild(contentDiv);
        chatHistory.appendChild(msgDiv);

        // Stream chunks, accumulate raw text, re-render markdown each chunk
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let fullBotResponse = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunkText = decoder.decode(value, { stream: true });
            fullBotResponse += chunkText;
            // Re-render the full accumulated text as markdown on each chunk
            contentDiv.innerHTML = renderMarkdown(fullBotResponse);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }

        conversationHistory.push({ role: 'assistant', content: fullBotResponse });

    } catch (err) {
        removeTyping();
        addMessage("Connection error while talking to server.", 'bot');
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Guide Panel interactions
document.querySelectorAll('.code-block').forEach(block => {
    block.addEventListener('click', () => {
        userInput.value = block.textContent.trim();
        userInput.focus();
    });
});
