# Deployment

This project is prepared for deployment on Render with:

- a Django API service
- a Vite static frontend

## 1. Backend environment variables

Set these on the API service:

```env
DJANGO_SECRET_KEY=generate-a-long-random-secret
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-api-domain.onrender.com
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-api-domain.onrender.com,https://your-frontend-domain.onrender.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
DATABASE_URL=postgres://...
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4.1-mini
AI_CHAT_RATE_LIMIT=20/hour
```

Notes:

- `DATABASE_URL` is the preferred production database input.
- If `DATABASE_URL` is missing, the app falls back to `DB_ENGINE`-based config, then SQLite.

## 2. Frontend environment variables

Set this on the frontend service:

```env
VITE_API_BASE_URL=https://your-api-domain.onrender.com/api
```

## 3. Render deployment

This repo includes [render.yaml](/abs/path/c:/Users/ahmed/OneDrive/Desktop/student_management_system/render.yaml:1).

On Render:

1. Create a new Blueprint deployment from this repository.
2. Attach a PostgreSQL database and copy its `DATABASE_URL` into the API service.
3. Replace the placeholder domains in `render.yaml` or override them in the Render dashboard.
4. Redeploy.

## 4. Post-deploy checks

Verify:

- `https://your-api-domain/health/` returns JSON with `"status": "ok"`.
- `https://your-frontend-domain/` loads successfully.
- Login works against the API.
- Static files load without 404s.
