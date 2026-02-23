"""
OCR/URL 분석 API 테스트 스크립트
"""

import requests
import json


# API 베이스 URL
BASE_URL = "http://localhost:8000"


def test_health_check():
    """헬스체크 테스트"""
    print("\n" + "="*60)
    print("🏥 테스트 1: 헬스체크")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/v1/health")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200, "헬스체크 실패"
    print("헬스체크 통과")


def test_analyze_text_safe():
    """안전한 텍스트 분석 테스트"""
    print("\n" + "="*60)
    print("📝 테스트 2: 안전한 텍스트 분석")
    print("="*60)
    
    payload = {
        "text": "안녕하세요. 자세한 내용은 https://www.google.com 을 참고하세요."
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze/text",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200, "API 호출 실패"
    assert result['success'] == True, "분석 실패"
    assert result['final_risk_level'] == 'low', "위험도 판정 오류"
    print("안전한 URL 정상 판정")


def test_analyze_text_malicious():
    """악성 URL 텍스트 분석 테스트"""
    print("\n" + "="*60)
    print("⚠️ 테스트 3: 악성 URL 텍스트 분석")
    print("="*60)
    
    payload = {
        "text": "[Web발신]\n택배가 도착했습니다.\n확인: http://testsafebrowsing.appspot.com/apiv4/ANY_PLATFORM/MALWARE/URL/"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze/text",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200, "API 호출 실패"
    assert result['success'] == True, "분석 실패"
    assert result['final_risk_level'] == 'high', "악성 URL 미탐지"
    print("✅ 악성 URL 정상 탐지")


def test_analyze_text_no_url():
    """URL 없는 텍스트 분석 테스트"""
    print("\n" + "="*60)
    print("💬 테스트 4: URL 없는 텍스트 분석")
    print("="*60)
    
    payload = {
        "text": "안녕하세요. 오늘 날씨가 좋네요."
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze/text",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200, "API 호출 실패"
    assert result['success'] == True, "분석 실패"
    assert result['final_risk_level'] == 'low', "위험도 판정 오류"
    print("✅ URL 없음 정상 판정")


def test_analyze_text_empty():
    """빈 텍스트 에러 테스트"""
    print("\n" + "="*60)
    print("❌ 테스트 5: 빈 텍스트 에러 처리")
    print("="*60)
    
    payload = {
        "text": ""
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze/text",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 422, "검증 오류 미발생"
    print("✅ 빈 텍스트 검증 정상")


def test_analyze_image():
    """이미지 분석 테스트 (실제 이미지 파일 필요)"""
    print("\n" + "="*60)
    print("🖼️ 테스트 6: 이미지 분석 (스킵)")
    print("="*60)
    
    print("ℹ️ 이미지 분석 테스트는 실제 이미지 파일이 필요합니다.")
    print("   테스트 이미지를 준비한 후 다음 코드를 사용하세요:")
    print("""
    with open('test_image.jpg', 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze/image",
            files=files
        )
    """)


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "🚀"*30)
    print("FastAPI 엔드포인트 테스트 시작")
    print("🚀"*30)
    
    try:
        test_health_check()
        test_analyze_text_safe()
        test_analyze_text_malicious()
        test_analyze_text_no_url()
        test_analyze_text_empty()
        test_analyze_image()
        
        print("\n" + "="*60)
        print("🎉 모든 테스트 통과!")
        print("="*60)
        print("\n✅ API 서버가 정상적으로 작동합니다.")
        print(f"📍 API 문서: {BASE_URL}/docs")
        print(f"📍 ReDoc: {BASE_URL}/redoc")
        
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 연결 실패: API 서버가 실행 중인지 확인하세요.")
        print(f"   서버 주소: {BASE_URL}")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")


if __name__ == "__main__":
    run_all_tests()
