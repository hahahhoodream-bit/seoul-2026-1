"""
우리반 마음 지도 : 또래관계 네트워크 시각화 도구 — Streamlit
"""

import io
import re
from collections import Counter

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
    
    # [★오류 해결 완료★] 원래 코드에 박혀있던 한글 '또는'을 파이썬 문법 'or'로 확실하게 고쳤습니다.
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
    """Plotly를 사용한 네트워크 그래프 시각화"""
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    in_degree_count = {}
    for name in df["name"]:
        total_selections = G.in_degree(name)
        in_degree_count[name] = total_selections
    
    max_degree = max(in_degree_count.values()) if in_degree_count.values() else 1
    min_degree = min(in_degree_count.values()) if in_degree_count.values() else 0
    
    node_sizes = {}
    for name in df["name"]:
        if max_degree == min_degree:
            normalized = 0.5
        else:
            normalized = (in_degree_count[name] - min_degree) / (max_degree - min_degree)
        node_sizes[name] = 15 + normalized * 35
    
    edge_x = []
    edge_y = []
    edge_colors = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_colors.append(edge[2].get("color", "gray"))
    
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_labels = list(G.nodes())
    
    sizes = [node_sizes[node] for node in node_labels]
    
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
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_labels,
        textposition="top center",
        hoverinfo='text',
        hovertext=[f"{label}<br>선택 받음: {in_degree_count[label]}명" for label in node_labels],
        marker=dict(
            size=sizes,
            color='lightblue',
            line_width=2,
            line_color='darkblue'
        ),
        showlegend=False
    )
    
    fig = go.Figure(data=edge_trace_list + [node_trace])
    
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
        best_friends_received = sum(1 for _, target, data in G.in_edges(name, data=True) 
                                   if data.get("relation") == "best")
        
        distant_received = sum(1 for _, target, data in G.in_edges(name, data=True) 
                              if data.get("relation") == "distant")
        
        centrality = nx.degree_centrality(G).get(name, 0)
        
        metrics.append({
            "이름": name,
            "👍 받은 친밀표시": best_friends_received,
            "👎 받은 소외표시": distant_received,
            "🔗 중심성": round(centrality, 3),
            "📊 관계성향": "외향적" if best_friends_received > distant_received else "내향적"
        })
    
    return pd.DataFrame(metrics).sort_values("👍 받은 친밀표시", ascending=False)


def extract_keywords(reason_list, top_n=3):
    """주관식 서술형 응답에서 핵심 키워드를 빈도 기반으로 추출하는 함수"""
    stop_words = {
        '때문', '때문에', '대해서', '대해', '하는', '해서', '하고', '했다', 
        '이다', '아니라', '많이', '조금', '매우', '그냥', '항상', '자주', 
        '같다', '같은', '있어서', '있음', '없음', '친구', '친구가', '애가'
    }
    
    words = []
    for reason in reason_list:
        if pd.isna(reason):
            continue
        cleaned_reason = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', str(reason))
        for word in cleaned_reason.split():
            if len(word) >= 2 및 word not in stop_words:
                words.append(word)
                
    most_common = Counter(words).most_common(top_n)
    if not most_common:
        return "특별한 사유 없음"
        
    return ", ".join([f"{word}({count})" for word, count in most_common])


# ──────────────────────────────────────────────────────────────
# 사이드바: 파일 업로더
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 데이터 업로드")
    uploaded = st.file_uploader("CSV 파일", type=["csv"])
    st.markdown(
        """
        **필수 컬럼 (5개)**
        - `name`: 학생 이름
        - `best_friend`: 가장 친한 친구
        - `distant_friend`: 서먹한 친구
        - `reason_pos`: 친한 이유
        - `reason_neg`: 서먹한 이유
        """
    )

if uploaded is None:
    st.info("👈 왼쪽 사이드바에서 CSV 파일을 업로드하세요.")
    st.stop()

df = read_csv_any(uploaded)

is_valid, validation_msg = validate_csv(df)
if not is_valid:
    st.error(f"❌ 데이터 검증 실패: {validation_msg}")
    st.stop()

st.성공(validation_msg)


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

G = build_network_graph(df)
fig = visualize_network(G, df)
st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# 기능 3. 관계 분석 지표 & 주관식 키워드 요약 연동
# ──────────────────────────────────────────────────────────────
st.subheader("③ 관계 분석 지표")

metrics_df = calculate_network_metrics(df, G)
st.dataframe(metrics_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### 🔍 주요 학생 관계 및 선택 사유 분석 (상위 5명)")
st.caption("해당 학생을 선택한 친구들의 답변에서 가장 많이 언급된 핵심 키워드입니다.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏆 우리반 친밀도 상위 5명")
    top_5_intimate = metrics_df.nlargest(5, "👍 받은 친밀표시").copy()
    
    pos_reasons = []
    for idx, row in top_5_intimate.iterrows():
        student_name = row["이름"]
        student_reasons = df[df["best_friend"] == student_name]["reason_pos"].tolist()
        pos_reasons.append(extract_keywords(student_reasons, top_n=3))
        
    top_5_intimate["🎯 주된 친밀 사유 (핵심어)"] = pos_reasons
    st.dataframe(
        top_5_intimate[["이름", "👍 받은 친밀표시", "🎯 주된 친밀 사유 (핵심어)"]], 
        use_container_width=True, 
        hide_index=True
    )

with col2:
    st.markdown("### ⚠️ 우리반 소외도 상위 5명")
    top_5_isolated = metrics_df.nlargest(5, "👎 받은 소외표시").copy()
    
    neg_reasons = []
    for idx, row in top_5_isolated.iterrows():
        student_name = row["이름"]
        student_reasons = df[df["distant_friend"] == student_name]["reason_neg"].tolist()
        neg_reasons.append(extract_keywords(student_reasons, top_n=3))
        
    top_5_isolated["🎯 주된 서먹한 사유 (핵심어)"] = neg_reasons
    st.dataframe(
        top_5_isolated[["이름", "👎 받은 소외표시", "🎯 주된 서먹한 사유 (핵심어)"]], 
        use_container_width=True, 
        hide_index=True
    )
