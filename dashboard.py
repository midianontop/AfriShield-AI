import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

# ====================================
# Page Configuration
# ====================================

st.set_page_config(
    page_title="AfriShield AI Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AfriShield AI Security Dashboard")

# ====================================
# Load Incident Logs
# ====================================

LOG_FILE = "incident_logs.json"

if not os.path.exists(LOG_FILE):
    st.warning("No incident logs found.")
    st.stop()

try:
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = json.load(f)

except Exception as e:
    st.error(f"Error loading logs: {e}")
    st.stop()

if not logs:
    st.warning("No incidents recorded yet.")
    st.stop()

# ====================================
# Create DataFrame
# ====================================

df = pd.DataFrame(logs)

# ====================================
# Process Timestamp
# ====================================

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df["date"] = df["timestamp"].dt.date

# ====================================
# Process Confidence
# ====================================

if "confidence" in df.columns:
    df["confidence"] = pd.to_numeric(
        df["confidence"],
        errors="coerce"
    )

# ====================================
# Clean Severity Values
# ====================================

if "severity" in df.columns:

    df["severity_clean"] = (
        df["severity"]
        .astype(str)
        .str.replace("🔴 ", "", regex=False)
        .str.replace("🟠 ", "", regex=False)
        .str.replace("🟡 ", "", regex=False)
        .str.replace("🟢 ", "", regex=False)
    )

else:
    df["severity_clean"] = "Unknown"

# ====================================
# Sidebar Filters
# ====================================

st.sidebar.header("⚙️ Dashboard Controls")

severity_options = sorted(
    df["severity_clean"].dropna().unique()
)

selected_severity = st.sidebar.multiselect(
    "Filter Severity",
    options=severity_options,
    default=severity_options
)

filtered_df = df[
    df["severity_clean"].isin(
        selected_severity
    )
]

# ====================================
# Dashboard Metrics
# ====================================

total_incidents = len(filtered_df)

critical_count = len(
    filtered_df[
        filtered_df["severity_clean"] == "Critical"
    ]
)

high_count = len(
    filtered_df[
        filtered_df["severity_clean"] == "High"
    ]
)

medium_count = len(
    filtered_df[
        filtered_df["severity_clean"] == "Medium"
    ]
)

low_count = len(
    filtered_df[
        filtered_df["severity_clean"] == "Low"
    ]
)

avg_confidence = 0

if (
    "confidence" in filtered_df.columns
    and not filtered_df["confidence"].isna().all()
):
    avg_confidence = round(
        filtered_df["confidence"].mean(),
        1
    )

# ====================================
# Most Common Threat
# ====================================

most_common_threat = "N/A"

if (
    "threat" in filtered_df.columns
    and not filtered_df["threat"].dropna().empty
):
    most_common_threat = (
        filtered_df["threat"]
        .value_counts()
        .idxmax()
    )

# ====================================
# Metrics Display
# ====================================

st.subheader("📈 Security Overview")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Total", total_incidents)
col2.metric("Critical", critical_count)
col3.metric("High", high_count)
col4.metric("Medium", medium_count)
col5.metric("Low", low_count)
col6.metric(
    "Avg Confidence",
    f"{avg_confidence}%"
)

st.info(
    f"🛡️ Most Common Threat: {most_common_threat}"
)

st.markdown("---")

# ====================================
# Threat Distribution
# ====================================

if "threat" in filtered_df.columns:

    st.subheader("🛡️ Threat Distribution")

    threat_counts = (
        filtered_df["threat"]
        .fillna("Unknown")
        .value_counts()
    )

    fig1, ax1 = plt.subplots()

    ax1.pie(
        threat_counts.values,
        labels=threat_counts.index,
        autopct="%1.1f%%"
    )

    st.pyplot(fig1)

# ====================================
# Severity Distribution
# ====================================

st.subheader("⚠️ Severity Distribution")

severity_counts = (
    filtered_df["severity_clean"]
    .value_counts()
)

fig2, ax2 = plt.subplots()

ax2.bar(
    severity_counts.index,
    severity_counts.values
)

ax2.set_xlabel("Severity")
ax2.set_ylabel("Incidents")

st.pyplot(fig2)

# ====================================
# Incident Trend
# ====================================

if "date" in filtered_df.columns:

    st.subheader("📈 Incident Trend")

    trend = (
        filtered_df.groupby("date")
        .size()
        .reset_index(name="count")
    )

    if not trend.empty:

        st.line_chart(
            trend.set_index("date")
        )

# ====================================
# Confidence Trend
# ====================================

if (
    "confidence" in filtered_df.columns
    and "timestamp" in filtered_df.columns
):

    confidence_df = (
        filtered_df
        .dropna(subset=["confidence"])
        .sort_values("timestamp")
    )

    if not confidence_df.empty:

        st.subheader(
            "🎯 Confidence Trend"
        )

        st.line_chart(
            confidence_df.set_index(
                "timestamp"
            )["confidence"]
        )

# ====================================
# Recent Incidents
# ====================================

st.subheader("📋 Recent Incidents")

display_columns = [
    col for col in [
        "timestamp",
        "threat",
        "severity",
        "confidence",
        "question"
    ]
    if col in filtered_df.columns
]

st.dataframe(
    filtered_df[display_columns].tail(20),
    use_container_width=True
)

# ====================================
# Export Reports
# ====================================

st.subheader("⬇️ Export Reports")

csv_data = filtered_df.to_csv(
    index=False
)

json_data = filtered_df.to_json(
    orient="records",
    indent=4,
    date_format="iso"
)

col1, col2 = st.columns(2)

with col1:

    st.download_button(
        "📥 Download CSV",
        csv_data,
        "afrishield_report.csv",
        "text/csv"
    )

with col2:

    st.download_button(
        "📥 Download JSON",
        json_data,
        "afrishield_report.json",
        "application/json"
    )

# ====================================
# Full Incident Log
# ====================================

with st.expander("🔍 View Full Incident Log"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )