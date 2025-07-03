import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import platform

# ✅ 한글 폰트 설정
if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

# ✅ 페이지 설정
st.set_page_config(page_title="영농폐기물 통합 대시보드", layout="wide")
st.title("♻️ 전북 및 전국 영농폐기물 통합 대시보드 (2020~2023)")

# ✅ 사이드바 탭
st.sidebar.title("🔧 분석 항목 선택")
tab_option = st.sidebar.radio("📁 분석 대상", [
    "폐비닐",
    "폐농약",
    "폐농약용기 수거량(전국)",
    "폐농약용기 재활용량(전국)"
])

# ✅ 데이터 불러오기 함수
@st.cache_data
def load_vinyl_data():
    return pd.read_csv("전북_영농폐비닐_발생량_2020_2023.csv", encoding="cp949")

@st.cache_data
def load_pesticide_data():
    return pd.read_csv("전북_영농폐농약_발생량_2020_2023.csv", encoding="cp949")

@st.cache_data
def load_container_data():
    try:
        return pd.read_csv("영농_폐농약용기_수거량 수정본.csv", encoding="utf-8")
    except:
        return pd.read_csv("영농_폐농약용기_수거량 수정본.csv", encoding="cp949")

@st.cache_data
def load_recycle_data():
    return pd.read_csv("영농_폐농약용기_재활용량_증감_추이.csv", encoding="cp949")

# ───────────────────────────────
# 📌 폐비닐
if tab_option == "폐비닐":
    st.header("📌 전북 영농 폐비닐 발생량 분석")
    df = load_vinyl_data()
    df = df[df["구분"] != "전체"]
    selected_regions = st.sidebar.multiselect("📍 지역 선택", df["구분"].unique(), default=df["구분"].unique())

    years = sorted({col[:4] for col in df.columns if "_" in col and "계" not in col and "증감" not in col})
    tabs = st.tabs([f"{y}년" for y in years])

    for i, year in enumerate(years):
        with tabs[i]:
            material_cols = [col for col in df.columns if col.startswith(year) and "계" not in col and "증감" not in col]
            short_cols = {col: col.replace(f"{year}_", "") for col in material_cols}
            filtered = df[df["구분"].isin(selected_regions)][["구분"] + material_cols]
            plot_df = filtered.rename(columns=short_cols).set_index("구분")

            st.dataframe(plot_df)
            fig, ax = plt.subplots(figsize=(12, 6))
            bottoms = np.zeros(len(plot_df))
            x = np.arange(len(plot_df.index))
            for col in plot_df.columns:
                ax.bar(x, plot_df[col], bottom=bottoms, label=col)
                bottoms += plot_df[col].values
            ax.set_xticks(x)
            ax.set_xticklabels(plot_df.index)
            ax.set_ylabel("발생량 (톤)")
            ax.set_title(f"{year}년 지역별 재질별 폐비닐 발생량")
            ax.legend()
            st.pyplot(fig)

# ───────────────────────────────
# 🧪 폐농약
elif tab_option == "폐농약":
    st.header("🧪 전북 영농 폐농약 발생량 분석")
    df = load_pesticide_data()
    df = df[df["구분"] != "전체"]
    selected_regions = st.sidebar.multiselect("📍 지역 선택", df["구분"].unique(), default=df["구분"].unique())

    years = sorted({col[:4] for col in df.columns if "_" in col})
    tabs = st.tabs([f"{y}년" for y in years])

    for i, year in enumerate(years):
        with tabs[i]:
            cols = [f"{year}_플라스틱", f"{year}_농약봉지류"]
            filtered = df[df["구분"].isin(selected_regions)][["구분"] + cols]
            plot_df = filtered.set_index("구분")

            st.dataframe(plot_df)
            fig, ax = plt.subplots(figsize=(12, 6))
            bottoms = np.zeros(len(plot_df))
            x = np.arange(len(plot_df.index))
            for col in plot_df.columns:
                ax.bar(x, plot_df[col], bottom=bottoms, label=col)
                bottoms += plot_df[col].values
            ax.set_xticks(x)
            ax.set_xticklabels(plot_df.index)
            ax.set_ylabel("발생량 (개수)")
            ax.set_title(f"{year}년 지역별 폐농약 발생량")
            ax.legend()
            st.pyplot(fig)

