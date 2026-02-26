/**
 * SCIENCEMENTOR - Chat Interface JavaScript
 * With subject-gated sessions
 */

// Configuration
const API_BASE_URL = 'http://localhost:5001';
const STORAGE_KEY = 'sciencementor_current_session';

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const questionInput = document.getElementById('questionInput');
const sendButton = document.getElementById('sendButton');
const loadingIndicator = document.getElementById('loading');
const newChatButton = document.getElementById('newChatButton');
const chatHistory = document.getElementById('chatHistory');
const welcomeScreen = document.getElementById('welcomeScreen');
const fileUpload = document.getElementById('fileUpload');
const filePreview = document.getElementById('filePreview');
const fileName = document.getElementById('fileName');
const fileRemove = document.getElementById('fileRemove');

// Subject UI
const subjectModal = document.getElementById('subjectModal');
const subjectBadge = document.getElementById('subjectBadge');
const changeSubjectBtn = document.getElementById('changeSubjectBtn');
const subjectCards = document.querySelectorAll('.subject-card');

// State
let currentSessionId = null;
let sessions = [];
let uploadedFile = null;
let uploadedFileContent = null;
let selectedSubject = null; // 'Biology', 'Physics', 'Chemistry'

/**
 * Initialize the application
 */
async function init() {
    // Load existing sessions
    await loadSessions();

    // Try to restore previous session
    const savedSessionId = localStorage.getItem(STORAGE_KEY);

    if (savedSessionId && sessions.some(s => s.id === savedSessionId)) {
        // Restore previous session
        await loadSession(savedSessionId);
    } else {
        // If no active session, wait for user to start new chat -> which triggers subject modal
        // Or if we want to force subject selection immediately:
        // showSubjectModal();
        // But better to show "New Chat" empty state? 
        // Actually, the requirement says "On new session creation, the user must select a subject".
        // So we can show the welcome screen, but disable interaction?
        // OR better: Just show the welcome screen generic, and prompt modal when they try to chat or click New Chat.
        // Let's force modal on "New Chat" click, and if they type in the box without a session.
    }

    // Set up event listeners
    sendButton.addEventListener('click', handleSend);
    questionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    questionInput.addEventListener('input', autoResizeTextarea);
    newChatButton.addEventListener('click', () => showSubjectModal());
    changeSubjectBtn.addEventListener('click', () => showSubjectModal());

    // Subject Selection
    subjectCards.forEach(card => {
        card.addEventListener('click', (e) => {
            const subject = card.dataset.subject;
            handleSubjectSelect(subject);
        });
    });

    // File upload handling
    if (fileUpload) {
        fileUpload.addEventListener('change', handleFileSelect);
    }
    if (fileRemove) {
        fileRemove.addEventListener('click', removeFile);
    }

    // Topic card clicks
    document.querySelectorAll('.topic-card').forEach(card => {
        card.addEventListener('click', () => {
            const topic = card.dataset.topic;
            if (topic) {
                // If no session, logic in handleSend will handle it?
                // Actually need to ensure subject is selected.
                if (!currentSessionId && !selectedSubject) {
                    // Start logic for this topic
                    // Use a heuristic or ask modal?
                    // Let's ask modal, then autofill the question.
                    pendingQuestion = topic;
                    showSubjectModal();
                    return;
                }
                questionInput.value = topic;
                handleSend();
            }
        });
    });

    questionInput.focus();
}

// Temporary storage for question if modal interrupts
let pendingQuestion = "";

/**
 * Show Subject Selection Modal
 */
function showSubjectModal() {
    subjectModal.classList.add('active');
}

/**
 * Hide Subject Selection Modal
 */
function hideSubjectModal() {
    subjectModal.classList.remove('active');
}

/**
 * Handle Subject Selection
 */
async function handleSubjectSelect(subject) {
    selectedSubject = subject;
    hideSubjectModal();

    // Create a new session with this subject
    await createNewSession(subject);

    // If there was a pending question (from topic card), send it
    if (pendingQuestion) {
        questionInput.value = pendingQuestion;
        pendingQuestion = "";
        handleSend();
    }
}

/**
 * Update UI for specific subject
 */
