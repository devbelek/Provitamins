import requests
import base64

# URL вашего API
BASE_URL = 'http://localhost:8000/api/1c/products/'

# Данные для Basic Auth
username = '1c_user'
password = 'secure_password'
credentials = base64.b64encode(f'{username}:{password}'.encode()).decode('utf-8')

# Заголовки запроса
headers = {
    'Authorization': f'Basic {credentials}',
    'Content-Type': 'application/json'
}

# Тестовые данные
test_data = {
    "name_en": "Baby D3 Liquid",
    "vendor_code": "CGN-01034",
    "price": 500,
    "status": "in_stock"
}

# Отправка запроса
response = requests.post(
    BASE_URL,
    json=test_data,
    headers=headers
)

# Вывод результатов
print(f'Status Code: {response.status_code}')
print(f'Response: {response.json()}')