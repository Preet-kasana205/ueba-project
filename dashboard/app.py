import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="UEBA Platform",
    page_icon="🛡️",
    layout="wide"
)


# ── Auth Helpers ──────────────────────────────────────────────────────────────
def get_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_get(path):
    try:
        r = requests.get(f"{BASE_URL}{path}", headers=get_headers())
        return r.json() if r.status_code == 200 else []
    except:
        return []


def api_post(path, **kwargs):
    try:
        return requests.post(f"{BASE_URL}{path}", headers=get_headers(), **kwargs)
    except:
        return None


def api_patch(path, **kwargs):
    try:
        return requests.patch(f"{BASE_URL}{path}", headers=get_headers(), **kwargs)
    except:
        return None


# ── Login Gate ────────────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.title("🛡️ UEBA Platform")
    st.markdown("### Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", type="primary"):
        try:
            r = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": username, "password": password}
            )
            if r.status_code == 200:
                st.session_state["token"] = r.json()["access_token"]
                st.rerun()
            else:
                st.error("Invalid username or password")
        except Exception as e:
            st.error(f"Could not connect to API: {e}")
    st.stop()


# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_logout = st.columns([8, 1])
with col_title:
    st.title("🛡️ UEBA Platform")
    st.markdown(
        "**User and Entity Behaviour Analytics** — "
        "Identity Trust Framework for Insider Threat Detection"
    )
with col_logout:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Logout"):
        del st.session_state["token"]
        st.rerun()

st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🎮 Demo Controls")
st.sidebar.markdown(
    "This platform monitors user behaviour and detects "
    "insider threats using statistical baselines and rule-based detection."
)
st.sidebar.markdown("---")

st.sidebar.markdown("### Quick Demo")
st.sidebar.markdown(
    "Loads 30 days of normal activity for 3 users, "
    "injects a suspicious scenario, and runs full detection."
)

if st.sidebar.button("🚀 Run Full Demo", type="primary", use_container_width=True):
    progress = st.sidebar.progress(0)
    status = st.sidebar.empty()

    try:
        status.text("Creating users...")
        users_to_create = [
            {"external_id": "AD\\john.smith", "username": "john.smith", "department": "Finance", "role": "analyst"},
            {"external_id": "AD\\preet.kasana", "username": "preet.kasana", "department": "Engineering", "role": "developer"},
            {"external_id": "AD\\sara.jones", "username": "sara.jones", "department": "HR", "role": "hr_manager"},
        ]
        for user in users_to_create:
            api_post("/users", json=user)
        progress.progress(20)

        status.text("Loading 30 days of activity logs...")
        try:
            with open("data/sample_logs/events.json") as f:
                events = json.load(f)
            batch_size = 100
            for i in range(0, len(events), batch_size):
                api_post("/ingest/events/batch", json={"events": events[i:i + batch_size]})
        except FileNotFoundError:
            status.text("Sample data not found. Run the generator first.")
        progress.progress(40)

        status.text("Normalizing events...")
        api_post("/ingest/normalize")
        progress.progress(60)

        status.text("Computing behavioural baseline...")
        api_post("/baseline/compute")
        progress.progress(75)

        status.text("Running anomaly detection...")
        api_post("/detection/run")
        progress.progress(88)

        status.text("Generating alerts...")
        api_post("/alerts/generate")
        progress.progress(100)

        status.text("✅ Demo complete")
        st.sidebar.success("Demo loaded. Scroll down to see detected threats.")
        st.cache_data.clear()

    except Exception as e:
        st.sidebar.error(f"Error: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### Manual Controls")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Normalize", use_container_width=True):
        r = api_post("/ingest/normalize")
        st.sidebar.info(f"Done: {r.json()}")
with col2:
    if st.button("Baselines", use_container_width=True):
        r = api_post("/baseline/compute")
        st.sidebar.info(f"Done: {r.json()}")

col3, col4 = st.sidebar.columns(2)
with col3:
    if st.button("Detect", use_container_width=True):
        r = api_post("/detection/run")
        st.sidebar.info(f"Done: {r.json()}")
with col4:
    if st.button("Alerts", use_container_width=True):
        r = api_post("/alerts/generate")
        st.sidebar.info(f"Done: {r.json()}")

if st.sidebar.button("🔄 Refresh Dashboard", use_container_width=True):
    st.cache_data.clear()
    st.rerun()


# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=10)
def load_alerts(token):
    try:
        r = requests.get(f"{BASE_URL}/alerts", headers={"Authorization": f"Bearer {token}"})
        return r.json() if r.status_code == 200 else []
    except:
        return []


@st.cache_data(ttl=10)
def load_users(token):
    try:
        r = requests.get(f"{BASE_URL}/users", headers={"Authorization": f"Bearer {token}"})
        return r.json() if r.status_code == 200 else []
    except:
        return []


token = st.session_state["token"]
alerts = load_alerts(token)
users = load_users(token)
user_map = {u["id"]: u for u in users}

# ── Empty State ───────────────────────────────────────────────────────────────
if not alerts and not users:
    st.info(
        "👈 No data loaded yet. Click **Run Full Demo** in the sidebar to "
        "load sample data and see the platform in action."
    )
    st.markdown("### How This Platform Works")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 📥 Ingest")
        st.markdown("Collects logs from authentication systems, file servers, and network devices. Each event is checksummed for forensic integrity.")
    with col2:
        st.markdown("#### 🧠 Analyse")
        st.markdown("Builds behavioural baselines per user — normal login hours, known devices, typical data volumes. Detects statistical deviations using z-score analysis.")
    with col3:
        st.markdown("#### 🚨 Alert")
        st.markdown("Generates explainable alerts with risk scores. Automatically triggers step-up verification when risk exceeds threshold.")
    st.stop()

