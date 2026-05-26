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


def visualize_network(G, df):
    """Plotly를 사용한 네트워크 그래프 시각화
    
    노드 크기: 받은 선택의 총 개수 (친밀도 + 소외도)에 따라 동적으로 조절
    선: 친밀 관계는 초록색, 소외 관계는 빨간색
    """
    # Spring layout으로 노드 위치 계산
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # 각 학생이 받은 선택 횟수 계산 (노드 크기 기준)
    in_degree_count = {}
    for name in df["name"]:
        total_selections = G.in_degree(name)  # 모든 들어오는 엣지 수
        in_degree_count[name] = total_selections
    
    # 노드 크기 정규화 (최소 15, 최대 50)
    max_degree = max(in_degree_count.values()) if in_degree_count.values() else 1
    min_degree = min(in_degree_count.values()) if in_degree_count.values() else 0
    
    node_sizes = {}
    for name in df["name"]:
        if max_degree == min_degree:
            normalized = 0.5
        else:
            normalized = (in_degree_count[name] - min_degree) / (max_degree - min_degree)
        node_sizes[name] = 15 + normalized * 35  # 15~50 범위
    
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
    
    # 노드 크기 리스트
    sizes = [node_sizes[node] for node in node_labels]
    
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
    
    # 노드 추적 생성 (크기 동적 조절)
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_labels,
        textposition="top center",
        hoverinfo='text',
        hovertext=[f"{label}<br>선택 받음: {in_degree_count[label]}명" for label in node_labels],
        marker=dict(
            size=sizes,  # 동적 크기
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
        title_text="또래관계 네트워크 (화살표 방향: 자신 → 대상) | 노드 크기: 받은 선택의 많고 적음",
        showlegend=True,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        plot_bgcolor='rgba(240, 240, 240, 0.5)'
    )
    
    return fig


def calculate_network_metrics(df, G):
    """사회네트워크 지표 계산"""
    metrics = []
    
    for name in df["name"]:
        # 1. 친밀도 (In-degree of best_friend edges)
        best_friends_received = sum(1 for _, target, data in G.in_edges(name, data=True) 
                                   if data.get("relation") == "best")
        
        # 2. 소외도 (In-degree of distant_friend edges)
        distant_received = sum(1 for _, target, data in G.in_edges(name, data=True) 
                              if data.get("relation") == "distant")
        
        # 3. 중심성 (Degree Centrality)
        centrality = nx.degree_centrality(G).get(name, 0)
        
        # 4. 친한 친구 수 (Outgoing best_friend edges)
        best_friends_count = sum(1 for _, _, data in G.out_edges(name, data=True) 
                                if data.get("relation") == "best")
        
        # 5. 서먹한 친구 수 (Outgoing distant_friend edges)
        distant_count = sum(1 for _, _, data in G.out_edges(name, data=True) 
                           if data.get("relation") == "distant")
        
        metrics.append({
            "이름": name,
            "👍 받은 친밀표시": best_friends_received,
            "👎 받은 소외표시": distant_received,
            "🔗 중심성": round(centrality, 3),
            "💚 선택한 친한친구": best_friends_count,
            "💔 선택한 소외친구": distant_count,
            "📊 관계성향": "외향적" if best_friends_received > distant_received else "내향적"
        })
    
    return pd.DataFrame(metrics).sort_values("👍 받은 친밀표시", ascending=False)


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
fig = visualize_network(G, df)
st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# 기능 3. 관계 분석 (친밀도, 소외도, 중심성)
# ──────────────────────────────────────────────────────────────
st.subheader("③ 관계 분석 지표")
st.write("각 학생의 사회네트워크 지표 (친밀도, 소외도, 중심성 등)")

# 메트릭 계산
metrics_df = calculate_network_metrics(df, G)

# 지표 설명
with st.expander("📖 지표 설명"):
    st.markdown("""
    - **👍 받은 친밀표시**: 다른 학생들이 이 학생을 '친한 친구'로 선택한 횟수
    - **👎 받은 소외표시**: 다른 학생들이 이 학생을 '서먹한 친구'로 선택한 횟수
    - **🔗 중심성**: 0~1 사이의 값으로, 1에 가까울수록 네트워크의 중심에 있음 (사교성 지표)
    - **💚 선택한 친한친구**: 이 학생이 '친한 친구'로 선택한 수
    - **💔 선택한 소외친구**: 이 학생이 '서먹한 친구'로 선택한 수
    - **📊 관계성향**: 받은 친밀표시 > 소외표시면 '외향적', 반대면 '내향적'
    """)

st.dataframe(metrics_df, use_container_width=True, hide_index=True)

# 추가 분석: 상위/하위 분석
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏆 친밀도 상위 5명")
    top_intimate = metrics_df.nlargest(5, "👍 받은 친밀표시")[["이름", "👍 받은 친밀표시"]]
    st.dataframe(top_intimate, use_container_width=True, hide_index=True)

with col2:
    st.markdown("### ⚠️ 소외도 상위 5명")
    top_isolated = metrics_df.nlargest(5, "👎 받은 소외표시")[["이름", "👎 받은 소외표시"]]
    st.dataframe(top_isolated, use_container_width=True, hide_index=True)
