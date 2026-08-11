def test_chat_without_login(client, auth_headers):
    response = client.post(
        "/qa/test/chat",
        json={
            "message": "你好",
        },
    )

    assert response.status_code == 401


def test_chat_with_login(client, auth_headers):
    response = client.post(
        "/qa/test/chat",
        json={
            "message": "什么是金融?",
        },
        headers=auth_headers["headers"]
    )

    assert response.status_code == 200

    data = response.json()
    assert data["answer"] == "这是测试回答"
    assert "references" in data


def test_chat_memory_permission(
        client,
        auth_headers,
        another_user
):
    response_a = client.post(
        "/qa/test/chat",
        headers=auth_headers["headers"],
        json={
            "message": "我的名字叫张三"
        }
    )
    assert response_a.status_code == 200

    response_b = client.post(
        "/qa/test/chat",
        headers=another_user["headers"],
        json={
            "message": "我叫什么"
        }
    )
    assert response_b.status_code == 200

    from app.main import app
    from langchain_core.messages import HumanMessage
    user_a_memory = app.state.chat_memory.cache[
        auth_headers["username"]
    ]

    user_b_memory = app.state.chat_memory.cache[
        another_user["username"]
    ]
    assert HumanMessage(
        content="我的名字叫张三"
    ) in user_a_memory

    assert HumanMessage(
        content="我的名字叫张三"
    ) not in user_b_memory
    # assert user_a_memory is not user_b_memory


def test_stream_chat(
        client,
        auth_headers
):
    response = client.post(
        "/qa/test/stream_chat",
        headers=auth_headers["headers"],
        json={
            "message": "你好"
        }
    )

    assert response.status_code == 200

    text = response.text

    assert "token" in text
