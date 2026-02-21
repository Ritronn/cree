// ============================================================
// Weekly Test Generator — Backend API Server
// Express.js + SQLite backend for the n8n automation workflow
// ============================================================
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const Database = require('better-sqlite3');
const { v4: uuidv4 } = require('uuid');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const TEST_EXPIRY_HOURS = parseInt(process.env.TEST_EXPIRY_HOURS || '6', 10);

// ── Middleware ──────────────────────────────────────────
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// ── Database Connection ────────────────────────────────
const DB_PATH = path.join(__dirname, 'data', 'weekly_tests.db');
let db;

try {
    db = new Database(DB_PATH);
    db.pragma('journal_mode = WAL');
    console.log('✅ Connected to SQLite database');
} catch (err) {
    console.error('❌ Database connection failed. Run "npm run seed" first!');
    console.error(err.message);
    process.exit(1);
}

// ── Helper: Auto-expire old tests ──────────────────────
function expireOldTests() {
    const now = new Date().toISOString();
    db.prepare(`
    UPDATE tests SET status = 'expired' 
    WHERE status = 'active' AND expires_at < ?
  `).run(now);
}

// ════════════════════════════════════════════════════════
//  API ROUTES
// ════════════════════════════════════════════════════════

// ── GET /api/users ─────────────────────────────────────
// Returns all registered users
app.get('/api/users', (req, res) => {
    try {
        const users = db.prepare('SELECT * FROM users ORDER BY name').all();
        res.json({
            success: true,
            count: users.length,
            data: users,
        });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// ── GET /api/sessions ──────────────────────────────────
// Query params: userId (required), days (default: 7)
// Returns sessions for a user within the past N days
app.get('/api/sessions', (req, res) => {
    try {
        const { userId, days = 7 } = req.query;

        if (!userId) {
            return res.status(400).json({
                success: false,
                error: 'userId query parameter is required',
            });
        }

        // Calculate the date N days ago
        const sinceDate = new Date();
        sinceDate.setDate(sinceDate.getDate() - parseInt(days, 10));

        const sessions = db.prepare(`
      SELECT s.*, u.name as user_name, u.email as user_email
      FROM sessions s
      JOIN users u ON s.user_id = u.id
      WHERE s.user_id = ? AND s.created_at >= ?
      ORDER BY s.created_at DESC
    `).all(userId, sinceDate.toISOString());

        // Build aggregated context from all sessions
        const context = {
            topics: sessions.map(s => s.topic),
            allKeyConcepts: [...new Set(sessions.flatMap(s => s.key_concepts.split(', ')))],
            totalDuration: sessions.reduce((sum, s) => sum + s.duration_minutes, 0),
            summaries: sessions.map(s => `[${s.topic}]: ${s.summary}`).join('\n\n'),
        };

        res.json({
            success: true,
            userId,
            userName: sessions[0]?.user_name || 'Unknown',
            userEmail: sessions[0]?.user_email || '',
            sessionCount: sessions.length,
            context,
            data: sessions,
        });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// ── GET /api/sessions/all-users ────────────────────────
// Returns sessions grouped by user for the past N days
// Used by the n8n workflow to batch-fetch all data
app.get('/api/sessions/all-users', (req, res) => {
    try {
        const { days = 7 } = req.query;
        const sinceDate = new Date();
        sinceDate.setDate(sinceDate.getDate() - parseInt(days, 10));

        const users = db.prepare('SELECT * FROM users ORDER BY name').all();
        const result = [];

        for (const user of users) {
            const sessions = db.prepare(`
        SELECT * FROM sessions
        WHERE user_id = ? AND created_at >= ?
        ORDER BY created_at DESC
      `).all(user.id, sinceDate.toISOString());

            if (sessions.length > 0) {
                const context = {
                    topics: sessions.map(s => s.topic),
                    allKeyConcepts: [...new Set(sessions.flatMap(s => s.key_concepts.split(', ')))],
                    totalDuration: sessions.reduce((sum, s) => sum + s.duration_minutes, 0),
                    summaries: sessions.map(s => `[${s.topic}]: ${s.summary}`).join('\n\n'),
                };

                result.push({
                    userId: user.id,
                    userName: user.name,
                    userEmail: user.email,
                    sessionCount: sessions.length,
                    context,
                    sessions,
                });
            }
        }

        res.json({
            success: true,
            totalUsers: result.length,
            data: result,
        });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// ── POST /api/tests ────────────────────────────────────
// Create a new weekly test for a user
// Body: { userId, title, questions (array), totalQuestions }
app.post('/api/tests', (req, res) => {
    try {
        const { userId, title, questions, totalQuestions } = req.body;

        if (!userId || !title || !questions) {
            return res.status(400).json({
                success: false,
                error: 'userId, title, and questions are required',
            });
        }

        // Calculate expiry time (6 hours from now)
        const now = new Date();
        const expiresAt = new Date(now.getTime() + TEST_EXPIRY_HOURS * 60 * 60 * 1000);

        const testId = uuidv4();
        const questionsJson = typeof questions === 'string' ? questions : JSON.stringify(questions);

        db.prepare(`
      INSERT INTO tests (id, user_id, title, questions, total_questions, created_at, expires_at, status)
      VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
    `).run(
            testId,
            userId,
            title,
            questionsJson,
            totalQuestions || (Array.isArray(questions) ? questions.length : 0),
            now.toISOString(),
            expiresAt.toISOString()
        );

        res.status(201).json({
            success: true,
            message: 'Test created successfully',
            data: {
                id: testId,
                userId,
                title,
                totalQuestions: totalQuestions || (Array.isArray(questions) ? questions.length : 0),
                createdAt: now.toISOString(),
                expiresAt: expiresAt.toISOString(),
                expiresInHours: TEST_EXPIRY_HOURS,
                status: 'active',
            },
        });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// ── GET /api/tests/:userId ─────────────────────────────
// Get the active (non-expired) test for a user
app.get('/api/tests/:userId', (req, res) => {
    try {
        expireOldTests(); // Auto-expire before querying

        const { userId } = req.params;
        const test = db.prepare(`
      SELECT * FROM tests
      WHERE user_id = ? AND status = 'active'
      ORDER BY created_at DESC
      LIMIT 1
    `).get(userId);

        if (!test) {
            return res.json({
                success: true,
                message: 'No active test found for this user',
                data: null,
            });
        }

        // Calculate remaining time
        const now = new Date();
        const expiresAt = new Date(test.expires_at);
        const remainingMs = expiresAt - now;
        const remainingMinutes = Math.max(0, Math.floor(remainingMs / 60000));

        res.json({
            success: true,
            data: {
                ...test,
                questions: JSON.parse(test.questions),
                remainingMinutes,
                isExpired: remainingMs <= 0,
            },
        });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// ── GET /api/tests ─────────────────────────────────────
// Get all tests (with optional status filter)
app.get('/api/tests', (req, res) => {
    try {
        expireOldTests();

        const { status } = req.query;
        let query = 'SELECT t.*, u.name as user_name FROM tests t JOIN users u ON t.user_id = u.id';
        const params = [];

        if (status) {
            query += ' WHERE t.status = ?';
            params.push(status);
        }

        query += ' ORDER BY t.created_at DESC';

        const tests = db.prepare(query).all(...params);

        res.json({
            success: true,
            count: tests.length,
            data: tests.map(t => ({
                ...t,
                questions: JSON.parse(t.questions),
            })),
        });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// ── POST /api/tests/:testId/submit ─────────────────────
// Submit test answers and get score
app.post('/api/tests/:testId/submit', (req, res) => {
    try {
        expireOldTests();

        const { testId } = req.params;
        const { answers } = req.body;

        const test = db.prepare('SELECT * FROM tests WHERE id = ?').get(testId);

        if (!test) {
            return res.status(404).json({ success: false, error: 'Test not found' });
        }

        if (test.status === 'expired') {
            return res.status(410).json({
                success: false,
                error: 'This test has expired. It was only valid for 6 hours after creation.',
            });
        }

        const questions = JSON.parse(test.questions);
        let score = 0;
        const results = [];

        for (let i = 0; i < questions.length; i++) {
            const q = questions[i];
            const userAnswer = answers?.[i] || '';
            const isCorrect = userAnswer.toString().toLowerCase().trim() === (q.correct_answer || q.correctAnswer || '').toString().toLowerCase().trim();

            if (isCorrect) score++;

            results.push({
                question: q.question,
                yourAnswer: userAnswer,
                correctAnswer: q.correct_answer || q.correctAnswer,
                isCorrect,
            });
        }

        // Mark test as completed
        db.prepare(`UPDATE tests SET status = 'completed' WHERE id = ?`).run(testId);

        res.json({
            success: true,
            data: {
                testId,
                score,
                totalQuestions: questions.length,
                percentage: Math.round((score / questions.length) * 100),
                results,
            },
        });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// ── GET /api/health ────────────────────────────────────
app.get('/api/health', (req, res) => {
    res.json({
        success: true,
        service: 'Weekly Test Generator API',
        timestamp: new Date().toISOString(),
        testExpiryHours: TEST_EXPIRY_HOURS,
    });
});

// ── GET /api/test/trigger ──────────────────────────────
// Helper to provide the trigger command
app.get('/api/test/trigger', (req, res) => {
    res.json({
        success: true,
        message: 'To trigger the n8n workflow manually, run the following command in your terminal:',
        curlCommand: 'curl -X POST http://localhost:5678/webhook-test/trigger-weekly-test',
        note: 'Ensure your n8n workflow is active and listening for this webhook.'
    });
});

// ── Start Server ───────────────────────────────────────
app.listen(PORT, () => {
    console.log(`
╔══════════════════════════════════════════════════╗
║   📝 Weekly Test Generator API                   ║
║   🌐 Running on http://localhost:${PORT}            ║
║   ⏰ Test expiry: ${TEST_EXPIRY_HOURS} hours                       ║
╚══════════════════════════════════════════════════╝

Available Endpoints:
  GET    /api/health              → Health check
  GET    /api/users               → List all users
  GET    /api/sessions?userId=X   → Get user sessions (past 7 days)
  GET    /api/sessions/all-users  → Get all users' sessions
  POST   /api/tests               → Create a new test
  GET    /api/tests/:userId       → Get active test for user
  GET    /api/tests               → List all tests
  POST   /api/tests/:id/submit    → Submit test answers
  `);
});
