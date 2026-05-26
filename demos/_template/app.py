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
import networkx as nx
import plotly.graph_objects as go

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


def validate_csv(df) -> tuple[bool, str]:
    """CSV 검증: 컬럼 확인, 필수값 체크"""
    required_cols = ["name", "best_friend", "distant_friend", "reason_pos", "reason_neg"]
    
    # 컬럼 확인
    if not all(col in df.columns for col in required_cols):
        return False, f"필수 컬럼 누락: {required_cols}"
    
    # 행 수 확인
    if len(df) != 22:
        return False, f"22행이어야 합니다. (현재: {len(df)}행)"
    
    # 필수값 확인
    for col in required_cols:
        if df[col].isna().any() or (df[col] == "").any():
            missing_rows = df[df[col].isna() | (df[col] == "")].index.tolist()
            return False, f"'{col}' 컬럼에 빈 값이 있습니다: {missing_rows}"
    
    return True, "✅ 검증 완료"


def build_network_graph(df):
    """네트워크 그래프 생성 (best_friend: 초록색, distant_friend: 빨간색)"""
    G = nx.DiGraph()
    
    # 모든 학생을 노드로 추가
    for name in df["name"]:
        G.add_node(name)
    
    # best_friend 엣지 (초록색 - 친밀 관계)
    for _, row in df.iterrows():
        if pd.notna(row["best_friend"]) and row["best_friend"] in df["name"].values:
            G.add_edge(row["name"], row["best_friend"], relation="best", color="green")
    
    # distant_friend 엣지 (빨간색 - 소외 관계)
    for _, row in df.iterrows():
        if pd.notna(row["distant_friend"]) and row["distant_friend"] in df["name"].values:
            G.add_edge(row["name"], row["distant_friend"], relation="distant", color="red")
    
    return G


def visualize_network(G):
    """Plotly를 사용한 네트워크 그래프 시각화"""
    # Spring layout으로 노드 위치 계산
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # 엣지 좌표 생성
    edge_x = []
    edge_y = []
    edge_colors = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_colors.append(edge[2].get("color", "gray"))
    
    # 노드 좌표 생성
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_labels = list(G.nodes())
    
    # 엣지 추적 생성
    edge_trace_list = []
    for i in range(0, len(edge_x), 3):
        edge_trace = go.Scatter(
            x=edge_x[i:i+3],
            y=edge_y[i:i+3],
            mode='lines',
            line=dict(width=2, color=edge_colors[i//3]),
            hoverinfo='none',
            showlegend=False
        )
        edge_trace_list.append(edge_trace)
    
    # 노드 추적 생성
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_labels,
        textposition="top center",
        hoverinfo='text',
        hovertext=node_labels,
        marker=dict(
            size=20,
            color='lightblue',
            line_width=2,
            line_color='darkblue'
        ),
        showlegend=False
    )
    
    # Figure 생성
    fig = go.Figure(data=edge_trace_list + [node_trace])
    
    # 범례 추가
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', 
                            line=dict(color='green', width=3),
                            name='친한 친구 (best_friend)'))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines',
                            line=dict(color='red', width=3),
                            name='서먹한 친구 (distant_friend)'))
    
    fig.update_layout(
        title_text="또래관계 네트워크 (화살표 방향: 자신 → 대상)",
        showlegend=True,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        plot_bgcolor='rgba(240, 240, 240, 0.5)'
    )
    
    return fig


# ──────────────────────────────────────────────────────────────
# 사이드바: 파일 업로더
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 데이터 업로드")
    uploaded = st.file_uploader("CSV 파일", type=["csv"])
    st.markdown(
        """
        **필수 컬럼 (5개)**
        - `name`: 학생 이름 (필수)
        - `best_friend`: 가장 친하고 자주 노는 친구 이름 (필수)
        - `distant_friend`: 평소 이야기를 거의 안하거나 서먹한 친구 이름 (필수)
        - `reason_pos`: 친한 친구를 선택한 구체적인 이유 (필수)
        - `reason_neg`: 서먹한 친구를 선택한 구체적인 이유 (필수)
        
        **데이터 조건**
        - 총 22행 (학생 수)
        - 모든 필드는 필수 응답
        - 모든 컬럼: 문자열(String)

        샘플 파일이 필요하면 `sample_data.csv`를 사용하세요.
        """
    )

if uploaded is None:
    st.info("👈 왼쪽 사이드바에서 CSV 파일을 업로드하세요.")
    st.stop()

df = read_csv_any(uploaded)

# CSV 검증
is_valid, validation_msg = validate_csv(df)
if not is_valid:
    st.error(f"❌ 데이터 검증 실패: {validation_msg}")
    st.stop()

st.success(validation_msg)


# ──────────────────────────────────────────────────────────────
# 기능 1. 표 + 응답자 수 메트릭
# ──────────────────────────────────────────────────────────────
st.subheader("① 데이터 확인")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📋 총 응답자", len(df))
with col2:
    st.metric("👥 응답 완료", len(df[df.notna().all(axis=1)]))
with col3:
    st.metric("⚡ 완성도", f"{(len(df[df.notna().all(axis=1)]) / len(df) * 100):.0f}%")

st.dataframe(df, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────
# 기능 2. 관계도 네트워크 시각화
# ──────────────────────────────────────────────────────────────
st.subheader("② 관계도 네트워크 시각화")
st.write("🟢 초록 화살표: 가장 친한 친구 / 🔴 빨간 화살표: 서먹한 친구")

# 네트워크 그래프 생성 및 시각화
G = build_network_graph(df)
fig = visualize_network(G)
st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# 기능 3. (TODO) 관계 분석 (친밀도, 소외 등)
# ──────────────────────────────────────────────────────────────
st.subheader("③ 관계 분석 (작성 예정)")
st.write("Copilot에게: '소외도, 친밀도, 중심성 등 사회네트워크 지표를 계산해서 표로 보여줘'")
