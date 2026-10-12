
from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Project paths
BASE_DIR = Path(__file__).parent

DATA_FILE = BASE_DIR / "data" / "campus_water_simulated.csv"
ANOMALY_FILE = BASE_DIR / "outputs" / "anomaly_detection_results.csv"
RECOMMENDATION_FILE = (
    BASE_DIR / "outputs" / "water_conservation_recommendations.csv"
)

# Dashboard settings
st.set_page_config(
    page_title="Smart Campus Water Dashboard",
    page_icon="💧",
    layout="wide",
)

st.title("💧 Smart Campus Water Consumption Dashboard")
st.write(
    "Monitor water consumption, identify potential anomalies, "
    "and review water conservation recommendations."
)

st.warning(
    "This dashboard uses simulated data. Flagged records are "
    "potential anomalies, not confirmed leaks or overflows."
)

# Load existing files
required_files = [
    DATA_FILE,
    ANOMALY_FILE,
    RECOMMENDATION_FILE,
]

missing_files = [file.name for file in required_files if not file.exists()]

if missing_files:
    st.error("The following files are missing:")
    for filename in missing_files:
        st.write(f"- {filename}")
    st.info(
        "Run your existing Python modules first to generate the "
        "required CSV files."
    )
    st.stop()

try:
    df = pd.read_csv(DATA_FILE)
    anomaly_df = pd.read_csv(ANOMALY_FILE)
    recommendations_df = pd.read_csv(RECOMMENDATION_FILE)
except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError) as error:
    st.error(f"Unable to read a project CSV file: {error}")
    st.stop()

# Validate required columns
required_data_columns = [
    "date",
    "expected_litres",
    "actual_litres",
]

required_anomaly_columns = [
    "date",
    "actual_litres",
    "deviation_pct",
    "robust_z_score",
    "anomaly_status",
]

required_recommendation_columns = [
    "date",
    "issue",
    "deviation_pct",
    "recommendation",
]

if df.empty or anomaly_df.empty:
    st.error("The dataset or anomaly results CSV is empty.")
    st.stop()

missing_columns = (
    set(required_data_columns) - set(df.columns)
    | set(required_anomaly_columns) - set(anomaly_df.columns)
    | set(required_recommendation_columns)
    - set(recommendations_df.columns)
)

if missing_columns:
    st.error(
        "Required columns are missing: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()

# Prepare data
df["date"] = pd.to_datetime(df["date"], errors="coerce")
anomaly_df["date"] = pd.to_datetime(
    anomaly_df["date"], errors="coerce"
)
recommendations_df["date"] = pd.to_datetime(
    recommendations_df["date"], errors="coerce"
)

df = df.dropna(subset=["date"]).sort_values("date")
anomaly_df = anomaly_df.dropna(subset=["date"]).sort_values("date")

df["actual_litres"] = pd.to_numeric(
    df["actual_litres"], errors="coerce"
)
df["expected_litres"] = pd.to_numeric(
    df["expected_litres"], errors="coerce"
)

df = df.dropna(subset=["actual_litres", "expected_litres"])

if df.empty:
    st.error("No valid consumption records are available.")
    st.stop()

# Summary metrics
flagged_count = (
    anomaly_df["anomaly_status"].eq("Potential Anomaly").sum()
)

total_consumption = df["actual_litres"].sum()
average_consumption = df["actual_litres"].mean()
maximum_consumption = df["actual_litres"].max()

st.subheader("Consumption Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Days Recorded", f"{len(df):,}")
col2.metric("Total Consumption", f"{total_consumption:,.0f} L")
col3.metric("Average Daily Use", f"{average_consumption:,.0f} L")
col4.metric("Potential Anomalies", f"{flagged_count:,}")

# Actual vs expected chart
st.subheader("Actual vs Expected Water Consumption")

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    df["date"],
    df["actual_litres"],
    label="Actual consumption",
)

ax.plot(
    df["date"],
    df["expected_litres"],
    label="Expected consumption",
)

ax.set_xlabel("Date")
ax.set_ylabel("Water consumption (litres)")
ax.grid(True, alpha=0.3)
ax.legend()
fig.autofmt_xdate()
fig.tight_layout()

st.pyplot(fig)
plt.close(fig)

# Consumption statistics
st.subheader("Consumption Statistics")

stat_col1, stat_col2, stat_col3 = st.columns(3)

stat_col1.metric(
    "Maximum Daily Consumption",
    f"{maximum_consumption:,.0f} L",
)
stat_col2.metric(
    "Minimum Daily Consumption",
    f"{df['actual_litres'].min():,.0f} L",
)
stat_col3.metric(
    "Median Daily Consumption",
    f"{df['actual_litres'].median():,.0f} L",
)

# Anomaly records
st.subheader("Potential Anomaly Records")

flagged_df = anomaly_df[
    anomaly_df["anomaly_status"].eq("Potential Anomaly")
].copy()

if flagged_df.empty:
    st.success("No potential anomalies were found.")
else:
    display_columns = [
        "date",
        "expected_litres",
        "actual_litres",
        "deviation_pct",
        "robust_z_score",
    ]

    st.dataframe(
        flagged_df[display_columns].round(2),
        use_container_width=True,
        hide_index=True,
    )

# Recommendations
st.subheader("Water Conservation Recommendations")

if recommendations_df.empty:
    st.info("No recommendations are available.")
else:
    st.dataframe(
        recommendations_df[
            [
                "date",
                "issue",
                "deviation_pct",
                "recommendation",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "Project module: Anomaly Detection & Water Conservation. "
    "Unusual consumption should be investigated before concluding "
    "that a leak or overflow has occurred."
)
