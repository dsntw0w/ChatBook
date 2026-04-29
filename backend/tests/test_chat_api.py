# backend/tests/test_chat_api.py
"""대화방 및 채팅 API 통합 테스트"""
import pytest


def test_create_conversation(client):
    """새 대화방 생성"""
    response = client.post("/api/conversations", json={
        "title": "테스트 대화",
        "provider": "openai",
        "model": "gpt-5-nano"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "테스트 대화"
    assert data["provider"] == "openai"
    assert "id" in data


def test_list_conversations(client):
    """대화방 목록 조회"""
    # 대화방 2개 생성
    client.post("/api/conversations", json={"title": "대화1"})
    client.post("/api/conversations", json={"title": "대화2"})

    response = client.get("/api/conversations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_conversation_not_found(client):
    """존재하지 않는 대화방 조회 시 404"""
    response = client.get("/api/conversations/nonexistent-id")
    assert response.status_code == 404


def test_get_conversation_with_messages(client):
    """대화방 + 메시지 조회"""
    create_resp = client.post("/api/conversations", json={"title": "메시지 포함 대화"})
    conv_id = create_resp.json()["id"]

    response = client.get(f"/api/conversations/{conv_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conv_id
    assert "messages" in data


def test_update_conversation_title(client):
    """대화방 제목 수정"""
    create_resp = client.post("/api/conversations", json={"title": "원래 제목"})
    conv_id = create_resp.json()["id"]

    update_resp = client.patch(f"/api/conversations/{conv_id}", json={"title": "변경된 제목"})
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "변경된 제목"


def test_delete_conversation(client):
    """대화방 삭제"""
    create_resp = client.post("/api/conversations", json={"title": "삭제될 대화"})
    conv_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/conversations/{conv_id}")
    assert delete_resp.status_code == 204

    # 삭제 확인
    get_resp = client.get(f"/api/conversations/{conv_id}")
    assert get_resp.status_code == 404
