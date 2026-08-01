# Public deployment setup

This repository can be published as a public web app by deploying the FastAPI backend and the React frontend separately.

## Recommended hosting choices

- Backend: Render, Railway, Fly.io, or any container/Python host
- Frontend: Vercel, Netlify, or Cloudflare Pages

## 1. Backend deployment

### Option A: Render
1. Create a new Web Service for the backend folder.
2. Set the build command to:
   ```bash
   pip install -r requirements.txt
   ```
3. Set the start command to:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 10000
   ```
4. Set environment variables:
   - `PYTHON_BACKEND_URL` = your public backend URL
   - `PORT` = `10000`
   - `ENVIRONMENT` = `prod`
   - `DATABASE_URL` = your production database URL if the app needs persistence

### Option B: Railway / Fly.io
Use the same Python runtime and the same start command above.

### GitHub Actions trigger
The workflow at [.github/workflows/public-deploy.yml](.github/workflows/public-deploy.yml) will call a Render deploy hook automatically when the repository secret `RENDER_DEPLOY_HOOK_URL` is set.

## 2. Frontend deployment

### Vercel
1. Create a Vercel project from the frontend directory.
2. Set these build settings:
   - Build command: `pnpm build`
   - Output directory: `dist`
3. Add environment variables:
   - `VITE_API_BASE_URL` = your public backend URL
   - `VITE_APP_NAME` = `Hosamahad Platform`
   - `VITE_APP_ENV` = `production`
4. Add the following GitHub repository secrets:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`

The workflow at [.github/workflows/public-deploy.yml](.github/workflows/public-deploy.yml) will build and publish the frontend automatically on pushes to the main branch.

## 3. Local verification

From the repository root:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

```bash
cd frontend
pnpm install
pnpm build
```

## 4. GitHub secrets and variables

### Repository secrets
- `RENDER_DEPLOY_HOOK_URL` (optional, backend)
- `VERCEL_TOKEN` (optional, frontend)
- `VERCEL_ORG_ID` (optional, frontend)
- `VERCEL_PROJECT_ID` (optional, frontend)

### Repository variables
- `VITE_API_BASE_URL` (optional, frontend)
- `VITE_APP_NAME` (optional, frontend)

## 5. Public URL shape

Once deployed, the app should be reachable at:
- Frontend: `https://<your-vercel-domain>`
- Backend API: `https://<your-backend-host>/api/v1/...`
