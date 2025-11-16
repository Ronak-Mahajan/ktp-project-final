# Deployment Guide

This guide covers deploying the frontend to Vercel and the backend to Railway.

## Prerequisites

- GitHub account
- Vercel account (sign up at https://vercel.com)
- Railway account (sign up at https://railway.app)
- Git repository with your code

## Backend Deployment (Railway)

### Step 1: Prepare Backend

1. Make sure your `backend/requirements.txt` is up to date
2. The backend is already configured with:
   - `Procfile` for Railway
   - `railway.json` for Railway configuration
   - Environment variable support for CORS and port

### Step 2: Deploy to Railway

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect it's a Python project
6. Set the root directory to `backend/`
7. Railway will automatically:
   - Install dependencies from `requirements.txt`
   - Run the app using the `Procfile`

### Step 3: Configure Environment Variables in Railway

In Railway dashboard, go to your project → Variables tab and add:

```
CORS_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3000
KALSHI_API_BASE=https://api.elections.kalshi.com/trade-api/v2
PORT=8000
HOST=0.0.0.0
```

**Important:** Replace `your-vercel-app.vercel.app` with your actual Vercel deployment URL (you'll get this after deploying the frontend).

### Step 4: Get Your Railway URL

After deployment, Railway will provide a URL like:
```
https://your-app-name.up.railway.app
```

Copy this URL - you'll need it for the frontend configuration.

## Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

1. Make sure your `frontend/package.json` is up to date
2. The frontend is already configured with:
   - `vercel.json` for Vercel configuration
   - Environment variable support for API URL

### Step 2: Deploy to Vercel

#### Option A: Deploy via Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build` (or leave default)
   - **Install Command:** `npm install --legacy-peer-deps`
   - **Output Directory:** `.next` (default)

#### Option B: Deploy via Vercel CLI

```bash
cd frontend
npm i -g vercel
vercel
```

Follow the prompts to deploy.

### Step 3: Configure Environment Variables in Vercel

In Vercel dashboard, go to your project → Settings → Environment Variables and add:

```
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
```

**Important:** Replace `your-railway-app.up.railway.app` with your actual Railway deployment URL.

### Step 4: Update Railway CORS

After getting your Vercel URL, go back to Railway and update the `CORS_ORIGINS` variable:

```
CORS_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3000
```

Then redeploy the backend (Railway will auto-redeploy on variable changes).

## Verification

1. **Backend:** Visit `https://your-railway-app.up.railway.app/docs` - you should see the FastAPI docs
2. **Backend Health:** Visit `https://your-railway-app.up.railway.app/health` - should return `{"status":"healthy"}`
3. **Frontend:** Visit your Vercel URL - the correlation charts should load data from the backend

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:
1. Make sure `CORS_ORIGINS` in Railway includes your exact Vercel URL (with `https://`)
2. Make sure there are no trailing slashes in the URLs
3. Redeploy the backend after updating CORS_ORIGINS

### API Connection Errors

If the frontend can't connect to the backend:
1. Verify `NEXT_PUBLIC_API_URL` in Vercel matches your Railway URL
2. Check that the Railway service is running
3. Test the backend API directly: `https://your-railway-app.up.railway.app/api/v1/correlation`

### Build Errors

**Frontend:**
- Make sure you're using `npm install --legacy-peer-deps` in the install command
- Check that all dependencies are in `package.json`

**Backend:**
- Verify all dependencies are in `requirements.txt`
- Check Railway logs for specific error messages

## Local Development

For local development, create `.env.local` files:

**Frontend (`frontend/.env.local`):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend (`backend/.env`):**
```
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
KALSHI_API_BASE=https://api.elections.kalshi.com/trade-api/v2
PORT=8000
HOST=0.0.0.0
```

## Continuous Deployment

Both Vercel and Railway support automatic deployments:
- **Vercel:** Automatically deploys on push to main branch
- **Railway:** Automatically deploys on push to main branch (if connected to GitHub)

Make sure your main branch is set up correctly in both platforms.

