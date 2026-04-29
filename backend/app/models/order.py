# backend/app/models/order.py
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.conversation import generate_uuid

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(
        String,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    status = Column(String, nullable=False, default="접수")
    quantity = Column(Integer, nullable=False, default=1)
    cover_style = Column(String, nullable=False, default="basic")
    memo = Column(Text, default="")
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # 관계
    conversation = relationship("Conversation", back_populates="order")

    __table_args__ = (
        CheckConstraint(
            "status IN ('접수', '제작중', '완료', '취소')",
            name="ck_order_status"
        ),
        CheckConstraint("quantity >= 1", name="ck_order_quantity"),
    )
