from pyzbar import pyzbar
import cv2
import numpy as np
from PIL import Image
from typing import Union, List, Dict
import io

# 이미지에서 QR 코드를 디코딩하는 클래스
class QRDecoder:

    # QR 디코더 초기화
    def __init__(self):
        print("QR Decoder 초기화 완료")

    # 이미지에서 QR 코드 디코딩
    def decode_from_image(
        self, 
        image_source: Union[str, bytes, np.ndarray]
    ) -> Dict[str, any]:
        try:
            # 이미지 로드
            image = self._load_image(image_source)
            
            if image is None:
                return {
                    'success': False,
                    'qr_codes': [],
                    'urls': [],
                    'message': '이미지 로드 실패'
                }
            
            # QR 코드 디코딩
            decoded_objects = pyzbar.decode(image)
            
            if not decoded_objects:
                return {
                    'success': True,
                    'qr_codes': [],
                    'urls': [],
                    'message': 'QR 코드가 감지되지 않았습니다'
                }
            
            # 결과 파싱
            qr_codes = []
            urls = []
            
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')
                qr_info = {
                    'type': obj.type,
                    'data': data,
                    'rect': {
                        'left': obj.rect.left,
                        'top': obj.rect.top,
                        'width': obj.rect.width,
                        'height': obj.rect.height
                    },
                    'quality': obj.quality
                }
                qr_codes.append(qr_info)
                
                # URL인 경우 urls 리스트에 추가
                if self._is_url(data):
                    urls.append(data)
            
            return {
                'success': True,
                'qr_codes': qr_codes,
                'urls': urls,
                'message': f'{len(qr_codes)}개의 QR 코드 감지 ({len(urls)}개 URL)'
            }
            
        except Exception as e:
            return {
                'success': False,
                'qr_codes': [],
                'urls': [],
                'message': f'QR 디코딩 중 오류: {str(e)}'
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

    # 텍스트가 URL인지 확인
    def _is_url(self, text: str) -> bool:
        url_indicators = ['http://', 'https://', 'www.', '.com', '.kr', '.net']
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in url_indicators)

    # QR 코드 인식을 위한 이미지 전처리 (선택적 사용)
    def preprocess_for_qr(self, image: np.ndarray) -> np.ndarray:
        # 그레이스케일 변환
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 대비 향상
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # 이진화
        _, binary = cv2.threshold(
            enhanced, 0, 255, 
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        return binary


# 사용 예시
if __name__ == "__main__":
    # QR 디코더 초기화
    decoder = QRDecoder()
    
    # 테스트 (QR 코드 이미지가 있는 경우)
    # result = decoder.decode_from_image('qr_test.jpg')
    # print(result)
    
    print("QR 디코더 모듈이 정상적으로 로드되었습니다.")
