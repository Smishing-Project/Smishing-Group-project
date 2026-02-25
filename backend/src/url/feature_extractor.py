"""
URL 특징 추출 모듈
피싱 URL 탐지를 위한 30개 특징 추출
"""

import re
import socket
from urllib.parse import urlparse
from typing import Dict, List
import tldextract
import whois
from datetime import datetime


class URLFeatureExtractor:
    """URL에서 ML 모델용 특징을 추출하는 클래스"""
    
    def __init__(self):
        """특징 추출기 초기화"""
        # 의심스러운 키워드 리스트
        self.suspicious_keywords = [
            'login', 'signin', 'account', 'update', 'secure', 'banking',
            'verify', 'confirm', 'password', 'credit', 'paypal', 'amazon',
            'ebay', 'apple', 'google', 'microsoft', 'facebook', 'netflix',
            'suspended', 'locked', 'unusual', 'alert', 'urgent'
        ]
        
        # TLD (Top-Level Domain) 신뢰도
        self.trusted_tlds = ['com', 'org', 'net', 'edu', 'gov', 'mil']
        
        print("✅ URL Feature Extractor 초기화 완료")
    
    def extract_features(self, url: str) -> Dict[str, float]:
        """
        URL에서 30개 특징 추출
        
        Args:
            url: 분석할 URL
        
        Returns:
            dict: 특징 이름과 값의 딕셔너리
        """
        features = {}
        
        try:
            # URL 파싱
            parsed = urlparse(url)
            extracted = tldextract.extract(url)
            
            # 1-10: URL 구조 특징
            features.update(self._extract_url_structure_features(url, parsed, extracted))
            
            # 11-20: 도메인 특징
            features.update(self._extract_domain_features(parsed, extracted))
            
            # 21-30: 콘텐츠 특징
            features.update(self._extract_content_features(url, parsed))
            
        except Exception as e:
            print(f"⚠️ 특징 추출 실패: {e}")
            # 오류 시 기본값 반환
            features = self._get_default_features()
        
        return features
    
    def _extract_url_structure_features(
        self, 
        url: str, 
        parsed, 
        extracted
    ) -> Dict[str, float]:
        """URL 구조 관련 특징 (1-10)"""
        features = {}
        
        # 1. URL 길이
        features['url_length'] = len(url)
        
        # 2. 도메인 길이
        features['domain_length'] = len(parsed.netloc)
        
        # 3. 경로 길이
        features['path_length'] = len(parsed.path)
        
        # 4. 하이픈 개수
        features['hyphen_count'] = url.count('-')
        
        # 5. 언더스코어 개수
        features['underscore_count'] = url.count('_')
        
        # 6. 슬래시 개수
        features['slash_count'] = url.count('/')
        
        # 7. 점(.) 개수
        features['dot_count'] = url.count('.')
        
        # 8. @ 기호 존재 여부 (피싱에 자주 사용)
        features['has_at_symbol'] = 1 if '@' in url else 0
        
        # 9. 숫자 개수
        features['digit_count'] = sum(c.isdigit() for c in url)
        
        # 10. 특수문자 개수
        special_chars = re.findall(r'[!#$%&*+=?^`{|}~]', url)
        features['special_char_count'] = len(special_chars)
        
        return features
    
    def _extract_domain_features(self, parsed, extracted) -> Dict[str, float]:
        """도메인 관련 특징 (11-20)"""
        features = {}
        
        domain = parsed.netloc
        
        # 11. IP 주소 사용 여부
        features['is_ip_address'] = 1 if self._is_ip_address(domain) else 0
        
        # 12. 서브도메인 개수
        subdomain = extracted.subdomain
        features['subdomain_count'] = len(subdomain.split('.')) if subdomain else 0
        
        # 13. 도메인에 숫자 포함 여부
        features['domain_has_digits'] = 1 if any(c.isdigit() for c in domain) else 0
        
        # 14. 신뢰할 수 있는 TLD 여부
        tld = extracted.suffix
        features['is_trusted_tld'] = 1 if tld in self.trusted_tlds else 0
        
        # 15. www 접두사 존재 여부
        features['has_www'] = 1 if domain.startswith('www.') else 0
        
        # 16. 도메인에 하이픈 개수
        features['domain_hyphen_count'] = domain.count('-')
        
        # 17. 도메인 엔트로피 (복잡도)
        features['domain_entropy'] = self._calculate_entropy(domain)
        
        # 18. 도메인이 숫자로 시작하는지
        features['starts_with_digit'] = 1 if domain and domain[0].isdigit() else 0
        
        # 19. 도메인 점(.) 개수
        features['domain_dot_count'] = domain.count('.')
        
        # 20. 긴 도메인 여부 (15자 이상)
        features['is_long_domain'] = 1 if len(domain) > 15 else 0
        
        return features
    
    def _extract_content_features(self, url: str, parsed) -> Dict[str, float]:
        """콘텐츠 관련 특징 (21-30)"""
        features = {}
        
        url_lower = url.lower()
        
        # 21. HTTPS 사용 여부
        features['is_https'] = 1 if parsed.scheme == 'https' else 0
        
        # 22. 포트 번호 명시 여부
        features['has_port'] = 1 if ':' in parsed.netloc and not parsed.netloc.startswith('[') else 0
        
        # 23. 의심스러운 키워드 개수
        suspicious_count = sum(1 for keyword in self.suspicious_keywords if keyword in url_lower)
        features['suspicious_keyword_count'] = suspicious_count
        
        # 24. 쿼리 파라미터 개수
        query_params = parsed.query.split('&') if parsed.query else []
        features['query_param_count'] = len(query_params)
        
        # 25. Fragment 존재 여부
        features['has_fragment'] = 1 if parsed.fragment else 0
        
        # 26. 경로 깊이 (슬래시 개수)
        path_depth = len([p for p in parsed.path.split('/') if p])
        features['path_depth'] = path_depth
        
        # 27. 파일 확장자 존재 여부
        path = parsed.path
        features['has_file_extension'] = 1 if '.' in path.split('/')[-1] else 0
        
        # 28. URL에 중복 문자 패턴 (aaa, 111 등)
        features['has_repetitive_chars'] = 1 if re.search(r'(.)\1{2,}', url) else 0
        
        # 29. 도메인과 브랜드명 불일치 (예: paypal-secure.com)
        features['brand_mismatch'] = self._check_brand_mismatch(url_lower)
        
        # 30. 단축 URL 여부
        short_url_domains = ['bit.ly', 't.co', 'goo.gl', 'tinyurl.com', 'ow.ly']
        features['is_shortened_url'] = 1 if any(domain in url_lower for domain in short_url_domains) else 0
        
        return features
    
    def _is_ip_address(self, domain: str) -> bool:
        """도메인이 IP 주소인지 확인"""
        # IPv4 패턴
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ipv4_pattern, domain):
            return True
        
        # IPv6 패턴 (간단한 체크)
        if ':' in domain and not domain.startswith('['):
            return True
        
        return False
    
    def _calculate_entropy(self, text: str) -> float:
        """문자열의 엔트로피 계산 (복잡도 측정)"""
        if not text:
            return 0.0
        
        from collections import Counter
        import math
        
        # 문자 빈도 계산
        char_freq = Counter(text)
        text_len = len(text)
        
        # 엔트로피 계산
        entropy = 0.0
        for count in char_freq.values():
            probability = count / text_len
            entropy -= probability * math.log2(probability)
        
        return round(entropy, 4)
    
    def _check_brand_mismatch(self, url: str) -> int:
        """브랜드명 불일치 검사"""
        # 유명 브랜드 리스트
        brands = ['paypal', 'amazon', 'google', 'apple', 'microsoft', 
                  'facebook', 'netflix', 'ebay', 'bank', 'secure']
        
        # URL에 브랜드명이 있지만 실제 도메인이 아닌 경우
        for brand in brands:
            if brand in url:
                # 도메인이 실제로 해당 브랜드가 아니면 의심
                if f'{brand}.com' not in url and f'{brand}.net' not in url:
                    return 1
        
        return 0
    
    def _get_default_features(self) -> Dict[str, float]:
        """오류 시 기본 특징 값 반환"""
        feature_names = [
            'url_length', 'domain_length', 'path_length', 'hyphen_count',
            'underscore_count', 'slash_count', 'dot_count', 'has_at_symbol',
            'digit_count', 'special_char_count', 'is_ip_address', 'subdomain_count',
            'domain_has_digits', 'is_trusted_tld', 'has_www', 'domain_hyphen_count',
            'domain_entropy', 'starts_with_digit', 'domain_dot_count', 'is_long_domain',
            'is_https', 'has_port', 'suspicious_keyword_count', 'query_param_count',
            'has_fragment', 'path_depth', 'has_file_extension', 'has_repetitive_chars',
            'brand_mismatch', 'is_shortened_url'
        ]
        
        return {name: 0.0 for name in feature_names}
    
    def get_feature_names(self) -> List[str]:
        """특징 이름 리스트 반환 (학습 시 사용)"""
        return [
            'url_length', 'domain_length', 'path_length', 'hyphen_count',
            'underscore_count', 'slash_count', 'dot_count', 'has_at_symbol',
            'digit_count', 'special_char_count', 'is_ip_address', 'subdomain_count',
            'domain_has_digits', 'is_trusted_tld', 'has_www', 'domain_hyphen_count',
            'domain_entropy', 'starts_with_digit', 'domain_dot_count', 'is_long_domain',
            'is_https', 'has_port', 'suspicious_keyword_count', 'query_param_count',
            'has_fragment', 'path_depth', 'has_file_extension', 'has_repetitive_chars',
            'brand_mismatch', 'is_shortened_url'
        ]


# 사용 예시
if __name__ == "__main__":
    extractor = URLFeatureExtractor()
    
    # 테스트 URL
    test_urls = [
        "https://www.google.com",
        "http://paypal-secure-login.com/verify",
        "http://192.168.1.1/admin",
        "http://bit.ly/abc123"
    ]
    
    for url in test_urls:
        print(f"\n🔍 URL: {url}")
        features = extractor.extract_features(url)
        print(f"특징 개수: {len(features)}")
        print(f"주요 특징:")
        for key, value in list(features.items())[:5]:
            print(f"  - {key}: {value}")
