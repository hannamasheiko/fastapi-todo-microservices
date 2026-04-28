import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Реєстрація
user_data = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "alice_password_123"
}
register_response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
print("Register status:", register_response.status_code)
print("Register body:", register_response.json())

# Вхід
login_data = {
    "username": "alice",
    "password": "alice_password_123"
}
login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
print("Login status:", login_response.status_code)
print("Login body:", login_response.json())

token = login_response.json()["access_token"]
print("Token:", token)

# Авторизовані запити
headers = {"Authorization": f"Bearer {token}"}

# Створити завдання
todo_data = {
    "title": "Вивчити PostgreSQL",
    "description": "CRUD операції",
    "completed": False,
    "priority": 2
}
create_todo_response = requests.post(f"{BASE_URL}/todos", json=todo_data, headers=headers)
print("Create todo status:", create_todo_response.status_code)
print("Created todo:", create_todo_response.json())

# Отримати завдання
get_todos_response = requests.get(f"{BASE_URL}/todos", headers=headers)
print("Get todos status:", get_todos_response.status_code)
print("My todos:", get_todos_response.json())