function setSubjectMode(subject) {
    if (!subjectBadge) return;

    selectedSubject = subject;
    subjectBadge.style.display = 'flex';
    subjectBadge.className = `subject-badge ${subject.toLowerCase()}`;
    subjectBadge.querySelector('.subject-name').textContent = `${subject} Mode`;

    // Optional: Update welcome screen topics strictly for this subject?
    // For now, keeping generic welcome screen but could filter it.
}

/**
 * Auto-resize textarea
 */
function autoResizeTextarea() {
    questionInput.style.height = 'auto';
    questionInput.style.height = Math.min(questionInput.scrollHeight, 200) + 'px';
}

/**
 * Handle file selection
 */
async function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['text/plain', 'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword'];
    const allowedExtensions = ['.txt', '.pdf', '.docx', '.doc'];
    const extension = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedExtensions.includes(extension)) {
        alert('Please upload a .txt, .pdf, or .docx file');
        fileUpload.value = '';
        return;
    }

    uploadedFile = file;

    // Read file content for text files
    if (file.type === 'text/plain' || extension === '.txt') {
        const reader = new FileReader();
        reader.onload = (event) => {
            uploadedFileContent = event.target.result;
            showFilePreview(file.name);
        };
        reader.readAsText(file);
    } else {
        // For PDF and DOCX, we'll send to backend for processing
        uploadedFileContent = null; // Will be processed server-side
        showFilePreview(file.name);
    }
}

/**
 * Show file preview
 */
function showFilePreview(name) {
    fileName.textContent = name;
    filePreview.style.display = 'flex';
}

/**
 * Remove selected file
 */
function removeFile() {
    uploadedFile = null;
    uploadedFileContent = null;
    fileUpload.value = '';
    filePreview.style.display = 'none';
}

/**
 * Load sessions from backend
 */
async function loadSessions() {
    try {
        const response = await fetch(`${API_BASE_URL}/sessions`);
        if (response.ok) {
            const data = await response.json();
            sessions = data.sessions || [];
            renderChatHistory();
        }
    } catch (error) {
        console.warn('Could not load sessions:', error.message);
    }
}

/**
 * Render chat history sidebar
 */
function renderChatHistory() {
    const title = document.createElement('div');
    title.className = 'history-section-title';
    title.textContent = 'Recent Chats';

    chatHistory.innerHTML = '';
    chatHistory.appendChild(title);

    if (sessions.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'history-empty';
        empty.style.cssText = 'padding: 1rem; color: var(--text-muted); font-size: 0.8rem; text-align: center;';
        empty.textContent = 'No chats yet';
        chatHistory.appendChild(empty);
        return;
    }

    sessions.slice(0, 30).forEach(session => {
        const item = document.createElement('div');
        item.className = 'history-item' + (session.id === currentSessionId ? ' active' : '');
        item.dataset.sessionId = session.id;

        // Use title if available, otherwise show "New Chat"
        const displayText = session.title || 'New Chat';

        // Subject indicator (small dot or text?)
        // Assuming session.metadata is available from list_sessions update
        let subject = '';
        if (session.metadata) {
            // Check if it's a string (needs parsing) or already an object
            if (typeof session.metadata === 'string') {
                try {
                    const meta = JSON.parse(session.metadata);
                    subject = meta.subject;
                } catch (e) {
                    console.warn('Failed to parse metadata', e);
                }
            } else if (typeof session.metadata === 'object') {
                subject = session.metadata.subject;
            }
        }

        const subjectHtml = subject ?
            `<span style="margin-left:auto; font-size:0.7em; padding:2px 6px; border-radius:4px; background:rgba(255,255,255,0.1);">${subject.substring(0, 3)}</span>` : '';

        item.innerHTML = `
            <div class="history-item-left" style="flex:1">
                <svg class="history-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
                </svg>
                <span class="history-item-text">${escapeHtml(displayText)}</span>
                ${subjectHtml}
            </div>
            <button class="history-item-delete" title="Delete chat" data-session-id="${session.id}">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                </svg>
            </button>
        `;

        // Click to load session
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.history-item-delete')) {
                loadSession(session.id);
            }
        });

        // Delete button
        const deleteBtn = item.querySelector('.history-item-delete');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteSession(session.id);
        });

        chatHistory.appendChild(item);
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Load a session
 */