# ───────────────────────────────
# 🚜 폐농약용기 수거량
elif tab_option == "폐농약용기 수거량(전국)":
    st.header("🚜 전국 폐농약용기 수거량 분석")
    df = load_container_data()
    df_long = df.melt(id_vars='구분', var_name='연도', value_name='수거량')
    df_long.dropna(inplace=True)
    df_long['연도'] = df_long['연도'].astype(int)
    df_long['수거량'] = pd.to_numeric(df_long['수거량'], errors='coerce')

    category_filter = st.sidebar.multiselect("📦 수거 품목 선택", df_long["구분"].unique(), default=df_long["구분"].unique())
    filtered_df = df_long[df_long["구분"].isin(category_filter)]

    years = sorted(filtered_df["연도"].unique())
    tabs = st.tabs([f"{y}년" for y in years])
    for i, y in enumerate(years):
        with tabs[i]:
            view_df = filtered_df[filtered_df["연도"] == y][['구분', '수거량']]
            st.dataframe(view_df)

    chart_type = st.sidebar.radio("📊 시각화 형태", ["Bar", "Line", "Pie"])
    if chart_type == "Bar":
        fig = px.bar(filtered_df, x="연도", y="수거량", color="구분")
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "Line":
        fig = px.line(filtered_df, x="연도", y="수거량", color="구분", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "Pie":
        latest = filtered_df["연도"].max()
        pie_df = filtered_df[filtered_df["연도"] == latest]
        fig = px.pie(pie_df, names="구분", values="수거량", title=f"{latest}년 품목별 비율")
        st.plotly_chart(fig, use_container_width=True)

# ───────────────────────────────
# ♻️ 폐농약용기 재활용량
elif tab_option == "폐농약용기 재활용량(전국)":
    st.header("♻️ 영농 폐농약용기 재활용량 추이 대시보드")
    df = load_recycle_data()
    df_long = df.melt(id_vars='구분', var_name='연도', value_name='재활용량(개)')
    df_long['재활용량(개)'] = pd.to_numeric(df_long['재활용량(개)'], errors='coerce')
    df_long['연도'] = df_long['연도'].astype(float).astype(int)

    category_filter = st.sidebar.multiselect('용기 종류 선택', options=df_long['구분'].unique(), default=df_long['구분'].unique())
    chart_type = st.sidebar.selectbox('시각화 형태 선택', ['막대그래프', '선그래프', '파이차트'])

    filtered_df = df_long[df_long['구분'].isin(category_filter)]

    # ✅ 연도별 탭 구조
    years = sorted(filtered_df['연도'].unique())
    tabs = st.tabs([f"{y}년" for y in years])
    for i, year in enumerate(years):
        with tabs[i]:
            view_df = filtered_df[filtered_df['연도'] == year][['구분', '재활용량(개)']]
            st.dataframe(view_df)

    # ✅ 요약지표
    total_amount = filtered_df['재활용량(개)'].sum()
    avg_amount = filtered_df.groupby('연도')['재활용량(개)'].sum().mean()
    top_category = filtered_df.groupby('구분')['재활용량(개)'].sum().idxmax()
    col1, col2, col3 = st.columns(3)
    col1.metric("총 재활용량(개)", f"{total_amount:,.0f}")
    col2.metric("연 평균 재활용량(개)", f"{avg_amount:,.0f}")
    col3.metric("최다 재활용 품목", top_category)

    st.subheader("📉 재활용량 시각화")
    if chart_type == '막대그래프':
        fig = px.bar(filtered_df, x='연도', y='재활용량(개)', color='구분', barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == '선그래프':
        fig = px.line(filtered_df, x='연도', y='재활용량(개)', color='구분', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == '파이차트':
        latest_year = filtered_df['연도'].max()
        pie_df = filtered_df[(filtered_df['연도'] == latest_year) & (filtered_df['구분'] != '수거계')]
        fig = px.pie(pie_df, names='구분', values='재활용량(개)', title=f'{latest_year}년 품목별 재활용 비율')
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("📈 연도별 품목별 증감 비교"):
        growth_df = df_long.pivot(index='구분', columns='연도', values='재활용량(개)')
        growth_df['증감량(개)'] = growth_df[growth_df.columns[-1]] - growth_df[growth_df.columns[0]]
        st.dataframe(growth_df.sort_values('증감량(개)', ascending=False))
