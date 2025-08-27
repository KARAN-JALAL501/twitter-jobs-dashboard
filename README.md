# 🔎 Twitter Jobs Dashboard (Streamlit)

A personal dashboard to discover freelance **brand identity / UI/UX** opportunities on Twitter/X using **free tools** only.

## ✨ Features
- Live tweet search via **snscrape** (no paid APIs).
- Sidebar filters: keywords, max tweets, region/location.
- Clean **Twitter-like feed** (click a card to open the real tweet).
- Shows number of results and lets you **export CSV**.
- **Sample data fallback** so you can test without scraping.
- Optional charts: jobs per location.

## 🚀 Quickstart

> Requires Python 3.10+

```bash
git clone <this-zip-unpacked-folder>
cd twitter_jobs_dashboard
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Or just double‑click `run.bat` (Windows) / run `bash run.sh` (macOS/Linux).

## 🔧 Usage
- Adjust **Keywords** using Twitter search syntax. Example:
  ```
  ("ui designer" OR "ux designer" OR "product designer" OR "brand identity designer") lang:en
  ```
  The app automatically adds: `exclude:retweets exclude:replies`.
- Set **Max tweets** and optional **Region** (comma‑separated, matches user profile locations).

## 📦 Files
- `app.py` — Streamlit app
- `requirements.txt` — dependencies
- `run.bat` — Windows helper
- `run.sh` — macOS/Linux helper

## ❗ Notes & Tips
- If live scraping returns nothing (rate limiting, query too specific, etc.), the app falls back to high‑quality sample data.
- Location comes from the user profile; many users leave it blank or put creative strings — filter broadly.
- For best results, refine keywords with OR/quotes and iterate.

## 🛡️ Disclaimer
This project is for personal/educational use. Respect content policies and platform terms. Do not spam or automate unsolicited outreach.
