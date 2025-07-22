# 🇰🇷 한글 번역 가이드

기존 수집된 영문 기사들을 한글로 번역하는 방법입니다.

## 🚀 빠른 시작

### 1단계: Gemini API 키 설정
```bash
# Google AI Studio에서 API 키 생성: https://makersuite.google.com/app/apikey
export GEMINI_API_KEY="your-api-key-here"
```

### 2단계: 기존 데이터 번역
```bash
cd context-engineering-news
source venv/bin/activate  # 가상환경 활성화 (있는 경우)
python translate_existing.py
```

### 3단계: 결과 확인
- `docs/index.html`: 번역된 뉴스레터 확인
- GitHub에 커밋하여 사이트 업데이트

번역 완료 후 https://hundong2.github.io/copilot_answer_set/ 에서 한글 버전 확인!
