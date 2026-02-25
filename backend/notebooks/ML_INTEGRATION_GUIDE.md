# ML 모델 통합 가이드

Google Colab에서 학습한 모델을 프로젝트에 통합하는 방법

---

## 📋 현재 상태

**구현 완료:**
- ✅ 특징 추출기 (`feature_extractor.py`)
- ✅ URL 분류기 클래스 (`url_classifier.py`)
- ✅ Colab 학습 노트북 (`URL_Phishing_Detection_Colab.ipynb`)
- ✅ Analyzer에 분류기 추가

**필요한 작업:**
- ⏳ Colab에서 모델 학습
- ⏳ 학습된 모델 파일 업로드
- ⏳ analyzer.py에서 ML 모델 사용

---

## 🚀 통합 단계

### 1️⃣ Colab에서 모델 학습

`backend/notebooks/URL_Phishing_Detection_Colab.ipynb` 실행

**다운로드할 파일:**
```
url_classifier.pkl
feature_names.pkl
metadata.pkl
```

---

### 2️⃣ 모델 파일 업로드

```
backend/models/
├── url_classifier.pkl
├── feature_names.pkl
└── metadata.pkl
```

---

### 3️⃣ analyzer.py 수정 (2차 검사 추가)

`_analyze_urls` 메서드에 다음 코드 추가:

```python
def _analyze_urls(self, text: str, additional_urls: list) -> Dict:
    # ... (기존 코드)
    
    # Google Safe Browsing 검사
    safe_browsing_result = self.safe_browsing.check_urls(all_urls)
    
    # ✨ ML 모델 2차 검사 추가 ✨
    ml_predictions = {}
    if self.url_classifier.is_model_loaded():
        print("\n   🤖 ML 모델 2차 검사 중...")
        
        # Safe Browsing에서 안전하다고 판정된 URL도 2차 검사
        urls_to_check = safe_browsing_result.get('safe_urls', all_urls)
        
        for url in urls_to_check:
            pred = self.url_classifier.predict(url)
            ml_predictions[url] = pred
            
            if pred['is_malicious']:
                print(f"      ⚠️ ML 탐지: {url} (신뢰도: {pred['confidence']:.2%})")
    
    return {
        'has_urls': True,
        'url_count': len(all_urls),
        'urls': all_urls,
        'safe_browsing_result': safe_browsing_result,
        'ml_predictions': ml_predictions  # ML 결과 추가
    }
```

---

### 4️⃣ _determine_risk_level 수정

ML 모델 결과도 고려하도록 수정:

```python
def _determine_risk_level(self, result: dict) -> str:
    url_analysis = result.get('url_analysis')
    
    if not url_analysis or not url_analysis['has_urls']:
        return 'low'
    
    # 1차: Safe Browsing 검사
    safe_browsing = url_analysis.get('safe_browsing_result')
    if safe_browsing and not safe_browsing['safe']:
        return 'high'  # Safe Browsing에서 위험 감지
    
    # 2차: ML 모델 검사
    ml_predictions = url_analysis.get('ml_predictions', {})
    malicious_urls = [url for url, pred in ml_predictions.items() 
                     if pred.get('is_malicious')]
    
    if malicious_urls:
        return 'high'  # ML 모델이 악성 판정
    
    if not safe_browsing or not safe_browsing['success']:
        return 'medium'  # API 실패
    
    return 'low'  # 모두 안전
```

---

### 5️⃣ _generate_message 수정

ML 탐지 결과도 메시지에 포함:

```python
def _generate_message(self, result: dict) -> str:
    risk_level = result['final_risk_level']
    url_analysis = result.get('url_analysis', {})
    
    if risk_level == 'high':
        # Safe Browsing 위험 URL
        sb_dangerous = url_analysis.get('safe_browsing_result', {}).get('dangerous_urls', [])
        
        # ML 모델 위험 URL
        ml_predictions = url_analysis.get('ml_predictions', {})
        ml_dangerous = [url for url, pred in ml_predictions.items() 
                       if pred.get('is_malicious')]
        
        total_dangerous = len(set(sb_dangerous + ml_dangerous))
        
        if ml_dangerous:
            return f"⚠️ 위험! {total_dangerous}개의 악성 URL 감지 (ML 모델: {len(ml_dangerous)}개)"
        else:
            return f"⚠️ 위험! {total_dangerous}개의 악성 URL 감지"
    
    # ... (기존 코드)
```

---

## 🧪 테스트

```bash
docker-compose exec backend bash

python -c "
from src.analyzer import SmishingAnalyzer

analyzer = SmishingAnalyzer()

# Safe Browsing은 통과하지만 ML이 탐지할 수 있는 URL
test_url = 'http://paypal-secure-login-verify.com'

result = analyzer.analyze_text(f'확인: {test_url}')
print(f'\\n위험도: {result[\"final_risk_level\"]}')
print(f'메시지: {result[\"message\"]}')
"
```

---

## 📊 기대 효과

**1차 검사만 (Safe Browsing):**
- 알려진 악성 URL 탐지
- 빠른 응답
- API 호출 필요

**1차 + 2차 검사 (Safe Browsing + ML):**
- 알려진 악성 URL 탐지
- **새로운 피싱 URL 탐지** ⭐
- 브랜드 사칭 URL 탐지
- 더 높은 정확도

---

##  작업 순서

1. ✅ Colab 노트북으로 모델 학습
2. ✅ 모델 파일 다운로드 (3개)
3. ✅ `backend/models/`에 업로드
4. ✅ analyzer.py 수정 (위 코드 추가)
5. ✅ Docker 재시작
6. ✅ 테스트

---

**Colab 학습이 완료되면 알려주세요!** 🚀
그때 analyzer.py 수정을 도와드리겠습니다.
