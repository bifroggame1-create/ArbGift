"""
Admin Panel - Main FastAPI Application

Полный контроль над gambling:
- RTP / House Edge настройки
- Таргетирование пользователей (win/lose)
- Ручное управление раундами
- Статистика и аналитика
- Аудит лог всех действий
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db, close_db
from .api.admin import router
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown"""
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Gambling Admin Panel",
    description="Full control over all gambling games",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "admin-panel"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.admin.app.main:app", host="0.0.0.0", port=8001, reload=True)