async function loadSession(sessionId) {
    currentSessionId = sessionId;
    localStorage.setItem(STORAGE_KEY, sessionId);

    // Update sidebar
    document.querySelectorAll('.history-item').forEach(item => {
        item.classList.toggle('active', item.dataset.sessionId === sessionId);
    });

    // Retrieve subject from sessions list
    const session = sessions.find(s => s.id === sessionId);
    if (session) {
        let subject = null;
        if (session.metadata) {
            if (typeof session.metadata === 'string') {
                try {
                    const meta = JSON.parse(session.metadata);
                    subject = meta.subject;
                } catch (e) { }
            } else {
                subject = session.metadata.subject;
            }
        }
        if (subject) {
            setSubjectMode(subject);
        } else {
            // Legacy session or no subject
            if (subjectBadge) subjectBadge.style.display = 'none';
        }
    }

    // Load messages
    try {
        const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/messages`);
        if (response.ok) {
            const data = await response.json();

            if (!data.messages || data.messages.length === 0) {
                showWelcomeScreen();
            } else {
                hideWelcomeScreen();
                chatMessages.innerHTML = '';
                // Ensure messages are sorted appropriately if needed, but backend sends chrono order
                data.messages.forEach(msg => {
                    // Safety check for content
                    if (msg.content) {
                        addMessage(msg.content, msg.role === 'user' ? 'user' : 'bot', false);
                    }
                });
                scrollToBottom();
            }
        } else {
            console.error('Failed to fetch messages:', response.status);
        }
    } catch (error) {
        console.error('Failed to load session:', error);
    }
}

/**
 * Create new session
 */
async function createNewSession(subject) {
    try {
        const body = subject ? JSON.stringify({ subject }) : "{}";

        const response = await fetch(`${API_BASE_URL}/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: body
        });

        if (response.ok) {
            const data = await response.json();
            currentSessionId = data.session_id;
            localStorage.setItem(STORAGE_KEY, currentSessionId);

            // Set mode
            if (subject) {
                setSubjectMode(subject);
            }

            sessions.unshift({
                id: currentSessionId,
                created_at: new Date().toISOString(),
                metadata: { subject }
            });
            renderChatHistory();
            showWelcomeScreen();
        }
    } catch (error) {
        console.warn('Could not create session:', error.message);
    }

    questionInput.focus();
}

/**
 * Delete a session
 */
async function deleteSession(sessionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            sessions = sessions.filter(s => s.id !== sessionId);

            if (currentSessionId === sessionId) {
                if (sessions.length > 0) {
                    await loadSession(sessions[0].id);
                } else {
                    currentSessionId = null;
                    localStorage.removeItem(STORAGE_KEY);
                    showWelcomeScreen();
                    if (subjectBadge) subjectBadge.style.display = 'none';
                }
            }

            renderChatHistory();
        }
    } catch (error) {
        console.error('Failed to delete session:', error);
    }
}

/**
 * Show welcome screen
 */
function showWelcomeScreen() {
    chatMessages.innerHTML = '';
    const welcome = document.createElement('div');
    welcome.className = 'welcome-screen';
    welcome.id = 'welcomeScreen';
    welcome.innerHTML = `
        <div class="welcome-logo">SM</div>
        <h1 class="welcome-title">Welcome to SCIENCEMENTOR</h1>
        <p class="welcome-subtitle">Your personal Science tutor for Malaysian students</p>
        
        <div class="topic-grid">
            <!-- Biology -->
            <div class="topic-card" data-topic="What is mitosis?">
                <div class="topic-icon biology">🧬</div>
                <span>Cell Division</span>
            </div>
            <div class="topic-card" data-topic="Explain photosynthesis">
                <div class="topic-icon biology">🌱</div>
                <span>Photosynthesis</span>
            </div>
            <!-- Physics -->
            <div class="topic-card" data-topic="Explain Newton's three laws of motion">
                <div class="topic-icon physics">⚡</div>
                <span>Newton's Laws</span>
            </div>
            <div class="topic-card" data-topic="How do electric circuits work?">
                <div class="topic-icon physics">🔌</div>
                <span>Electricity</span>
            </div>
            <!-- Chemistry -->
            <div class="topic-card" data-topic="What is covalent bonding?">
                <div class="topic-icon chemistry">🧪</div>
                <span>Chemical Bonding</span>
            </div>
            <div class="topic-card" data-topic="Explain acids and bases">
                <div class="topic-icon chemistry">⚗️</div>
                <span>Acids & Bases</span>
            </div>
        </div>
    `;
    chatMessages.appendChild(welcome);

    // Rebind topic card clicks
    welcome.querySelectorAll('.topic-card').forEach(card => {
        card.addEventListener('click', () => {
            const topic = card.dataset.topic;
            if (topic) {
                // Check if session exists
                if (!currentSessionId) {
                    pendingQuestion = topic;
                    showSubjectModal();
                    return;
                }
                questionInput.value = topic;
                handleSend();
            }
        });
    });
}

