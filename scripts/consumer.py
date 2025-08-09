from kafka import KafkaConsumer
import json
import math

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

    # Extract and map fields
    lap_time = data.get("lap_time", 0)
    speed = data.get("wheel_speed_0", "N/A")
    throttle = data.get("throttle", "N/A")
    brake = data.get("brake_0", "N/A")
    lap = data.get("lap_number", "N/A")

    # Compute g-force magnitude
    gx = data.get("gforce_X", 0)
    gy = data.get("gforce_Y", 0)
    gz = data.get("gforce_Z", 0)
    g_force = round(math.sqrt(gx**2 + gy**2 + gz**2), 2)

    print(f"Lap {lap} | Time: {lap_time:.3f}s | Speed: {speed} km/h | Throttle: {throttle}% | Brake: {brake}% | G-Force: {g_force}")