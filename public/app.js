// ── Application State ────────────────────────────────
let currentUser = null;
let activeTest = null;
let userAnswers = {};
let timerInterval = null;

// ── DOM Elements ─────────────────────────────────────
const userSelect = document.getElementById('user-select');
const welcomeScreen = document.getElementById('welcome-screen');
const testScreen = document.getElementById('test-screen');
const resultScreen = document.getElementById('result-screen');
const testAvailable = document.getElementById('test-available');
const noTestMessage = document.getElementById('no-test-message');
const loading = document.getElementById('loading');
const questionsContainer = document.getElementById('questions-container');
const progressBar = document.getElementById('progress-bar');
const timerDisplay = document.getElementById('test-timer');
const timerLarge = document.getElementById('test-timer-large');

// ── Initialization ────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    fetchUsers();

    userSelect.addEventListener('change', (e) => {
        const userId = e.target.value;
        if (userId) {
            loadUserData(userId);
        } else {
            resetDashboard();
        }
    });

    document.getElementById('start-test-btn').addEventListener('click', startTest);
    document.getElementById('submit-test-btn').addEventListener('click', submitTest);
});

// ── Fetch Users ───────────────────────────────────────
async function fetchUsers() {
    try {
        const res = await fetch('/api/users');
        const { data } = await res.json();

        userSelect.innerHTML = '<option value="">Select a user...</option>';
        data.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = user.name;
            userSelect.appendChild(option);
        });
    } catch (err) {
        console.error('Failed to fetch users:', err);
    }
}

// ── Load User Data ────────────────────────────────────
async function loadUserData(userId) {
    loading.classList.remove('hidden');
    testAvailable.classList.add('hidden');
    noTestMessage.classList.add('hidden');

    try {
        const res = await fetch(`/api/tests/${userId}`);
        const { data } = await res.json();

        loading.classList.add('hidden');

        if (data && !data.isExpired) {
            activeTest = data;
            document.getElementById('test-title').textContent = data.title;
            document.getElementById('q-count').textContent = `${data.total_questions || data.questions.length} Questions`;
            testAvailable.classList.remove('hidden');
            startTimer(data.expires_at, [timerDisplay, timerLarge]);
        } else {
            noTestMessage.classList.remove('hidden');
        }
    } catch (err) {
        console.error('Failed to load user test:', err);
    }
}

// ── Test Logic ────────────────────────────────────────
function startTest() {
    welcomeScreen.classList.remove('active');
    testScreen.classList.add('active');
    document.getElementById('active-test-title').textContent = activeTest.title;

    renderQuestions();
    updateProgress();
    window.scrollTo(0, 0);
}

function renderQuestions() {
    questionsContainer.innerHTML = '';
    activeTest.questions.forEach((q, index) => {
        const card = document.createElement('div');
        card.className = 'question-card';
        card.id = `q-${index}`;

        let optionsHtml = '';
        if (q.type === 'mcq') {
            optionsHtml = `
                <div class="options-grid">
                    ${q.options.map((opt, i) => `
                        <button class="option-btn" onclick="selectOption(${index}, '${opt.charAt(0)}')">
                            ${opt}
                        </button>
                    `).join('')}
                </div>
            `;
        } else {
            optionsHtml = `
                <textarea placeholder="Type your answer here..." oninput="saveTextAnswer(${index}, this.value)"></textarea>
            `;
        }

        card.innerHTML = `
            <div class="question-meta">
                <span class="tag">Question ${index + 1}</span>
                <span class="tag">${q.topic}</span>
                <span class="tag">${q.difficulty}</span>
            </div>
            <div class="question-text">${q.question}</div>
            ${optionsHtml}
        `;
        questionsContainer.appendChild(card);
    });
}

function selectOption(qIndex, choice) {
    userAnswers[qIndex] = choice;

    // UI update
    const card = document.getElementById(`q-${qIndex}`);
    const buttons = card.querySelectorAll('.option-btn');
    buttons.forEach(btn => {
        btn.classList.remove('selected');
        if (btn.textContent.trim().startsWith(choice)) {
            btn.classList.add('selected');
        }
    });

    updateProgress();
}

function saveTextAnswer(qIndex, text) {
    userAnswers[qIndex] = text;
    updateProgress();
}

function updateProgress() {
    const total = activeTest.questions.length;
    const answered = Object.keys(userAnswers).length;
    const percent = (answered / total) * 100;
    progressBar.style.width = `${percent}%`;
}

// ── Timer Logic ───────────────────────────────────────
function startTimer(expiresAt, displays) {
    if (timerInterval) clearInterval(timerInterval);

    const expiryDate = new Date(expiresAt).getTime();

    const update = () => {
        const now = new Date().getTime();
        const distance = expiryDate - now;

        if (distance < 0) {
            clearInterval(timerInterval);
            displays.forEach(d => d.textContent = "EXPIRED");
            alert("Your 6-hour time limit has expired!");
            location.reload();
            return;
        }

        const hours = Math.floor(distance / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        const timeStr = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        displays.forEach(d => d.textContent = timeStr);
    };

    update();
    timerInterval = setInterval(update, 1000);
}

// ── Submission ────────────────────────────────────────
async function submitTest() {
    const total = activeTest.questions.length;
    const answered = Object.keys(userAnswers).length;

    if (answered < total) {
        if (!confirm(`You have only answered ${answered} out of ${total} questions. Submit anyway?`)) {
            return;
        }
    }

    try {
        const res = await fetch(`/api/tests/${activeTest.id}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: userAnswers })
        });

        const { data } = await res.json();
        showResults(data);
    } catch (err) {
        console.error('Submission failed:', err);
        alert('Failed to submit test. Please try again.');
    }
}

function showResults(data) {
    testScreen.classList.remove('active');
    resultScreen.classList.add('active');

    document.getElementById('final-score').textContent = `${data.percentage}%`;
    document.getElementById('correct-count').textContent = data.score;
    document.getElementById('total-count').textContent = data.totalQuestions;

    // Animate score circle
    const circle = document.getElementById('score-progress');
    const radius = 60;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (data.percentage / 100) * circumference;
    circle.style.strokeDashoffset = offset;

    // Render feedback
    const feedbackContainer = document.getElementById('feedback-container');
    feedbackContainer.innerHTML = data.results.map((r, i) => `
        <div class="info-card" style="border-left: 4px solid ${r.isCorrect ? '#22c55e' : '#ef4444'}">
            <h4>Q${i + 1}: ${r.isCorrect ? '✅ Correct' : '❌ Incorrect'}</h4>
            <p><strong>Your Answer:</strong> ${r.yourAnswer || 'None'}</p>
            <p><strong>Correct Answer:</strong> ${r.correctAnswer}</p>
        </div>
    `).join('');

    window.scrollTo(0, 0);
}

function resetDashboard() {
    testAvailable.classList.add('hidden');
    noTestMessage.classList.add('hidden');
    welcomeScreen.classList.add('active');
    testScreen.classList.remove('active');
    resultScreen.classList.remove('active');
}
