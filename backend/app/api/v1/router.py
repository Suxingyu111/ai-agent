from fastapi import APIRouter

from app.modules.conversations.api import router as conversations_router
from app.modules.health.api import router as health_router
from app.modules.knowledge.api import router as knowledge_router

api_router = APIRouter()
api_router.include_router(conversations_router, tags=["conversations"])
api_router.include_router(health_router, tags=["health"])
api_router.include_router(knowledge_router, tags=["knowledge-bases"])
