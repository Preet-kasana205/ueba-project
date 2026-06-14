import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="UEBA Platform",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ UEBA Platform — Insider Threat Detection")
st.caption("User and Entity Behaviour Analytics | Identity Trust Framework")

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("Controls")

if st.sidebar.button("▶ Run Full Pipeline", type="primary"):
    with st.spinner("Running pipeline..."):
        requests.post(f"{BASE_URL}/ingest/normalize")
        requests.post(f"{BASE_URL}/baseline/compute")
        requests.post(f"{BASE_URL}/detection/run")
        requests.post(f"{BASE_URL}/alerts/generate")
    st.sidebar.success("Pipeline complete")

st.sidebar.markdown("---")
st.sidebar.markdown("**Pipeline Steps**")
if st.sidebar.button("Normalize Events"):
    requests.post(f"{BASE_URL}/ingest/normalize")
    st.sidebar.success("Done")
if st.sidebar.button("Compute Baselines"):
    requests.post(f"{BASE_URL}/baseline/compute")
    st.sidebar.success("Done")
if st.sidebar.button("Run Detection"):
    requests.post(f"{BASE_URL}/detection/run")
    st.sidebar.success("Done")
if st.sidebar.button("Generate Alerts"):
    requests.post(f"{BASE_URL}/alerts/generate")
    st.sidebar.success("Done")

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=10)
def load_alerts():
    try:
        r = requests.get(f"{BASE_URL}/alerts")
        return r.json() if r.status_code == 200 else []
    except:
        return []

@st.cache_data(ttl=10)
def load_users():
    try:
        r = requests.get(f"{BASE_URL}/users")
        return r.json() if r.status_code == 200 else []
    except:
        return []

alerts = load_alerts()
users = load_users()

# ── Metrics Row ───────────────────────────────────────────────────────────────
st.markdown("## Fleet Overview")
col1, col2, col3, col4 = st.columns(4)

open_alerts = [a for a in alerts if a["status"] == "open"]
critical = [a for a in alerts if a["severity"] == "critical"]
verification_needed = [a for a in alerts if a["requires_verification"]]
high_risk_users = [u for u in users if u["risk_level"] in ("high", "critical")]

col1.metric("Open Alerts", len(open_alerts), delta=None)
col2.metric("Critical Severity", len(critical))
col3.metric("Verification Required", len(verification_needed))
col4.metric("High Risk Users", len(high_risk_users))

st.markdown("---")

# ── Alerts Table ──────────────────────────────────────────────────────────────
st.markdown("## Active Alerts")

if not alerts:
    st.info("No alerts generated yet. Run the pipeline from the sidebar.")
else:
    df_alerts = pd.DataFrame(alerts)
    df_alerts["created_at"] = pd.to_datetime(
        df_alerts["created_at"]
    ).dt.strftime("%Y-%m-%d %H:%M")

    def color_severity(val):
        colors = {
            "critical": "background-color: #ff4444; color: white",
            "high": "background-color: #ff8800; color: white",
            "medium": "background-color: #ffcc00; color: black",
            "low": "background-color: #44bb44; color: white"
        }
        return colors.get(val, "")

    display_cols = [
        "title", "risk_score", "severity",
        "status", "requires_verification", "created_at"
    ]
    styled = df_alerts[display_cols].style.map(
        color_severity, subset=["severity"]
    )
    st.dataframe(styled, use_container_width=True)

st.markdown("---")

# ── Risk Score Chart ──────────────────────────────────────────────────────────
st.markdown("## User Risk Scores")

if alerts:
    user_map = {u["id"]: u["username"] for u in users}
    risk_data = []

    for alert in alerts:
        username = user_map.get(alert["user_id"], alert["user_id"])
        risk_data.append({
            "user": username,
            "risk_score": alert["risk_score"],
            "severity": alert["severity"]
        })

    if risk_data:
        df_risk = pd.DataFrame(risk_data)
        df_risk = df_risk.sort_values("risk_score", ascending=False)

        color_map = {
            "critical": "#ff4444",
            "high": "#ff8800",
            "medium": "#ffcc00",
            "low": "#44bb44"
        }

        fig = px.bar(
            df_risk,
            x="user",
            y="risk_score",
            color="severity",
            color_discrete_map=color_map,
            title="Current Risk Score Per User",
            labels={"risk_score": "Risk Score (0-100)", "user": "User"},
            range_y=[0, 100]
        )
        fig.add_hline(
            y=70,
            line_dash="dash",
            line_color="red",
            annotation_text="Verification Threshold (70)"
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Alert Detail ──────────────────────────────────────────────────────────────
st.markdown("## Alert Detail")

if alerts:
    alert_titles = {a["id"]: a["title"] for a in alerts}
    selected_id = st.selectbox(
        "Select alert to inspect",
        options=list(alert_titles.keys()),
        format_func=lambda x: alert_titles[x]
    )

    selected = next((a for a in alerts if a["id"] == selected_id), None)
    if selected:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Alert Information**")
            st.write(f"**Title:** {selected['title']}")
            st.write(f"**Risk Score:** {selected['risk_score']} / 100")
            st.write(f"**Severity:** {selected['severity'].upper()}")
            st.write(f"**Status:** {selected['status']}")
            st.write(
                f"**Step-up Verification:** "
                f"{'🔴 REQUIRED' if selected['requires_verification'] else '✅ Not Required'}"
            )

        with col2:
            st.markdown("**Detected Anomalies**")
            description_lines = selected["description"].split("\n")
            for line in description_lines:
                if line.strip():
                    st.warning(line)

st.markdown("---")

# ── User Risk Table ───────────────────────────────────────────────────────────
st.markdown("## User Risk Levels")

if users:
    df_users = pd.DataFrame(users)
    display_user_cols = [
        "username", "department", "role", "risk_level"
    ]
    available = [c for c in display_user_cols if c in df_users.columns]

    def color_risk(val):
        colors = {
            "critical": "background-color: #ff4444; color: white",
            "high": "background-color: #ff8800; color: white",
            "medium": "background-color: #ffcc00; color: black",
            "low": "background-color: #44bb44; color: white"
        }
        return colors.get(val, "")

    styled_users = df_users[available].style.map(
        color_risk, subset=["risk_level"]
    )
    st.dataframe(styled_users, use_container_width=True)

st.markdown("---")
st.caption("UEBA Platform — Identity Trust Framework for Banking Security")