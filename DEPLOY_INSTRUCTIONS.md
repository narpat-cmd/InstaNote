# InstaNote Deployment Instructions

## Quick Deploy to Render (Recommended - Free Tier)

### Option 1: One-Click Deploy via Render Dashboard

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account (if not already connected)
4. Search for `InstaNote` repository (or create it first)
5. Configure:
   - **Name**: `instanote`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -c "from src.admin_panel import run_admin_panel; run_admin_panel(host='0.0.0.0', port=8080)"`
   - **Plan**: Free
6. Add Environment Variables:
   - `ADMIN_PASSWORD` = `your-secure-password`
   - `SECRET_KEY` = `your-random-secret-key`
   - `PYTHON_VERSION` = `3.11`
7. Click **"Create Web Service"**

### Option 2: Using render.yaml (Infrastructure as Code)

1. Push code to GitHub first (see below)
2. Go to https://dashboard.render.com
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub repo
5. Render will auto-detect `render.yaml` and deploy

---

## Push to GitHub (Required for Render)

Since GitHub CLI authentication needs setup, run these commands in PowerShell:

```powershell
cd D:\InstaNote

# Option A: Use GitHub CLI (if authenticated)
gh repo create InstaNote --public --source=. --remote=origin --push

# Option B: Manual push (create repo on GitHub.com first, then):
git remote add origin https://github.com/YOUR_USERNAME/InstaNote.git
git push -u origin master
```

---

## After Deployment

Your live URL will be: **https://instanote.onrender.com**

Admin panel: **https://instanote.onrender.com/login**
- Username: `admin`
- Password: (value of ADMIN_PASSWORD env var)

---

## Alternative: Deploy to Railway

1. Go to https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Select InstaNote repo
4. Add environment variables (same as above)
5. Deploy!

Live URL format: `https://instanote-production.up.railway.app`

---

## Alternative: Deploy to Heroku

```bash
heroku create instanote-app
heroku config:set ADMIN_PASSWORD=your-password SECRET_KEY=your-secret
git push heroku master
```

Live URL: `https://instanote-app.herokuapp.com`

---

## Local Testing Before Deploy

```bash
cd D:\InstaNote
pip install -r requirements.txt
python -c "from src.admin_panel import run_admin_panel; run_admin_panel()"
# Visit http://localhost:8080
```