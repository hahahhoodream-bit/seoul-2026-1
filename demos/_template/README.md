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

## 📋 본인 프로젝트 작성 흐름 (10~14주차)

| 주차 | 할 일 | 산출물 |
|---|---|---|
| 10 | 요구사항 작성 | `요구사항.docx` |
| 11 | 샘플 데이터 + v0 프로토타입 | `app.py` 기능 1 동작 |
| 12 | 기능 확장 + 디버깅 | 기능 2, 3 동작 |
| 13 | UI 정비 + 최종 배포 | Streamlit Cloud URL |
| 14 | 발표 + 상호 피드백 | 시연 + `PROMPT_LOG.md` 10개+ |

---

## 🛡️ 개인정보 / 보안 (필수 체크)

- [ ] 실제 학생 이름·번호가 든 CSV는 **절대 git에 commit 하지 않음** (`.gitignore`가 `*.csv` 차단)
- [ ] API 키·비밀번호는 `.streamlit/secrets.toml` 또는 Streamlit Cloud Secrets에만 저장
- [ ] Public 저장소여도 부끄럽지 않은 코드/데이터만 둘 것
- [ ] `PROMPT_LOG.md`는 매주 업데이트

## 5. Out of Scope

- 로그인 / DB / 외부 AI API / 이메일 / 모바일 반응형
