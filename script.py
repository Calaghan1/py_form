import requests

url = "http://127.0.0.1:8000/get_form?lead_email=calaghan@yandex.ru&number=8 916 374 39 73"

# Пример тестового запроса
data = {
    "email": "calaghan@yandex.ru"
}


response = requests.post(url)
print(response.json())