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
            G.add_edge(row["name"], row["best_friend"], relation="best", color="#2E8B57")
    for _, row in df.iterrows():
        if pd.notna(row["distant_friend"]) and row["distant_friend"] in df["name"].values:
            G.add_edge(row["name"], row["distant_friend"], relation="distant", color="#CD5C5C")
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
            line=dict(width=1.5, color=edge_colors[i//3]),
            opacity=0.6,
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
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='#2E8B57', width=3), name='친한 친구 (best_friend)'))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='#CD5C5C', width=3), name='서먹한 친구 (distant_friend)'))

    fig.update_layout(
        title_text="또래관계 네트워크 (화살표 방향: 자신 → 대상) | 노드 크기: 받은 선택의 총량",
        showlegend=True, hovermode='closest', margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600, plot_bgcolor='rgba(240, 240, 240, 0.5)'
    )
    return fig


def summarize_reasons_by_group(reason_list, is_positive=True):
    if not reason_list:
        return "특별한 사유 없음"

    # 카테고리별 키워드 — 넓게 설정하여 웬만한 답변 흡수
    POS_CATEGORIES = [
        ("밝고 활발한 성격",        ["성격", "착하", "활발", "밝다", "밝아", "좋다", "좋아", "친하", "긍정", "웃기", "재미", "재밌", "개그", "유머", "웃음", "즐거", "신나", "유쾌"]),
        ("친절하고 배려심이 많음",   ["친절", "도와", "배려", "잘해", "챙겨", "다정", "상냥", "따뜻", "살펴"]),
        ("취미와 대화가 잘 통함",    ["취미", "게임", "통한다", "통해", "관심사", "이야기", "코드", "좋아하는", "같이 좋아", "공통", "얘기"]),
        ("자주 같이 어울림",         ["같이", "함께", "놀아", "놀았", "어울", "항상", "매일", "자주", "붙어"]),
        ("오래된 인연",              ["오래", "어릴", "초등", "같은 반", "예전", "친구였", "알고 지", "오랫동안"]),
    ]

    NEG_CATEGORIES = [
        ("대화나 교류가 적음",        ["말", "대화", "이야기", "서먹", "어색", "안친", "모름", "모르", "얘기", "말수", "말이 없", "접점"]),
        ("과도한 장난이나 갈등",      ["싸움", "장난", "괴롭", "시비", "때려", "다퉜", "싫어", "미워", "짜증", "화나", "다툼"]),
        ("성격 차이 또는 배려 부족",  ["무시", "이기", "욕", "성격", "나빠", "불편", "차갑", "거슬", "예민", "부딪"]),
        ("함께할 기회가 없었음",      ["반", "조", "기회", "자리", "없어서", "같이", "못", "만난 적", "접할"]),
        ("특별한 이유 없는 서먹함",   ["조용", "말없", "관심 없", "없다", "모르겠", "그냥", "딱히", "별로", "특별히", "이유"]),
    ]

    categories = POS_CATEGORIES if is_positive else NEG_CATEGORIES
    counter = Counter()
    has_unmatched = False

    for reason in reason_list:
        if pd.isna(reason) or str(reason).strip() == "":
            continue
        text = str(reason).strip()
        matched = False
        for label, keywords in categories:
            if any(w in text for w in keywords):
                counter[label] += 1
                matched = True
                break
        if not matched:
            has_unmatched = True

    # 분류 안 된 답변이 있을 경우 고정 문구로 처리
    if has_unmatched:
        fallback = "그 외 개인적 친밀감" if is_positive else "그 외 개인적 거리감"
        counter[fallback] += 1

    top = counter.most_common(2)
    if not top:
        return "특별한 사유 없음"
    return " / ".join([f"{label}({count}명)" for label, count in top])


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
# [기능 ③] 친밀도·소외도 상위 5명 및 사유 요약
# ──────────────────────────────────────────────────────────────
st.subheader("③ 친밀도·소외도 상위 5명 및 사유 요약")

name_stats = []
for name in df["name"]:
    best_received = sum(1 for _, _, data in G.in_edges(name, data=True) if data.get("relation") == "best")
    distant_received = sum(1 for _, _, data in G.in_edges(name, data=True) if data.get("relation") == "distant")
    name_stats.append({"이름": name, "best": best_received, "distant": distant_received})
stats_df = pd.DataFrame(name_stats)

col_pos, col_neg = st.columns(2)

with col_pos:
    st.markdown("#### 🏆 친밀도 상위 5명")
    top5_pos = stats_df.nlargest(5, "best")
    result_pos = []
    for _, row in top5_pos.iterrows():
        reason_summary = summarize_reasons_by_group(
            df[df["best_friend"] == row["이름"]]["reason_pos"].tolist(), is_positive=True
        )
        result_pos.append({
            "이름": row["이름"],
            "친한 친구로 선택받은 횟수": row["best"],
            "주된 친밀 사유": reason_summary
        })
    st.dataframe(pd.DataFrame(result_pos), use_container_width=True, hide_index=True)

with col_neg:
    st.markdown("#### ⚠️ 소외도 상위 5명")
    top5_neg = stats_df.nlargest(5, "distant")
    result_neg = []
    for _, row in top5_neg.iterrows():
        reason_summary = summarize_reasons_by_group(
            df[df["distant_friend"] == row["이름"]]["reason_neg"].tolist(), is_positive=False
        )
        result_neg.append({
            "이름": row["이름"],
            "서먹한 친구로 선택받은 횟수": row["distant"],
            "주된 서먹 사유": reason_summary
        })
    st.dataframe(pd.DataFrame(result_neg), use_container_width=True, hide_index=True)
