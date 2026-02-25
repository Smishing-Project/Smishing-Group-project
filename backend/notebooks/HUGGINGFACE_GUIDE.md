# Hugging Face 통합 가이드 🤗

ML 모델을 Hugging Face Hub에 업로드하고 프로젝트에 통합하는 완전 가이드

---

## 🎯 Hugging Face를 사용하는 이유

### ✅ 장점

1. **팀 협업** - 모델을 중앙 집중식으로 관리
2. **버전 관리** - Git처럼 모델 버전 추적
3. **쉬운 배포** - 클라우드 저장소에서 자동 다운로드
4. **무료** - Public 모델은 무료로 호스팅
5. **문서화** - Model Card로 자동 문서화

### 📊 vs 기존 방식

| 방식 | 파일 관리 | 팀 공유 | 버전 관리 | 배포 |
|------|-----------|---------|-----------|------|
| **로컬 파일** | 수동 복사 | 어려움 | Git (용량 문제) | 수동 |
| **Hugging Face** | 자동 다운로드 | 쉬움 | 자동 | 자동 ✅ |

---

## 🚀 전체 워크플로우

```
1. Colab에서 모델 학습
2. Hugging Face Hub에 업로드
3. 프로젝트에서 자동 다운로드
4. 프로덕션 배포
```

---

## 📋 단계별 가이드

### STEP 1: Hugging Face 계정 설정

#### 1-1. 회원가입
- https://huggingface.co/join
- GitHub 계정으로 간편 가입 가능

#### 1-2. Access Token 발급
1. https://huggingface.co/settings/tokens
2. "New token" 클릭
3. Name: `colab-training`
4. Role: **Write** 선택 ⭐
5. 토큰 복사 (한 번만 보임!)

---

### STEP 2: Google Colab에서 학습 및 업로드

#### 2-1. Colab Secrets 설정 (추천 ⭐)

```
1. Colab 노트북 열기
2. 왼쪽 🔑 아이콘 클릭 (Secrets)
3. "Add new secret" 클릭
4. Name: HF_TOKEN
5. Value: 복사한 토큰 붙여넣기
6. ✅ "Notebook access" 체크
```

#### 2-2. 노트북 실행

**파일:** `backend/notebooks/URL_Phishing_Detection_Colab_HF.ipynb`

```python
# 1. 환경 설정
!pip install huggingface_hub

# 2. 로그인
from google.colab import userdata
from huggingface_hub import login

HF_TOKEN = userdata.get('HF_TOKEN')
login(token=HF_TOKEN)

# 3. 모델 학습
# ... (학습 코드)

# 4. Hugging Face에 업로드
HF_USERNAME = "your-username"  # 본인 username으로 변경
REPO_NAME = "url-phishing-detector"

# Repository 생성 및 업로드
create_repo(f"{HF_USERNAME}/{REPO_NAME}", exist_ok=True)

upload_file(
    path_or_fileobj="url_classifier.pkl",
    path_in_repo="url_classifier.pkl",
    repo_id=f"{HF_USERNAME}/{REPO_NAME}"
)
```

#### 2-3. 확인

업로드 완료 후:
- 모델 URL: `https://huggingface.co/{username}/url-phishing-detector`
- 웹에서 파일 확인 가능

---

### STEP 3: 프로젝트에 통합

#### 3-1. Docker 컨테이너에서 다운로드

```bash
docker-compose exec backend bash

# Hugging Face에서 모델 다운로드
python -c "
from src.url.hf_utils import download_model_from_hf

REPO_ID = 'your-username/url-phishing-detector'  # 본인 것으로 변경
download_model_from_hf(REPO_ID)
"
```

#### 3-2. 자동 다운로드 (url_classifier.py 수정)

`backend/src/url/url_classifier.py`:

