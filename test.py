import requests

def test_responce():
    url = "http://0.0.0.0:8000/get_form?order_date=12.02.2021&cal=13"
    response = requests.post(url).json()
    assert response == {'cal': 'text', 'order_date': 'data'}
    url = "http://0.0.0.0:8000/get_form?lead_email=calaghan@yandex.ru&number=8 916 374 39 73"
    response = requests.post(url).json()
    assert response == "OrderForm"