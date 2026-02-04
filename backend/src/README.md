# OCR/QR + URL 위험 판단 모듈

스미싱 문자 이미지/텍스트에서 URL을 추출하고 안전성을 검사하는 모듈

---

## 📁 구조

```
backend/src/
├── ocr/
│   ├── ocr_extractor.py     # EasyOCR 텍스트 추출
│   └── qr_decoder.py        # pyzbar QR 코드 디코딩
├── url/
│   ├── url_extractor.py     # 정규표현식 URL 추출
│   └── safe_browsing.py     # Google Safe Browsing API
└── analyzer.py              # 통합 분석 파이프라인
```

---

## 🚀 사용법

### 텍스트 분석

```python
from .analyzer import SmishingAnalyzer

analyzer = SmishingAnalyzer()

text = """
[Web발신]
택배가 도착했습니다.
확인: http://suspicious-url.com
"""

result = analyzer.analyze_text(text)
print(f"위험도: {result['final_risk_level']}")  # high / medium / low
```

### 이미지 분석

```python
from .analyzer import SmishingAnalyzer

analyzer = SmishingAnalyzer()

# 이미지 파일 분석
result = analyzer.analyze_image('path/to/screenshot.jpg')

# 또는 bytes
with open('screenshot.jpg', 'rb') as f:
    result = analyzer.analyze_image(f.read())
```

---

## 🧪 테스트

```bash
# Docker 컨테이너 접속
docker-compose exec backend bash

# 테스트 실행
python tests/test_ocr_url.py
```

---

## 📊 응답 형식

```python
{
    'input_type': 'text' | 'image',
    'url_analysis': {
        'has_urls': True,
        'url_count': 2,
        'urls': ['http://...'],
        'safe_browsing_result': {
            'safe': False,
            'dangerous_urls': [...]
        }
    },
    'final_risk_level': 'high' | 'medium' | 'low',
    'message': '위험도 설명...'
}
```
