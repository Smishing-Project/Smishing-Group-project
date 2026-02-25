# Google Colab 모델 학습 가이드

ML 모델을 Google Colab에서 학습하고 프로젝트에 통합하는 방법

---

## 📋 작업 순서

### 1️⃣ Google Colab에서 노트북 열기

1. Google Colab 접속: https://colab.research.google.com/
2. **파일 업로드:**
   - `backend/notebooks/URL_Phishing_Detection_Colab.ipynb` 업로드
3. **실행 환경 설정:**
   - 런타임 > 런타임 유형 변경 > GPU 선택 (선택사항)

---

### 2️⃣ 노트북 실행

**순서대로 모든 셀 실행:**

```
1. 환경 설정 (라이브러리 설치)
2. 샘플 데이터셋 생성
3. 특징 추출 함수 정의
4. 전체 데이터셋 특징 추출
5. 데이터 분할
6. 모델 학습 ⭐
7. 모델 평가
8. 특징 중요도 확인
9. 모델 저장 ⭐
10. 테스트
```

**예상 소요 시간:** 5-10분

---

### 3️⃣ 모델 파일 다운로드

학습 완료 후 **3개 파일 다운로드:**

```
✅ url_classifier.pkl     (모델 파일)
✅ feature_names.pkl      (특징 이름)
✅ metadata.pkl           (메타데이터)
```

**다운로드 방법:**
```python
# Colab 노트북에서 실행
from google.colab import files

files.download('url_classifier.pkl')
files.download('feature_names.pkl')
files.download('metadata.pkl')
```

---

### 4️⃣ 프로젝트에 모델 업로드

**다운로드한 파일을 프로젝트 폴더에 복사:**

```
backend/models/
├── url_classifier.pkl     ← 여기에 복사
├── feature_names.pkl      ← 여기에 복사
└── metadata.pkl           ← 여기에 복사
```

**Windows PowerShell에서:**
```powershell
# 다운로드 폴더에서 복사 (경로는 본인 환경에 맞게)
Copy-Item "C:\Users\사용자\Downloads\url_classifier.pkl" "C:\Users\kanel\Desktop\TeamProject_smithing\backend\models\"
Copy-Item "C:\Users\사용자\Downloads\feature_names.pkl" "C:\Users\kanel\Desktop\TeamProject_smithing\backend\models\"
Copy-Item "C:\Users\사용자\Downloads\metadata.pkl" "C:\Users\kanel\Desktop\TeamProject_smithing\backend\models\"
```

---

### 5️⃣ Docker 컨테이너에서 테스트

```bash
# 컨테이너 재시작
docker-compose restart backend

# 컨테이너 접속
docker-compose exec backend bash

# 모델 테스트
python -c "
from src.url.url_classifier import URLClassifier

classifier = URLClassifier()

if classifier.is_model_loaded():
    result = classifier.predict('http://paypal-secure.com/verify')
    print(f'예측: {result}')
else:
    print('모델이 로드되지 않았습니다.')
"
```

**예상 출력:**
```
✅ URL Classifier 모델 로드 완료
   - 모델: RandomForest
   - Accuracy: 95.00%
   - Recall: 90.00%
   
예측: {'is_malicious': True, 'confidence': 0.95, ...}
```

---

## 📊 데이터셋 개선 (선택사항)

샘플 데이터 대신 실제 데이터를 사용하려면:

### 악성 URL 수집
```python
# Colab 노트북에 추가
!wget http://data.phishtank.com/data/online-valid.csv -O phishing.csv

import pandas as pd
phishing_df = pd.read_csv('phishing.csv')
malicious_urls = phishing_df['url'].tolist()[:5000]
```

### 정상 URL 수집
```python
!wget https://tranco-list.eu/top-1m.csv.zip
!unzip top-1m.csv.zip

tranco_df = pd.read_csv('top-1m.csv', names=['rank', 'domain'])
benign_urls = ['https://' + domain for domain in tranco_df['domain'].tolist()[:5000]]
```

---

## 🎯 목표 성능

- **Accuracy:** 85% 이상
- **Recall:** 90% 이상 (악성 URL 놓치지 않기)

**샘플 데이터로도 목표 달성 가능!**

---

## ⚠️ 주의사항

1. **모델 파일 이름 확인:**
   - 정확히 `url_classifier.pkl`로 저장
   - 오타 없이 복사

2. **경로 확인:**
   - `backend/models/` 폴더에 저장
   - 폴더가 없으면 생성

3. **Git 커밋 시:**
   - 모델 파일은 용량이 크므로 `.gitignore`에 추가 권장
   - 또는 GitHub LFS 사용

---

## 🚀 다음 단계

모델 학습 완료 후:
1. ✅ analyzer.py에 ML 모델 통합
2. ✅ API 테스트
3. ✅ 프론트엔드 연동

---

**질문이 있으면 팀에 문의하세요!** 💬
