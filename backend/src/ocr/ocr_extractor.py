import easyocr
import cv2
import numpy as np
from PIL import Image
from typing import Union, List, Dict
import io

# 이미지에서 텍스트를 추출하는 클래스
class OCRExtractor:

    # OCR 추출기 초기화
    def __init__(self, languages: List[str] = ['ko', 'en']):
        self.reader = easyocr.Reader(languages, gpu=False)
        print(f"OCR Reader 초기화 완료 (언어: {languages})")

    # 이미지에서 텍스트 추출
    def extract_from_image(
        self, 
        image_source: Union[str, bytes, np.ndarray],
        detail: int = 1
    ) -> Dict[str, any]:
        try:
            # 이미지 로드
            image = self._load_image(image_source)
            
            if image is None:
                return {
                    'success': False,
                    'text': '',
                    'details': [],
                    'message': '이미지 로드 실패'
                }
            
            # OCR 실행
            results = self.reader.readtext(image, detail=detail)
            
            if not results:
                return {
                    'success': True,
                    'text': '',
                    'details': [],
                    'message': '텍스트가 감지되지 않았습니다'
                }
            
            # 결과 파싱
            if detail == 0:
                # 텍스트만 반환
                full_text = ' '.join(results)
                details = [{'text': text} for text in results]
            else:
                # 상세 정보 포함
                full_text = ' '.join([text for _, text, _ in results])
                details = [
                    {
                        'bbox': bbox,
                        'text': text,
                        'confidence': round(confidence, 4)
                    }
                    for bbox, text, confidence in results
                ]
            
            return {
                'success': True,
                'text': full_text,
                'details': details,
                'message': f'{len(details)}개의 텍스트 블록 감지'
            }
            
        except Exception as e:
            return {
                'success': False,
                'text': '',
                'details': [],
                'message': f'OCR 처리 중 오류: {str(e)}'
            }

    # 다양한 형식의 이미지를 numpy array로 변환
    def _load_image(self, image_source: Union[str, bytes, np.ndarray]) -> np.ndarray:
        try:
            # 이미 numpy array인 경우
            if isinstance(image_source, np.ndarray):
                return image_source
            
            # 파일 경로인 경우
            if isinstance(image_source, str):
                return cv2.imread(image_source)
            
            # bytes인 경우
            if isinstance(image_source, bytes):
                image = Image.open(io.BytesIO(image_source))
                return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            return None
            
        except Exception as e:
            print(f"❌ 이미지 로드 실패: {e}")
            return None

    # OCR 정확도 향상을 위한 이미지 전처리
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 이진화 (Otsu's method)
        _, binary = cv2.threshold(
            gray, 0, 255, 
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        # 노이즈 제거
        denoised = cv2.fastNlMeansDenoising(binary)
        
        return denoised


# 사용 예시
if __name__ == "__main__":
    # OCR 추출기 초기화
    extractor = OCRExtractor()
    
    # 테스트 (이미지 파일이 있는 경우)
    # result = extractor.extract_from_image('test_image.jpg')
    # print(result['text'])
    
    print("OCR 추출기 모듈이 정상적으로 로드되었습니다.")
