# 📊 우리반 마음 지도 : 또래관계 네트워크 시각화 도구

초등학교 담임교사를 위한 학생들의 교우관계에 대한 데이터를 입력하면 관계도를 도식화하여 전반적인 관계 및 소외, 친밀도 등을 분석해주는 웹 애플리케이션

> 2026-1학기 클라우드 프로그래밍 · {{M20261509/원지은}}

---

## 1. 무엇을 할 수 있나요

1. **(기능 1) 데이터 업로드 및 현황 확인**: 다중 인코딩 자동 감지 기능으로 엑셀 출력 CSV 파일을 깨짐 없이 업로드하고, 학급 전체의 응답 완성도 메트릭과 데이터 표를 확인합니다.[cite: 4]
2. **(기능 2) 관계도 네트워크 시각화**: `NetworkX`와 `Plotly`를 통해 학생 간 친밀(초록)/서먹(빨간) 관계를 화살표 그래프로 시각화하며, 노드 크기는 받은 선택량에 비례하고 호버 시 세부 인원수가 쪼개져 나타납니다.
3. **(기능 3) 관계 분석 지표 및 사유 그룹 요약**: 중심성 지표 기반의 상위/하위 5명 명단을 추출하고, 파편화된 주관식 지목 사유들을 의미론적으로 결합하여 교사가 알아보기 쉬운 '문장 형태의 요약 결과'를 제공합니다.
   
## 2. 입력 CSV 형식

| 컬럼명 | 타입 | 예시 | 필수 |
|--------|------|------|------|
| `name` | String | 홍길동 | ✅ |
| `best_friend` | String | 이영희 | ✅ |
| `distant_friend` | String | 김철수 | ✅ |
| `reason_pos` | String | 성격이 활발하고 착해요 | ✅ |
| `reason_neg` | String | 평소에 장난이 너무 심해요 | ✅ |

샘플: [`sample_data.csv`](sample_data.csv)[cite: 4]

## 3. 로컬 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```[cite: 4]

## 4. Streamlit Cloud 배포

1. GitHub public 저장소에 푸시
2. <https://share.streamlit.io> → New app → 저장소·`app.py` 선택
3. Deploy[cite: 4]

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
