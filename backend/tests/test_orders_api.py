# backend/tests/test_orders_api.py
"""주문 CRUD 및 상태 머신 통합 테스트"""
import pytest


def create_test_conversation(client):
    """테스트용 대화방 생성 헬퍼"""
    resp = client.post("/api/conversations", json={"title": "주문 테스트 대화"})
    assert resp.status_code == 201
    return resp.json()["id"]


def test_create_order(client):
    """주문 생성"""
    conv_id = create_test_conversation(client)

    response = client.post("/api/orders", json={
        "conversation_id": conv_id,
        "quantity": 2,
        "cover_style": "premium",
        "memo": "테스트 주문입니다"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "접수"
    assert data["quantity"] == 2
    assert data["cover_style"] == "premium"


def test_list_orders(client):
    """주문 목록 조회"""
    conv_id = create_test_conversation(client)
    client.post("/api/orders", json={"conversation_id": conv_id})

    response = client.get("/api/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_duplicate_order_prevented(client):
    """접수/제작중 상태의 동일 대화방 중복 주문 방지"""
    conv_id = create_test_conversation(client)

    # 첫 번째 주문 (접수 상태)
    client.post("/api/orders", json={"conversation_id": conv_id})
    # 두 번째 주문 (중복) → 409
    resp = client.post("/api/orders", json={"conversation_id": conv_id})
    assert resp.status_code == 409


def test_reorder_allowed_for_completed_order(client):
    """완료된 주문이 있는 대화방에 재주문 가능 (201)"""
    conv_id = create_test_conversation(client)

    # 첫 번째 주문 생성 → 완료까지 진행
    order_resp = client.post("/api/orders", json={"conversation_id": conv_id})
    order_id = order_resp.json()["id"]
    client.patch(f"/api/orders/{order_id}/status", json={"status": "제작중"})
    client.patch(f"/api/orders/{order_id}/status", json={"status": "완료"})

    # 완료된 주문이 있지만 새 주문 생성 가능
    resp = client.post("/api/orders", json={"conversation_id": conv_id})
    assert resp.status_code == 201
    assert resp.json()["status"] == "접수"


def test_reorder_allowed_for_cancelled_order(client):
    """취소된 주문이 있는 대화방에 재주문 가능 (201)"""
    conv_id = create_test_conversation(client)

    # 첫 번째 주문 생성 → 취소
    order_resp = client.post("/api/orders", json={"conversation_id": conv_id})
    order_id = order_resp.json()["id"]
    client.delete(f"/api/orders/{order_id}")

    # 취소된 주문만 있으므로 새 주문 생성 가능
    resp = client.post("/api/orders", json={"conversation_id": conv_id})
    assert resp.status_code == 201
    assert resp.json()["status"] == "접수"


def test_reorder_blocked_for_in_progress(client):
    """제작중 상태의 주문이 있는 대화방은 재주문 불가 (409)"""
    conv_id = create_test_conversation(client)

    # 첫 번째 주문 생성 → 제작중
    order_resp = client.post("/api/orders", json={"conversation_id": conv_id})
    order_id = order_resp.json()["id"]
    client.patch(f"/api/orders/{order_id}/status", json={"status": "제작중"})

    # 제작중인 주문이 있으므로 새 주문 불가
    resp = client.post("/api/orders", json={"conversation_id": conv_id})
    assert resp.status_code == 409


def test_order_state_transitions(client):
    """주문 상태 머신 검증"""
    conv_id = create_test_conversation(client)
    order_resp = client.post("/api/orders", json={"conversation_id": conv_id})
    order_id = order_resp.json()["id"]

    # 접수 → 제작중 (정상)
    resp = client.patch(f"/api/orders/{order_id}/status", json={"status": "제작중"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "제작중"

    # 제작중 → 완료 (정상)
    resp = client.patch(f"/api/orders/{order_id}/status", json={"status": "완료"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "완료"

    # 완료 → 취소 (거부)
    resp = client.patch(f"/api/orders/{order_id}/status", json={"status": "취소"})
    assert resp.status_code == 400


def test_cancel_order_only_received(client):
    """접수 상태만 취소 가능"""
    conv_id = create_test_conversation(client)
    order_resp = client.post("/api/orders", json={"conversation_id": conv_id})
    order_id = order_resp.json()["id"]

    # 접수 → 취소 (정상)
    resp = client.delete(f"/api/orders/{order_id}")
    assert resp.status_code == 204

    # 취소된 주문은 상태가 '취소'
    get_resp = client.get(f"/api/orders/{order_id}")
    assert get_resp.json()["status"] == "취소"


def test_cannot_cancel_in_progress(client):
    """제작중 상태 주문은 DELETE 취소 불가, PATCH '접수' 전이는 가능"""
    conv_id = create_test_conversation(client)
    order_resp = client.post("/api/orders", json={"conversation_id": conv_id})
    order_id = order_resp.json()["id"]

    # 접수 → 제작중
    client.patch(f"/api/orders/{order_id}/status", json={"status": "제작중"})

    # 제작중 → 취소 (DELETE) 거부
    resp = client.delete(f"/api/orders/{order_id}")
    assert resp.status_code == 400

    # 제작중 → 접수 (PATCH, 제작 취소) 성공
    resp = client.patch(f"/api/orders/{order_id}/status", json={"status": "접수"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "접수"


def test_cancel_production_to_received(client):
    """제작중 → 접수 PATCH가 200 응답을 반환"""
    conv_id = create_test_conversation(client)
    order_resp = client.post("/api/orders", json={"conversation_id": conv_id})
    order_id = order_resp.json()["id"]

    # 접수 → 제작중
    client.patch(f"/api/orders/{order_id}/status", json={"status": "제작중"})

    # 제작중 → 접수 (제작 취소)
    resp = client.patch(f"/api/orders/{order_id}/status", json={"status": "접수"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "접수"
    assert data["id"] == order_id


def test_invalid_state_transition(client):
    """잘못된 상태 전이 → 400"""
    conv_id = create_test_conversation(client)
    order_resp = client.post("/api/orders", json={"conversation_id": conv_id})
    order_id = order_resp.json()["id"]

    # 접수 → 완료 (바로 건너뛰기 불가)
    resp = client.patch(f"/api/orders/{order_id}/status", json={"status": "완료"})
    assert resp.status_code == 400
