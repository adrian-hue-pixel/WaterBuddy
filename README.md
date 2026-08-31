# WaterBuddy

WaterBuddy is a polished Streamlit hydration companion with a premium UI, guided goals, quick logging, analytics, AI coaching, and profile-based personalization.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Environment variables

Create a local `.env` file from `.env.example` and fill in the keys you need:

- `GEMINI_API_KEY` for AI coaching
- `OPENWEATHER_API_KEY` for weather conditions

## GitHub-ready setup

This repository is ready to push to GitHub. A standard workflow is:

```bash
git init
git add .
git commit -m "Initial WaterBuddy app"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```

## Deployment notes

- Streamlit Cloud: connect the repo and set the startup command to `streamlit run app.py`.
- Heroku: the included `Procfile` is available for Python deployments.
- Daily hydration data is stored in SQLite via the local `waterbuddy.db` database.
- The AI and weather features gracefully fall back when API keys are missing.
