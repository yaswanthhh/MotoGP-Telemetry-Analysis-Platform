import pandas as pd
import time
import json
from kafka import KafkaProducer

# Load telemetry data
df = pd.read_csv("MOTOGP18_interpolated_by_time.csv")

# Ensure lap_time is float and sorted by lapNum and lap_time
df["lap_time"] = df["lap_time"].astype(float).round(3)
df["cumulative_time"] = df.groupby("lapNum")["lap_time"].cumsum()

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

try:
    for i in range(len(df) - 1):
        current_row = df.iloc[i].to_dict()
        next_row = df.iloc[i + 1].to_dict()

        # Send current row
        producer.send("motogp-telemetry", value=current_row)

        # Calculate delay
        delay = max(next_row["lap_time"] - current_row["lap_time"], 0)
        time.sleep(delay)

    # Send final row
    producer.send("motogp-telemetry", value=df.iloc[-1].to_dict())

except Exception as e:
    print(f"❌ Streaming error: {e}")

finally:
    producer.flush()
    producer.close()
    print("✅ Telemetry stream completed.")