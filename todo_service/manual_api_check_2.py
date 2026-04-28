import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

# # Реєстрація
# user_data = {
#     "username": "alla",
#     "email": "alla@example.com",
#     "password": "passwordalla123"
# }
# response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
# print("Register:", response.json())

# Логін
response = requests.post(
    f"{BASE_URL}/auth/login",
    params={"username": "alice", "password": "alice_password_123"}
)
print("Login:", response.json())

login_result = response.json()
if "access_token" not in login_result:
    raise RuntimeError(f"Login failed: {login_result}")

token = login_result["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Перший запит
response = requests.get(f"{BASE_URL}/todos", headers=headers)
print("First request (from DB):", response.json())

# Другий запит
response = requests.get(f"{BASE_URL}/todos", headers=headers)
print("Second request (from Cache):", response.json())

# Статистика кешу
response = requests.get("http://127.0.0.1:8000/cache/stats")
print("Cache stats:", response.json())