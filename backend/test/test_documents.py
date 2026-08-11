def test_upload_document(
        client,
        auth_headers,
        vector_store
):
    response = client.post(
        "/documents/upload",
        headers=auth_headers["headers"],
        files={
            "file": (
                "test.txt",
                "这是测试知识库内容",
                "text/plain"
            )
        }
    )

    assert response.status_code == 200

    result = vector_store.get(
        where={
            "$and": [
                {
                    "uploader": auth_headers["username"]
                },
                {
                    "source": "test.txt"
                }
            ]
        }
    )

    assert len(result["ids"]) > 0


def test_delete_document(client, auth_headers, vector_store, session):
    # 上传
    response = client.post(
        "/documents/upload",
        headers=auth_headers["headers"],
        files={
            "file": (
                "delete_test.txt",
                "删除测试内容",
                "text/plain"
            )
        }
    )

    assert response.status_code == 200

    # 删除
    response = client.delete(
        "/documents/delete_test.txt",
        headers=auth_headers["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "删除成功"

    vec_result = vector_store.get(
        where={
            "$and": [
                {
                    "source": "delete_test.txt"
                },
                {
                    "uploader": auth_headers["username"]
                }
            ]
        }
    )

    assert len(vec_result["ids"]) == 0

    from sqlmodel import select
    from app.model.file_model import File

    # 获得session
    stmt = select(File).where(
        File.filename == "delete_test.txt",
        File.uploader_name == auth_headers["username"]
    )
    rel_result = session.exec(statement=stmt).first()
    assert rel_result is None


def test_delete_document_auth(auth_headers, another_user, client):
    # 用户1上传文件
    response = client.post(
        "/documents/upload",
        headers=auth_headers["headers"],
        files={
            "file": (
                "user1_upload.txt",
                "用户1上传的文件",
                "text/plain"
            )
        }
    )

    assert response.status_code == 200

    # 用户2删除用户1上传的文件
    response = client.delete(
        "/documents/user1_upload.txt",
        headers=another_user["headers"],
    )
    assert response.status_code == 404


def test_list_document_permission(
        client,
        auth_headers,
        another_user
):
    # 用户A上传
    response = client.post(
        "/documents/upload",
        headers=auth_headers["headers"],
        files={
            "file": (
                "user_a.txt",
                "用户A文件",
                "text/plain"
            )
        }
    )

    assert response.status_code == 200

    # 用户B查看列表
    response = client.get(
        "/documents",
        headers=another_user["headers"]
    )

    assert response.status_code == 200

    documents = response.json()

    filenames = [
        item["filename"]
        for item in documents
    ]

    assert "user_a.txt" not in filenames

def test_upload_duplicate_document(
    client,
    auth_headers
):

    file = {
        "file": (
            "same.txt",
            "测试内容",
            "text/plain"
        )
    }

    response = client.post(
        "/documents/upload",
        headers=auth_headers["headers"],
        files=file
    )

    assert response.status_code == 200


    response = client.post(
        "/documents/upload",
        headers=auth_headers["headers"],
        files=file
    )

    assert response.status_code == 400

def test_delete_not_exist_document(
    client,
    auth_headers
):

    response = client.delete(
        "/documents/not_exist.txt",
        headers=auth_headers["headers"]
    )

    assert response.status_code == 404