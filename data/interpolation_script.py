import pandas as pd

# Load your telemetry data
df = pd.read_csv("MOTOGP18_raw_1.csv", sep="\t")
df["lap_time"] = df["lap_time"].astype(float)

# Identify numeric and non-numeric columns
numeric_cols = ["gforce_X", "gforce_Y", "gforce_Z"] + list(
    df.select_dtypes(include=["number"]).columns.difference(["lap_time", "lap_number", "gforce_X", "gforce_Y", "gforce_Z"])
)
non_numeric_cols = df.select_dtypes(exclude=["number"]).columns

interpolated_laps = []

for lap_num, lap_df in df.groupby("lap_number"):
    # Drop duplicate lap_time by averaging only numeric columns
    numeric_part = lap_df[["lap_time"] + list(numeric_cols)].groupby("lap_time").mean().reset_index()

    # Interpolate numeric data
    numeric_part.set_index("lap_time", inplace=True)
    numeric_part = numeric_part.interpolate(method="linear").reset_index()

    # Forward-fill non-numeric columns from first valid row
    static_values = lap_df[non_numeric_cols].iloc[0]
    for col in non_numeric_cols:
        numeric_part[col] = static_values[col]

    # Add lap_number back
    numeric_part["lap_number"] = lap_num
    interpolated_laps.append(numeric_part)

# Combine all laps
interpolated_df = pd.concat(interpolated_laps, ignore_index=True)

# Save to CSV
interpolated_df.to_csv("MOTOGP18_interpolated_by_time.csv", index=False)
print("✅ Interpolated telemetry saved to MOTOGP18_interpolated_by_time.csv")