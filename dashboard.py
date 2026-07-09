import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

# ====================================
# Page Configuration
# ====================================

st.set_page_config(
    page_title="Cybersecurity Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Cybersecurity Dashboard")

# ====================================
# Load Incident Logs
# ====================================

LOG_FILE = "incident_logs.json"

if not os.path.exists(LOG_FILE):

    st.warning("No incident logs found.")
    st.stop()

try:

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

except Exception as e:

    st.error(f"Error loading logs: {e}")
    st.stop()

if len(logs) == 0:

    st.warning("No incidents recorded yet.")
    st.stop()

# ====================================
# Create DataFrame
# ====================================

df = pd.DataFrame(logs)

# ====================================
# Timestamp Processing
# ====================================

if "timestamp" in df.columns:

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    df["date"] = df["timestamp"].dt.date

# ====================================
# Dashboard Metrics
# ====================================

total_incidents = len(df)

critical_count = len(
    df[df["severity"] == "Critical"]
)

high_count = len(
    df[df["severity"] == "High"]
)

medium_count = len(
    df[df["severity"] == "Medium"]
)

low_count = len(
    df[df["severity"] == "Low"]
)

st.subheader("📈 Incident Summary")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total", total_incidents)
col2.metric("Critical", critical_count)
col3.metric("High", high_count)
col4.metric("Medium", medium_count)
col5.metric("Low", low_count)

st.markdown("---")

# ====================================
# Threat Distribution Chart
# ====================================

st.subheader("🛡️ Threat Distribution")

threat_counts = df["threat"].value_counts()

fig1, ax1 = plt.subplots()

ax1.pie(
    threat_counts,
    labels=threat_counts.index,
    autopct="%1.1f%%"
)

st.pyplot(fig1)

# ====================================
# Severity Distribution Chart
# ====================================

st.subheader("⚠️ Severity Distribution")

severity_counts = df["severity"].value_counts()

fig2, ax2 = plt.subplots()

ax2.bar(
    severity_counts.index,
    severity_counts.values
)

ax2.set_xlabel("Severity")
ax2.set_ylabel("Count")

st.pyplot(fig2)

# ====================================
# Incident Trend Chart
# ====================================

if "date" in df.columns:

    st.subheader("📈 Incident Trend")

    trend = (
        df.groupby("date")
        .size()
        .reset_index(name="count")
    )

    st.line_chart(
        trend.set_index("date")
    )

# ====================================
# Recent Incidents
# ====================================

st.subheader("📋 Recent Incidents")

st.dataframe(
    df.tail(10),
    use_container_width=True
)

# ====================================
# Full Incident Log
# ====================================

with st.expander("View Full Incident Log"):

    st.dataframe(
        df,
        use_container_width=True
    )