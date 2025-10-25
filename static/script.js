document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analyze-form');
    const codeInput = document.getElementById('code-input');
    const dropdownButton = document.querySelector('.dropdown-container .button');
    const selectedLanguageDisplay = document.getElementById('selected-language-display');
    const languageOptionsContainer = document.getElementById('language-options-container');
    const apiKeyInput = document.getElementById('api-key-input');
    const analyzeButton = document.getElementById('analyze-button');
    const chatLog = document.getElementById('chat-log');
    const statusIndicator = document.getElementById('status-indicator');
    const emptyState = document.getElementById('empty-state');
    const newSessionButton = document.getElementById('new-session-button');
    const composerEditor = document.querySelector('.composer-editor');
    const themeSwitchInput = document.querySelector('.switch input[type="checkbox"]');
    const chatList = document.getElementById('chat-list');
    const chatListEmpty = document.getElementById('chat-list-empty');
    const authButton = document.getElementById('auth-button');
    const authOverlay = document.getElementById('auth-overlay');
    const authClose = document.getElementById('auth-close');
    const authTabs = document.querySelectorAll('[data-auth-tab]');
    const authForms = document.querySelectorAll('.auth-form');
    const loginForm = document.getElementById('auth-login-form');
    const signupForm = document.getElementById('auth-signup-form');
    const authFeedback = document.getElementById('auth-feedback');
    const authEmailDisplay = document.getElementById('auth-email-display');
    const authSignedInPane = document.getElementById('auth-signed-in');
    const authFormsPane = document.getElementById('auth-forms');
    const logoutButton = document.getElementById('logout-button');

    const themeStorageKey = 'codemind-ai:theme';
    const prefersDark = typeof window.matchMedia === 'function'
        ? window.matchMedia('(prefers-color-scheme: dark)')
        : null;

    const languageOptions = [
        { value: 'python', text: 'Python' },
        { value: 'javascript', text: 'JavaScript' },
        { value: 'html', text: 'HTML' },
        { value: 'css', text: 'CSS' },
        { value: 'java', text: 'Java' },
        { value: 'csharp', text: 'C#' },
        { value: 'go', text: 'Go' },
        { value: 'ruby', text: 'Ruby' },
        { value: 'php', text: 'PHP' },
        { value: 'typescript', text: 'TypeScript' },
        { value: 'json', text: 'JSON' },
        { value: 'xml', text: 'XML' },
        { value: 'markdown', text: 'Markdown' },
        { value: 'text', text: 'Plain Text' },
    ];

    const defaultButtonText = analyzeButton.textContent;
    const chatState = {
        chats: [],
        activeChatId: null,
        hasMessages: false,
    };

    const authState = {
        authenticated:
            (authOverlay?.dataset.authenticated === 'true') ||
            (authButton?.dataset.authenticated === 'true'),
        email: authOverlay?.dataset.email || authButton?.dataset.email || '',
    };

    initializeTheme();
    initializeLanguageDropdown();
    bootstrapChatStack();
    initializeAuth();

    form.addEventListener('submit', handleSubmit);
    codeInput.addEventListener('input', () => composerEditor.classList.remove('invalid'));
    newSessionButton?.addEventListener('click', handleNewSessionClick);

    function initializeTheme() {
        if (!themeSwitchInput) {
            return;
        }

        const storedTheme = localStorage.getItem(themeStorageKey);
        if (storedTheme === 'light' || storedTheme === 'dark') {
            applyTheme(storedTheme);
        } else {
            const systemPrefersDark = prefersDark ? prefersDark.matches : true;
            applyTheme(systemPrefersDark ? 'dark' : 'light', false);
        }

        themeSwitchInput.addEventListener('change', () => {
            const nextTheme = themeSwitchInput.checked ? 'dark' : 'light';
            applyTheme(nextTheme);
        });

        if (prefersDark) {
            const handleSystemThemeChange = (event) => {
                if (!localStorage.getItem(themeStorageKey)) {
                    applyTheme(event.matches ? 'dark' : 'light', false);
                }
            };

            if (typeof prefersDark.addEventListener === 'function') {
                prefersDark.addEventListener('change', handleSystemThemeChange);
            } else if (typeof prefersDark.addListener === 'function') {
                prefersDark.addListener(handleSystemThemeChange);
            }
        }
    }

    function applyTheme(theme, persist = true) {
        const normalized = theme === 'light' ? 'light' : 'dark';
        document.body.classList.toggle('light-theme', normalized === 'light');
        document.body.classList.toggle('dark-theme', normalized === 'dark');
        updateThemeToggle(normalized);

        if (persist) {
            localStorage.setItem(themeStorageKey, normalized);
        } else {
            localStorage.removeItem(themeStorageKey);
        }
    }

    function updateThemeToggle(theme) {
        if (!themeSwitchInput) {
            return;
        }

        const isDark = theme === 'dark';
        themeSwitchInput.checked = isDark;
    }

    function initializeAuth() {
        applyAuthState();

        authButton?.addEventListener('click', () => {
            toggleAuthOverlay(true);
        });

        authClose?.addEventListener('click', () => {
            toggleAuthOverlay(false);
        });

        authOverlay?.addEventListener('click', (event) => {
            if (event.target === authOverlay) {
                toggleAuthOverlay(false);
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && !authOverlay?.classList.contains('hidden')) {
                toggleAuthOverlay(false);
            }
        });

        authTabs.forEach((tab) => {
            tab.addEventListener('click', () => {
                const mode = tab.dataset.authTab;
                switchAuthTab(mode);
            });
        });

        loginForm?.addEventListener('submit', (event) => {
            handleAuthFormSubmit(event, '/auth/login');
        });

        signupForm?.addEventListener('submit', (event) => {
            handleAuthFormSubmit(event, '/auth/signup');
        });

        logoutButton?.addEventListener('click', handleLogout);
    }

    function applyAuthState() {
        const signedIn = Boolean(authState.authenticated && authState.email);

        if (authButton) {
            authButton.textContent = signedIn ? authState.email : 'Sign in';
            authButton.dataset.authenticated = signedIn ? 'true' : 'false';
            authButton.dataset.email = signedIn ? authState.email : '';
        }

        if (authFormsPane) {
            authFormsPane.classList.toggle('hidden', signedIn);
        }

        if (authSignedInPane) {
            authSignedInPane.classList.toggle('hidden', !signedIn);
        }

        if (authEmailDisplay) {
            authEmailDisplay.textContent = authState.email || '';
        }

        if (authOverlay) {
            authOverlay.dataset.authenticated = signedIn ? 'true' : 'false';
            authOverlay.dataset.email = signedIn ? authState.email : '';
        }

        if (chatListEmpty) {
            chatListEmpty.textContent = signedIn
                ? 'No chats yet. Start by creating a new review.'
                : 'Sign in to access your review history.';
        }

        if (!signedIn) {
            switchAuthTab('login');
        }
    }

    function toggleAuthOverlay(forceOpen) {
        if (!authOverlay) {
            return;
        }

        const shouldOpen = forceOpen === true || (forceOpen !== false && authOverlay.classList.contains('hidden'));

        if (shouldOpen) {
            resetAuthForms();
            authOverlay.classList.remove('hidden');
            requestAnimationFrame(() => authOverlay.classList.add('auth-overlay--visible'));
            authOverlay.setAttribute('aria-hidden', 'false');
            document.body.classList.add('auth-modal-open');
            if (authState.authenticated) {
                logoutButton?.focus({ preventScroll: true });
            } else {
                switchAuthTab('login');
                document.getElementById('auth-login-email')?.focus({ preventScroll: true });
            }
        } else {
            authOverlay.classList.add('hidden');
            authOverlay.classList.remove('auth-overlay--visible');
            authOverlay.setAttribute('aria-hidden', 'true');
            document.body.classList.remove('auth-modal-open');
            resetAuthForms();
        }
    }

    function switchAuthTab(mode) {
        if (!mode) {
            return;
        }

        authTabs.forEach((tab) => {
            const isActive = tab.dataset.authTab === mode;
            tab.classList.toggle('active', isActive);
            tab.setAttribute('aria-selected', String(isActive));
        });

        authForms.forEach((form) => {
            const isMatch = form.dataset.mode === mode;
            form.classList.toggle('hidden', !isMatch);
        });

        setAuthFeedback('');
    }

    function resetAuthForms() {
        loginForm?.reset();
        signupForm?.reset();
        setAuthFeedback('');
    }

    async function handleAuthFormSubmit(event, endpoint) {
        event.preventDefault();

        const form = event.target;
        if (!form) {
            return;
        }

        const emailInput = form.querySelector('input[name="email"]');
        const passwordInput = form.querySelector('input[name="password"]');
        const submitButton = form.querySelector('.auth-submit');

        const email = emailInput?.value.trim();
        const password = passwordInput?.value.trim();

        if (!email || !password) {
            setAuthFeedback('Email and password are required.');
            return;
        }

        submitButton?.setAttribute('disabled', 'true');
        setAuthFeedback('');

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            const payload = await response.json();

            if (!response.ok) {
                setAuthFeedback(payload?.error || 'Unable to complete the request.');
                return;
            }

            authState.authenticated = Boolean(payload?.authenticated);
            authState.email = payload?.email || email;
            applyAuthState();
            await bootstrapChatStack();
            toggleAuthOverlay(false);
        } catch (error) {
            console.error(error);
            setAuthFeedback('Something went wrong. Please try again.');
        } finally {
            submitButton?.removeAttribute('disabled');
        }
    }

    async function handleLogout() {
        if (!logoutButton) {
            return;
        }

        logoutButton.setAttribute('disabled', 'true');
        setAuthFeedback('');

        try {
            const response = await fetch('/auth/logout', { method: 'POST' });
            if (!response.ok) {
                throw new Error('Logout failed');
            }
            authState.authenticated = false;
            authState.email = '';
            applyAuthState();
            await bootstrapChatStack();
            toggleAuthOverlay(false);
        } catch (error) {
            console.error(error);
            setAuthFeedback('Unable to sign out. Please try again.');
        } finally {
            logoutButton.removeAttribute('disabled');
        }
    }

    function setAuthFeedback(message, tone = 'error') {
        if (!authFeedback) {
            return;
        }

        authFeedback.textContent = message || '';
        const hasMessage = Boolean(message);
        authFeedback.classList.toggle('hidden', !hasMessage);
        authFeedback.classList.toggle('auth-feedback--error', hasMessage && tone === 'error');
        authFeedback.classList.toggle('auth-feedback--success', hasMessage && tone === 'success');
    }

    function handleUnauthorized() {
        authState.authenticated = false;
        authState.email = '';
        applyAuthState();
        bootstrapChatStack();
        toggleAuthOverlay(true);
        setTimeout(() => setAuthFeedback('Please sign in to continue.'), 0);
    }

    function initializeLanguageDropdown() {
        if (!languageOptionsContainer || !selectedLanguageDisplay) {
            return;
        }

        languageOptionsContainer.innerHTML = '';

        languageOptions.forEach(option => {
            const row = document.createElement('div');
            row.className = 'row';
            row.textContent = option.text;
            row.dataset.value = option.value;
            row.addEventListener('click', () => {
                setLanguageSelection(option.value, option.text);
                document.body.classList.remove('expanded');
            });
            languageOptionsContainer.appendChild(row);
        });

        const initial = languageOptions[0];
        setLanguageSelection(initial.value, initial.text);

        document.addEventListener('click', (event) => {
            if (!dropdownButton.contains(event.target) && !languageOptionsContainer.contains(event.target)) {
                document.body.classList.remove('expanded');
            }
        });
    }

    function setLanguageSelection(value, text) {
        selectedLanguageDisplay.textContent = text;
        selectedLanguageDisplay.dataset.value = value;
    }

    async function bootstrapChatStack() {
        if (!authState.authenticated) {
            chatState.chats = [];
            chatState.activeChatId = null;
            chatState.hasMessages = false;
            renderChatList();
            if (emptyState) {
                emptyState.classList.remove('hidden');
                chatLog.innerHTML = '';
                chatLog.appendChild(emptyState);
            }
            return;
        }

        await refreshChats();
        if (!chatState.chats.length) {
            const chat = await createChat();
            if (chat) {
                chatState.chats = [chat];
            }
        }
        if (chatState.chats.length) {
            await setActiveChat(chatState.chats[0].id);
        }
    }

    async function refreshChats() {
        try {
            const response = await fetch('/api/chats');
            if (response.status === 401) {
                handleUnauthorized();
                return;
            }
            if (!response.ok) {
                throw new Error('Failed to load chats');
            }
            const payload = await response.json();
            chatState.chats = Array.isArray(payload.data) ? payload.data : [];
            renderChatList();
        } catch (error) {
            console.error(error);
        }
    }

    function renderChatList() {
        if (!chatList) {
            return;
        }

        chatList.innerHTML = '';
        if (!chatState.chats.length) {
            chatListEmpty?.classList.remove('hidden');
            return;
        }
        chatListEmpty?.classList.add('hidden');

        chatState.chats.forEach((chat) => {
            const item = document.createElement('button');
            item.type = 'button';
            item.className = 'chat-list-item';
            item.dataset.chatId = chat.id;
            item.setAttribute('role', 'option');

            const title = document.createElement('span');
            title.className = 'chat-list-title';
            title.textContent = chat.title || 'Untitled review';

            const preview = document.createElement('span');
            preview.className = 'chat-list-preview';
            preview.textContent = truncateText(chat.last_message_preview || '', 80);

            const meta = document.createElement('span');
            meta.className = 'chat-list-meta';
            meta.textContent = formatRelativeTime(chat.updated_at);

            item.appendChild(title);
            item.appendChild(preview);
            item.appendChild(meta);

            item.addEventListener('click', () => setActiveChat(chat.id));

            chatList.appendChild(item);
        });

        highlightActiveChat();
    }

    function highlightActiveChat() {
        const items = chatList?.querySelectorAll('.chat-list-item') || [];
        items.forEach((item) => {
            const isActive = item.dataset.chatId === chatState.activeChatId;
            item.classList.toggle('active', isActive);
            if (isActive) {
                item.setAttribute('aria-selected', 'true');
            } else {
                item.removeAttribute('aria-selected');
            }
        });
    }

    async function setActiveChat(chatId) {
        if (!chatId || chatState.activeChatId === chatId) {
            chatState.activeChatId = chatId;
            highlightActiveChat();
            return;
        }

        chatState.activeChatId = chatId;
        highlightActiveChat();
        await loadChat(chatId);
    }

    async function loadChat(chatId, { scroll = true } = {}) {
        try {
            const response = await fetch(`/api/chats/${chatId}`);
            if (response.status === 401) {
                handleUnauthorized();
                return;
            }
            if (!response.ok) {
                throw new Error('Unable to load chat');
            }
            const payload = await response.json();
            renderHistory(payload.messages || []);
            const language = payload.chat?.language;
            if (language) {
                const option = languageOptions.find((item) => item.value === language);
                if (option) {
                    setLanguageSelection(option.value, option.text);
                } else {
                    setLanguageSelection(language, language.toUpperCase());
                }
            }
            if (scroll) {
                scrollToBottom();
            }
        } catch (error) {
            console.error(error);
        }
    }

    function renderHistory(messages) {
        chatLog.innerHTML = '';
        if (!messages.length) {
            chatState.hasMessages = false;
            if (emptyState) {
                emptyState.classList.remove('hidden');
                chatLog.appendChild(emptyState);
            }
            return;
        }

        chatState.hasMessages = true;
        hideEmptyState();

        messages.forEach((message) => appendMessageFromRecord(message));
    }

    function appendMessageFromRecord(record) {
        const role = record.role === 'assistant' ? 'assistant' : 'user';
        const meta = role === 'user'
            ? (record.language ? record.language.toUpperCase() : 'You')
            : 'CodeMind AI';
        const element = createMessageElement(role, meta);
        const contentEl = element.querySelector('.message-content');

        if (role === 'user') {
            const parts = [];
            if (record.display_content) {
                parts.push(`<pre>${escapeHtml(record.display_content)}</pre>`);
            }
            if (record.code_diff) {
                parts.push(`
                    <details class="diff-block" open>
                        <summary>Changes since previous snippet</summary>
                        <pre><code>${escapeHtml(record.code_diff)}</code></pre>
                    </details>
                `);
            }
            contentEl.innerHTML = parts.join('').trim() || '<p>(empty)</p>';
        } else {
            const text = record.display_content || record.content;
            contentEl.innerHTML = renderMarkdown(text);
        }

        return element;
    }

    function createMessageElement(role, metaText) {
        const wrapper = document.createElement('article');
        wrapper.className = `message ${role}`;
        const metaMarkup = metaText ? `<div class="message-meta">${escapeHtml(metaText)}</div>` : '';
        wrapper.innerHTML = `
            <div class="message-avatar">${role === 'user' ? 'You' : 'AI'}</div>
            <div class="message-bubble">
                ${metaMarkup}
                <div class="message-content"></div>
            </div>
        `;
        chatLog.appendChild(wrapper);
        return wrapper;
    }

    async function handleNewSessionClick() {
        if (!authState.authenticated) {
            toggleAuthOverlay(true);
            setTimeout(() => setAuthFeedback('Please sign in to start a new review.'), 0);
            return;
        }

        const language = selectedLanguageDisplay.dataset.value;
        const chat = await createChat(language);
        if (!chat) {
            return;
        }
        chatState.chats.unshift(chat);
        renderChatList();
        await setActiveChat(chat.id);
        resetComposer();
        codeInput.focus();
    }

    function resetComposer() {
        codeInput.value = '';
        apiKeyInput.value = '';
        composerEditor.classList.remove('invalid');
        chatState.hasMessages = false;
        if (emptyState) {
            emptyState.classList.remove('hidden');
            chatLog.innerHTML = '';
            chatLog.appendChild(emptyState);
        }
    }

    async function handleSubmit(event) {
        event.preventDefault();

        if (!authState.authenticated) {
            toggleAuthOverlay(true);
            setTimeout(() => setAuthFeedback('Please sign in to analyze your code.'), 0);
            return;
        }

        const code = codeInput.value.trim();
        const languageText = selectedLanguageDisplay.textContent;
        const languageValue = selectedLanguageDisplay.dataset.value;
        const apiKey = apiKeyInput.value.trim();

        if (!code) {
            composerEditor.classList.add('invalid');
            codeInput.focus();
            return;
        }

        if (!chatState.activeChatId) {
            const chat = await createChat(languageValue);
            if (!chat) {
                return;
            }
            chatState.chats.unshift(chat);
            renderChatList();
            chatState.activeChatId = chat.id;
            highlightActiveChat();
        }

        composerEditor.classList.remove('invalid');

        const userMessage = createMessageElement('user', languageText.toUpperCase());
        const userContent = userMessage.querySelector('.message-content');
        userContent.innerHTML = `<pre>${escapeHtml(code)}</pre>`;

        const assistantMessage = createMessageElement('assistant', 'CodeMind AI');
        const assistantContent = assistantMessage.querySelector('.message-content');
        assistantContent.innerHTML = '<p><em>Thinking through your code&hellip;</em></p>';

        chatState.hasMessages = true;
        hideEmptyState();
        scrollToBottom();

        statusIndicator.classList.remove('hidden');
        analyzeButton.disabled = true;
        analyzeButton.textContent = 'Reviewing...';
        const originalButtonText = defaultButtonText;

        try {
            const response = await fetch(`/api/chats/${chatState.activeChatId}/messages`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, language: languageValue, api_key: apiKey }),
            });

            if (response.status === 401) {
                handleUnauthorized();
                return;
            }

            if (!response.ok) {
                const errorData = await safeJson(response);
                const message = errorData?.error || 'Unexpected error while analyzing your code.';
                assistantContent.innerHTML = renderMarkdown(`**Error:** ${message}`);
                return;
            }

            const reader = response.body?.getReader();
            if (!reader) {
                assistantContent.innerHTML = renderMarkdown('**Error:** Unable to read the response stream.');
                return;
            }

            const decoder = new TextDecoder();
            let accumulatedText = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                accumulatedText += decoder.decode(value, { stream: true });
                assistantContent.innerHTML = renderMarkdown(accumulatedText);
                scrollToBottom();
            }

            const finalChunk = decoder.decode();
            if (finalChunk) {
                accumulatedText += finalChunk;
                assistantContent.innerHTML = renderMarkdown(accumulatedText);
            }

            await refreshChats();
            await loadChat(chatState.activeChatId, { scroll: true });
        } catch (error) {
            assistantContent.innerHTML = renderMarkdown(`**Network error:** ${error.message}`);
        } finally {
            statusIndicator.classList.add('hidden');
            analyzeButton.disabled = false;
            analyzeButton.textContent = originalButtonText;
            codeInput.value = '';
            codeInput.focus();
        }
    }

    function hideEmptyState() {
        if (chatState.hasMessages && emptyState && !emptyState.classList.contains('hidden')) {
            emptyState.classList.add('hidden');
        }
    }

    function scrollToBottom() {
        requestAnimationFrame(() => {
            chatLog.scrollTop = chatLog.scrollHeight;
        });
    }

    async function createChat(language) {
        try {
            const response = await fetch('/api/chats', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language }),
            });
            if (response.status === 401) {
                handleUnauthorized();
                return null;
            }
            if (!response.ok) {
                throw new Error('Failed to create chat');
            }
            const payload = await response.json();
            return payload.chat;
        } catch (error) {
            console.error(error);
            return null;
        }
    }

    async function safeJson(response) {
        try {
            return await response.json();
        } catch (error) {
            return null;
        }
    }

    function formatRelativeTime(value) {
        if (!value) {
            return '';
        }
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) {
            return '';
        }
        const deltaSeconds = Math.floor((Date.now() - date.getTime()) / 1000);
        if (deltaSeconds < 60) {
            return 'Just now';
        }
        if (deltaSeconds < 3600) {
            const minutes = Math.floor(deltaSeconds / 60);
            return `${minutes}m ago`;
        }
        if (deltaSeconds < 86400) {
            const hours = Math.floor(deltaSeconds / 3600);
            return `${hours}h ago`;
        }
        const days = Math.floor(deltaSeconds / 86400);
        return `${days}d ago`;
    }

    function truncateText(text, length) {
        if (!text) {
            return '';
        }
        if (text.length <= length) {
            return text;
        }
        const safeLength = Math.max(0, length - 3);
        return `${text.slice(0, safeLength)}...`;
    }

    function renderMarkdown(text) {
        if (!text) {
            return '';
        }

        const segments = [];
        const fenceRegex = /```([\s\S]*?)```/g;
        let lastIndex = 0;
        let match;

        while ((match = fenceRegex.exec(text)) !== null) {
            if (match.index > lastIndex) {
                segments.push({ type: 'text', value: text.slice(lastIndex, match.index) });
            }

            segments.push({ type: 'code', value: match[1] });
            lastIndex = fenceRegex.lastIndex;
        }

        if (lastIndex < text.length) {
            segments.push({ type: 'text', value: text.slice(lastIndex) });
        }

        return segments.map((segment) => {
            if (segment.type === 'code') {
                return `<pre><code>${escapeHtml(segment.value.trim())}</code></pre>`;
            }

            return textToHtml(segment.value);
        }).join('').trim();
    }

    function textToHtml(value) {
        const trimmed = value.replace(/^[\n\r]+|[\n\r]+$/g, '');
        if (!trimmed) {
            return '';
        }

        const paragraphs = trimmed.split(/\n{2,}/).map((para) => {
            const lines = para.split(/\n/).filter((line) => line.trim() !== '');
            const isList = lines.length > 0 && lines.every((line) => /^\s*-\s/.test(line));
            const escaped = escapeHtml(para);
            const bold = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            const inlineCode = bold.replace(/`([^`]+)`/g, '<code>$1</code>');

            if (isList) {
                const listItems = lines.map((item) => {
                    const cleaned = item.replace(/^\s*-\s/, '');
                    const escapedItem = escapeHtml(cleaned)
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/`([^`]+)`/g, '<code>$1</code>');
                    return `<li>${escapedItem}</li>`;
                }).join('');
                return `<ul>${listItems}</ul>`;
            }

            return `<p>${inlineCode.replace(/\n/g, '<br>')}</p>`;
        });

        return paragraphs.join('');
    }

    function escapeHtml(value) {
        return value
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
});
