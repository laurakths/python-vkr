const translations = {
    ru: {
        siteTitle: "Пайтон-компас",
        contents: "Оглавление",
        getTask: "Получить задачу",
        task: "Задание",
        taskPlaceholder: 'Выберите тему и нажмите "Получить задачу"',
        editor: "Редактор кода",
        run: "Выполнить",
        check: "Проверить с ИИ",
        clear: "Очистить",
        inputTitle: "Ввод данных",
        outputTitle: "Вывод программы",
        result: "Результат",
        feedbackPlaceholder: "Здесь появится результат проверки",
        footer: "изучай Python и практикуйся!",
        footerText: "Пайтон-компас",
        generating: "Генерация...",
        checking: "Проверка...",
        running: "Выполнение...",
        enterCode: "Введите код перед проверкой",
        getTaskFirst: "Сначала получите задачу",
        error: "Ошибка. Попробуйте ещё раз.",
        noCodeRun: "Напишите код для выполнения",
        themeClassic: "Классическая",
        themeCosmic: "Космос",
        themeCandy: "Конфеты",
        themeCyber: "Киберпанк",
        themeCat: "Котики",
        userGreeting: "Привет, ",
        profile: "Личный кабинет",
        logout: "Выйти",
        about: "О разработчике"
    },
    en: {
        siteTitle: "PythonCompass",
        contents: "Contents",
        getTask: "Get Task",
        task: "Task",
        taskPlaceholder: 'Select a topic and click "Get Task"',
        editor: "Code Editor",
        run: "Run",
        check: "AI Check",
        clear: "Clear",
        inputTitle: "Input",
        outputTitle: "Program Output",
        result: "Result",
        feedbackPlaceholder: "The check result will appear here",
        footer: "learn Python and practice!",
        footerText: "PythonCompass",
        generating: "Generating...",
        checking: "Checking...",
        running: "Running...",
        enterCode: "Enter code before checking",
        getTaskFirst: "Get a task first",
        error: "Error. Try again.",
        noCodeRun: "Write code to run",
        themeClassic: "Classic",
        themeCosmic: "Cosmic",
        themeCandy: "Candy",
        themeCyber: "Cyberpunk",
        themeCat: "Cats",
        userGreeting: "Hello, ",
        profile: "Profile",
        logout: "Logout",
        about: "About"
    }
};

let currentTopic = null;
let currentTask = '';
let theoryData = {};
let currentLang = 'ru';
let currentTheme = 'default';
let currentUserName = '';

const elements = {
    chapterList: document.getElementById('chapter-list'),
    theoryContent: document.getElementById('theory-content'),
    taskText: document.getElementById('task-text'),
    codeEditor: document.getElementById('code-editor'),
    feedback: document.getElementById('feedback'),
    lineNumbers: document.getElementById('line-numbers'),
    getTaskBtn: document.getElementById('get-task-btn'),
    runCodeBtn: document.getElementById('run-code-btn'),
    checkBtn: document.getElementById('check-btn'),
    clearBtn: document.getElementById('clear-btn'),
    inputData: document.getElementById('input-data'),
    outputBlock: document.getElementById('output-block'),
    outputContent: document.getElementById('output-content'),
    langSelect: document.getElementById('lang-select'),
    themeSelect: document.getElementById('theme-select'),
    practicePanel: document.getElementById('practice-panel'),
    feedbackBlock: document.getElementById('feedback-block'),
    userInfo: document.getElementById('user-info'),
    userGreeting: document.getElementById('user-greeting'),
    btnProfile: document.getElementById('btn-profile'),
    btnLogout: document.getElementById('btn-logout')
};

async function checkAuth() {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    try {
        const response = await fetch('/api/user', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUserName = data.name;
            const t = translations[currentLang];
            elements.userInfo.style.display = 'flex';
            elements.userGreeting.textContent = t.userGreeting + currentUserName + '!';
            if (elements.btnProfile) elements.btnProfile.textContent = t.profile;
            if (elements.btnLogout) elements.btnLogout.textContent = t.logout;
        } else {
            localStorage.removeItem('authToken');
            window.location.href = '/login';
        }
    } catch (e) {
        window.location.href = '/login';
    }
} 

function init() {
    loadSettings();
    checkAuth().then(() => {
        loadTheory();
        setupEventListeners();
        updateLineNumbers();
    });
}

function loadSettings() {
    const savedLang = localStorage.getItem('lang') || 'ru';
    let savedTheme = localStorage.getItem('theme') || 'classic';
    if (!savedTheme || savedTheme === 'default') {
        savedTheme = 'classic';
    }
    
    currentLang = savedLang;
    currentTheme = savedTheme;
    
    elements.langSelect.value = savedLang;
    elements.themeSelect.value = savedTheme;
    
    applyTheme(savedTheme);
    applyLanguage(savedLang);
}

