import pandas as pd
import time

# Path to your CSV
csv_path = "data/SachenRing_M1_Rossi.csv"

# Read CSV with SEMICOLON separator
df = pd.read_csv(csv_path, sep=';')

print("Column names in the CSV:")
print(df.columns.tolist())
print("\n" + "=" * 80 + "\n")

# Clean -1 values to NaN
df.replace(-1, pd.NA, inplace=True)

# Convert total_time to numeric (in case it's read as string)
df['total_time'] = pd.to_numeric(df['total_time'], errors='coerce')

# Filter out rows where validBin = 0 (invalid data)
df = df[df['validBin'] == 1].reset_index(drop=True)

# Sort by total_time to ensure chronological order
df = df.sort_values('total_time').reset_index(drop=True)

print("First 5 rows of valid data:")
print(df.head())
print("\n" + "=" * 80 + "\n")

# Simulation speed multiplier
SPEED = 1  # Higher is faster, 1 is real time

print(f"Starting MotoGP Telemetry data stream (Speed: {SPEED}x)...\n")

# STEP 3: Stream the data
for idx, row in df.iterrows():
    # Display telemetry info
    print(f"[Lap {row['lapNum']}] {row['carId']} | "
          f"Speed: {row['velocity_X']:.2f} m/s | "
          f"RPM: {row['rpm']:.0f} | "
          f"Gear: {row['gear']} | "
          f"Throttle: {row['throttle']:.1f}% | "
          f"Brake: {row['brake_0']:.1f} | "
          f"Time: {row['total_time']:.3f}s")

    # Calculate delay based on time difference
    if idx < len(df) - 1:
        t_now = row['total_time']
        t_next = df.loc[idx + 1, 'total_time']

        # Only sleep if both times are valid
        if pd.notna(t_now) and pd.notna(t_next):
            sleep_time = max((t_next - t_now) / SPEED, 0.001)
            time.sleep(sleep_time)
        else:
            time.sleep(0.01)
    else:
        time.sleep(0.01)

print("\n" + "=" * 80)
print("Stream complete!")
