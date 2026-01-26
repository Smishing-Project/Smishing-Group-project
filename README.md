# 🛡️ 스미싱 예방 코치

고령층 사기 예방 코치 + QR/URL(큐싱) 검사 서비스

> 프로젝트 설명 작성 예정

---

## 📁 프로젝트 구조

```
smi.proct/
├── backend/          # FastAPI 백엔드
├── frontend/         # React + Vite 프론트엔드
├── ai_ocr/           # OCR/QR + URL 위험 판단 모듈
├── ai_bert/          # BERT 스미싱 유형 분류 모듈
├── ai_group_risk/    # 집단 위험 판단 모듈
├── ai_rag/           # RAG 대응 가이드 모듈
└── docs/             # 프로젝트 문서
```

## 🚀 시작하기

Docker 환경 설정은 [DOCKER_SETUP.md](./DOCKER_SETUP.md) 참고

## 👥 팀 역할

| 역할                   | 담당 모듈        |
| ---------------------- | ---------------- |
| OCR/QR + URL 위험 판단 | `ai_ocr/`        |
| BERT 스미싱 유형 분류  | `ai_bert/`       |
| 집단 위험 판단         | `ai_group_risk/` |
| RAG + NER 대응 가이드  | `ai_rag/`        |
