from typing import Union, Dict
import numpy as np

from .ocr.ocr_extractor import OCRExtractor
from .ocr.qr_decoder import QRDecoder
from .url.url_extractor import URLExtractor
from .url.safe_browsing import SafeBrowsingChecker
from .url.url_classifier import URLClassifier

# 스미싱 문자 분석 통합 클래스
class SmishingAnalyzer:

    def __init__(self, api_key: str = None):
        print("스미싱 분석기 초기화 중...")
        
        self.ocr_extractor = OCRExtractor()
        self.qr_decoder = QRDecoder()
        self.url_extractor = URLExtractor()
        self.safe_browsing = SafeBrowsingChecker(api_key)
        self.url_classifier = URLClassifier()  # ML 모델 추가
        
        print("모든 모듈 초기화 완료!\n")

    # 이미지에서 텍스트/QR 추출 후 URL 안전성 검사
    def analyze_image(self, image_source: Union[str, bytes, np.ndarray]) -> Dict:
        print("이미지 분석 시작...\n")
        
        result = {
            'input_type': 'image',
            'ocr_result': None,
            'qr_result': None,
            'url_analysis': None,
            'final_risk_level': 'unknown',
            'message': ''
        }
        
        # 1. OCR로 텍스트 추출
        print("1️OCR 텍스트 추출...")
        ocr_result = self.ocr_extractor.extract_from_image(image_source)
        result['ocr_result'] = ocr_result
        
        if ocr_result['success']:
            print(f"   {ocr_result['message']}")
            if ocr_result['text']:
                print(f"   추출된 텍스트: {ocr_result['text'][:100]}...")
        else:
            print(f"   {ocr_result['message']}")
        
        # 2. QR 코드 디코딩
        print("\n QR 코드 디코딩...")
        qr_result = self.qr_decoder.decode_from_image(image_source)
        result['qr_result'] = qr_result
        
        if qr_result['success'] and qr_result['qr_codes']:
            print(f"   {qr_result['message']}")
            for qr in qr_result['qr_codes']:
                print(f"   QR 데이터: {qr['data']}")
        else:
            print(f"   {qr_result['message']}")
        
        # 3. URL 추출 및 분석
        combined_text = ocr_result.get('text', '')
        qr_urls = qr_result.get('urls', [])
        
        result['url_analysis'] = self._analyze_urls(combined_text, qr_urls)
        
        # 4. 최종 위험도 판정
        result['final_risk_level'] = self._determine_risk_level(result)
        result['message'] = self._generate_message(result)
        
        print("\n" + "="*60)
        print(f"🎯 최종 판정: {result['final_risk_level'].upper()}")
        print(f"📝 {result['message']}")
        print("="*60 + "\n")
        
        return result

    # 텍스트에서 URL 추출 후 안전성 검사
    def analyze_text(self, text: str) -> Dict:
        print("텍스트 분석 시작...\n")
        
        result = {
            'input_type': 'text',
            'ocr_result': None,
            'qr_result': None,
            'url_analysis': None,
            'final_risk_level': 'unknown',
            'message': ''
        }
        
        # URL 추출 및 분석
        result['url_analysis'] = self._analyze_urls(text, [])
        
        # 최종 위험도 판정
        result['final_risk_level'] = self._determine_risk_level(result)
        result['message'] = self._generate_message(result)
        
        print("\n" + "="*60)
        print(f"최종 판정: {result['final_risk_level'].upper()}")
        print(f"{result['message']}")
        print("="*60 + "\n")
        
        return result

    # URL 추출 및 안전성 검사
    def _analyze_urls(self, text: str, additional_urls: list) -> Dict:
        print("\n🔗 URL 추출 및 안전성 검사...")
        
        # 텍스트에서 URL 추출
        extraction_result = self.url_extractor.extract_urls(text)
        
        # 모든 URL 합치기
        all_urls = list(set(
            extraction_result.get('normalized_urls', []) + 
            additional_urls
        ))
        
        if not all_urls:
            print("   URL이 발견되지 않았습니다")
            return {
                'has_urls': False,
                'url_count': 0,
                'urls': [],
                'safe_browsing_result': None,
                'ml_predictions': {},
                'ml_detected_urls': []
            }
        
        print(f"   {len(all_urls)}개의 URL 발견")
        for url in all_urls:
            print(f"      - {url}")
        
        # 1차: Google Safe Browsing 검사
        print("\n   🔍 [1차 검사] Google Safe Browsing API...")
        safe_browsing_result = self.safe_browsing.check_urls(all_urls)
        
        if safe_browsing_result['success']:
            if safe_browsing_result['safe']:
                print("      ✅ Safe Browsing: 모든 URL 안전")
            else:
                print(f"      ⚠️ Safe Browsing: {len(safe_browsing_result['dangerous_urls'])}개 위험 URL 발견!")
                for url in safe_browsing_result['dangerous_urls']:
                    print(f"         ❌ {url}")
        else:
            print(f"      ⚠️ API 검사 실패: {safe_browsing_result['message']}")
        
        # 2차: ML 모델 검사
        ml_predictions = {}
        ml_detected_urls = []
        
        if self.url_classifier.is_model_loaded():
            print("\n   🤖 [2차 검사] ML 모델 (Random Forest)...")
            
            # Safe Browsing에서 안전하다고 판정된 URL도 2차 검사
            urls_to_check = all_urls
            
            for url in urls_to_check:
                pred = self.url_classifier.predict(url)
                ml_predictions[url] = pred
                
                if pred.get('is_malicious'):
                    ml_detected_urls.append(url)
                    confidence = pred.get('confidence', 0)
                    print(f"      ⚠️ ML 탐지: {url}")
                    print(f"         신뢰도: {confidence:.1%} | 악성 확률: {pred['probability']['malicious']:.1%}")
            
            if not ml_detected_urls:
                print("      ✅ ML 모델: 모든 URL 안전")
        else:
            print("\n   ℹ️ ML 모델이 로드되지 않음 (1차 검사만 사용)")
        
        return {
            'has_urls': True,
            'url_count': len(all_urls),
            'urls': all_urls,
            'safe_browsing_result': safe_browsing_result,
            'ml_predictions': ml_predictions,
            'ml_detected_urls': ml_detected_urls
        }

    # 최종 위험도 판정
    def _determine_risk_level(self, result: dict) -> str:
        url_analysis = result.get('url_analysis')
        
        if not url_analysis or not url_analysis['has_urls']:
            return 'low'  # URL 없음 = 낮은 위험
        
        safe_browsing = url_analysis.get('safe_browsing_result')
        ml_detected_urls = url_analysis.get('ml_detected_urls', [])
        
        # 1차: Safe Browsing 검사 결과
        if safe_browsing and safe_browsing['success'] and not safe_browsing['safe']:
            return 'high'  # Safe Browsing에서 위험 감지 = 높은 위험
        
        # 2차: ML 모델 검사 결과
        if ml_detected_urls:
            return 'high'  # ML 모델이 악성 판정 = 높은 위험
        
        # API 실패
        if not safe_browsing or not safe_browsing['success']:
            return 'medium'  # API 실패 = 중간 위험
        
        return 'low'  # 모두 안전 = 낮은 위험

    # 결과 메시지 생성
    def _generate_message(self, result: dict) -> str:
        risk_level = result['final_risk_level']
        url_analysis = result.get('url_analysis', {})
        
        if risk_level == 'high':
            # Safe Browsing 위험 URL
            sb_dangerous = url_analysis.get('safe_browsing_result', {}).get('dangerous_urls', [])
            # ML 모델 위험 URL
            ml_dangerous = url_analysis.get('ml_detected_urls', [])
            
            # 중복 제거하고 총 개수 계산
            total_dangerous = len(set(sb_dangerous + ml_dangerous))
            
            # 탐지 방법 표시
            detection_methods = []
            if sb_dangerous:
                detection_methods.append(f"Safe Browsing {len(sb_dangerous)}개")
            if ml_dangerous:
                detection_methods.append(f"ML 모델 {len(ml_dangerous)}개")
            
            detection_info = " + ".join(detection_methods) if detection_methods else ""
            
            return f"⚠️ 위험! {total_dangerous}개의 악성 URL이 감지되었습니다 ({detection_info}). 절대 클릭하지 마세요!"
        
        elif risk_level == 'medium':
            if url_analysis.get('has_urls'):
                return "⚠️ 주의! URL 안전성 검사에 실패했습니다. 신중하게 확인하세요."
            return "ℹ️ URL이 포함되어 있습니다. 발신자를 확인하세요."
        
        else:  # low
            if url_analysis.get('has_urls'):
                return "✅ URL은 안전한 것으로 확인되었습니다 (1차 + 2차 검사 통과)."
            return "✅ URL이 감지되지 않았습니다."


# 사용 예시
if __name__ == "__main__":
    # 분석기 초기화
    analyzer = SmishingAnalyzer()
    
    # 텍스트 분석 예시
    test_text = """
    [Web발신]
    택배가 도착했습니다.
    확인: http://testsafebrowsing.appspot.com/apiv4/ANY_PLATFORM/MALWARE/URL/
    """
    
    result = analyzer.analyze_text(test_text)
    
    print("\n상세 결과:")
    print(f"위험도: {result['final_risk_level']}")
    print(f"메시지: {result['message']}")
    
    if result['url_analysis']:
        print(f"\nURL 개수: {result['url_analysis']['url_count']}")
        print(f"발견된 URL: {result['url_analysis']['urls']}")
