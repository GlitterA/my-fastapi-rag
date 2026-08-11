def test_create_user(client, test_username):
    response = client.post(
        "/create",
        json={
            "username": test_username,
            "password": "123456"
        }
    )

    assert response.status_code == 200


def test_login(client, test_username):
    # 先注册
    response = client.post(
        "/create",
        json={
            "username": test_username,
            "password": "123456"
        }
    )

    assert response.status_code == 200

    # 再登录
    response = client.post(
        "/login/access-token",
        data={
            "username": test_username,
            "password": "123456"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