function applyTheme(theme) {
    if (!theme || theme === 'default') {
        theme = 'classic';
    }
    document.body.setAttribute('data-theme', theme);
    currentTheme = theme;
    localStorage.setItem('theme', theme);
}

function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    
    document.querySelectorAll('[data-lang-key]').forEach(el => {
        const key = el.getAttribute('data-lang-key');
        if (translations[lang] && translations[lang][key]) {
            el.textContent = translations[lang][key];
        }
    });
    
    if (currentUserName) {
        elements.userGreeting.textContent = translations[lang].userGreeting + currentUserName + '!';
    }
    
    const placeholder = lang === 'ru' 
        ? '# Напишите ваш код здесь\nprint("Hello, World!")'
        : '# Write your code here\nprint("Hello, World!")';
    elements.codeEditor.setAttribute('placeholder', placeholder);
    
    document.title = lang === 'ru' 
        ? 'Пайтон-компас — Изучай Python с нейросетью'
        : 'PythonCompass — Learn Python with AI';
    
    const t = translations[lang];
    const themeSelect = elements.themeSelect;
    themeSelect.options[0].text = t.themeClassic;
    themeSelect.options[1].text = t.themeCosmic;
    themeSelect.options[2].text = t.themeCandy;
    themeSelect.options[3].text = t.themeCyber;
    themeSelect.options[4].text = t.themeCat;
}

async function loadTheory() {
    const response = await fetch('/api/theory?lang=' + currentLang);
    theoryData = await response.json();
    const topics = theoryData.map(t => t.key);
    if (topics.length > 0 && currentTopic === null) {
        currentTopic = topics[0];
    }
    renderChapterList();
    renderTheory(currentTopic);
}

function renderChapterList() {
    elements.chapterList.innerHTML = '';
    
    theoryData.forEach((chapter) => {
        const li = document.createElement('li');
        const btn = document.createElement('button');
        btn.textContent = chapter.title;
        btn.dataset.topic = chapter.key;
        
        if (chapter.key === currentTopic) {
            btn.classList.add('active');
        }
        
        btn.addEventListener('click', () => {
            currentTopic = chapter.key;
            renderChapterList();
            renderTheory(chapter.key);
            clearTask();
        });
        
        li.appendChild(btn);
        elements.chapterList.appendChild(li);
    });
}

function renderTheory(topic) {
    const chapter = theoryData.find(t => t.key === topic);
    if (!chapter) return;
    
    if (chapter.content) {
        if (typeof marked !== 'undefined') {
            elements.theoryContent.innerHTML = marked.parse(chapter.content);
        } else {
            elements.theoryContent.innerHTML = '<pre style="white-space:pre-wrap">' + chapter.content.replace(/</g, '&lt;') + '</pre>';
        }
    } else {
        elements.theoryContent.innerHTML = '<p>No content available</p>';
    }
    
    document.querySelectorAll('#theory-content pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
    
    if (topic === 'fun') {
        elements.practicePanel.style.display = 'none';
        elements.getTaskBtn.style.display = 'none';
    } else {
        elements.practicePanel.style.display = '';
        elements.getTaskBtn.style.display = '';
    }
}

function clearTask() {
    const t = translations[currentLang];
    elements.taskText.innerHTML = '<p class="placeholder">' + t.taskPlaceholder + '</p>';
    elements.codeEditor.value = '';
    elements.inputData.value = '';
    elements.feedback.innerHTML = '<p class="placeholder">' + t.feedbackPlaceholder + '</p>';
    elements.feedback.className = 'feedback';
    elements.outputBlock.style.display = 'none';
    elements.outputContent.textContent = '';
    currentTask = '';
}

function setupEventListeners() {
    elements.getTaskBtn.addEventListener('click', generateTask);
    elements.runCodeBtn.addEventListener('click', runCode);
    elements.checkBtn.addEventListener('click', checkCode);
    elements.clearBtn.addEventListener('click', () => {
        elements.codeEditor.value = '';
        elements.inputData.value = '';
        elements.outputBlock.style.display = 'none';
        elements.outputContent.textContent = '';
        updateLineNumbers();
    });
    
    elements.codeEditor.addEventListener('input', updateLineNumbers);
    elements.codeEditor.addEventListener('scroll', syncScroll);
    elements.codeEditor.addEventListener('keydown', handleTab);
    
    elements.langSelect.addEventListener('change', (e) => {
        applyLanguage(e.target.value);
        loadTheory();
    });
    
    elements.themeSelect.addEventListener('change', (e) => {
        applyTheme(e.target.value);
    });
}

function updateLineNumbers() {
    const lines = elements.codeEditor.value.split('\n').length;
    let html = '';
    
    for (let i = 1; i <= Math.max(lines, 1); i++) {
        html += '<span>' + i + '</span>';
    }
    
    elements.lineNumbers.innerHTML = html;
}

function syncScroll() {
    elements.lineNumbers.scrollTop = elements.codeEditor.scrollTop;
}

function handleTab(e) {
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = elements.codeEditor.selectionStart;
        const end = elements.codeEditor.selectionEnd;
        
        elements.codeEditor.value = 
            elements.codeEditor.value.substring(0, start) + 
            '    ' + 
            elements.codeEditor.value.substring(end);
        
        elements.codeEditor.selectionStart = elements.codeEditor.selectionEnd = start + 4;
        updateLineNumbers();
    }
}