/**
 * Hide welcome screen
 */
function hideWelcomeScreen() {
    const welcome = document.getElementById('welcomeScreen');
    if (welcome) welcome.remove();
}

/**
 * Handle send
 */
async function handleSend() {
    const question = questionInput.value.trim();
    if (!question && !uploadedFile) return;

    // Create session if none exists
    const isNewSession = !currentSessionId;
    if (isNewSession) {
        // If no session, we MUST force subject selection
        showSubjectModal();
        pendingQuestion = question;
        return;
    }

    hideWelcomeScreen();

    // Build the message to display
    let displayMessage = question;
    if (uploadedFile) {
        displayMessage = question ? `📎 ${uploadedFile.name}\n\n${question}` : `📎 ${uploadedFile.name}`;
    }
    addMessage(displayMessage, 'user');

    questionInput.value = '';
    questionInput.style.height = 'auto';

    setLoading(true);

    try {
        // Create bot message container for streaming
        const botMessage = createEmptyBotMessage();

        // Prepare the question with file content if available
        let fullQuestion = question;
        if (uploadedFileContent) {
            fullQuestion = `[File content from ${uploadedFile.name}]:\n${uploadedFileContent}\n\n[Question/Request]: ${question || 'Please analyze and explain the content above.'}`;
        } else if (uploadedFile) {
            // For non-text files, we need to send to backend for processing
            // For now, just note that a file was attached
            fullQuestion = `[Attached file: ${uploadedFile.name}] ${question || 'Please help me with this file.'}`;
        }

        // Use streaming API
        await askQuestionStream(fullQuestion, botMessage);

        // Clear file after sending
        removeFile();

        // Update session in list - set title from first question
        const session = sessions.find(s => s.id === currentSessionId);
        if (session) {
            if (!session.title) {
                session.title = question.substring(0, 50) || uploadedFile?.name || 'New Chat';
            }
            session.updated_at = new Date().toISOString();
            sessions.sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at));
            renderChatHistory();
        }
    } catch (error) {
        addMessage(`Sorry, I encountered an error: ${error.message}. Please try again.`, 'bot');
    } finally {
        setLoading(false);
        questionInput.focus();
    }
}

/**
 * Create empty bot message for streaming
 */
function createEmptyBotMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'SM';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<p></p>';

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();

    return contentDiv;
}

/**
 * Ask question with streaming response
 */
