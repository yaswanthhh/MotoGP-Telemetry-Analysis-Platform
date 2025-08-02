import time
import random
import csv
from datetime import datetime

# Configuration
OUTPUT_FILE = "data/advanced_telemetry.csv"
SIMULATION_DURATION = 60  # seconds
INTERVAL = 1  # seconds
RIDERS = ["A.Marquez", "V.Rossi", "M.Marquez"]  # Example rider IDs

# Helper functions
def get_gear(speed):
    if speed < 40: return 1
    elif speed < 80: return 2
    elif speed < 130: return 3
    elif speed < 180: return 4
    elif speed < 240: return 5
    else: return 6

def get_sector(elapsed):
    return f"Sector {((elapsed // 10) % 3) + 1}"

def generate_telemetry(rider_id, lap, elapsed):
    speed = round(random.uniform(80, 340), 2)
    rpm = random.randint(8000, 18000)
    throttle = round(random.uniform(0, 100), 2)
    lean = round(random.uniform(-60, 60), 2)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "rider_id": rider_id,
        "lap": lap,
        "sector": get_sector(elapsed),
        "speed_kph": speed,
        "rpm": rpm,
        "gear": get_gear(speed),
        "throttle_pct": throttle,
        "brake_pressure": round(random.uniform(0, 100), 2),
        "lean_angle_deg": lean,
        "gps_lat": round(random.uniform(43.5, 43.6), 6),
        "gps_long": round(random.uniform(-0.3, -0.2), 6),
        "tire_temp_c": round(random.uniform(60, 120), 2),
        "engine_temp_c": round(70 + (rpm - 8000) / 200, 2),
        "front_susp_mm": round(random.uniform(10, 120), 2),
        "rear_susp_mm": round(random.uniform(10, 120), 2),
        "wheel_slip_pct": round(min(100, abs(lean) * throttle / 100), 2)
    }

# Write header
with open(OUTPUT_FILE, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=generate_telemetry(RIDERS[0], 1, 0).keys())
    writer.writeheader()

    print(f"Starting advanced telemetry simulation for {SIMULATION_DURATION} seconds...")
    start_time = time.time()

    while time.time() - start_time < SIMULATION_DURATION:
        elapsed = int(time.time() - start_time)
        lap = (elapsed // 20) + 1  # New lap every 20 seconds

        for rider in RIDERS:
            data = generate_telemetry(rider, lap, elapsed)
            writer.writerow(data)
            print(data)

        time.sleep(INTERVAL)

print(f"Simulation complete. Data saved to {OUTPUT_FILE}")