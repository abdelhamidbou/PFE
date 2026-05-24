import requests
import random

url = "http://localhost:8000/auth/register"
data = {
    "first_name": "Test",
    "last_name": "User",
    "email": f"test{random.randint(1,10000)}@example.com",
    "phone": "1234567890",
    "password": "testpass123",
    "role": "patient",
    "subscription": "basic"
}

try:
    response = requests.post(url, json=data, timeout=5)
    print(f"Statut: {response.status_code}")
    print(f"Réponse: {response.json()}")
except Exception as e:
    print(f"Erreur: {e}")
