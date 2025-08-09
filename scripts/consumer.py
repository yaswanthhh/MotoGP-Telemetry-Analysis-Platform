from kafka import KafkaConsumer
import json
import pandas as pd

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'motogp-telemetry',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='motogp-consumer-group'
)

print("📡 Listening to motogp-telemetry stream...\n")

for message in consumer:
    data = message.value

    # ✅ Convert to single-row DataFrame
    df_row = pd.DataFrame([data])

    # ✅ Print all columns in a readable format
    print(df_row.to_string(index=False))