async function askQuestionStream(question, messageContainer) {
    const isGuided = document.getElementById('guidedModeToggle')?.checked || false;

    const body = {
        question,
        guided_mode: isGuided
    };
    if (currentSessionId) body.session_id = currentSessionId;

    const response = await fetch(`${API_BASE_URL}/ask/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to get response');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullText = '';

    // Add visual indicator if guided (optional)
    if (isGuided && messageContainer.parentElement) {
        // Maybe add a small icon? For now, the text style is enough.
    }

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const data = JSON.parse(line.slice(6));
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    if (data.text) {
                        fullText += data.text;
                        messageContainer.innerHTML = formatMessage(fullText);
                        scrollToBottom();
                    }
                } catch (e) {
                    if (e instanceof SyntaxError) continue; // Skip malformed JSON
                    throw e;
                }
            }
        }
    }

    return fullText;
}

/**
 * Ask question API (non-streaming fallback)
 */
async function askQuestion(question) {
    const isGuided = document.getElementById('guidedModeToggle')?.checked || false;

    const body = {
        question,
        guided_mode: isGuided
    };
    if (currentSessionId) body.session_id = currentSessionId;

    const response = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Failed to get response');

    return data;
}

/**
 * Add message to chat
 */
function addMessage(content, type, animate = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    if (!animate) {
        messageDiv.style.animation = 'none';
        messageDiv.style.opacity = '1';
    }

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? 'U' : 'SM';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessage(content);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    scrollToBottom();
}

/**
 * Format message using marked.js
 */
function formatMessage(content) {
    if (!content) return '';

    // Fallback if marked is not loaded
    if (typeof marked === 'undefined') {
        console.warn('Marked.js not loaded, using plain text');
        const div = document.createElement('div');
        div.textContent = content;
        return div.innerHTML.replace(/\n/g, '<br>');
    }

    // Configure marked options
    try {
        marked.setOptions({
            highlight: function (code, lang) {
                if (lang && typeof hljs !== 'undefined' && hljs.getLanguage(lang)) {
                    return hljs.highlight(code, { language: lang }).value;
                }
                if (typeof hljs !== 'undefined') {
                    return hljs.highlightAuto(code).value;
                }
                return code;
            },
            breaks: true,
            gfm: true
        });
        return marked.parse(content);
    } catch (e) {
        console.error('Markdown parsing error:', e);
        // Fallback to plain text safe html
        const div = document.createElement('div');
        div.textContent = content;
        return div.innerHTML.replace(/\n/g, '<br>');
    }
}

/**
 * Scroll to bottom
 */
function scrollToBottom() {
    const container = document.getElementById('chatContainer');
    container.scrollTop = container.scrollHeight;
}

/**
 * Set loading state
 */
function setLoading(isLoading) {
    loadingIndicator.classList.toggle('visible', isLoading);
    sendButton.disabled = isLoading;
    questionInput.disabled = isLoading;
    scrollToBottom();
}

// Initialize
document.addEventListener('DOMContentLoaded', init);

// ==========================================
// QUIZ MODE
// ==========================================

/**
 * Quiz State
 */
let quizState = {
    questions: [],
    currentIndex: 0,
    score: 0,
    selectedAnswer: null,
    answered: false
};

/**
 * Initialize Quiz Mode listeners (called after DOM ready)
 */
function initQuizListeners() {
    const startQuizBtn = document.getElementById('startQuizBtn');
    const quizNextBtn = document.getElementById('quizNextBtn');
    const quizExitBtn = document.getElementById('quizExitBtn');

    if (startQuizBtn) {
        startQuizBtn.addEventListener('click', startQuiz);
    }
    if (quizNextBtn) {
        quizNextBtn.addEventListener('click', nextQuestion);
    }
    if (quizExitBtn) {
        quizExitBtn.addEventListener('click', exitQuiz);
    }
}

// Call after DOMContentLoaded
document.addEventListener('DOMContentLoaded', initQuizListeners);

/**
 * Start Quiz
 */
async function startQuiz() {
    if (!currentSessionId) {
        showSubjectModal();
        return;
    }

    // Show loading state
    const startBtn = document.getElementById('startQuizBtn');
    const originalText = startBtn.innerHTML;
    startBtn.innerHTML = `
        <svg class="spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" stroke-dasharray="31.4" stroke-dashoffset="10"/>
        </svg>
        Generating Quiz...
    `;
    startBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/quiz/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                difficulty: 'medium'
            })
        });

        const data = await response.json();
        if (!response.ok) {
            alert(data.error || 'Failed to start quiz');
            startBtn.innerHTML = originalText;
            startBtn.disabled = false;
            return;
        }

        // Initialize quiz state
        quizState = {
            questions: [],
            currentIndex: data.index || 0,
            score: 0,
            selectedAnswer: null,
            answered: false
        };

        // Show quiz UI, hide chat
        document.getElementById('chatContainer').style.display = 'none';
        document.getElementById('quizContainer').style.display = 'block';
        document.querySelector('.input-area').style.display = 'none';

        // Render first question
        renderQuestion(data);

    } catch (error) {
        console.error('Quiz start error:', error);
        alert('Failed to start quiz: ' + error.message);
    } finally {
        // Reset button
        startBtn.innerHTML = originalText;
        startBtn.disabled = false;
    }
}

/**
 * Render Quiz Question
 */
function renderQuestion(data) {
    document.getElementById('qIndex').textContent = (data.index || 0) + 1;
    document.getElementById('qTotal').textContent = data.total || 5;
    document.getElementById('qScore').textContent = quizState.score;
    document.getElementById('qText').textContent = data.question;

    const optionsGrid = document.getElementById('qOptions');
    optionsGrid.innerHTML = '';

    (data.options || []).forEach((option, idx) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.textContent = option;
        btn.dataset.index = idx;
        btn.addEventListener('click', () => selectOption(idx, btn));
        optionsGrid.appendChild(btn);
    });

    // Reset state
    quizState.selectedAnswer = null;
    quizState.answered = false;
    document.getElementById('qFeedback').style.display = 'none';
    document.getElementById('quizNextBtn').style.display = 'none';
}

/**
 * Select Option
 */
function selectOption(idx, btn) {
    if (quizState.answered) return;

    // Clear previous selection
    document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));

    // Mark selected
    btn.classList.add('selected');
    quizState.selectedAnswer = idx;

    // Auto-submit after selection
    submitAnswer();
}

/**
 * Submit Answer
 */
async function submitAnswer() {
    if (quizState.selectedAnswer === null || quizState.answered) return;

    try {
        const response = await fetch(`${API_BASE_URL}/quiz/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                answer_index: quizState.selectedAnswer
            })
        });

        const data = await response.json();
        if (!response.ok) {
            alert(data.error || 'Failed to submit answer');
            return;
        }

        quizState.answered = true;
        quizState.score = data.score || quizState.score;

        // Update score display
        document.getElementById('qScore').textContent = quizState.score;

        // Show feedback
        const feedbackDiv = document.getElementById('qFeedback');
        const feedbackStatus = document.getElementById('feedbackStatus');
        const feedbackText = document.getElementById('feedbackText');

        if (data.correct) {
            feedbackDiv.className = 'quiz-feedback correct';
            feedbackStatus.textContent = '✓ Correct!';
        } else {
            feedbackDiv.className = 'quiz-feedback incorrect';
            feedbackStatus.textContent = '✗ Incorrect';
        }
        feedbackText.textContent = data.explanation || '';
        feedbackDiv.style.display = 'block';

        // Mark options
        document.querySelectorAll('.option-btn').forEach((btn, idx) => {
            btn.disabled = true;
            if (idx === data.correct_index) {
                btn.classList.add('correct');
            } else if (idx === quizState.selectedAnswer && !data.correct) {
                btn.classList.add('incorrect');
            }
        });

        // Show next button
        document.getElementById('quizNextBtn').style.display = 'inline-block';

    } catch (error) {
        console.error('Submit error:', error);
        alert('Failed to submit answer: ' + error.message);
    }
}

