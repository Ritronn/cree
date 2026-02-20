# ⚡ Quick Start Guide

Get the Eisenhower Matrix Task Manager running in 5 minutes!

## 🎯 Prerequisites

- Python 3.9+ installed
- Node.js 16+ installed
- Supabase account (free tier)

## 🚀 Setup Steps

### 1️⃣ Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/eisenhower-matrix-task-manager.git
cd eisenhower-matrix-task-manager
```

### 2️⃣ Backend Setup (2 minutes)
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Supabase credentials:
```env
DATABASE_HOST=your-project.supabase.co
DATABASE_PASSWORD=your-password
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

Run migrations:
```bash
python manage.py migrate
python manage.py runserver
```

✅ Backend running at http://localhost:8000

### 3️⃣ Frontend Setup (2 minutes)
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```

✅ Frontend running at http://localhost:5174

### 4️⃣ Test It Out (1 minute)
1. Open http://localhost:5174
2. Create a task with:
   - Title: "Complete project report"
   - Deadline: Tomorrow
   - Estimated time: 4 hours
3. Watch it automatically categorize! 🎉

## 🎨 What You'll See

- **4-Quadrant Dashboard** with color-coded sections
- **Automatic Scoring** based on deadline and time
- **Real-time Categorization** into Eisenhower Matrix

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database Connection Error
- Check Supabase credentials in `.env`
- Verify database is accessible
- Run migrations: `python manage.py migrate`

### Frontend Not Loading
- Check backend is running
- Verify CORS settings in `backend/eisenhower_matrix/settings.py`
- Clear browser cache

## 📚 Next Steps

- Read [README.md](README.md) for full documentation
- Check [COMMANDS.md](COMMANDS.md) for all commands
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## 🎉 You're Ready!

Start managing your tasks with the Eisenhower Matrix! 🚀
