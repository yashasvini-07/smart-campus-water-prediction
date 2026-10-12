
from pathlib import Path

import pandas as pd

# Locate the anomaly detection results
BASE_DIR = Path(__file__).parent
RESULTS_FILE = BASE_DIR / "outputs" / "anomaly_detection_results.csv"
OUTPUT_DIR = BASE_DIR / "outputs"

# Load results
df = pd.read_csv(RESULTS_FILE)
df["date"] = pd.to_datetime(df["date"])

print("WATER CONSERVATION RECOMMENDATIONS")
print("=" * 45)

recommendations = []

# Check unusually high daily consumption
anomalies = df[df["anomaly_status"] == "Potential Anomaly"]

for _, row in anomalies.iterrows():
    if row["deviation_pct"] >= 40:
        message = (
            "Investigate the sudden increase in daily usage. "
            "Inspect tanks, valves and possible overflow."
        )
    else:
        message = (
            "Inspect the water supply and plumbing for possible leaks. "
            "Compare the reading with normal campus activity."
        )

    recommendations.append({
        "date": row["date"].strftime("%Y-%m-%d"),
        "issue": "Unusually high water consumption",
        "deviation_pct": round(row["deviation_pct"], 2),
        "recommendation": message,
    })

# Check high nighttime usage relative to daily usage
df["night_usage_pct"] = (
    df["night_litres"] / df["actual_litres"].replace(0, float("nan"))
) * 100

night_threshold = df["night_usage_pct"].median() * 1.5

high_night_usage = df[
    (df["night_usage_pct"] > night_threshold)
    & (df["anomaly_status"] == "Normal")
]

for _, row in high_night_usage.iterrows():
    recommendations.append({
        "date": row["date"].strftime("%Y-%m-%d"),
        "issue": "Unusually high nighttime usage",
        "deviation_pct": round(row["night_usage_pct"], 2),
        "recommendation": (
            "Review nighttime water use and inspect taps, pipes "
            "and storage tanks for possible continuous flow."
        ),
    })

# Save recommendations
recommendations_df = pd.DataFrame(recommendations)

output_file = OUTPUT_DIR / "water_conservation_recommendations.csv"
recommendations_df.to_csv(output_file, index=False)

# Display results
print(f"\nPotential issues identified: {len(recommendations_df)}")

if recommendations_df.empty:
    print("No unusual patterns requiring recommendations were found.")
else:
    for _, item in recommendations_df.iterrows():
        print(f"\nDate: {item['date']}")
        print(f"Issue: {item['issue']}")
        print(f"Recommendation: {item['recommendation']}")

print(f"\nRecommendations saved to: {output_file}")
print("\nRecommendation generation completed successfully.")