async function generateTask() {
    const t = translations[currentLang];
    
    elements.getTaskBtn.disabled = true;
    elements.getTaskBtn.innerHTML = '<span class="spinner"></span> ' + t.generating;
    elements.taskText.innerHTML = '<p class="placeholder">' + t.generating + '</p>';
    
    const response = await fetch('/api/generate_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            topic: currentTopic,
            lang: currentLang
        })
    });
    
    const data = await response.json();
    currentTask = data.task;
    
    elements.taskText.innerHTML = '<p>' + currentTask + '</p>';
    elements.feedback.innerHTML = '<p class="placeholder">' + t.feedbackPlaceholder + '</p>';
    elements.feedback.className = 'feedback';
    elements.outputBlock.style.display = 'none';
    elements.outputContent.textContent = '';
    
    elements.getTaskBtn.disabled = false;
    elements.getTaskBtn.innerHTML = '<span class="btn-icon">✨</span> <span data-lang-key="getTask">' + t.getTask + '</span>';
}

async function runCode() {
    const t = translations[currentLang];
    const code = elements.codeEditor.value.trim();
    
    if (!code) {
        elements.outputBlock.style.display = 'block';
        elements.outputContent.textContent = t.noCodeRun;
        elements.outputContent.className = 'output-content output-error';
        return;
    }
    
    elements.runCodeBtn.disabled = true;
    elements.runCodeBtn.innerHTML = '<span class="spinner"></span> ' + t.running;
    elements.outputBlock.style.display = 'block';
    elements.outputContent.textContent = t.running;
    
    let output = '';
    const originalLog = console.log;
    console.log = function(...args) {
        output += args.join(' ') + '\n';
        originalLog(...args);
    };
    
    try {
        const func = new Function(code);
        func();
        elements.outputContent.textContent = output || '(нет вывода)';
        elements.outputContent.className = 'output-content';
    } catch (error) {
        elements.outputContent.textContent = 'Ошибка: ' + error.message;
        elements.outputContent.className = 'output-content output-error';
    } finally {
        console.log = originalLog;
    }
    
    elements.runCodeBtn.disabled = false;
    elements.runCodeBtn.innerHTML = '<span class="btn-icon">▶</span> ' + t.run;
}  
    
 
async function checkCode() {
    const t = translations[currentLang];
    const code = elements.codeEditor.value.trim();
    
    if (!code) {
        elements.feedback.innerHTML = '<p class="placeholder">' + t.enterCode + '</p>';
        return;
    }
    
    if (!currentTask) {
        elements.feedback.innerHTML = '<p class="placeholder">' + t.getTaskFirst + '</p>';
        return;
    }
    
    elements.checkBtn.disabled = true;
    elements.checkBtn.innerHTML = '<span class="spinner"></span> ' + t.checking;
    elements.feedback.innerHTML = '<p class="placeholder">' + t.checking + '</p>';
    
    const response = await fetch('/api/check_code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            task: currentTask,
            code: code,
            lang: currentLang
        })
    });
    
    const data = await response.json();
    const feedback = data.feedback;
    
    if (feedback.includes('✅') || feedback.includes('✓') || feedback.toLowerCase().includes('correct') || feedback.toLowerCase().includes('great')) {
        elements.feedback.className = 'feedback success';
    } else {
        elements.feedback.className = 'feedback error';
    }
    
    elements.feedback.innerHTML = '<p>' + feedback + '</p>';
    
    elements.checkBtn.disabled = false;
    elements.checkBtn.innerHTML = '<span class="btn-icon">✓</span> ' + t.check;
}

document.addEventListener('DOMContentLoaded', init);
