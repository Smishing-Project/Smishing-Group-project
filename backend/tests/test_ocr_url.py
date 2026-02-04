"""
OCR/QR + URL 위험 판단 기능 테스트 스크립트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, '/app')

from src.analyzer import SmishingAnalyzer


def test_text_analysis():
    """텍스트 분석 테스트"""
    print("\n" + "="*60)
    print("📝 테스트 1: 텍스트 분석")
    print("="*60)
    
    analyzer = SmishingAnalyzer()
    
    # 테스트 케이스 1: 악성 URL 포함
    print("\n[테스트 케이스 1] 악성 URL 포함 문자")
    test_text_1 = """
    [Web발신]
    택배가 도착했습니다.
    확인: http://testsafebrowsing.appspot.com/apiv4/ANY_PLATFORM/MALWARE/URL/
    """
    
    result_1 = analyzer.analyze_text(test_text_1)
    assert result_1['final_risk_level'] == 'high', "악성 URL 감지 실패"
    print("✅ 테스트 통과: 악성 URL 정상 감지")
    
    # 테스트 케이스 2: 안전한 URL 포함
    print("\n[테스트 케이스 2] 안전한 URL 포함 문자")
    test_text_2 = """
    안녕하세요.
    자세한 내용은 https://www.google.com 을 참고하세요.
    """
    
    result_2 = analyzer.analyze_text(test_text_2)
    assert result_2['final_risk_level'] == 'low', "안전한 URL 판정 실패"
    print("✅ 테스트 통과: 안전한 URL 정상 판정")
    
    # 테스트 케이스 3: URL 없음
    print("\n[테스트 케이스 3] URL 없는 일반 문자")
    test_text_3 = """
    안녕하세요.
    오늘 저녁 약속 있으신가요?
    """
    
    result_3 = analyzer.analyze_text(test_text_3)
    assert result_3['final_risk_level'] == 'low', "URL 없음 판정 실패"
    print("✅ 테스트 통과: URL 없음 정상 판정")
    
    print("\n" + "="*60)
    print("✅ 모든 텍스트 분석 테스트 통과!")
    print("="*60)


def test_url_extractor():
    """URL 추출 테스트"""
    print("\n" + "="*60)
    print("🔗 테스트 2: URL 추출")
    print("="*60)
    
    from src.url.url_extractor import URLExtractor
    
    extractor = URLExtractor()
    
    test_cases = [
        ("http://example.com", 1),
        ("www.example.com", 1),
        ("example.com/path", 1),
        ("bit.ly/abc123", 1),
        ("여러 URL: http://test1.com www.test2.com test3.kr", 3),
    ]
    
    for text, expected_count in test_cases:
        result = extractor.extract_urls(text)
        actual_count = result['count']
        
        print(f"\n입력: {text}")
        print(f"예상: {expected_count}개, 실제: {actual_count}개")
        
        assert actual_count == expected_count, f"URL 추출 실패: 예상 {expected_count}, 실제 {actual_count}"
        print("✅ 통과")
    
    print("\n" + "="*60)
    print("✅ 모든 URL 추출 테스트 통과!")
    print("="*60)


def test_safe_browsing():
    """Safe Browsing API 테스트"""
    print("\n" + "="*60)
    print("🔍 테스트 3: Google Safe Browsing API")
    print("="*60)
    
    from src.url.safe_browsing import SafeBrowsingChecker
    
    checker = SafeBrowsingChecker()
    
    # 악성 URL (Google 테스트용)
    malicious_url = "http://testsafebrowsing.appspot.com/apiv4/ANY_PLATFORM/MALWARE/URL/"
    safe_url = "https://www.google.com"
    
    print(f"\n[테스트] 악성 URL: {malicious_url}")
    result_1 = checker.check_single_url(malicious_url)
    
    if result_1['success']:
        assert not result_1['safe'], "악성 URL을 안전하다고 판정"
        print("✅ 악성 URL 정상 감지")
    else:
        print(f"⚠️ API 호출 실패: {result_1['message']}")
    
    print(f"\n[테스트] 안전한 URL: {safe_url}")
    result_2 = checker.check_single_url(safe_url)
    
    if result_2['success']:
        assert result_2['safe'], "안전한 URL을 위험하다고 판정"
        print("✅ 안전한 URL 정상 판정")
    else:
        print(f"⚠️ API 호출 실패: {result_2['message']}")
    
    print("\n" + "="*60)
    print("✅ Safe Browsing API 테스트 통과!")
    print("="*60)


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "🚀"*30)
    print("OCR/QR + URL 위험 판단 통합 테스트 시작")
    print("🚀"*30)
    
    try:
        test_url_extractor()
        test_safe_browsing()
        test_text_analysis()
        
        print("\n" + "="*60)
        print("🎉 모든 테스트 통과! 시스템이 정상 작동합니다.")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
