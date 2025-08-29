from fastapi import APIRouter
from app.api.v1.endpoints import chat, auth, users, vector, data_import, assessment

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(vector.router, prefix="/vector", tags=["vector"])
api_router.include_router(data_import.router, prefix="/data", tags=["data-import"])
api_router.include_router(assessment.router, prefix="/assessment", tags=["assessment"])

