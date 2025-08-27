import sys
import typing as t
import importlib
from dataclasses import dataclass
import pandas as pd
import streamlit as st

# ---------- Page config & basic styles ----------
st.set_page_config(page_title="Twitter Jobs Dashboard", page_icon="🔎", layout="wide")

CUSTOM_CSS = '''
<style>
/* Global tweaks */
.block-container {padding-top: 2rem; padding-bottom: 4rem;}
/* Tweet cards */
a.tweet-card {
  display: block;
  text-decoration: none;
  border: 1px solid rgba(0,0,0,0.08);
  padding: 14px 16px;
  border-radius: 12px;
  margin-bottom: 12px;
  transition: box-shadow 0.15s ease, transform 0.05s ease;
  background: rgba(255,255,255,0.65);
}
a.tweet-card:hover {box-shadow: 0 6px 24px rgba(0,0,0,0.06); transform: translateY(-1px);}
.tweet-hdr {font-weight: 700; font-size: 15px; color: #0F1419;}
.tweet-handle {font-weight: 500; color: #536471; margin-left: 6px;}
.tweet-body {margin-top: 6px; font-size: 15px; line-height: 1.5; color: #0F1419;}
.tweet-meta {margin-top: 10px; font-size: 13px; color: #536471;}
.badge {display:inline-block; font-size:12px; padding:2px 8px; border-radius:999px; border:1px solid rgba(0,0,0,0.1); margin-left:8px;}
.footer-note {color:#536471; font-size:13px;}
</style>
'''
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- Utils ----------
def _get_snscrape():
    """Try to import snscrape. If not installed, return None (we'll fall back to sample data)."""
    try:
        return importlib.import_module("snscrape.modules.twitter")
    except Exception:
        return None

def generate_sample_data(n: int = 40) -> pd.DataFrame:
    # Simple deterministic sample data
    names = [
        ("Aditi Sharma", "aditidesigns", "Hiring UI/UX designer for a fintech MVP. DM your portfolio!", "Bengaluru, India"),
        ("Ravi Patel", "brandkraft_ravi", "Looking for a freelance brand identity designer for a quick turnaround", "Ahmedabad, IN"),
        ("UX Careers", "ux_careers_daily", "We are hiring UI/UX Designer (Remote, India). Figma, prototyping, user testing.", "Remote"),
        ("TechNest", "technest_jobs", "Product team needs a UI Designer. Mobile-first. 3-month contract.", "Pune"),
        ("CreativeHub", "creativehub", "Brand identity designer needed for D2C skincare brand.", "Mumbai"),
        ("Sarah Lee", "sarahdesigns", "Hiring UI/UX (Mid-level). SaaS. Apply with case studies.", "San Francisco, CA"),
        ("Ankit Gupta", "ankit_hires", "UI/UX freelancer for a marketplace redesign. Weekly sprints.", "Gurugram"),
        ("StartUpWave", "startup_wave", "Brand identity + UI kit for a stealth AI startup. Paid, remote.", "Remote"),
    ]
    rows = []
    for i in range(n):
        name, handle, text, loc = names[i % len(names)]
        rows.append({
            "display_name": name,
            "handle": f"@{handle}",
            "text": text + f" #{1000+i}",
            "url": f"https://twitter.com/{handle}/status/{1700000000000000000 + i}",
            "location": loc
        })
    return pd.DataFrame(rows)

def scrape_tweets(query: str, limit: int) -> pd.DataFrame:
    sntwitter = _get_snscrape()
    if sntwitter is None:
        st.info("snscrape is not installed. Showing sample data. Install dependencies to enable live scraping.")
        return generate_sample_data(limit)

    rows = []
    try:
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= limit:
                break
            # Derive fields with fallbacks
            handle = getattr(tweet.user, "username", None) or ""
            display_name = getattr(tweet.user, "displayname", None) or handle
            location = getattr(tweet.user, "location", None) or ""
            text = getattr(tweet, "content", None) or getattr(tweet, "rawContent", "")
            url = getattr(tweet, "url", None) or f"https://twitter.com/{handle}"
            rows.append({
                "display_name": display_name,
                "handle": f"@{handle}" if handle else "",
                "text": text,
                "url": url,
                "location": location or ""
            })
    except Exception as e:
        st.warning(f"Live scraping failed ({type(e).__name__}). Showing sample data instead.")
        return generate_sample_data(limit)

    df = pd.DataFrame(rows)
    if df.empty:
        st.info("No live results returned. Showing sample data.")
        return generate_sample_data(limit)
    return df

