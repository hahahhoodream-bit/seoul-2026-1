"""
우리반 마음 지도 : 또래관계 네트워크 시각화 도구 — Streamlit 최종본
"""

import io
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
# 공용 유틸 및 검증
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
    required_cols = ["name", "best_friend", "distant_friend", "reason_pos", "reason_neg"]

    if not all(col in df.columns for col in required_cols):
        missing = [c for c in required_cols if c not in df.columns]
        return False, f"엑셀 파일에 필수 열(컬럼)이 누락되었습니다. 빠진 열: {missing} | 파일 양식을 다시 확인해 주세요."

    if len(df) != 22:
        return False, f"학급 학생 수 설정(22명)과 업로드된 데이터의 행 수가 맞지 않습니다. (현재 업로드된 학생 수: {len(df)}명)"

    col_korean = {
        "name": "학생 이름", "best_friend": "친한 친구", "distant_friend": "서먹한 친구",
        "reason_pos": "친함 이유", "reason_neg": "서먹함 이유"
    }
    for col in required_cols:
        if df[col].isna().any() or (df[col] == "").any():
            missing_rows = [idx + 2 for idx in df[df[col].isna() | (df[col] == "")].index]
            return False, f"엑셀 파일의 [{col_korean.get(col, col)}] 열에 빈 칸이 발견되었습니다. (해당 엑셀 줄번호: {missing_rows}번째 줄) 공백을 채운 뒤 다시 업로드해 주세요."

    return True, "✅ 데이터 검증 완료! 우리반 마음 지도를 성공적으로 분석했습니다."


def build_network_graph(df):
    G = nx.DiGraph()
    for name in df["name"]:
        G.add_node(name)
    for _, row in df.iterrows():
        if pd.notna(row["best_friend"]) and row["best_friend"] in df["name"].values:
            G.add_edge(row["name"], row["best_friend"], relation="best", color="green")
    for _, row in df.iterrows():
        if pd.notna(row["distant_friend"]) and row["distant_friend"] in df["name"].values:
            G.add_edge(row["name"], row["distant_friend"], relation="distant", color="red")
    return G


def visualize_network(G, df):
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    node_details = {}
    for name in df["name"]:
        best_received = sum(1 for _, _, data in G.in_edges(name, data=True) if data.get("relation") == "best")
        distant_received = sum(1 for _, _, data in G.in_edges(name, data=True) if data.get("relation") == "distant")
        total_received = best_received + distant_received
        node_details[name] = {"total": total_received, "best": best_received, "distant": distant_received}

    max_degree = max(d["total"] for d in node_details.values()) if node_details else 1
    min_degree = min(d["total"] for d in node_details.values()) if node_details else 0

    node_sizes = {}
    for name in df["name"]:
        if max_degree == min_degree:
            normalized = 0.5
        else:
            normalized = (node_details[name]["total"] - min_degree) / (max_degree - min_degree)
        node_sizes[name] = 15 + normalized * 35

    edge_x, edge_y, edge_colors = [], [], []
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
            x=edge_x[i:i+3], y=edge_y[i:i+3], mode='lines',
            line=dict(width=2, color=edge_colors[i//3]),
            hoverinfo='none', showlegend=False
        )
        edge_trace_list.append(edge_trace)

    hover_texts = []
    for label in node_labels:
        d = node_details[label]
        hover_texts.append(
            f"<b>{label}</b><br>선택 받음: 총 {d['total']}명<br>  - 😊 친한 친구: {d['best']}명<br>  - 🔺 서먹한 친구: {d['distant']}명"
        )

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        text=node_labels, textposition="top center",
        hoverinfo='text', hovertext=hover_texts,
        marker=dict(size=sizes, color='lightblue', line_width=2, line_color='darkblue'),
        showlegend=False
    )

    fig = go.Figure(data=edge_trace_list + [node_trace])
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='green', width=3), name='친한 친구 (best_friend)'))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='red', width=3), name='서먹한 친구 (distant_friend)'))

    fig.update_layout(
        title_text="또래관계 네트워크 (화살표 방향: 자신 → 대상) | 노드 크기: 받은 선택의 총량",
        showlegend=True, hovermode='closest', margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600, plot_bgcolor='rgba(240, 240, 240, 0.5)'
    )
    return fig


def calculate_network_metrics(df, G):
    """기능 3: 중심성·관계성향만 표시 (친밀/소외 수치는 그래프 호버로 확인 가능하므로 제외)"""
    metrics = []
    for name in df["name"]:
        best_received = sum(1 for _, _, data in G.in_edges(name, data=True) if data.get("relation") == "best")
        distant_received = sum(1 for _, _, data in G.in_edges(name, data=True) if data.get("relation") == "distant")
        centrality = nx.degree_centrality(G).get(name, 0)
        metrics.append({
            "이름": name,
            "🔗 중심성": round(centrality, 3),
            "📊 관계성향": "외향적" if best_received > distant_received else "내향적"
        })
    return pd.DataFrame(metrics).sort_values("🔗 중심성", ascending=False)


