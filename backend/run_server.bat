@echo off
REM Set database environment variables directly
set DATABASE_NAME=postgres
set DATABASE_USER=postgres.qhjyubskblmfqrkoygiz
set DATABASE_PASSWORD=OmkarisMahabali
set DATABASE_HOST=aws-1-ap-northeast-2.pooler.supabase.com
set DATABASE_PORT=5432

REM Run Django server
python manage.py runserver
