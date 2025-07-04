import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit.components.v1 import html
import os

# --------------------------
# 공통 함수
# --------------------------
def safe_format(x):
    try:
        return f"{x:,.0f}"
    except:
        return x

# --------------------------
# 데이터 로딩
# --------------------------
@st.cache_data
def load_vinyl_data():
    df = pd.read_csv("전북_영농폐비닐_발생량_2020_2023.csv", encoding="utf-8-sig")
    df.rename(columns={"범용형_LDPE": "멀칭형_LDPE"}, inplace=True)
    return df.loc[:, ~df.columns.str.startswith("증감_")]

@st.cache_data
def load_pesticide_data():
    df = pd.read_csv("전북_영농폐농약_발생량_2020_2023.csv", encoding="cp949")
    return df.loc[:, ~df.columns.str.startswith("증감_")]

@st.cache_data
def load_vinyl_collection_data():
    return pd.read_csv("연도별_영농폐비닐_수거량.csv", encoding="utf-8-sig")

@st.cache_data
def load_vinyl_recycle_data():
    return pd.read_csv("연도별_영농폐비닐_재활용량_증감_추이.csv", encoding="utf-8-sig")

@st.cache_data
def load_container_data():
    try:
        return pd.read_csv("영농_폐농약용기_수거량 수정본.csv", encoding="utf-8")
    except:
        return pd.read_csv("영농_폐농약용기_수거량 수정본.csv", encoding="cp949")

@st.cache_data
def load_recycle_data():
    return pd.read_csv("영농_폐농약용기_재활용량_증감_추이.csv", encoding="cp949")


# --------------------------
# 페이지 설정
# --------------------------
st.set_page_config(page_title="영농폐기물 통합 대시보드", layout="wide")
st.title("♻️ 영농폐기물 통합 대시보드 ")

# --------------------------
# 탭 옵션
# --------------------------
tab_option = st.sidebar.radio("📁 분석 대상", [
    "폐비닐",
    "폐농약",
    "폐비닐 수거량(전국)",
    "폐비닐 재활용량(전국)",
    "폐농약용기 수거량(전국)",
    "폐농약용기 재활용량(전국)",
    "폐농약용기 분포지도(전북)",
    "폐비닐 분포지도(전북)"
])


# --------------------------
# 폐비닐
if tab_option == "폐비닐":
    df = load_vinyl_data()
    df = df[df["구분"] != "전체"]
    years = sorted({col[:4] for col in df.columns if "_" in col})

    st.header("🧪 전북 영농 폐비닐 발생량")
    selected_regions = st.sidebar.multiselect("📍 지역 선택", df["구분"].unique(), default=df["구분"].unique())
    tabs = st.tabs([f"{y}년" for y in years])

    for i, year in enumerate(years):
        with tabs[i]:
            # 해당 연도 데이터 추출
            cols = [col for col in df.columns if col.startswith(year)]
            filtered = df[df["구분"].isin(selected_regions)][["구분"] + cols]
            renamed = {col: col.replace(f"{year}_", "") for col in cols}
            df_plot = filtered.rename(columns=renamed).set_index("구분")

            # ✅ 쉼표 제거 + 숫자형으로 변환
            for col in df_plot.columns:
                df_plot[col] = (
                    df_plot[col]
                    .astype(str)
                    .str.replace(",", "")
                    .str.strip()
                )
                df_plot[col] = pd.to_numeric(df_plot[col], errors="coerce")  # 숫자만 남음

            # ✅ 숫자형 유지 + 쉼표 포맷 적용
            st.dataframe(df_plot.style.format("{:,.0f}"))

            # ✅ 시각화
            fig = px.bar(
                df_plot,
                x=df_plot.index,
                y=df_plot.columns,
                barmode="stack",
                title=f"{year}년 폐비닐 발생량"
            )
            fig.update_layout(
                yaxis_title="발생량(톤)",
                yaxis_tickformat=","
            )
            st.plotly_chart(fig, use_container_width=True)

