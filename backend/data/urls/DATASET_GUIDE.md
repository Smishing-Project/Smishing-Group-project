# URL 데이터셋 수집 가이드

ML 모델 학습을 위한 악성/정상 URL 데이터셋 수집 방법

---

## 📊 필요한 데이터

**목표:** 약 10,000개 URL (악성 5,000 + 정상 5,000)

---

## 1️⃣ 악성 URL 데이터셋

### PhishTank (추천 ⭐)
**URL:** https://www.phishtank.com/developer_info.php

**다운로드:**
```bash
# CSV 형식
wget http://data.phishtank.com/data/online-valid.csv

# JSON 형식  
wget http://data.phishtank.com/data/online-valid.json
```

**특징:**
- 검증된 피싱 URL
- 매일 업데이트
- 무료 사용 가능

---

### URLhaus (악성 코드 URL)
**URL:** https://urlhaus.abuse.ch/

**다운로드:**
```bash
wget https://urlhaus.abuse.ch/downloads/csv_recent/
```

**특징:**
- 멀웨어 배포 URL
- 실시간 업데이트
- CSV 형식

---

### OpenPhish
**URL:** https://openphish.com/feed.txt

**다운로드:**
```bash
wget https://openphish.com/feed.txt
```

**특징:**
- 피싱 URL 피드
- 텍스트 파일 형식
- 무료 (제한적)

---

## 2️⃣ 정상 URL 데이터셋

### Tranco Top Sites (추천 ⭐)
**URL:** https://tranco-list.eu/

**다운로드:**
```bash
# 최신 Top 10K 사이트
wget https://tranco-list.eu/top-1m.csv.zip
unzip top-1m.csv.zip
```

**특징:**
- 신뢰할 수 있는 상위 사이트
- 매일 업데이트
- 무료

---

### Alexa Top Sites (대안)
**URL:** https://www.domcop.com/top-10-million-domains

**다운로드:**
```bash
# Top 10M 도메인 리스트
wget https://www.domcop.com/files/top/top10milliondomains.csv.zip
```

---

### 한국 주요 사이트 (수동 수집)
```
naver.com
daum.net
google.co.kr
youtube.com
kakao.com
coupang.com
nate.com
zum.com
tistory.com
gmarket.co.kr
11st.co.kr
인터파크.com
yes24.com
알라딘.co.kr
```

---

## 3️⃣ 데이터 저장 위치

```
backend/data/urls/
├── raw/
│   ├── phishing_urls.csv       # 악성 URL
│   ├── malware_urls.csv        # 멀웨어 URL
│   └── benign_urls.csv         # 정상 URL
└── processed/
    ├── train.csv               # 학습 데이터 (80%)
    ├── test.csv                # 테스트 데이터 (20%)
    └── features.csv            # 추출된 특징
```

---

## 4️⃣ 데이터 형식

**CSV 형식 예시:**
```csv
url,label
http://phishing-site.com,1
https://www.google.com,0
http://malware.com/download,1
https://www.naver.com,0
```

- `url`: URL 문자열
- `label`: 0 (정상), 1 (악성)

---

## 5️⃣ 빠른 시작 (샘플 데이터)

테스트용으로 소량의 데이터로 먼저 시작:

```python
# backend/notebooks/00_create_sample_dataset.ipynb

import pandas as pd

# 샘플 악성 URL
malicious_urls = [
    "http://paypal-secure.com/login",
    "http://192.168.1.1/admin",
    "http://bit.ly/free-iphone",
    "http://amazon-verify-account.com",
    # ... 더 추가
]

# 샘플 정상 URL
benign_urls = [
    "https://www.google.com",
    "https://www.naver.com",
    "https://www.github.com",
    "https://www.stackoverflow.com",
    # ... 더 추가
]

# 데이터프레임 생성
df = pd.DataFrame({
    'url': malicious_urls + benign_urls,
    'label': [1] * len(malicious_urls) + [0] * len(benign_urls)
})

# 저장
df.to_csv('../data/urls/raw/sample_dataset.csv', index=False)
```

---

## 6️⃣ 주의사항

⚠️ **악성 URL 처리 시 주의:**
- 절대 브라우저로 직접 접속하지 말 것
- 가상 환경에서만 테스트
- 데이터 수집 시 robots.txt 준수

✅ **데이터 품질:**
- 중복 제거
- URL 정규화
- 라벨 검증

---

## 7️⃣ 다음 단계

데이터 수집 후:
1. `notebooks/01_data_preprocessing.ipynb` - 데이터 전처리
2. `notebooks/02_feature_extraction.ipynb` - 특징 추출
3. `notebooks/03_model_training.ipynb` - 모델 학습

---

**질문이 있으면 팀에 문의하세요!** 🚀
