from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import io
from PIL import Image
import numpy as np

from ..analyzer import SmishingAnalyzer


# APIRouter 생성
router = APIRouter(prefix="/api/v1", tags=["analysis"])

# SmishingAnalyzer 인스턴스 (앱 시작 시 한 번만 초기화)
analyzer = None

# SmishingAnalyzer 싱글톤 인스턴스 반환
def get_analyzer():
    global analyzer
    if analyzer is None:
        analyzer = SmishingAnalyzer()
    return analyzer

# 텍스트 분석 요청
class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="분석할 텍스트")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "[Web발신]\n택배가 도착했습니다.\n확인: http://example.com"
            }
        }


# 분석 결과 응답
class AnalysisResponse(BaseModel):
    success: bool = Field(..., description="분석 성공 여부")
    input_type: str = Field(..., description="입력 타입 (text/image)")
    final_risk_level: str = Field(..., description="최종 위험도 (high/medium/low)")
    message: str = Field(..., description="위험도 설명 메시지")
    url_analysis: Optional[Dict[str, Any]] = Field(None, description="URL 분석 상세 결과")
    ocr_result: Optional[Dict[str, Any]] = Field(None, description="OCR 결과 (이미지만)")
    qr_result: Optional[Dict[str, Any]] = Field(None, description="QR 결과 (이미지만)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "input_type": "text",
                "final_risk_level": "high",
                "message": "위험 감지: 1개의 악성 URL이 감지되었습니다.",
                "url_analysis": {
                    "has_urls": True,
                    "url_count": 1,
                    "urls": ["http://example.com"]
                }
            }
        }


class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str = Field(..., description="서비스 상태")
    message: str = Field(..., description="상태 메시지")
    version: str = Field(..., description="API 버전")

# API 엔드포인트

# API 서버 상태 확인
@router.get("/health", response_model=HealthResponse, summary="헬스체크")
async def health_check():
    return HealthResponse(
        status="healthy",
        message="OCR/QR + URL Analysis API is running",
        version="1.0.0"
    )


@router.post(
    "/analyze/text",
    response_model=AnalysisResponse,
    summary="텍스트 분석",
    status_code=status.HTTP_200_OK
)

# 텍스트에서 URL을 추출하고 위험도를 분석
async def analyze_text(request: TextAnalysisRequest):
    """
    **작동 방식:**
    1. 텍스트에서 URL 추출 (정규표현식)
    2. Google Safe Browsing API로 악성 URL 검사
    3. 위험도 판정 (high/medium/low)
    
    **Parameters:**
    - **text**: 분석할 텍스트 (필수, 1-10000자)
    
    **Returns:**
    - 위험도 분석 결과
    """
    try:
        # SmishingAnalyzer 가져오기
        smishing_analyzer = get_analyzer()
        
        # 텍스트 분석
        result = smishing_analyzer.analyze_text(request.text)
        
        # 응답 생성
        return AnalysisResponse(
            success=True,
            input_type=result['input_type'],
            final_risk_level=result['final_risk_level'],
            message=result['message'],
            url_analysis=result.get('url_analysis'),
            ocr_result=None,
            qr_result=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"텍스트 분석 중 오류 발생: {str(e)}"
        )


@router.post(
    "/analyze/image",
    response_model=AnalysisResponse,
    summary="이미지 분석",
    status_code=status.HTTP_200_OK
)

# 이미지에서 텍스트/QR 코드를 추출하고 URL 위험도를 분석
async def analyze_image(file: UploadFile = File(..., description="분석할 이미지 파일")):
    """
    **작동 방식:**
    1. OCR로 텍스트 추출 (EasyOCR)
    2. QR 코드 디코딩 (pyzbar)
    3. URL 추출 및 Safe Browsing 검사
    4. 위험도 판정
    
    **Parameters:**
    - **file**: 이미지 파일 (jpg, png, jpeg)
    
    **Returns:**
    - 위험도 분석 결과 (OCR/QR 결과 포함)
    """
    try:
        # 파일 형식 검증
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미지 파일만 업로드 가능합니다."
            )
        
        # 파일 크기 제한 (10MB)
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="파일 크기는 10MB 이하여야 합니다."
            )
        
        # 이미지 로드
        try:
            image = Image.open(io.BytesIO(contents))
            image_array = np.array(image)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이미지 로드 실패: {str(e)}"
            )
        
        # SmishingAnalyzer 가져오기
        smishing_analyzer = get_analyzer()
        
        # 이미지 분석
        result = smishing_analyzer.analyze_image(image_array)
        
        # 응답 생성
        return AnalysisResponse(
            success=True,
            input_type=result['input_type'],
            final_risk_level=result['final_risk_level'],
            message=result['message'],
            url_analysis=result.get('url_analysis'),
            ocr_result=result.get('ocr_result'),
            qr_result=result.get('qr_result')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 분석 중 오류 발생: {str(e)}"
        )