# --------------------------
# 폐농약
elif tab_option == "폐농약":
    df = load_pesticide_data()
    df = df[df["구분"] != "전체"]

    years = sorted({col[:4] for col in df.columns if "_" in col and col[:4].isdigit()})

    st.header("💧 전북 영농 폐농약 발생량")
    selected_regions = st.sidebar.multiselect("📍 지역 선택", df["구분"].unique(), default=df["구분"].unique())
    tabs = st.tabs([f"{y}년" for y in years])

    for i, year in enumerate(years):
        with tabs[i]:
            cols = [col for col in df.columns if col.startswith(f"{year}_")]
            filtered = df[df["구분"].isin(selected_regions)][["구분"] + cols]

            if filtered[cols].dropna(how="all").empty:
                st.warning(f"⚠️ {year}년의 폐농약 데이터가 존재하지 않습니다.")
            else:
                # ✅ 숫자 쉼표 포맷
                def safe_format(x):
                    try:
                        return f"{x:,.0f}"
                    except:
                        return x

                st.dataframe(filtered.set_index("구분").applymap(safe_format))

                # ✅ 그래프용 데이터 변환
                df_plot = filtered.melt(id_vars="구분", var_name="항목", value_name="발생량(기기)")

                # ✅ 그래프
                fig = px.bar(
                    df_plot,
                    x="구분",
                    y="발생량(기기)",
                    color="항목",
                    barmode="stack",
                    text_auto=True,
                )
                fig.update_layout(title=f"{year}년 폐농약 발생량", yaxis_title="발생량 (기기)")
                st.plotly_chart(fig, use_container_width=True)



# --------------------------
# 폐비닐 수거량(전국)
elif tab_option == "폐비닐 수거량(전국)":
    st.header("🧾 폐비닐 수거량 분석 (연도별 추이)")
    df = load_vinyl_collection_data()

    # 데이터 변환
    df_long = df.melt(id_vars='구분', var_name='연도', value_name='수거량')
    df_long['수거량'] = (
        df_long['수거량']
        .astype(str)
        .str.replace(",", "", regex=False)
    )
    df_long['수거량'] = pd.to_numeric(df_long['수거량'], errors='coerce')

    # ⚠️ 여기 수정 핵심: 연도를 문자열로 강제 변환
    df_long["연도"] = df_long["연도"].astype(str)

    df_long = df_long.dropna(subset=['수거량'])

    selected = st.sidebar.multiselect("📍 품목 선택", df_long["구분"].unique(), default=df_long["구분"].unique())
    chart_type = st.sidebar.radio("📊 시각화 선택", ["막대그래프", "선그래프", "파이차트"])

    tabs = st.tabs(selected)
    for i, item in enumerate(selected):
        with tabs[i]:
            view_df = df_long[df_long["구분"] == item].copy()

            styled_df = view_df.copy()
            styled_df["수거량"] = styled_df["수거량"].apply(lambda x: f"{x:,.0f}")
            st.dataframe(styled_df[["연도", "수거량"]])

            if chart_type == "막대그래프":
                fig = px.bar(view_df, x="연도", y="수거량", title=f"{item} 연도별 수거량")
            elif chart_type == "선그래프":
                fig = px.line(view_df, x="연도", y="수거량", markers=True, title=f"{item} 수거량 추이")
            else:
                fig = px.pie(view_df, names="연도", values="수거량", title=f"{item} 연도별 수거 비율")

            fig.update_layout(
                yaxis_tickformat=",",
                yaxis_title="수거량 (톤)",
                xaxis=dict(type='category')  # 🎯 핵심: x축을 범주형으로 강제!
              
            )
            st.plotly_chart(fig, use_container_width=True)


