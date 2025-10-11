from django.test import TestCase

# Create your tests here.
import requests

# test_api.py
import requests

BASE_URL = "http://127.0.0.1:8000/api"

#
# def test_register():
#     """Тестируем регистрацию"""
#     print("🔐 Тестируем регистрацию...")
#
#     url = f"{BASE_URL}/register/"
#     data = {
#         "first_name": "John",
#         "last_name": "Doe",
#         "email": "john@example.com",
#         "password": "password123",
#         "password_confirm": "password123"
#     }
#
#     response = requests.post(url, json=data)
#     print(f"Статус: {response.status_code}")
#     print(f"Ответ: {response.json()}")
#     return response.json()
#
#
# def test_login():
#     """Тестируем логин"""
#     print("\n🔑 Тестируем логин...")
#
#     url = f"{BASE_URL}/login/"
#     data = {
#         "email": "john@example.com",
#         "password": "password123"
#     }
#
#     response = requests.post(url, json=data)
#     print(f"Статус: {response.status_code}")
#     print(f"Ответ: {response.json()}")
#
#     if response.status_code == 200:
#         return response.json()['token']  # Сохраняем токен
#     return None
#
#
# def test_profile(token):
#     """Тестируем получение профиля с токеном"""
#     print("\n👤 Тестируем профиль...")
#
#     url = f"{BASE_URL}/profile/"
#     headers = {
#         "Authorization": f"Bearer {token}"
#     }
#
#     response = requests.get(url, headers=headers)
#     print(f"Статус: {response.status_code}")
#     print(f"Ответ: {response.json()}")
#
#
# def test_products(token):
#     """Тестируем доступ к товарам"""
#     print("\n📦 Тестируем доступ к товарам...")
#
#     url = f"{BASE_URL}/products/"
#     headers = {
#         "Authorization": f"Bearer {token}"
#     }
#
#     response = requests.get(url, headers=headers)
#     print(f"Статус: {response.status_code}")
#     print(f"Ответ: {response.json()}")
#
#
# if __name__ == "__main__":
#     # Запускаем тесты по порядку
#     test_register()  # 1. Регистрация
#     token = test_login()  # 2. Логин (получаем токен)
#
#     if token:
#         test_profile(token)  # 3. Профиль с токеном
#         test_products(token)  # 4. Товары с токеном
"""Тестируем логин"""
print("\n🔑 Тестируем логин...")

url = f"{BASE_URL}/login/"
data = {
    "email": "john@example.com",
    "password": "password123"
}

response = requests.post(url, json=data)
print(f"Статус: {response.status_code}")
print(f"Ответ: {response.json()}")