# ── Fleet Metrics ─────────────────────────────────────────────────────────────
st.markdown("## 📊 Fleet Overview")

open_alerts = [a for a in alerts if a["status"] == "open"]
critical = [a for a in alerts if a["severity"] == "critical"]
verification_needed = [a for a in alerts if a["requires_verification"]]
high_risk_users = [u for u in users if u["risk_level"] in ("high", "critical")]

col1, col2, col3, col4 = st.columns(4)
col1.metric("🚨 Open Alerts", len(open_alerts))
col2.metric("🔴 Critical Severity", len(critical))
col3.metric("🔐 Verification Required", len(verification_needed))
col4.metric("⚠️ High Risk Users", len(high_risk_users))

st.markdown("---")

# ── Risk Score Chart ──────────────────────────────────────────────────────────
st.markdown("## 👤 User Risk Scores")

risk_data = []
for alert in alerts:
    user = user_map.get(alert["user_id"], {})
    risk_data.append({
        "user": user.get("username", alert["user_id"]),
        "risk_score": alert["risk_score"],
        "severity": alert["severity"],
        "department": user.get("department", "Unknown")
    })

if risk_data:
    df_risk = pd.DataFrame(risk_data).sort_values("risk_score", ascending=False)
    color_map = {"critical": "#ff4444", "high": "#ff8800", "medium": "#ffcc00", "low": "#44bb44"}
    fig = px.bar(
        df_risk, x="user", y="risk_score", color="severity",
        color_discrete_map=color_map,
        title="Current Risk Score Per User",
        labels={"risk_score": "Risk Score (0-100)", "user": "User"},
        range_y=[0, 100], hover_data=["department"]
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="🔐 Step-up Verification Threshold")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Alerts Table ──────────────────────────────────────────────────────────────
st.markdown("## 🚨 Active Alerts")

if alerts:
    severity_colors = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    for alert in sorted(alerts, key=lambda x: x["risk_score"], reverse=True):
        user = user_map.get(alert["user_id"], {})
        icon = severity_colors.get(alert["severity"], "⚪")

        with st.expander(
            f"{icon} {alert['title']} — Risk Score: {alert['risk_score']}/100",
            expanded=alert["severity"] == "critical"
        ):
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"**User:** {user.get('username', 'Unknown')}")
            col1.markdown(f"**Department:** {user.get('department', 'Unknown')}")
            col2.markdown(f"**Severity:** {alert['severity'].upper()}")
            col2.markdown(f"**Status:** {alert['status']}")
            col3.markdown(f"**Risk Score:** {alert['risk_score']} / 100")
            col3.markdown(f"**Step-up Verification:** {'🔴 REQUIRED' if alert['requires_verification'] else '✅ Not Required'}")

            st.markdown("**Detected Anomalies:**")
            for line in alert["description"].split("\n"):
                if line.strip():
                    st.warning(line)

            st.markdown("**Analyst Actions:**")
            action_col1, action_col2, action_col3 = st.columns(3)
            with action_col1:
                if st.button("✅ Acknowledge", key=f"ack_{alert['id']}"):
                    api_patch(f"/alerts/{alert['id']}/status", params={"status": "acknowledged"})
                    st.cache_data.clear()
                    st.rerun()
            with action_col2:
                if st.button("⬆️ Escalate", key=f"esc_{alert['id']}"):
                    api_patch(f"/alerts/{alert['id']}/status", params={"status": "escalated"})
                    st.cache_data.clear()
                    st.rerun()
            with action_col3:
                if st.button("❌ Close", key=f"cls_{alert['id']}"):
                    api_patch(f"/alerts/{alert['id']}/status", params={"status": "closed"})
                    st.cache_data.clear()
                    st.rerun()

st.markdown("---")

# ── User Risk Table ───────────────────────────────────────────────────────────
st.markdown("## 👥 User Risk Levels")

if users:
    df_users = pd.DataFrame(users)
    available = [c for c in ["username", "department", "role", "risk_level"] if c in df_users.columns]

    def color_risk(val):
        colors = {"critical": "background-color: #ff4444; color: white", "high": "background-color: #ff8800; color: white", "medium": "background-color: #ffcc00; color: black", "low": "background-color: #44bb44; color: white"}
        return colors.get(val, "")

    st.dataframe(df_users[available].style.map(color_risk, subset=["risk_level"]), use_container_width=True)

st.markdown("---")

# ── How It Works ──────────────────────────────────────────────────────────────
st.markdown("## ⚙️ How Detection Works")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("#### Unusual Login Time")
    st.markdown("Computes each user's mean login hour and standard deviation over 30 days. Flags logins more than 2 standard deviations from their normal time using z-score analysis.")
with col2:
    st.markdown("#### New Device Detection")
    st.markdown("Maintains a registry of known devices per user. Any login from a device not seen in the user's 30-day history triggers a high severity alert.")
with col3:
    st.markdown("#### Data Volume Spike")
    st.markdown("Tracks daily data transfer volume per user. Downloads exceeding 2 standard deviations above the user's normal volume trigger a critical alert.")

st.markdown("---")
st.caption("UEBA Platform — Identity Trust Framework | Detects insider threats through behavioural analytics")