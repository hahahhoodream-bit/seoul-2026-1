# {{프로젝트 제목}}

{{한 줄 요약}}

> 2026-1학기 클라우드 프로그래밍 · {{학번/이름}}

---

## 1. 무엇을 할 수 있나요

1. (기능 1) ...
2. (기능 2) ...
3. (기능 3) ...

## 2. 입력 CSV 형식

| 컬럼명 | 타입 | 예시 | 필수 |
|--------|------|------|------|
| `___` | ___ | ___ | ✅ |

샘플: [`sample_data.csv`](sample_data.csv)

## 3. 로컬 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 4. Streamlit Cloud 배포

1. GitHub public 저장소에 푸시
2. <https://share.streamlit.io> → New app → 저장소·`app.py` 선택
3. Deploy

🚨 실제 학생 이름이 든 CSV는 **절대 저장소에 올리지 마세요.** `.gitignore`가 차단합니다.

## 5. Out of Scope

- 로그인 / DB / 외부 AI API / 이메일 / 모바일 반응형
