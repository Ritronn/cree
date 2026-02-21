// ============================================
// Database Seed Script
// Creates tables and populates with sample data
// ============================================
const Database = require('better-sqlite3');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const DB_PATH = path.join(__dirname, '..', 'data', 'weekly_tests.db');

// Ensure data directory exists
const fs = require('fs');
const dataDir = path.join(__dirname, '..', 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

const db = new Database(DB_PATH);

// Enable WAL mode for better performance
db.pragma('journal_mode = WAL');

console.log('🗄️  Creating database tables...\n');

// ── Create Tables ──────────────────────────────────────
db.exec(`
  DROP TABLE IF EXISTS tests;
  DROP TABLE IF EXISTS sessions;
  DROP TABLE IF EXISTS users;

  CREATE TABLE users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
  );

  CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    summary TEXT NOT NULL,
    key_concepts TEXT NOT NULL,
    notes TEXT,
    duration_minutes INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
  );

  CREATE TABLE tests (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    questions TEXT NOT NULL,
    total_questions INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users(id)
  );

  CREATE INDEX idx_sessions_user_id ON sessions(user_id);
  CREATE INDEX idx_sessions_created_at ON sessions(created_at);
  CREATE INDEX idx_tests_user_id ON tests(user_id);
  CREATE INDEX idx_tests_expires_at ON tests(expires_at);
  CREATE INDEX idx_tests_status ON tests(status);
`);

console.log('✅ Tables created successfully!\n');

// ── Seed Users ─────────────────────────────────────────
const users = [
  { id: uuidv4(), name: 'Kushan Patil', email: 'kushan@example.com' },
  { id: uuidv4(), name: 'Arjun Sharma', email: 'arjun@example.com' },
  { id: uuidv4(), name: 'Sneha Desai', email: 'sneha@example.com' },
];

const insertUser = db.prepare(`
  INSERT INTO users (id, name, email) VALUES (@id, @name, @email)
`);

for (const user of users) {
  insertUser.run(user);
  console.log(`👤 Created user: ${user.name} (${user.email})`);
}

// ── Seed Sessions (past 7 days) ────────────────────────
const sessionTemplates = [
  {
    topic: 'Introduction to Machine Learning',
    summary: 'Covered supervised vs unsupervised learning, key algorithms (linear regression, decision trees, KNN), and model evaluation metrics like accuracy, precision, recall.',
    key_concepts: 'Supervised Learning, Unsupervised Learning, Linear Regression, Decision Trees, KNN, Overfitting, Underfitting, Cross-Validation',
    notes: 'Focus on understanding bias-variance tradeoff. Practice implementing linear regression from scratch.',
    duration_minutes: 60,
  },
  {
    topic: 'Data Structures - Trees and Graphs',
    summary: 'Explored binary trees, BST operations (insert, delete, search), tree traversals (inorder, preorder, postorder), and introduction to graphs with BFS and DFS.',
    key_concepts: 'Binary Tree, BST, Inorder Traversal, Preorder Traversal, BFS, DFS, Graph Representation, Adjacency List',
    notes: 'Tree traversals are important for interviews. Practice implementing BFS and DFS both iteratively and recursively.',
    duration_minutes: 75,
  },
  {
    topic: 'Python Advanced Concepts',
    summary: 'Studied decorators, generators, context managers, and metaclasses. Implemented custom decorators for logging and timing functions.',
    key_concepts: 'Decorators, Generators, yield, Context Managers, __enter__, __exit__, Metaclasses, Closures',
    notes: 'Generators are memory efficient for large datasets. Context managers are crucial for resource management.',
    duration_minutes: 45,
  },
  {
    topic: 'Database Management Systems',
    summary: 'Covered normalization (1NF, 2NF, 3NF, BCNF), SQL joins (inner, outer, cross), indexing strategies, and transaction management with ACID properties.',
    key_concepts: 'Normalization, 1NF, 2NF, 3NF, BCNF, SQL Joins, Indexing, B-Tree Index, ACID Properties, Transactions',
    notes: 'Understanding normalization is key. Practice writing complex SQL queries with multiple joins.',
    duration_minutes: 90,
  },
  {
    topic: 'Web Development - React Fundamentals',
    summary: 'Learned component lifecycle, hooks (useState, useEffect, useContext), state management patterns, and React Router for single-page applications.',
    key_concepts: 'React Components, useState, useEffect, useContext, Props, State Management, React Router, Virtual DOM, JSX',
    notes: 'Hooks simplify state management. Focus on useEffect cleanup functions to avoid memory leaks.',
    duration_minutes: 65,
  },
  {
    topic: 'Operating Systems - Process Management',
    summary: 'Studied process scheduling algorithms (FCFS, SJF, Round Robin, Priority), process synchronization, deadlocks, and semaphores.',
    key_concepts: 'Process Scheduling, FCFS, SJF, Round Robin, Deadlock, Semaphore, Mutex, Critical Section, Context Switching',
    notes: 'Understand the differences between preemptive and non-preemptive scheduling. Deadlock conditions are frequently tested.',
    duration_minutes: 55,
  },
  {
    topic: 'Computer Networks - TCP/IP Model',
    summary: 'Explored the TCP/IP model layers, HTTP/HTTPS protocols, DNS resolution, socket programming basics, and network security fundamentals.',
    key_concepts: 'TCP/IP, HTTP, HTTPS, DNS, Socket Programming, TLS/SSL, Firewall, NAT, Subnetting, OSI Model',
    notes: 'Compare OSI vs TCP/IP models. HTTP status codes and methods are important for web development.',
    duration_minutes: 70,
  },
  {
    topic: 'Software Engineering - Design Patterns',
    summary: 'Covered creational patterns (Singleton, Factory, Builder), structural patterns (Adapter, Decorator), and behavioral patterns (Observer, Strategy).',
    key_concepts: 'Singleton, Factory Pattern, Builder Pattern, Adapter Pattern, Decorator Pattern, Observer Pattern, Strategy Pattern, SOLID Principles',
    notes: 'Design patterns improve code maintainability. Practice implementing at least 3 patterns in a real project.',
    duration_minutes: 80,
  },
];

const insertSession = db.prepare(`
  INSERT INTO sessions (id, user_id, topic, summary, key_concepts, notes, duration_minutes, created_at)
  VALUES (@id, @user_id, @topic, @summary, @key_concepts, @notes, @duration_minutes, @created_at)
`);

console.log('\n📚 Creating sessions for the past 7 days...\n');

for (const user of users) {
  // Assign 3-5 random sessions per user within the past 7 days
  const numSessions = 3 + Math.floor(Math.random() * 3);
  const shuffled = [...sessionTemplates].sort(() => Math.random() - 0.5);
  const selectedSessions = shuffled.slice(0, numSessions);

  for (let i = 0; i < selectedSessions.length; i++) {
    const session = selectedSessions[i];
    // Random time within the past 7 days
    const daysAgo = Math.floor(Math.random() * 7);
    const hoursAgo = Math.floor(Math.random() * 24);
    const sessionDate = new Date();
    sessionDate.setDate(sessionDate.getDate() - daysAgo);
    sessionDate.setHours(sessionDate.getHours() - hoursAgo);

    insertSession.run({
      id: uuidv4(),
      user_id: user.id,
      topic: session.topic,
      summary: session.summary,
      key_concepts: session.key_concepts,
      notes: session.notes,
      duration_minutes: session.duration_minutes,
      created_at: sessionDate.toISOString(),
    });

    console.log(`  📖 ${user.name} → ${session.topic} (${daysAgo}d ago)`);
  }
}

db.close();

console.log('\n🎉 Database seeded successfully!');
console.log(`📁 Database location: ${DB_PATH}`);
