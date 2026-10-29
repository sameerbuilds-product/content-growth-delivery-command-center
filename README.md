# Content Growth & Delivery Command Center

An interactive Streamlit portfolio app for content retention, product marketing, content performance, and end-to-end content delivery.

## App modules
1. **Content Performance** — genre and title-level impressions, starts, and completion.
2. **Retention & Engagement** — completion and listening-time signals, with clear caveats about missing user-level retention data.
3. **Product Marketing** — campaign spend, conversions, CPA, CTR, and attributed ROAS.
4. **Content Delivery** — pipeline stages, owners, priorities, quality checks, and blockers.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy from GitHub
1. Upload all files in this folder to a GitHub repository (or place them in a subfolder).
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Create a new app, select the repository and branch, and choose `app.py` (or the correct subfolder path).
4. Deploy.

## Data integrity
Every included CSV is synthetic and illustrative. No real user-level churn data is included; true retention analysis requires cohort/event-level data. Campaign-attributed revenue does not prove incremental impact.