# --------------------------
# 폐비닐 재활용량(전국)
elif tab_option == "폐비닐 재활용량(전국)":
    df = load_vinyl_recycle_data()
    df_long = df.melt(id_vars='구분', var_name='연도', value_name='재활용량')
    df_long['재활용량'] = df_long['재활용량'].astype(str).str.replace(",", "", regex=False).str.strip()
    df_long['재활용량'] = pd.to_numeric(df_long['재활용량'], errors='coerce')
    df_long['연도'] = pd.to_numeric(df_long['연도'], errors='coerce').dropna().astype(int).astype(str)

    selected = st.sidebar.multiselect("♻️ 품목 선택", df_long["구분"].unique(), default=df_long["구분"].unique())
    chart_type = st.sidebar.radio("📊 시각화 선택", ["막대그래프", "선그래프", "파이차트"])

    st.header("♻️ 폐비닐 재활용량 분석 (연도별 추이)")
    tabs = st.tabs(selected)

    for i, item in enumerate(selected):
        with tabs[i]:
            view_df = df_long[df_long["구분"] == item].dropna(subset=["연도", "재활용량"]).copy()
            view_df["연도"] = view_df["연도"].astype(str)

            styled_df = view_df.copy()
            styled_df["재활용량"] = styled_df["재활용량"].apply(lambda x: f"{x:,.0f}")
            st.dataframe(styled_df[["연도", "재활용량"]])

            if chart_type == "막대그래프":
                fig = px.bar(view_df, x="연도", y="재활용량", title=f"{item} 재활용량 추이")
            elif chart_type == "선그래프":
                fig = px.line(view_df, x="연도", y="재활용량", markers=True, title=f"{item} 재활용량 변화")
            else:
                fig = px.pie(view_df, names="연도", values="재활용량", title=f"{item} 연도별 재활용 비율")

            fig.update_layout(
                yaxis_tickformat=",",
                yaxis_title="재활용량 (톤)",
                xaxis=dict(type='category')
               
            )
            st.plotly_chart(fig, use_container_width=True)

# --------------------------
# 폐농약용기 수거량
elif tab_option == "폐농약용기 수거량(전국)":
    df = load_container_data()
    df_long = df.melt(id_vars="구분", var_name="연도", value_name="수거량")
    
    df_long["연도"] = df_long["연도"].astype(str).str.extract(r"(\d{4})")  # 연도 정규식 추출
    df_long["수거량"] = (
        df_long["수거량"]
        .astype(str)
        .str.replace(",", "")
        .str.strip()
    )
    df_long["수거량"] = pd.to_numeric(df_long["수거량"], errors="coerce")
    df_long = df_long.dropna(subset=["수거량"])

    st.header("📦 폐농약용기 수거량 분석 (연도별 추이)")

    selected = st.sidebar.multiselect("📦 품목 선택", df_long["구분"].unique(), default=df_long["구분"].unique())
    chart_type = st.sidebar.radio("📊 시각화 선택", ["막대그래프", "선그래프", "파이차트"])

    tabs = st.tabs(selected)
    for i, item in enumerate(selected):
        with tabs[i]:
            view_df = df_long[df_long["구분"] == item].copy()
            if view_df.empty:
                st.warning(f"⚠️ {item}의 데이터가 없습니다.")
                continue

            styled_df = view_df.copy()
            styled_df["수거량"] = styled_df["수거량"].apply(safe_format)
            st.dataframe(styled_df[["연도", "수거량"]])

            if chart_type == "막대그래프":
                fig = px.bar(view_df, x="연도", y="수거량", title=f"{item} 연도별 수거량")
            elif chart_type == "선그래프":
                fig = px.line(view_df, x="연도", y="수거량", markers=True, title=f"{item} 수거량 추이")
            else:
                fig = px.pie(view_df, names="연도", values="수거량", title=f"{item} 연도별 수거 비율")

            fig.update_layout(
                yaxis_tickformat=",",
                yaxis_title="수거량 (개)",
                xaxis=dict(type='category')
            )
            st.plotly_chart(fig, use_container_width=True)

