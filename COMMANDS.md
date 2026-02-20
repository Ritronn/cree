# Quick Command Reference

## Initial Setup

### Windows
```bash
setup.bat
```

### Mac/Linux
```bash
chmod +x setup.sh
./setup.sh
```

## Running the Application

### Backend (Terminal 1)
```bash
cd backend
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux
python manage.py runserver
```
Access at: http://localhost:8000

### Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
Access at: http://localhost:5174

## Database Commands

### Create migrations
```bash
cd backend
python manage.py makemigrations
```

### Apply migrations
```bash
python manage.py migrate
```

### Create superuser
```bash
python manage.py createsuperuser
```

### Access Django admin
http://localhost:8000/admin

## Development Commands

### Backend

**Run tests**
```bash
cd backend
python manage.py test
```

**Create new app**
```bash
python manage.py startapp app_name
```

**Django shell**
```bash
python manage.py shell
```

**Collect static files**
```bash
python manage.py collectstatic
```

### Frontend

**Install new package**
```bash
cd frontend
npm install package-name
```

**Build for production**
```bash
npm run build
```

**Preview production build**
```bash
npm run preview
```

**Lint code**
```bash
npm run lint
```

## Git Commands

### Initial commit
```bash
git init
git add .
git commit -m "Initial commit"
```

### Push to GitHub
```bash
git remote add origin https://github.com/yourusername/eisenhower-matrix.git
git branch -M main
git push -u origin main
```

### Create feature branch
```bash
git checkout -b feature/feature-name
```

### Commit changes
```bash
git add .
git commit -m "Add: feature description"
git push origin feature/feature-name
```

## Environment Setup

### Backend .env
```env
DATABASE_NAME=postgres
DATABASE_USER=postgres.your-project-ref
DATABASE_PASSWORD=your-password
DATABASE_HOST=your-project-ref.supabase.co
DATABASE_PORT=5432

SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

SECRET_KEY=your-django-secret-key
DEBUG=True
```

## Troubleshooting

### Port already in use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Clear Python cache
```bash
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

### Reinstall dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt --force-reinstall

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Reset database
```bash
cd backend
python manage.py flush
python manage.py migrate
```

## API Testing

### Using curl

**Get all tasks**
```bash
curl http://localhost:8000/api/tasks/
```

**Create task**
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Test description",
    "deadline": "2024-12-31T23:59:59Z",
    "estimated_time_hours": 2.5
  }'
```

**Update task**
```bash
curl -X PUT http://localhost:8000/api/tasks/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task",
    "is_completed": true
  }'
```

**Delete task**
```bash
curl -X DELETE http://localhost:8000/api/tasks/1/
```
