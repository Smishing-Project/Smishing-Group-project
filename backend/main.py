from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import create_tables

app = FastAPI(
    title="스미싱 예방 코치 API",
    description="고령층 사기 예방 서비스 백엔드",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def init_tables() -> None:
    await create_tables()


@app.get("/")
def root():
    return {"message": "스미싱 예방 코치 API"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
