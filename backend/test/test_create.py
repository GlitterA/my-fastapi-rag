import requests

def test_create_port(base_url):
    url = f"{base_url}/create"
    payload = {
        "title": "pytest 接口测试",
        "username": "李四",
        "password": 111
    }

    response = requests.post(url, json=payload)

    assert response.status_code == 201