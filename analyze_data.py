
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Locate project folders
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "campus_water_simulated.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Load the dataset
df = pd.read_csv(DATA_FILE)

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

print("WATER CONSUMPTION DATA ANALYSIS")
print("=" * 40)

# Dataset dimensions
print(f"\nNumber of records: {len(df)}")
print(f"Number of columns: {len(df.columns)}")

# Check missing values
print("\nMissing values in each column:")
print(df.isnull().sum())

# Check duplicate records
print("\nNumber of duplicate rows:", df.duplicated().sum())

# Summary statistics
print("\nWater consumption summary (litres):")
print(
    df[["expected_litres", "actual_litres", "night_litres"]]
    .describe()
    .round(2)
)

# Average consumption
print(
    "\nAverage actual daily consumption:",
    round(df["actual_litres"].mean(), 2),
    "litres"
)

# Plot actual and expected water consumption
plt.figure(figsize=(12, 6))

plt.plot(
    df["date"],
    df["actual_litres"],
    label="Actual consumption",
    linewidth=1.5,
)

plt.plot(
    df["date"],
    df["expected_litres"],
    label="Expected consumption",
    linewidth=1.5,
)

plt.title("Campus Water Consumption: Actual vs Expected")
plt.xlabel("Date")
plt.ylabel("Water consumption (litres)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plot_file = OUTPUT_DIR / "water_consumption_analysis.png"
plt.savefig(plot_file, dpi=150)
plt.close()

print(f"\nConsumption graph saved to: {plot_file}")
print("\nData analysis completed successfully.")