```python
class URLClassifier:
    def __init__(self, model_dir: str = '/app/models', hf_repo_id: str = None):
        self.model_dir = model_dir
        self.hf_repo_id = hf_repo_id
        
        # 로컬에 모델이 없으면 Hugging Face에서 다운로드
        model_path = os.path.join(model_dir, 'url_classifier.pkl')
        
        if not os.path.exists(model_path) and hf_repo_id:
            print(f"📥 로컬에 모델이 없습니다. Hugging Face에서 다운로드 중...")
            from src.url.hf_utils import download_model_from_hf
            download_model_from_hf(hf_repo_id, model_dir)
        
        self._load_model()
```

#### 3-3. 환경변수 설정 (.env)

```env
# Hugging Face
HF_REPO_ID=your-username/url-phishing-detector
```

---

### STEP 4: API에서 사용

`backend/src/analyzer.py`:

```python
import os

class SmishingAnalyzer:
    def __init__(self, api_key: str = None):
        # ...
        
        # Hugging Face repository ID
        hf_repo_id = os.getenv('HF_REPO_ID')
        self.url_classifier = URLClassifier(hf_repo_id=hf_repo_id)
```

---

## 💡 고급 기능

### 1️⃣ 모델 버전 관리

```python
# 특정 버전 다운로드
model_path = hf_hub_download(
    repo_id="username/url-phishing-detector",
    filename="url_classifier.pkl",
    revision="v1.0.0"  # 특정 버전
)
```

### 2️⃣ Private 모델

```python
# Private repository 생성
create_repo("username/url-phishing-detector", private=True)

# 다운로드 시 토큰 필요
model_path = hf_hub_download(
    repo_id="username/url-phishing-detector",
    filename="url_classifier.pkl",
    token=HF_TOKEN  # Private 모델은 토큰 필요
)
```

### 3️⃣ 데이터셋도 업로드

```python
from datasets import Dataset

# 학습 데이터셋을 Hugging Face Datasets로 업로드
dataset = Dataset.from_pandas(df)
dataset.push_to_hub("username/phishing-urls-dataset")
```

---

## 🔧 트러블슈팅

### ❌ "Repository not found"
- Repository 이름 확인
- Public/Private 설정 확인
- 토큰 권한 확인 (Write 필요)

### ❌ "Authentication failed"
- 토큰 재발급
- Colab Secrets 재설정
- `login(token=...)` 다시 실행

### ❌ "File too large"
- 모델 파일이 5GB 이상이면 Git LFS 필요
- Random Forest는 보통 1-10MB로 문제 없음

---

## 📊 비교: 3가지 방법

| 방법 | 장점 | 단점 | 추천 |
|------|------|------|------|
| **1. 로컬 파일** | 간단 | 팀 공유 어려움 | 개인 프로젝트 |
| **2. Hugging Face** | 팀 협업, 버전 관리 | 초기 설정 필요 | 팀 프로젝트 ⭐ |
| **3. AWS S3** | 프로덕션급 | 비용, 복잡함 | 대규모 서비스 |

---

## 🎯 추천 워크플로우

**개발 단계:**
```
1. Colab에서 학습
2. Hugging Face에 업로드 (dev 버전)
3. 로컬에서 테스트
4. 성능 만족 시 → main 버전으로 태그
```

**프로덕션 배포:**
```
1. Hugging Face에서 stable 버전 다운로드
2. Docker 이미지에 포함
3. 서버 배포
```

---

## ✅ 체크리스트

학습 전:
- [ ] Hugging Face 계정 생성
- [ ] Access Token 발급 (Write 권한)
- [ ] Colab Secrets 설정

학습 후:
- [ ] 모델 파일 3개 업로드 확인
- [ ] README.md (Model Card) 작성
- [ ] 프로젝트에서 다운로드 테스트

프로덕션:
- [ ] .env에 HF_REPO_ID 설정
- [ ] 자동 다운로드 로직 추가
- [ ] API 테스트

---

## 📚 참고 자료

- Hugging Face Hub 문서: https://huggingface.co/docs/hub
- Python 라이브러리: https://huggingface.co/docs/huggingface_hub
- Model Card 가이드: https://huggingface.co/docs/hub/model-cards

---

**질문이 있으면 팀에 문의하세요!** 💬