def summarize_reasons_by_group(reason_list, is_positive=True):
    if not reason_list:
        return "특별한 사유 없음"
    categories = Counter()
    for reason in reason_list:
        if pd.isna(reason) or str(reason).strip() == "":
            continue
        text = str(reason).strip()
        if is_positive:
            if any(w in text for w in ["성격", "착하다", "활발", "밝다", "좋다", "친하다"]):
                categories["성격이 좋고 활발함"] += 1
            elif any(w in text for w in ["친절", "도와", "배려", "잘해", "착해"]):
                categories["친절하고 배려심이 많음"] += 1
            elif any(w in text for w in ["재미", "웃기", "재밌", "개그"]):
                categories["유머러스하고 같이 있으면 즐거움"] += 1
            elif any(w in text for w in ["취미", "게임", "통한다", "관심사", "이야기", "코드"]):
                categories["취미나 대화가 잘 통함"] += 1
            else:
                categories["기타 친근감 표시"] += 1
        else:
            if any(w in text for w in ["말", "대화", "이야기", "서먹", "어색", "안친"]):
                categories["평소 대화나 소통이 부족함"] += 1
            elif any(w in text for w in ["싸움", "장난", "괴롭", "시비", "때려"]):
                categories["과도한 장난이나 갈등이 있었음"] += 1
            elif any(w in text for w in ["무시", "이기", "욕", "성격", "나빠"]):
                categories["성격적 차이 및 배려 부족"] += 1
            elif any(w in text for w in ["반", "조", "기회", "자리"]):
                categories["같은 모둠이나 놀 기회가 없었음"] += 1
            else:
                categories["특별한 갈등 없는 단순 서먹함"] += 1

    top_categories = categories.most_common(2)
    if not top_categories:
        return "특별한 사유 없음"
    return " / ".join([f"{cat}({count}명)" for cat, count in top_categories])


# ──────────────────────────────────────────────────────────────
# 사이드바
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 데이터 업로드")
    uploaded = st.file_uploader("CSV 파일 선택", type=["csv"])
    st.markdown("---")
    st.caption("필수 컬럼: name, best_friend, distant_friend, reason_pos, reason_neg")

if uploaded is None:
    st.info("👈 왼쪽 사이드바에서 교우관계 CSV 파일을 업로드하세요.")
    st.stop()

df = read_csv_any(uploaded)
is_valid, validation_msg = validate_csv(df)
if not is_valid:
    st.error(validation_msg)
    st.stop()

st.success(validation_msg)


# ──────────────────────────────────────────────────────────────
# [기능 ①] 데이터 확인
# ──────────────────────────────────────────────────────────────
st.subheader("① 데이터 확인")
c1, c2, c3 = st.columns(3)
with c1: st.metric("📋 총 응답자", len(df))
with c2: st.metric("👥 응답 완료", len(df[df.notna().all(axis=1)]))
with c3: st.metric("⚡ 완성도", f"{(len(df[df.notna().all(axis=1)]) / len(df) * 100):.0f}%")
st.dataframe(df, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────
# [기능 ②] 관계도 네트워크 시각화
# ──────────────────────────────────────────────────────────────
st.subheader("② 관계도 네트워크 시각화")
G = build_network_graph(df)
fig = visualize_network(G, df)
st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# [기능 ③] 관계 분석 지표 + 상위 5명 사유 요약
# ──────────────────────────────────────────────────────────────
st.subheader("③ 관계 분석 지표 및 사유 요약")
metrics_df = calculate_network_metrics(df, G)

with st.expander("📖 지표 설명 보기"):
    st.markdown(
        "- **🔗 중심성**: 학급 안에서 얼마나 많은 관계(친밀+서먹 모두)에 연결되어 있는지를 나타내는 수치\n"
        "- **📊 관계성향**: 친한 친구로 선택받은 횟수가 더 많으면 외향적, 서먹한 친구로 더 많이 선택받으면 내향적으로 분류\n"
        "- 친밀 표시·소외 표시 횟수는 ② 그래프에서 이름에 마우스를 올리면 확인할 수 있습니다"
    )

st.dataframe(metrics_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### 🔍 친밀도·소외도 상위 5명 및 선택 사유 요약")

col_pos, col_neg = st.columns(2)

with col_pos:
    st.markdown("#### 🏆 친밀도 상위 5명")
    top_5_intimate = []
    for _, row in metrics_df.nlargest(5, "🔗 중심성").iterrows():
        name = row["이름"]
        best_received = sum(1 for _, _, data in G.in_edges(name, data=True) if data.get("relation") == "best")
        reason_summary = summarize_reasons_by_group(
            df[df["best_friend"] == name]["reason_pos"].tolist(), is_positive=True
        )
        top_5_intimate.append({
            "이름": name,
            "친한 친구로 선택받은 횟수": best_received,
            "주된 친밀 사유 요약": reason_summary
        })
    st.dataframe(pd.DataFrame(top_5_intimate), use_container_width=True, hide_index=True)

with col_neg:
    st.markdown("#### ⚠️ 소외도 상위 5명")
    top_5_isolated = []
    for _, row in metrics_df.nlargest(5, "🔗 중심성").iterrows():
        name = row["이름"]
        distant_received = sum(1 for _, _, data in G.in_edges(name, data=True) if data.get("relation") == "distant")
        reason_summary = summarize_reasons_by_group(
            df[df["distant_friend"] == name]["reason_neg"].tolist(), is_positive=False
        )
        top_5_isolated.append({
            "이름": name,
            "서먹한 친구로 선택받은 횟수": distant_received,
            "주된 서먹 사유 요약": reason_summary
        })
    st.dataframe(pd.DataFrame(top_5_isolated), use_container_width=True, hide_index=True)
