document.addEventListener('DOMContentLoaded', () => {
    const userSelect = document.getElementById('demo-user-select');
    const sessionPreview = document.getElementById('session-preview');
    const triggerBtn = document.getElementById('trigger-n8n-btn');
    const triggerStatus = document.getElementById('trigger-status');
    const testResultPreview = document.getElementById('test-result-preview');
    const viewTestBtn = document.getElementById('view-test-btn');

    const step2 = document.getElementById('step-2');
    const step3 = document.getElementById('step-3');

    const API_BASE = ''; // Same origin

    // 1. Load users
    async function loadUsers() {
        try {
            const res = await fetch(`${API_BASE}/api/users`);
            const json = await res.json();

            userSelect.innerHTML = '<option value="">-- Choose a student --</option>';
            json.data.forEach(user => {
                const opt = document.createElement('option');
                opt.value = user.id;
                opt.textContent = `${user.name} (${user.email})`;
                userSelect.appendChild(opt);
            });
        } catch (err) {
            console.error('Failed to load users', err);
        }
    }

    // 2. Load session context for selected user
    userSelect.addEventListener('change', async () => {
        const userId = userSelect.value;
        if (!userId) {
            sessionPreview.classList.add('hidden');
            triggerBtn.disabled = true;
            step2.style.opacity = '0.5';
            return;
        }

        try {
            sessionPreview.classList.remove('hidden');
            sessionPreview.innerHTML = '<i>Extracting sessions...</i>';

            const res = await fetch(`${API_BASE}/api/sessions?userId=${userId}&days=7`);
            const json = await res.json();

            sessionPreview.innerHTML = `<h4>Weekly Context for ${json.userName}</h4>` +
                `<pre>${JSON.stringify(json.context, null, 2)}</pre>`;

            triggerBtn.disabled = false;
            step2.classList.add('active');
            step2.style.opacity = '1';
        } catch (err) {
            sessionPreview.innerHTML = `<span style="color:var(--danger)">Error: ${err.message}</span>`;
        }
    });

    // 3. Trigger n8n Webhook
    triggerBtn.addEventListener('click', async () => {
        triggerBtn.disabled = true;
        const statusDot = triggerStatus.querySelector('.status-dot');
        const statusText = triggerStatus.querySelector('span:last-child');

        statusDot.className = 'status-dot status-active';
        statusText.textContent = 'Triggering n8n workflow...';

        try {
            // Note: In a real demo, we'd trigger the webhook.
            // Since n8n is local, we call the test webhook.
            const res = await fetch('http://localhost:5678/webhook-test/trigger-weekly-test', {
                method: 'POST'
            });

            if (res.ok) {
                statusDot.className = 'status-dot status-success';
                statusText.textContent = 'Success! AI is generating the test...';

                // Poll for the new test
                startPolling(userSelect.value);
            } else {
                throw new Error('Webhook failed. Is n8n running and in "Execute" mode?');
            }
        } catch (err) {
            statusDot.className = 'status-dot status-error';
            statusText.textContent = err.message;
            triggerBtn.disabled = false;
        }
    });

    // 4. Poll for results
    async function startPolling(userId) {
        step3.classList.add('active');
        step3.style.opacity = '1';
        testResultPreview.classList.remove('hidden');
        testResultPreview.innerHTML = '<i>Waiting for AI to save test to database... (Polling every 3s)</i>';

        const poll = setInterval(async () => {
            try {
                const res = await fetch(`${API_BASE}/api/tests/${userId}`);
                const json = await res.json();

                if (json.data) {
                    clearInterval(poll);
                    testResultPreview.innerHTML = `<h4>✅ AI Generated Test Found!</h4>` +
                        `<pre>${JSON.stringify(json.data, null, 2)}</pre>`;

                    viewTestBtn.disabled = false;
                    viewTestBtn.onclick = () => {
                        window.location.href = `index.html?userId=${userId}`;
                    };
                }
            } catch (err) {
                console.error('Polling error', err);
            }
        }, 3000);

        // Timeout after 60s
        setTimeout(() => clearInterval(poll), 60000);
    }

    loadUsers();
});
