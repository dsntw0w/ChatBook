# backend/app/routes/__init__.py
from app.routes.chat import router as chat_router
from app.routes.orders import router as orders_router
from app.routes.export import router as export_router
from app.routes.character import router as character_router

__all__ = ["chat_router", "orders_router", "export_router", "character_router"]
