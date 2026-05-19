from locust import HttpUser, task, between
import random

class DeviceUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(3)
    def send_data(self):
        device_id = random.randint(1, 100)
        payload = {
            "x": random.uniform(-100, 100),
            "y": random.uniform(-100, 100),
            "z": random.uniform(-100, 100)
        }
        self.client.post(f"/devices/{device_id}/data", json=payload)

    @task(1)
    def request_device_stats(self):
        device_id = random.randint(1, 100)
        self.client.post(f"/devices/{device_id}/stats")