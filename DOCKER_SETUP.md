# Docker Compose 환경 설정 가이드

## 🚀 빠른 시작

### 1. 코드 받기

```bash
git clone <repository-url>
cd smi.proct
```

### 2. 환경변수 설정 (선택)

필요한 경우 `.env` 파일 생성 또는 수정

```bash
cp .env.example .env
```

### 3. Docker 실행

```bash
# 빌드 및 실행
docker compose up --build

# 백그라운드 실행
docker compose up -d --build
```

### 4. 접속

- **프론트엔드**: http://localhost:5000
- **백엔드 API**: http://localhost:8001
- **API 문서 (Swagger)**: http://localhost:8001/docs

---

## �️ DBeaver PostgreSQL 연결

### 연결 정보

| 항목     | 값                             |
| -------- | ------------------------------ |
| Host     | `localhost` (WSL2는 아래 참고) |
| Port     | `5432`                         |
| Database | `smishing_db`                  |
| Username | `postgres`                     |
| Password | `postgres`                     |

### 환경별 Host 설정

| 환경                                | Host                    |
| ----------------------------------- | ----------------------- |
| Windows + Docker Desktop (WSL 없이) | `localhost`             |
| Mac + Docker Desktop                | `localhost`             |
| Linux 네이티브                      | `localhost`             |
| **Windows + WSL2**                  | WSL IP 사용 (아래 확인) |

### WSL2 사용자 IP 확인 방법

```bash
# WSL2 터미널에서 실행
hostname -I
# 출력 예: 172.24.97.98 → 이 IP를 Host에 입력
```

---

## �🛑 Docker 중지

```bash
# 서비스 중지
docker compose down

# 볼륨까지 삭제 (DB 데이터 초기화)
docker compose down -v
```

---

## 🔄 재빌드

패키지 추가 등 Dockerfile 변경 시:

```bash
docker compose up --build
```

---

## 📦 패키지 추가 방법

### Python 패키지 추가 (백엔드)

```bash
# backend/requirements.txt에 추가
sentence-transformers>=2.2.0

# 재빌드
docker compose up --build
```

### Node 패키지 추가 (프론트엔드)

```bash
# frontend/package.json에 추가 후
docker compose up --build
```

---

## 🔧 문제 해결

### 포트 충돌

```bash
# 사용 중인 포트 확인
lsof -i :5000
lsof -i :8001
lsof -i :5432
```

### 캐시 없이 재빌드

```bash
docker compose build --no-cache
docker compose up
```

### 로그 확인

```bash
# 전체 로그
docker compose logs

# 특정 서비스 로그
docker compose logs backend
docker compose logs frontend
docker compose logs db
```

### DB 연결 안 될 때

```bash
# 볼륨 삭제 후 재시작
docker compose down -v
docker compose up --build
```
