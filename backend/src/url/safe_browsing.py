import requests
import os
from typing import List, Dict
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Google Safe Browsing API를 사용하여 URL 안전성을 검사하는 클래스
class SafeBrowsingChecker:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_SAFE_BROWSING_API_KEY')
        
        if not self.api_key:
            raise ValueError("API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
        
        self.endpoint = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
        
        # 위협 유형
        self.threat_types = [
            "MALWARE",  # 멀웨어
            "SOCIAL_ENGINEERING",  # 피싱
            "UNWANTED_SOFTWARE",  # 악성 소프트웨어
            "POTENTIALLY_HARMFUL_APPLICATION"  # 위험한 앱
        ]
        
        # 캐시 (동일 URL 재검사 방지)
        self.cache = {}
        self.cache_duration = timedelta(hours=1)
        
        print(f"Safe Browsing Checker 초기화 완료 (API 키: {self.api_key[:10]}...)")

    # URL 리스트 안전성 검사
    def check_urls(self, urls: List[str], use_cache: bool = True) -> Dict[str, any]:
        try:
            if not urls:
                return {
                    'success': True,
                    'safe': True,
                    'threats': [],
                    'safe_urls': [],
                    'dangerous_urls': [],
                    'message': '검사할 URL이 없습니다'
                }
            
            # 캐시 확인
            if use_cache:
                urls_to_check = []
                cached_threats = []
                
                for url in urls:
                    cached = self._get_from_cache(url)
                    if cached is not None:
                        if cached:  # 위험한 URL
                            cached_threats.extend(cached)
                    else:
                        urls_to_check.append(url)
                
                # 모두 캐시에 있는 경우
                if not urls_to_check:
                    dangerous_urls = [t['threat']['url'] for t in cached_threats]
                    safe_urls = [url for url in urls if url not in dangerous_urls]
                    
                    return {
                        'success': True,
                        'safe': len(cached_threats) == 0,
                        'threats': cached_threats,
                        'safe_urls': safe_urls,
                        'dangerous_urls': dangerous_urls,
                        'message': f'캐시에서 조회 완료 ({len(dangerous_urls)}개 위험)'
                    }
            else:
                urls_to_check = urls
                cached_threats = []
            
            # API 요청 페이로드
            payload = {
                "client": {
                    "clientId": "smishing-detector",
                    "clientVersion": "1.0.0"
                },
                "threatInfo": {
                    "threatTypes": self.threat_types,
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url} for url in urls_to_check]
                }
            }
            
            # API 호출
            response = requests.post(
                f"{self.endpoint}?key={self.api_key}",
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'safe': None,
                    'threats': [],
                    'safe_urls': [],
                    'dangerous_urls': [],
                    'message': f'API 오류: {response.status_code}'
                }
            
            data = response.json()
            
            # 위협이 없는 경우 (빈 응답)
            if not data or data == {}:
                # 캐시에 저장
                for url in urls_to_check:
                    self._save_to_cache(url, [])
                
                return {
                    'success': True,
                    'safe': True,
                    'threats': cached_threats,
                    'safe_urls': urls,
                    'dangerous_urls': [],
                    'message': '모든 URL 안전'
                }
            
            # 위협 발견
            threats = data.get('matches', [])
            all_threats = cached_threats + threats
            
            # 캐시에 저장
            for threat in threats:
                url = threat['threat']['url']
                self._save_to_cache(url, [threat])
            
            # 안전한 URL 저장
            dangerous_urls = [t['threat']['url'] for t in all_threats]
            safe_urls = [url for url in urls if url not in dangerous_urls]
            
            for url in safe_urls:
                if url in urls_to_check:
                    self._save_to_cache(url, [])
            
            return {
                'success': True,
                'safe': False,
                'threats': all_threats,
                'safe_urls': safe_urls,
                'dangerous_urls': dangerous_urls,
                'message': f'{len(all_threats)}개 위험 URL 발견'
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'safe': None,
                'threats': [],
                'safe_urls': [],
                'dangerous_urls': [],
                'message': 'API 요청 타임아웃'
            }
        except Exception as e:
            return {
                'success': False,
                'safe': None,
                'threats': [],
                'safe_urls': [],
                'dangerous_urls': [],
                'message': f'검사 중 오류: {str(e)}'
            }

    # 단일 URL 안전성 검사
    def check_single_url(self, url: str, use_cache: bool = True) -> Dict[str, any]:
        return self.check_urls([url], use_cache)

    # 캐시에서 URL 조회
    def _get_from_cache(self, url: str):
        if url in self.cache:
            cached_time, cached_data = self.cache[url]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        return None

    # 캐시에 URL 저장
    def _save_to_cache(self, url: str, threats: list):
        self.cache[url] = (datetime.now(), threats)

    # 캐시 초기화
    def clear_cache(self):
        self.cache = {}
        print("캐시가 초기화되었습니다")

    # 위협 정보를 읽기 쉬운 형태로 변환
    def get_threat_details(self, threat: dict) -> Dict[str, str]:
        threat_type_names = {
            'MALWARE': '멀웨어',
            'SOCIAL_ENGINEERING': '피싱',
            'UNWANTED_SOFTWARE': '악성 소프트웨어',
            'POTENTIALLY_HARMFUL_APPLICATION': '위험한 앱'
        }
        
        threat_type = threat.get('threatType', 'UNKNOWN')
        
        return {
            'url': threat['threat']['url'],
            'threat_type': threat_type,
            'threat_type_kr': threat_type_names.get(threat_type, '알 수 없음'),
            'platform': threat.get('platformType', 'ANY_PLATFORM'),
            'cache_duration': threat.get('cacheDuration', 'N/A')
        }


# 사용 예시
if __name__ == "__main__":
    try:
        checker = SafeBrowsingChecker()
        
        test_urls = [
            "http://testsafebrowsing.appspot.com/apiv4/ANY_PLATFORM/MALWARE/URL/",
            "https://www.google.com"
        ]
        
        print("\n🔍 URL 안전성 검사 시작...")
        result = checker.check_urls(test_urls)
        
        print(f"\n결과: {result['message']}")
        print(f"안전한 URL: {len(result['safe_urls'])}개")
        print(f"위험한 URL: {len(result['dangerous_urls'])}개")
        
        if result['threats']:
            print("\n위협 상세 정보:")
            for threat in result['threats']:
                details = checker.get_threat_details(threat)
                print(f"  - {details['url']}")
                print(f"    유형: {details['threat_type_kr']}")
        
        print("\nSafe Browsing API가 정상적으로 작동합니다!")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
