# backend/tests/test_export_api.py
"""데이터 익스포트 API 테스트"""
import pytest
import json
import zipfile
import io


def create_test_order_with_chat(client):
    """테스트용 주문 생성 헬퍼 (채팅 메시지 포함)"""
    conv_resp = client.post("/api/conversations", json={
        "title": "익스포트 테스트",
        "provider": "openai",
        "model": "gpt-5-nano"
    })
    conv_id = conv_resp.json()["id"]

    # 채팅 메시지 추가 (데모 모드 - 실제 API 호출은 DemoProvider가 처리)
    # SSE StreamingResponse 응답을 완전히 소비하여 AI 응답이 DB에 저장되도록 함
    chat_resp = client.post("/api/chat/send", json={
        "conversation_id": conv_id,
        "message": "안녕하세요",
        "provider": "demo",
        "model": "demo-model"
    })
    # SSE 응답 body를 소비하여 제너레이터가 끝까지 실행되도록 함
    _ = chat_resp.text

    order_resp = client.post("/api/orders", json={"conversation_id": conv_id})
    return order_resp.json()["id"]


def test_export_json(client):
    """JSON 형식 익스포트"""
    order_id = create_test_order_with_chat(client)

    response = client.get(f"/api/orders/{order_id}/export?format=json")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]

    data = response.json()
    assert "order" in data
    assert "conversation" in data
    assert data["order"]["status"] == "접수"


def test_export_zip(client):
    """ZIP 형식 익스포트"""
    order_id = create_test_order_with_chat(client)

    response = client.get(f"/api/orders/{order_id}/export?format=zip")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    # ZIP 내용 검증
    zip_data = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_data, "r") as zf:
        file_list = zf.namelist()
        assert any("order.json" in f for f in file_list)
        assert any("conversation.txt" in f for f in file_list)


def test_export_order_not_found(client):
    """존재하지 않는 주문 익스포트 시 404"""
    response = client.get("/api/orders/nonexistent/export?format=json")
    assert response.status_code == 404
