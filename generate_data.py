
from pathlib import Path

import numpy as np
import pandas as pd

# Generate reproducible sample data
rng = np.random.default_rng(42)

dates = pd.date_range("2026-02-01", periods=240, freq="D")
rows = []

# Illustrative abnormal events for testing
high_usage_dates = {
    "2026-03-10",
    "2026-06-05",
    "2026-07-14",
    "2026-09-02",
}

high_night_usage_dates = {
    "2026-04-08",
    "2026-04-09",
    "2026-04-10",
    "2026-08-22",
}

for date in dates:
    weekend = int(date.weekday() >= 5)

    vacation = int(
        pd.Timestamp("2026-05-18")
        <= date
        <= pd.Timestamp("2026-06-28")
    )

    occupancy = (
        rng.uniform(15, 25)
        if vacation
        else rng.uniform(75, 95)
    )

    temperature = rng.normal(30, 2)
    rainfall = (
        rng.exponential(5)
        if rng.random() < 0.25
        else 0
    )

    # Expected consumption in litres
    expected = 120000 + 3200 * occupancy

    if weekend:
        expected *= 0.92

    if vacation:
        expected *= 0.65

    expected *= 1 + 0.008 * (temperature - 28)

    actual = expected * rng.normal(1.0, 0.04)
    night = actual * rng.normal(0.06, 0.008)

    date_key = date.strftime("%Y-%m-%d")
    event = "none"

    if date_key in high_usage_dates:
        actual *= 1.6
        event = "high_usage_like"

    if date_key in high_night_usage_dates:
        actual *= 1.25
        night *= 4
        event = "high_night_usage_like"

    rows.append({
        "date": date_key,
        "day_of_week": date.day_name(),
        "is_weekend": weekend,
        "is_vacation": vacation,
        "hostel_occupancy_pct": round(occupancy, 1),
        "temperature_c": round(temperature, 1),
        "rainfall_mm": round(rainfall, 1),
        "expected_litres": round(expected),
        "actual_litres": round(actual),
        "night_litres": round(night),
        "simulated_event": event,
    })

df = pd.DataFrame(rows)

output_dir = Path(__file__).parent / "data"
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "campus_water_simulated.csv"
df.to_csv(output_file, index=False)

print("Simulated water dataset created successfully.")
print(f"Rows: {len(df)}")
print(f"Saved to: {output_file}")
print("\nFirst five records:")
print(df.head().to_string(index=False))

print(
    "\nSimulated abnormal-event days:",
    (df["simulated_event"] != "none").sum()
)
