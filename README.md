# 📊 Eisenhower Matrix Task Manager

> A full-stack task management application that automatically categorizes tasks using the Eisenhower Matrix (Urgent-Important Matrix) methodology.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791.svg)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Built with:** Django REST Framework • React • Vite • Supabase • PostgreSQL

---

## 📑 Table of Contents

- [Features](#-features)
- [Architecture](#️-architecture)
- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [Scoring Algorithm](#-scoring-algorithm)
- [UI Components](#-ui-components)
- [Tech Stack](#️-tech-stack)
- [Database Schema](#-database-schema)
- [Security](#-security)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Features

- **Smart Categorization**: Automatically calculates urgency and importance scores
- **4-Quadrant Dashboard**: Visual organization using the Eisenhower Matrix
  - 🔴 Urgent & Important (Do First)
  - 🟡 Important but Not Urgent (Schedule)
  - 🔵 Urgent but Not Important (Delegate)
  - ⚪ Neither (Eliminate)
- **Real-time Scoring**: Dynamic task prioritization based on deadlines and estimated time
- **RESTful API**: Clean Django REST Framework backend
- **Responsive UI**: Modern React frontend with color-coded quadrants
- **Supabase Integration**: PostgreSQL database with authentication ready

## 🏗️ Architecture

```
eisenhower-matrix/
├── backend/                    # Django REST API
│   ├── tasks/                  # Main app
│   │   ├── models.py          # Task model
│   │   ├── views.py           # API endpoints
│   │   ├── serializers.py     # JSON serialization
│   │   └── categorization.py  # Scoring algorithms
│   └── eisenhower_matrix/     # Project settings
├── frontend/                   # React app
│   └── src/
│       ├── components/        # React components
│       │   ├── Dashboard.jsx  # 4-quadrant layout
│       │   ├── TaskCard.jsx   # Task display
│       │   └── TaskForm.jsx   # Task creation
│       └── api/
│           └── client.js      # API client
└── .kiro/specs/               # Project specifications
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Supabase account (free tier works)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Copy `.env.example` to `.env` and fill in your Supabase credentials:
   ```env
   DATABASE_NAME=postgres
   DATABASE_USER=postgres.your-project-ref
   DATABASE_PASSWORD=your-password
   DATABASE_HOST=your-project-ref.supabase.co
   DATABASE_PORT=5432
   
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start backend server**
   ```bash
   python manage.py runserver
   ```
   Backend runs at: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```
   Frontend runs at: `http://localhost:5174`

## 📖 API Endpoints

### Tasks

- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Get task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

### Request Example

```json
POST /api/tasks/
{
  "title": "Complete project report",
  "description": "Finish the quarterly report",
  "deadline": "2024-03-15T18:00:00Z",
  "estimated_time_hours": 4.5
}
```

### Response Example

```json
{
  "id": 1,
  "title": "Complete project report",
  "description": "Finish the quarterly report",
  "deadline": "2024-03-15T18:00:00Z",
  "estimated_time_hours": "4.50",
  "urgency_score": "0.85",
  "importance_score": "0.72",
  "quadrant": "urgent_important",
  "is_manually_categorized": false,
  "is_completed": false,
  "created_at": "2024-03-10T10:30:00Z",
  "updated_at": "2024-03-10T10:30:00Z"
}
```

## 🧮 Scoring Algorithm

### Urgency Score (0.0 - 1.0)

Based on time until deadline:
- **< 24 hours**: 0.9 - 1.0 (Critical)
- **1-3 days**: 0.7 - 0.9 (High)
- **3-7 days**: 0.4 - 0.7 (Medium)
- **> 7 days**: 0.0 - 0.4 (Low)

### Importance Score (0.0 - 1.0)

Based on estimated time required:
- **> 8 hours**: 0.8 - 1.0 (Major task)
- **4-8 hours**: 0.6 - 0.8 (Significant)
- **2-4 hours**: 0.4 - 0.6 (Moderate)
- **< 2 hours**: 0.0 - 0.4 (Minor)

### Quadrant Assignment

- **Urgent & Important**: urgency ≥ 0.7 AND importance ≥ 0.7
- **Important but Not Urgent**: urgency < 0.7 AND importance ≥ 0.7
- **Urgent but Not Important**: urgency ≥ 0.7 AND importance < 0.7
- **Neither**: urgency < 0.7 AND importance < 0.7

## 🎨 UI Components

### Dashboard
4-quadrant grid layout with color-coded sections:
- Red: Urgent & Important
- Yellow: Important but Not Urgent
- Blue: Urgent but Not Important
- Gray: Neither

### Task Card
Displays:
- Task title and description
- Deadline (formatted)
- Estimated time
- Urgency and importance scores
- Manual categorization badge (if applicable)

### Task Form
Input fields:
- Title (required)
- Description (optional)
- Deadline (datetime picker)
- Estimated time in hours (number input)

## 🛠️ Tech Stack

### Backend
- **Django 4.2+**: Web framework
- **Django REST Framework**: API toolkit
- **PostgreSQL**: Database (via Supabase)
- **python-dotenv**: Environment management

### Frontend
- **React 18**: UI library
- **Vite**: Build tool
- **Axios**: HTTP client
- **CSS3**: Styling

### Database
- **Supabase**: PostgreSQL hosting
- **Row Level Security**: Built-in authentication support

## 📝 Database Schema

### Tasks Table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| user_id | UUID | Foreign key to auth.users |
| title | VARCHAR(255) | Task name |
| description | TEXT | Task details |
| deadline | TIMESTAMPTZ | Due date/time |
| estimated_time_hours | NUMERIC(5,2) | Hours to complete |
| urgency_score | NUMERIC(3,2) | 0.0 to 1.0 |
| importance_score | NUMERIC(3,2) | 0.0 to 1.0 |
| quadrant | VARCHAR(50) | Matrix quadrant |
| is_manually_categorized | BOOLEAN | User override flag |
| is_completed | BOOLEAN | Completion status |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last update timestamp |

## 🔒 Security

- CORS enabled for development (configure for production)
- Supabase Row Level Security (RLS) ready
- Environment variables for sensitive data
- SSL required for database connections

## 🚧 Future Enhancements

- [ ] User authentication with Supabase Auth
- [ ] Google Calendar integration
- [ ] Email notifications
- [ ] Task completion tracking
- [ ] Analytics dashboard
- [ ] Mobile responsive improvements
- [ ] Dark mode
- [ ] Task filtering and search
- [ ] Drag-and-drop task reordering
- [ ] Export tasks to CSV/PDF

## 📄 License

MIT License - feel free to use this project for learning or building your own task manager!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👨‍💻 Author

Built for a hackathon project demonstrating full-stack development with modern web technologies.

## 🙏 Acknowledgments

- Eisenhower Matrix methodology by Dwight D. Eisenhower
- Django and React communities
- Supabase for excellent PostgreSQL hosting

---

**⭐ Star this repo if you find it helpful!**