def apply_region_filter(df: pd.DataFrame, region_input: str) -> pd.DataFrame:
    if not region_input.strip():
        return df
    regions = [r.strip().lower() for r in region_input.split(",") if r.strip()]
    if not regions:
        return df
    def matches(loc: str) -> bool:
        loc_l = (loc or "").lower()
        return any(r in loc_l for r in regions)
    return df[df["location"].apply(matches)]

def tweet_card(display_name: str, handle: str, text: str, url: str, location: str):
    # Convert line breaks for HTML
    safe_text = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
    html = f'''
    <a class="tweet-card" href="{url}" target="_blank" rel="noopener">
      <div class="tweet-hdr">{display_name} <span class="tweet-handle">{handle}</span></div>
      <div class="tweet-body">{safe_text}</div>
      <div class="tweet-meta">📍 {location if location else "Location not specified"} <span class="badge">Open on X</span></div>
    </a>
    '''
    st.markdown(html, unsafe_allow_html=True)

# ---------- Sidebar controls ----------
with st.sidebar:
    st.title("Filters")
    default_keywords = '("ui designer" OR "ux designer" OR "ui/ux" OR "product designer" OR "brand identity designer" OR "hiring ui/ux")'
    keywords = st.text_input("Keywords (Twitter search syntax)", value=default_keywords, help="Use quotes and OR for better results. We also add language & exclude retweets/replies.")
    max_tweets = st.slider("Max tweets to fetch", min_value=10, max_value=500, value=120, step=10)
    region = st.text_input("Region/Location filter (comma-separated)", value="", placeholder="India, Remote, Bengaluru, USA")
    live = st.toggle("Use live scraping (snscrape)", value=True)
    st.caption("Tip: If live scraping fails or is off, the app will use high‑quality sample data so you can test everything.")

# Build query
query = f'{keywords} lang:en exclude:retweets exclude:replies'
st.caption(f"Search query: `{query}`")

# ---------- Fetch data ----------
if live:
    df = scrape_tweets(query, max_tweets)
else:
    df = generate_sample_data(max_tweets)

# ---------- Apply filters ----------
df_filtered = apply_region_filter(df, region)

# ---------- Summary & export ----------
left, right = st.columns([1,1])
with left:
    st.subheader("Results")
    st.write(f"Showing **{len(df_filtered)}** of **{len(df)}** tweets.")
with right:
    csv = df_filtered.to_csv(index=False)
    st.download_button("⬇️ Export filtered to CSV", data=csv, file_name="twitter_jobs_filtered.csv", mime="text/csv")

# ---------- Optional charts ----------
with st.expander("📊 Optional charts"):
    if df_filtered.empty:
        st.info("No data to chart yet.")
    else:
        # Jobs per location (top 15)
        loc_counts = (
            df_filtered.assign(location=df_filtered["location"].fillna("").replace("", "Unknown"))
            .groupby("location", as_index=False)
            .size()
            .sort_values("size", ascending=False)
            .head(15)
        )

        try:
            import altair as alt
            chart = alt.Chart(loc_counts).mark_bar().encode(
                x=alt.X('size:Q', title='Count'),
                y=alt.Y('location:N', sort='-x', title='Location'),
                tooltip=['location', 'size']
            ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)
        except Exception:
            st.info("Altair is not installed; skipping charts.")

# ---------- Feed ----------
if df_filtered.empty:
    st.warning("No tweets found with the current filters. Try changing keywords or removing the region filter.")
else:
    for _, row in df_filtered.iterrows():
        tweet_card(row["display_name"], row["handle"], row["text"], row["url"], row["location"])

# ---------- Footer ----------
st.markdown(
    '<div class="footer-note">Built with Streamlit • Uses snscrape for live search (no paid APIs) • Educational/portfolio use only.</div>',
    unsafe_allow_html=True
)
