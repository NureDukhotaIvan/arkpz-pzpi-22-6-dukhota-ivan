# iot_simulator.py

import requests
import time
import random
from datetime import datetime

API_URL = 'https://schooldef.onrender.com/api/sensor-data/'
TOKEN_URL = 'https://schooldef.onrender.com/api/token/'
USERNAME = 'root'                                 
PASSWORD = 'root'                                 

def get_jwt_token():
    response = requests.post(TOKEN_URL, data={'username': USERNAME, 'password': PASSWORD})
    if response.status_code == 200:
        return response.json().get('access')
    else:
        print('Не вдалося отримати токен:', response.text)
        return None

def get_all_data_from_paginated_endpoint(url, token):
    headers = {'Authorization': f'Bearer {token}'}
    data = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            data.extend(response_data.get('results', []))
            url = response_data.get('next')
        else:
            print(f'Не вдалося отримати дані з {url}:', response.text)
            break
    return data

def get_sensors(token):
    print("Отримання всіх сенсорів...")
    sensors = get_all_data_from_paginated_endpoint('https://schooldef.onrender.com/api/sensors/', token)
    sensors = [sensor for sensor in sensors if sensor['type'] != 'intrusion']
    print(f"Отримано {len(sensors)} сенсорів.")
    return sensors

def get_cameras(token):
    print("Отримання всіх камер...")
    cameras = get_all_data_from_paginated_endpoint('https://schooldef.onrender.com/api/cameras/', token)
    print(f"Отримано {len(cameras)} камер.")
    return cameras

def generate_weather_conditions():
    temperature = random.uniform(-10, 40)
    weather_conditions = random.choice(["Clear", "Rain", "Snow", "Fog", "Storm"])
    weather_risk = {
        "Clear": 1.0,
        "Rain": 1.2,
        "Snow": 1.5,
        "Fog": 1.3,
        "Storm": 1.3
    }[weather_conditions]
    return temperature, weather_conditions, weather_risk

def calculate_danger_percentage(temperature, weather_risk):
    base_danger = 15
    temperature_risk = max(0, (temperature - 25) * 2) if temperature > 25 else max(0, (10 - temperature) * 3)
    danger_percentage = base_danger + (temperature_risk * weather_risk)
    return min(100, max(1, int(danger_percentage))) 

def main():
    token = get_jwt_token()
    if not token:
        return

    sensors = get_sensors(token)
    if not sensors:
        print('Сенсорів не знайдено.')
        return

    cameras = get_cameras(token)
    if not cameras:
        print('Камер не знайдено.')
        return

    camera_ids = [camera['id'] for camera in cameras]

    print(f"Знайдено {len(sensors)} сенсорів та {len(camera_ids)} камер.")

    while True:
        for sensor in sensors:
            sensor_id = sensor['id']
            sensor_type = sensor['type']
            sensor_location = sensor['location']

            temperature, weather_conditions, weather_risk = generate_weather_conditions()

            danger_percentage = calculate_danger_percentage(temperature, weather_risk)

            camera_id = random.choice(camera_ids)

            description = (
                f"Увага, {sensor_type} відбувається у {sensor_location}. "
                f"Температура: {temperature:.1f}°C, Погода: {weather_conditions}."
            )

            current_date = datetime.now().isoformat()
            payload = {
                'sensor_id': sensor_id,
                'camera_id': camera_id,
                'type': sensor_type,
                'description': description,
                'danger_percentage': danger_percentage,
                'date': current_date
            }

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            try:
                response = requests.post(API_URL, json=payload, headers=headers)
                if response.status_code in [200, 201]:
                    print(f"Сенсор {sensor_id}: danger_percentage={danger_percentage} | Відповідь: {response.json()}")
                else:
                    print(f"Сенсор {sensor_id}: Не вдалося відправити дані | Статус: {response.status_code} | Повідомлення: {response.text}")
            except Exception as e:
                print(f"Сенсор {sensor_id}: Помилка при відправці даних | Помилка: {e}")

        time.sleep(20)

if __name__ == "__main__":
    main()
