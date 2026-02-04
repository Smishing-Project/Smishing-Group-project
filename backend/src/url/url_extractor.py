"""
URL 추출 모듈
텍스트에서 URL을 추출하고 정규화합니다.
"""

import re
import requests
from typing import List, Dict
from urllib.parse import urlparse, urlunparse


class URLExtractor:
    """텍스트에서 URL을 추출하는 클래스"""
    
    def __init__(self):
        """URL 추출기 초기화"""
        # URL 패턴 정의
        self.patterns = [
            # http:// 또는 https:// 포함
            r'https?://[^\s<>"{}|\\^`\[\]]+',
            # www. 시작
            r'www\.[^\s<>"{}|\\^`\[\]]+',
            # 도메인.확장자 형태
            r'\b[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:/[^\s<>"{}|\\^`\[\]]*)?',
            # 단축 URL (bit.ly, t.co 등)
            r'\b(?:bit\.ly|t\.co|goo\.gl|ow\.ly|tinyurl\.com)/[a-zA-Z0-9]+',
        ]
        
        # 단축 URL 도메인 리스트
        self.short_url_domains = [
            'bit.ly', 't.co', 'goo.gl', 'ow.ly', 'tinyurl.com',
            'short.ly', 'is.gd', 'buff.ly', 'adf.ly'
        ]
        
        print("✅ URL Extractor 초기화 완료")
    
    def extract_urls(self, text: str) -> Dict[str, any]:
        """
        텍스트에서 URL 추출
        
        Args:
            text: URL을 추출할 텍스트
        
        Returns:
            dict: {
                'success': bool,
                'urls': list,  # 추출된 URL 리스트
                'normalized_urls': list,  # 정규화된 URL 리스트
                'count': int,
                'message': str
            }
        """
        try:
            if not text:
                return {
                    'success': True,
                    'urls': [],
                    'normalized_urls': [],
                    'count': 0,
                    'message': '입력 텍스트가 비어있습니다'
                }
            
            # 모든 패턴으로 URL 추출
            urls = set()
            for pattern in self.patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                urls.update(matches)
            
            # 리스트로 변환
            urls = list(urls)
            
            # 다른 URL의 부분집합인 URL 제거 (예: www.example이 www.example.com에 포함)
            filtered_urls = []
            for url in urls:
                is_subset = False
                for other_url in urls:
                    if url != other_url and url in other_url:
                        is_subset = True
                        break
                if not is_subset:
                    filtered_urls.append(url)
            
            urls = filtered_urls
            
            if not urls:
                return {
                    'success': True,
                    'urls': [],
                    'normalized_urls': [],
                    'count': 0,
                    'message': 'URL이 발견되지 않았습니다'
                }
            
            # URL 정규화 및 중복 제거
            normalized_urls = list(set([self.normalize_url(url) for url in urls]))
            
            return {
                'success': True,
                'urls': urls,
                'normalized_urls': normalized_urls,
                'count': len(normalized_urls),  # 정규화 후 개수
                'message': f'{len(normalized_urls)}개의 URL 발견'
            }
            
        except Exception as e:
            return {
                'success': False,
                'urls': [],
                'normalized_urls': [],
                'count': 0,
                'message': f'URL 추출 중 오류: {str(e)}'
            }
    
    def normalize_url(self, url: str) -> str:
        """
        URL 정규화 (프로토콜 추가, 소문자 변환 등)
        
        Args:
            url: 정규화할 URL
        
        Returns:
            str: 정규화된 URL
        """
        # 공백 제거
        url = url.strip()
        
        # 프로토콜이 없으면 http:// 추가
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # URL 파싱
        parsed = urlparse(url)
        
        # 도메인 소문자 변환 및 www. 제거 (중복 방지)
        netloc = parsed.netloc.lower()
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        
        # URL 재구성
        normalized = urlunparse((
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        
        return normalized
    
    def expand_short_url(self, short_url: str, timeout: int = 5) -> str:
        """
        단축 URL을 원본 URL로 확장
        
        Args:
            short_url: 단축 URL
            timeout: 요청 타임아웃 (초)
        
        Returns:
            str: 확장된 URL (실패 시 원본 반환)
        """
        try:
            # HEAD 요청으로 리다이렉트 확인
            response = requests.head(
                short_url,
                allow_redirects=True,
                timeout=timeout
            )
            
            # 최종 URL 반환
            return response.url
            
        except Exception as e:
            print(f"⚠️ 단축 URL 확장 실패: {e}")
            return short_url
    
    def is_short_url(self, url: str) -> bool:
        """
        단축 URL 여부 확인
        
        Args:
            url: 확인할 URL
        
        Returns:
            bool: 단축 URL 여부
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # www. 제거
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain in self.short_url_domains
    
    def extract_domain(self, url: str) -> str:
        """
        URL에서 도메인 추출
        
        Args:
            url: URL
        
        Returns:
            str: 도메인
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ''


# 사용 예시
if __name__ == "__main__":
    # URL 추출기 초기화
    extractor = URLExtractor()
    
    # 테스트
    test_text = """
    택배가 도착했습니다. 확인: http://bit.ly/test123
    자세한 내용은 www.example.com을 참고하세요.
    문의: example.kr/contact
    """
    
    result = extractor.extract_urls(test_text)
    print(f"발견된 URL: {result['count']}개")
    print(f"URLs: {result['normalized_urls']}")
    
    print("\nURL 추출기 모듈이 정상적으로 로드되었습니다.")
