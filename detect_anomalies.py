
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Project paths
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "campus_water_simulated.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Load the dataset
df = pd.read_csv(DATA_FILE)
df["date"] = pd.to_datetime(df["date"])

# Calculate deviation from expected usage
df["deviation_litres"] = (
    df["actual_litres"] - df["expected_litres"]
)

df["deviation_pct"] = (
    df["deviation_litres"]
    / df["expected_litres"].replace(0, np.nan)
) * 100

# Use the median and MAD to identify unusually high deviations
median_deviation = df["deviation_pct"].median()

mad = (
    df["deviation_pct"] - median_deviation
).abs().median()

# Avoid division by zero if all deviations are identical
if mad == 0:
    df["robust_z_score"] = 0.0
else:
    df["robust_z_score"] = (
        0.6745
        * (df["deviation_pct"] - median_deviation)
        / mad
    )

# Flag unusually high consumption
df["anomaly_status"] = np.where(
    df["robust_z_score"] > 3.5,
    "Potential Anomaly",
    "Normal"
)

# Save results
output_file = OUTPUT_DIR / "anomaly_detection_results.csv"
df.to_csv(output_file, index=False)

# Display results
anomalies = df[df["anomaly_status"] == "Potential Anomaly"]

print("ANOMALY DETECTION RESULTS")
print("=" * 40)
print(f"Total records analysed: {len(df)}")
print(f"Potential anomalies found: {len(anomalies)}")

print("\nPotential anomalous days:")
if anomalies.empty:
    print("No unusually high deviations detected.")
else:
    print(
        anomalies[
            [
                "date",
                "expected_litres",
                "actual_litres",
                "deviation_pct",
                "robust_z_score",
            ]
        ].round(2).to_string(index=False)
    )

print(f"\nResults saved to: {output_file}")

# Plot actual consumption and highlight flagged days
plt.figure(figsize=(12, 6))

plt.plot(
    df["date"],
    df["actual_litres"],
    label="Actual consumption",
)

plt.plot(
    df["date"],
    df["expected_litres"],
    label="Expected consumption",
)

plt.scatter(
    anomalies["date"],
    anomalies["actual_litres"],
    color="red",
    label="Potential anomalies",
    zorder=3,
)

plt.title("Campus Water Consumption Anomaly Detection")
plt.xlabel("Date")
plt.ylabel("Water consumption (litres)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plot_file = OUTPUT_DIR / "anomaly_detection_plot.png"
plt.savefig(plot_file, dpi=150)
plt.close()

print(f"Anomaly graph saved to: {plot_file}")