# --------------------------
# 폐농약용기 재활용량
elif tab_option == "폐농약용기 재활용량(전국)":
    df = load_recycle_data()
    df_long = df.melt(id_vars="구분", var_name="연도", value_name="재활용량")

    df_long["연도"] = df_long["연도"].astype(str).str.extract(r"(\d{4})")
    df_long["재활용량"] = (
        df_long["재활용량"]
        .astype(str)
        .str.replace(",", "")
        .str.strip()
    )
    df_long["재활용량"] = pd.to_numeric(df_long["재활용량"], errors="coerce")
    df_long = df_long.dropna(subset=["재활용량"])

    st.header("♻️ 폐농약용기 재활용량 분석 (연도별 추이)")

    selected = st.sidebar.multiselect("♻️ 품목 선택", df_long["구분"].unique(), default=df_long["구분"].unique())
    chart_type = st.sidebar.radio("📊 시각화 선택", ["막대그래프", "선그래프", "파이차트"])

    tabs = st.tabs(selected)
    for i, item in enumerate(selected):
        with tabs[i]:
            view_df = df_long[df_long["구분"] == item].copy()
            if view_df.empty:
                st.warning(f"⚠️ {item}의 데이터가 없습니다.")
                continue

            styled_df = view_df.copy()
            styled_df["재활용량"] = styled_df["재활용량"].apply(safe_format)
            st.dataframe(styled_df[["연도", "재활용량"]])

            if chart_type == "막대그래프":
                fig = px.bar(view_df, x="연도", y="재활용량", title=f"{item} 연도별 재활용량")
            elif chart_type == "선그래프":
                fig = px.line(view_df, x="연도", y="재활용량", markers=True, title=f"{item} 재활용량 추이")
            else:
                fig = px.pie(view_df, names="연도", values="재활용량", title=f"{item} 연도별 재활용 비율")

            fig.update_layout(
                yaxis_tickformat=",",
                yaxis_title="재활용량 (개)",
                xaxis=dict(type='category')
            )
            st.plotly_chart(fig, use_container_width=True)



# --------------------------
# 지도: 폐농약용기
elif tab_option == "폐농약용기 분포지도(전북)":
    st.header("🗺️ 전라북도 폐농약용기 발생량 분포 지도")
    FILE_PATH = "전북_총폐농약용기.xlsx"
    if os.path.exists(FILE_PATH):
        df = pd.read_excel(FILE_PATH)
        df.dropna(subset=["위도", "경도"], inplace=True)
        m = folium.Map(location=[35.8, 127.1], zoom_start=9)
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in df.iterrows():
            popup_text = f"<b>{row['구분']}</b><br>총폐농약용기: {row['총폐농약용기']:,}개"
            folium.CircleMarker(
                location=[row["위도"], row["경도"]],
                radius=max(4, row["총폐농약용기"] / 100000),
                color="blue",
                fill=True,
                fill_color="blue",
                fill_opacity=0.6,
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=row["구분"]
            ).add_to(marker_cluster)
        html(m._repr_html_(), height=600, width=1000)
    else:
        st.error(f"❌ 파일이 존재하지 않습니다: {FILE_PATH}")

# --------------------------
# 지도: 폐비닐
elif tab_option == "폐비닐 분포지도(전북)":
    st.header("🗺️ 전라북도 폐비닐 발생량 분포 지도")
    FILE_PATH = "전북_총폐비닐.xlsx"
    if os.path.exists(FILE_PATH):
        df = pd.read_excel(FILE_PATH)
        df.dropna(subset=["위도", "경도", "총폐비닐"], inplace=True)
        df = df[df["구분"] != "전체"]
        m = folium.Map(location=[35.8, 127.1], zoom_start=9)
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in df.iterrows():
            popup_text = f"<b>{row['구분']}</b><br>총폐비닐: {row['총폐비닐']:,}톤"
            folium.CircleMarker(
                location=[row["위도"], row["경도"]],
                radius=max(4, row["총폐비닐"] / 1000),
                color="green",
                fill=True,
                fill_color="green",
                fill_opacity=0.6,
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=row["구분"]
            ).add_to(marker_cluster)
        html(m._repr_html_(), height=600, width=1000)
    else:
        st.error(f"❌ 파일이 존재하지 않습니다: {FILE_PATH}")
