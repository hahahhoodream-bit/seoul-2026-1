"""
우리반 마음 지도 : 또래관계 네트워크 시각화 도구 — Streamlit 시작 골격

⚠️ 이 파일은 빈 골격입니다. Copilot에게 다음 순서로 프롬프트하세요.
   1) 사이드바 CSV 업로더 만들기
   2) 표 + 응답자 수 메트릭 카드 추가
   3) 본인 명세의 기능 2, 3 추가

학생들이 손대지 않아도 되는 영역(인코딩 처리, 페이지 설정)은 미리 작성되어 있습니다.
"""

import io

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="우리반 마음 지도",
    page_icon="📊",
    layout="wide",
)

st.title("📊 우리반 마음 지도")
st.caption("또래관계 네트워크 시각화 도구")


# ──────────────────────────────────────────────────────────────
# 공용 유틸 (수정 불필요) — 엑셀 CP949 / 메모장 UTF-8 자동 처리
# ──────────────────────────────────────────────────────────────
def read_csv_any(uploaded_file) -> pd.DataFrame:
    raw = uploaded_file.read()
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(io.BytesIO(raw), encoding="utf-8", errors="replace")


# ──────────────────────────────────────────────────────────────
# 사이드바: 파일 업로더
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 데이터 업로드")
    uploaded = st.file_uploader("CSV 파일", type=["csv"])
    st.markdown(
        """
        **필수 컬럼** (본인 명세에 맞게 수정)
        - `컬럼1`
        - `컬럼2`

        샘플 파일이 필요하면 `sample_data.csv`를 사용하세요.
        """
    )

if uploaded is None:
    st.info("👈 왼쪽 사이드바에서 CSV 파일을 업로드하세요.")
    st.stop()

df = read_csv_any(uploaded)


# ──────────────────────────────────────────────────────────────
# 기능 1. (TODO) 표 + 상단 요약
# ──────────────────────────────────────────────────────────────
st.subheader("① 데이터 확인")
st.dataframe(df, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────
# 기능 2. (TODO) 본인 명세의 기능 2를 여기에 작성
# ──────────────────────────────────────────────────────────────
st.subheader("② (작성 예정)")
st.write("Copilot에게: '기능 2를 추가해줘. 사용자 동작은 ___, 화면 결과는 ___'")


# ──────────────────────────────────────────────────────────────
# 기능 3. (TODO) 본인 명세의 기능 3을 여기에 작성
# ──────────────────────────────────────────────────────────────
st.subheader("③ (작성 예정)")
st.write("Copilot에게: '기능 3을 추가해줘. ___'")