/**
 * Next Question
 */
async function nextQuestion() {
    try {
        const response = await fetch(`${API_BASE_URL}/quiz/next`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId
            })
        });

        const data = await response.json();
        if (!response.ok) {
            alert(data.error || 'Failed to get next question');
            return;
        }

        if (data.completed) {
            showQuizSummary(data);
        } else {
            quizState.currentIndex = data.index;
            renderQuestion(data);
        }

    } catch (error) {
        console.error('Next question error:', error);
        alert('Failed to get next question: ' + error.message);
    }
}

/**
 * Show Quiz Summary
 */
function showQuizSummary(data) {
    const quizCard = document.querySelector('.quiz-card');
    const total = data.total || 5;
    const score = data.score || quizState.score;
    const percentage = Math.round((score / total) * 100);

    let grade = '';
    if (percentage >= 80) grade = '🌟 Excellent!';
    else if (percentage >= 60) grade = '👍 Good Job!';
    else if (percentage >= 40) grade = '📚 Keep Practicing';
    else grade = '💪 Don\'t Give Up!';

    quizCard.innerHTML = `
        <div style="text-align: center; padding: 40px 20px;">
            <h2 style="font-size: 2rem; margin-bottom: 16px;">Quiz Complete!</h2>
            <div style="font-size: 3rem; margin: 24px 0;">${grade}</div>
            <p style="font-size: 1.5rem; color: var(--primary-light); margin-bottom: 8px;">
                Score: ${score}/${total}
            </p>
            <p style="color: var(--text-secondary); margin-bottom: 32px;">
                ${percentage}% correct
            </p>
            <button class="btn-primary" onclick="exitQuiz()" style="padding: 16px 32px; font-size: 1rem;">
                Back to Chat
            </button>
        </div>
    `;
}

/**
 * Exit Quiz
 */
function exitQuiz() {
    // Hide quiz, show chat
    document.getElementById('quizContainer').style.display = 'none';
    document.getElementById('chatContainer').style.display = 'block';
    document.querySelector('.input-area').style.display = 'block';

    // Reset quiz state
    quizState = {
        questions: [],
        currentIndex: 0,
        score: 0,
        selectedAnswer: null,
        answered: false
    };
}

