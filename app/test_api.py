import requests
import time
import json

BASE_URL = "http://localhost:8000"


def send_data():
    print("1. Отправка данных с устройства...")
    resp = requests.post(f"{BASE_URL}/devices/test-device/data", json={"x": 1.2, "y": 3.4, "z": 5.6})
    print("   Ответ:", resp.status_code, resp.json())
    return resp.json()


def create_user():
    print("\n2. Создание пользователя...")
    resp = requests.post(f"{BASE_URL}/users", json={"name": "Тестовый пользователь"})
    print("   Ответ:", resp.status_code, resp.json())
    return resp.json()


def assign_device(user_id, device_id):
    print(f"\n3. Привязка устройства {device_id} к пользователю {user_id}...")
    resp = requests.post(f"{BASE_URL}/users/{user_id}/devices", json={"device_id": device_id})
    print("   Ответ:", resp.status_code, resp.json())


def device_stats_async(device_id):
    print(f"\n4. Запуск асинхронной статистики для {device_id}...")
    resp = requests.post(f"{BASE_URL}/devices/{device_id}/stats")
    task_id = resp.json()["task_id"]
    print(f"   task_id = {task_id}")

    print("   Ожидание результата...")
    while True:
        resp2 = requests.get(f"{BASE_URL}/tasks/{task_id}")
        data = resp2.json()
        if data.get("status") == "pending":
            print("   ...ещё не готово")
            time.sleep(1)
        else:
            print("   Результат:", json.dumps(data, indent=2))
            break


if __name__ == "__main__":
    point = send_data()
    device_id = point["device_id"]

    user = create_user()
    user_id = user["id"]

    assign_device(user_id, device_id)

    device_stats_async(device_id)