import random
from datetime import datetime, timedelta

LEVELS = ["INFO", "WARN", "ERROR"]
SERVICES = ["auth-service", "api-gateway", "db-service"]

ERROR_MESSAGES = [
    "Database connection timeout",
    "Failed to authenticate user",
    "Service unavailable",
    "Memory limit exceeded",
    "Unhandled exception occurred"
]

INFO_MESSAGES = [
    "Request processed successfully",
    "User logged in",
    "Health check passed",
    "Cache hit"
]


def generate_logs(num_entries=500):
    logs = []
    current_time = datetime.now() - timedelta(hours=1)

    for i in range(num_entries):
        level = random.choices(
            LEVELS,
            weights=[0.7, 0.2, 0.1]
        )[0]

        service = random.choice(SERVICES)

        if level == "ERROR":
            message = random.choice(ERROR_MESSAGES)
            latency = random.randint(500, 3000)
            status = random.choice([500, 502, 503])
        else:
            message = random.choice(INFO_MESSAGES)
            latency = random.randint(50, 300)
            status = 200

        log = {
            "timestamp": current_time.isoformat(),
            "level": level,
            "service": service,
            "message": message,
            "latency_ms": latency,
            "status_code": status
        }

        logs.append(log)
        current_time += timedelta(seconds=random.randint(1, 5))

    return logs


if __name__ == "__main__":
    logs = generate_logs()
    with open("sample_logs.log", "w") as f:
        for log in logs:
            f.write(str(log) + "\n")

    print("✅ Sample logs generated: sample_logs.log")