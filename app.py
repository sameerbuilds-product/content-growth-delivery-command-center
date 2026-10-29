from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Content Growth Command Center", page_icon="🎧", layout="wide")
st.title("🎧 Content Growth & Delivery Command Center")
st.caption("Content performance • Retention • Product marketing • End-to-end delivery")
st.info("Portfolio demonstration using synthetic data only. Not real company or customer performance.")

ROOT = Path(__file__).parent
@st.cache_data
def load(name):
    return pd.read_csv(ROOT / name)

content = load("content_performance_synthetic.csv")
campaigns = load("campaign_performance_synthetic.csv")
pipeline = load("content_pipeline_synthetic.csv")
content["launch_date"] = pd.to_datetime(content["launch_date"])
campaigns["ctr"] = campaigns["clicks"] / campaigns["impressions"]
campaigns["conversion_rate"] = campaigns["conversions"] / campaigns["clicks"]
campaigns["cpa"] = campaigns["spend_inr"] / campaigns["conversions"].replace(0, pd.NA)
campaigns["roas"] = campaigns["attributed_revenue_inr"] / campaigns["spend_inr"].replace(0, pd.NA)
content["start_rate"] = content["starts"] / content["impressions"]
content["completion_rate"] = content["completed_plays"] / content["starts"].replace(0, pd.NA)

with st.sidebar:
    st.header("Filters")
    genres = sorted(content["genre"].unique())
    selected_genres = st.multiselect("Content genres", genres, default=genres)
    channels = sorted(campaigns["channel"].unique())
    selected_channels = st.multiselect("Campaign channels", channels, default=channels)
    segment = st.selectbox("Audience segment", ["All"] + sorted(campaigns["audience_segment"].unique()))

content_f = content[content.genre.isin(selected_genres)]
campaign_f = campaigns[campaigns.channel.isin(selected_channels)]
if segment != "All":
    campaign_f = campaign_f[campaign_f.audience_segment == segment]

tab1, tab2, tab3, tab4 = st.tabs(["Content Performance", "Retention & Engagement", "Product Marketing", "Content Delivery"])

