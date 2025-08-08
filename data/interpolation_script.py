import pandas as pd

df = pd.read_csv("MOTOGP18_raw_1.csv", sep="\t")
df["lap_time"] = df["lap_time"].astype(float)

lap_offset = 0
resampled_laps = []

for lap_num, lap_df in df.groupby("lap_number"):
    # Convert lap_time to Timedelta and offset
    lap_df["lap_time"] = pd.to_timedelta(lap_df["lap_time"], unit="s")
    lap_df["lap_time"] += pd.to_timedelta(lap_offset, unit="s")

    # Drop duplicate timestamps
    lap_df = lap_df.drop_duplicates(subset="lap_time")

    # Set index
    lap_df.set_index("lap_time", inplace=True)

    # Split numeric and non-numeric columns
    numeric_cols = lap_df.select_dtypes(include=["number"]).columns
    non_numeric_cols = lap_df.select_dtypes(exclude=["number"]).columns

    # Resample numeric data
    numeric_resampled = lap_df[numeric_cols].resample("10ms").interpolate(method="linear")

    # Forward-fill non-numeric data (e.g., carId, trackId)
    non_numeric_resampled = lap_df[non_numeric_cols].resample("10ms").ffill()

    # Combine both
    resampled = pd.concat([numeric_resampled, non_numeric_resampled], axis=1)
    resampled["lap_number"] = lap_num
    resampled_laps.append(resampled)

    # Update offset
    lap_offset += lap_df.index.max().total_seconds() + 1

# Combine all laps
resampled_df = pd.concat(resampled_laps).reset_index()
resampled_df["lap_time"] = resampled_df["lap_time"].dt.total_seconds().round(3)

# Combine all laps
resampled_df = pd.concat(resampled_laps).reset_index()

# Convert lap_time back to seconds for readability
resampled_df["lap_time"] = resampled_df["lap_time"].dt.total_seconds().round(3)

# Save to CSV
resampled_df.to_csv("MOTOGP18_resampled_100Hz.csv", index=False)