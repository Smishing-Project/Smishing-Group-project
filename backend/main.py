from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import create_tables
from src.api.routes import router as analysis_router

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

# OCR/URL 분석 라우터 등록
app.include_router(analysis_router)


@app.on_event("startup")
async def init_tables() -> None:
    try:
        await create_tables()
        print("데이터베이스 테이블 초기화 완료")
    except Exception as e:
        print(f"데이터베이스 연결 실패 (OCR/URL API는 정상 작동): {e}")


@app.get("/")
def root():
    return {"message": "스미싱 예방 코치 API"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