with tab1:
    st.subheader("Content portfolio performance")
    a,b,c,d = st.columns(4)
    a.metric("Titles tracked", f"{len(content_f):,}")
    b.metric("Impressions", f"{content_f.impressions.sum():,}")
    b2 = content_f.starts.sum() / content_f.impressions.sum() if content_f.impressions.sum() else 0
    c.metric("Start rate", f"{b2:.1%}")
    d.metric("Avg completion rate", f"{content_f.completed_plays.sum()/content_f.starts.sum():.1%}" if content_f.starts.sum() else "—")
    left,right = st.columns(2)
    with left:
        st.markdown("**Starts by genre**")
        g = content_f.groupby("genre", as_index=False).agg(starts=("starts","sum"), impressions=("impressions","sum"))
        st.plotly_chart(px.bar(g, x="genre", y="starts", color="genre"), use_container_width=True)
    with right:
        st.markdown("**Content funnel by title**")
        funnel = content_f.groupby("title", as_index=False).agg(impressions=("impressions","sum"), starts=("starts","sum"), completed_plays=("completed_plays","sum")).sort_values("starts", ascending=False).head(8)
        st.plotly_chart(px.bar(funnel, x="title", y=["impressions","starts","completed_plays"], barmode="group"), use_container_width=True)
    st.markdown("**Content-level diagnostic table**")
    st.dataframe(content_f.assign(start_rate_pct=(content_f.start_rate*100).round(1), completion_pct=(content_f.completion_rate*100).round(1))[["content_id","title","genre","impressions","starts","completed_plays","start_rate_pct","completion_pct","status"]], use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Retention and engagement signals")
    c1,c2,c3 = st.columns(3)
    c1.metric("Completed plays", f"{content_f.completed_plays.sum():,}")
    c2.metric("Average listening time", f"{content_f.avg_listen_min.mean():.1f} min" if len(content_f) else "—")
    c3.metric("Titles with completion below 50%", f"{int((content_f.completion_rate < .5).sum())}")
    st.markdown("**Retention investigation prompts**")
    if len(content_f):
        low = content_f.sort_values("completion_rate").iloc[0]
        st.warning(f"Investigate **{low['title']}** ({low['genre']}): synthetic completion rate is {low['completion_rate']:.1%}. Check episode-level drop-off, opening-hook strength, pacing, and audience/content fit.")
        st.write("Suggested analysis: compare day-1/day-7 return rate, episodes consumed per user, cohort retention, and completion by episode. These require user-level event data, which this sample dataset does not contain.")
    st.caption("This sample supports content engagement proxies, not true user-level churn measurement.")

with tab3:
    st.subheader("Product marketing & campaign performance")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Campaign spend", f"₹{campaign_f.spend_inr.sum():,.0f}")
    c2.metric("Conversions", f"{campaign_f.conversions.sum():,}")
    c3.metric("Blended CPA", f"₹{campaign_f.spend_inr.sum()/campaign_f.conversions.sum():,.0f}" if campaign_f.conversions.sum() else "—")
    c4.metric("Attributed ROAS", f"{campaign_f.attributed_revenue_inr.sum()/campaign_f.spend_inr.sum():.2f}x" if campaign_f.spend_inr.sum() else "—")
    left,right = st.columns(2)
    with left:
        st.markdown("**ROAS by campaign**")
        st.plotly_chart(px.bar(campaign_f.sort_values("roas", ascending=False), x="campaign_name", y="roas", color="channel"), use_container_width=True)
    with right:
        st.markdown("**Spend vs attributed revenue**")
        st.plotly_chart(px.scatter(campaign_f, x="spend_inr", y="attributed_revenue_inr", size="conversions", color="channel", hover_name="campaign_name"), use_container_width=True)
    st.dataframe(campaign_f[["campaign_name","product_line","channel","audience_segment","spend_inr","impressions","clicks","conversions","ctr","conversion_rate","cpa","roas"]].round(3), use_container_width=True, hide_index=True)
    st.caption("Attributed ROAS is not proof of incrementality. Use holdouts or sound experiments to estimate causal lift.")

with tab4:
    st.subheader("End-to-end content delivery pipeline")
    stage_order = ["Scripting","Audio Production","Quality Review","Marketing Prep","Ready to Publish","Live"]
    pipeline["stage"] = pd.Categorical(pipeline["stage"], categories=stage_order, ordered=True)
    p1,p2,p3 = st.columns(3)
    p1.metric("Pipeline titles", len(pipeline))
    p2.metric("High priority", int((pipeline.priority == "High").sum()))
    p3.metric("Open blockers", int(pipeline.blocker.fillna("").astype(str).str.strip().ne("").sum()))
    stage_counts = pipeline.groupby("stage", observed=False, as_index=False).size()
    left,right = st.columns([1,1.2])
    with left:
        st.markdown("**Titles by workflow stage**")
        st.plotly_chart(px.bar(stage_counts, x="stage", y="size", labels={"size":"Titles","stage":"Stage"}), use_container_width=True)
    with right:
        st.markdown("**Delivery risks and next actions**")
        blocked = pipeline[pipeline.blocker.fillna("").astype(str).str.strip().ne("")]
        for _, row in blocked.iterrows():
            st.markdown(f"- **{row['title']}** — {row['stage']}: {row['blocker']} (owner: {row['owner']}; priority: {row['priority']})")
    st.markdown("**Pipeline tracker**")
    st.dataframe(pipeline, use_container_width=True, hide_index=True)
    st.download_button("Download pipeline tracker CSV", pipeline.to_csv(index=False).encode("utf-8"), "content_pipeline_tracker.csv", "text/csv")

st.divider()
st.caption("Use this app to demonstrate how content, retention, campaign, and delivery metrics can support decisions. All data is synthetic; validate definitions and sources before real business use.")
