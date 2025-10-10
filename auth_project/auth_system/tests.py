from django.test import TestCase

# Create your tests here.
import requests

url = "http://127.0.0.1:8000/api/register/"
data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "password123",
    "password_confirm": "password123"
}

response = requests.post(url, json=data)
print(response.status_code)

print(response.json())