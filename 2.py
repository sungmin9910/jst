import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit.components.v1 import html
import os

# --------------------------
# 데이터 로딩
# --------------------------
@st.cache_data
def load_vinyl_data():
    df = pd.read_csv("구분,2020_계,2020_하우스용_LDPE,2020_멀칭형_LDPE,2020_HDPE,"2020_기타(PVC,EVA,PO)",2021_계,2021_하우스용_LDPE,2021_멀칭형_LDPE,2021_HDPE,"2021_기타(PVC,EVA,PO)",증감_계,증감_하우스용_LDPE,증감_멀칭형_LDPE,증감_HDPE,"증감_기타(PVC,EVA,PO)",2022_계,2022_하우스용_LDPE,2022_멀칭형_LDPE,2022_HDPE,"2022_기타(PVC,EVA,PO)",2023_계,2023_하우스용_LDPE,2023_멀칭형_LDPE,2023_HDPE,"2023_기타(PVC,EVA,PO)",증감_계,증감_하우스용_LDPE,증감_멀칭형_LDPE,증감_HDPE,"증감_기타(PVC,EVA,PO)"
전체,"36,917","4,045","30,831",327,714,"37,970","5,045","30,577",620,620,"1,729","2,063","1,000",-254,"1,015","38,223","4,246","31,819",941,"1,217","35,105","3,383","29,896",924,842,"-3,118",-863,"-1,923",-17,-375
전주시,"1,064",144,907,3,10,"1,206",185,985,20,16,136,42,78,17,46,"1,251",122,"1,062",32,35,"1,134",98,982,30,24,-117,-24,-80,-2,-11
군산시,936,64,849,8,15,759,68,654,14,23,-177,4,-195,6,8,792,57,697,21,16,826,45,748,21,11,34,-12,51,0,-5
익산시,"3,053",563,"2,372",28,90,"3,570",750,"2,514",46,257,474,187,142,18,167,"3,383",631,"2,499",71,183,"3,023",503,"2,313",82,125,-360,-128,-186,11,-58
정읍시,"3,752",189,"3,486",34,43,"3,314",190,"3,366",62,92,-438,1,-120,28,49,"3,474",266,"3,090",93,25,"3,317",180,"3,006",46,85,-157,-86,-84,-47,60
남원시,"2,992",680,"2,193",27,15,"3,288",712,"2,290",42,244,296,32,161,15,229,"3,092",599,"2,658",46,172,"2,635",478,"1,967",72,119,-457,-121,-691,26,-53
김제시,"3,829",558,"3,107",35,129,"3,703",784,"2,784",53,241,-47,145,-323,18,112,"3,703",592,"2,859",83,170,"3,293",472,"2,615",88,117,-410,-120,-244,5,-53
완주군,"3,831",509,"3,170",45,117,"4,133",688,"3,213",69,163,302,179,43,24,46,"3,401",537,"3,280",96,154,"3,679",428,"3,047",98,106,278,-109,-233,2,-48
진안군,"2,040",59,"1,949",18,14,"2,271",102,"2,088",46,35,231,43,139,28,21,"4,223",869,"2,244",68,25,"2,224",69,"2,081",57,17,-199,-17,-163,-11,-8
무주군,"1,693",44,"1,633",15,1,"1,848",81,"1,701",37,28,155,37,68,22,27,"1,959",69,"1,816",55,20,"1,840",55,"1,724",47,14,-119,-14,-92,-8,-6
장수군,"1,822",115,"1,665",26,1,"1,899",196,"1,655",35,53,77,81,-10,9,52,"1,996",131,"1,774",53,38,"1,833",105,"1,654",47,26,-163,-26,-120,-6,-12
임실군,"1,439",92,"1,313",13,21,"1,416",99,"1,257",27,34,-23,7,-56,14,13,"1,512",83,"1,364",41,24,"1,443",66,"1,323",37,16,-69,-17,-41,-4,-8
순창군,"1,724",147,"1,527",16,34,"1,847",152,"1,609",34,52,123,5,82,18,18,"1,890",145,"1,675",50,37,"1,810",102,"1,635",47,25,-80,-26,-40,-3,-12
고창군,"5,531",690,"4,771",51,19,"6,800",880,"5,991",101,302,750,190,220,50,283,"8,301",741,"5,195",153,"1,202","5,792",590,"4,902",153,147,-509,-151,-293,0,-55
부안군,"2,168",190,"1,953",20,5,"2,365",289,"1,937",40,99,197,99,-16,20,94,"2,380",243,"2,007",60,70,"2,257",194,"1,956",59,48,-123,-49,-51,-1,-22", encoding="cp949")
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
        return pd.read_csv("영농_폐농약용기_수거량 수정본.csv", encoding='utf-8')
    except:
        return pd.read_csv("영농_폐농약용기_수거량 수정본.csv", encoding='cp949')

@st.cache_data
def load_recycle_data():
    return pd.read_csv("영농_폐농약용기_재활용량_증감_추이.csv", encoding="cp949")

# --------------------------
st.set_page_config(page_title="영농폐기물 통합 대시보드", layout="wide")
st.title("♻️ 영농폐기물 통합 대시보드 ")

tab_option = st.sidebar.radio("📁 분석 대상", [
    "폐비닐",
    "폐농약",
    "폐비닐 수거량(전국)",
    "폐비닐 재활용량(전국)",  # ✅ 이 부분 추가
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
            # ✅ '계' 포함
            cols = [col for col in df.columns if col.startswith(year)]
            filtered = df[df["구분"].isin(selected_regions)][["구분"] + cols]
            renamed = {col: col.replace(f"{year}_", "") for col in cols}
            df_plot = filtered.rename(columns=renamed).set_index("구분")
            st.dataframe(df_plot.style.format("{:,.0f}"))
            fig = px.bar(df_plot, x=df_plot.index, y=df_plot.columns, barmode="stack", title=f"{year}년 폐비닐 발생량")
            fig.update_layout(yaxis_tickformat=",")
            st.plotly_chart(fig, use_container_width=True)



# --------------------------
# 폐농약
elif tab_option == "폐농약":
    df = load_pesticide_data()
    df = df[df["구분"] != "전체"]
    years = sorted({col[:4] for col in df.columns if "_" in col})

    st.header("💧 전북 영농 폐농약 발생량")
    selected_regions = st.sidebar.multiselect("📍 지역 선택", df["구분"].unique(), default=df["구분"].unique())
    tabs = st.tabs([f"{y}년" for y in years])

    for i, year in enumerate(years):
        with tabs[i]:
            # ✅ '계' 포함
            cols = [col for col in df.columns if col.startswith(year)]
            filtered = df[df["구분"].isin(selected_regions)][["구분"] + cols]
            df_plot = filtered.set_index("구분")
            st.dataframe(df_plot.style.format("{:,.0f}"))
            fig = px.bar(df_plot, x=df_plot.index, y=df_plot.columns, barmode="stack", title=f"{year}년 폐농약 발생량")
            fig.update_layout(yaxis_tickformat=",")
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
    df_long['연도'] = pd.to_numeric(df_long['연도'], errors='coerce')
    df_long = df_long.dropna(subset=['수거량'])

    selected = st.sidebar.multiselect("📍 품목 선택", df_long["구분"].unique(), default=df_long["구분"].unique())
    chart_type = st.sidebar.radio("📊 시각화 선택", ["막대그래프", "선그래프", "파이차트"])

    tabs = st.tabs(selected)
    for i, item in enumerate(selected):
        with tabs[i]:
            view_df = df_long[df_long["구분"] == item]
            styled_df = view_df.copy()
            styled_df["수거량"] = styled_df["수거량"].apply(lambda x: f"{x:,.0f}")
            st.dataframe(styled_df[["연도", "수거량"]])

            if chart_type == "막대그래프":
                fig = px.bar(view_df, x="연도", y="수거량", title=f"{item} 연도별 수거량")
            elif chart_type == "선그래프":
                fig = px.line(view_df, x="연도", y="수거량", markers=True, title=f"{item} 수거량 추이")
            else:
                fig = px.pie(view_df, names="연도", values="수거량", title=f"{item} 연도별 수거 비율")

            fig.update_layout(yaxis_tickformat=",")
            st.plotly_chart(fig, use_container_width=True)

# --------------------------
# 폐비닐 재활용량(전국)
elif tab_option == "폐비닐 재활용량(전국)":
    df = load_vinyl_recycle_data()
    df_long = df.melt(id_vars='구분', var_name='연도', value_name='재활용량')

    # 쉼표 제거 후 숫자 변환
    df_long['재활용량'] = (
        df_long['재활용량']
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df_long['재활용량'] = pd.to_numeric(df_long['재활용량'], errors='coerce')
    df_long['연도'] = pd.to_numeric(df_long['연도'], errors='coerce')

    # 필터 및 시각화
    selected = st.sidebar.multiselect("♻️ 품목 선택", df_long["구분"].unique(), default=df_long["구분"].unique())
    chart_type = st.sidebar.radio("📊 시각화 선택", ["막대그래프", "선그래프", "파이차트"])

    st.header("♻️ 폐비닐 재활용량 분석 (연도별 추이)")

    tabs = st.tabs(selected)

    for i, item in enumerate(selected):
        with tabs[i]:
            view_df = df_long[df_long["구분"] == item].dropna(subset=["연도", "재활용량"])
            styled_df = view_df.copy()
            styled_df["재활용량"] = styled_df["재활용량"].apply(lambda x: f"{x:,.0f}")
            st.dataframe(styled_df[["연도", "재활용량"]])

            if chart_type == "막대그래프":
                fig = px.bar(view_df, x="연도", y="재활용량", title=f"{item} 재활용량 추이")
            elif chart_type == "선그래프":
                fig = px.line(view_df, x="연도", y="재활용량", markers=True, title=f"{item} 재활용량 변화")
            else:
                fig = px.pie(view_df, names="연도", values="재활용량", title=f"{item} 연도별 재활용 비율")

            fig.update_layout(yaxis_tickformat=",")
            st.plotly_chart(fig, use_container_width=True)




# --------------------------
# 폐농약용기 수거량
elif tab_option == "폐농약용기 수거량(전국)":
    df = load_container_data()
    df_long = df.melt(id_vars='구분', var_name='연도', value_name='수거량')
    df_long['연도'] = pd.to_numeric(df_long['연도'], errors='coerce')
    df_long['수거량'] = pd.to_numeric(df_long['수거량'], errors='coerce')

    selected = st.sidebar.multiselect("📦 품목 선택", df_long["구분"].unique(), default=df_long["구분"].unique())
    chart_type = st.sidebar.radio("📊 시각화 선택", ["막대그래프", "선그래프", "파이차트"])

    st.header("📦 폐농약용기 수거량 분석 (연도별 추이)")

    tabs = st.tabs(selected)
    for i, item in enumerate(selected):
        with tabs[i]:
            view_df = df_long[df_long["구분"] == item].dropna()
            styled_df = view_df.copy()
            styled_df["수거량"] = styled_df["수거량"].apply(lambda x: f"{x:,.0f}")
            st.dataframe(styled_df[["연도", "수거량"]])

            if chart_type == "막대그래프":
                fig = px.bar(view_df, x="연도", y="수거량", title=f"{item} 연도별 수거량")
            elif chart_type == "선그래프":
                fig = px.line(view_df, x="연도", y="수거량", markers=True, title=f"{item} 수거량 추이")
            else:
                fig = px.pie(view_df, names="연도", values="수거량", title=f"{item} 연도별 수거 비율")

            fig.update_layout(yaxis_tickformat=",")
            st.plotly_chart(fig, use_container_width=True)


# --------------------------
# 폐농약용기 재활용량
elif tab_option == "폐농약용기 재활용량(전국)":
    df = load_recycle_data()
    df_long = df.melt(id_vars='구분', var_name='연도', value_name='재활용량')
    df_long['연도'] = pd.to_numeric(df_long['연도'], errors='coerce')
    df_long['재활용량'] = pd.to_numeric(df_long['재활용량'], errors='coerce')

    selected = st.sidebar.multiselect("♻️ 품목 선택", df_long["구분"].unique(), default=df_long["구분"].unique())
    chart_type = st.sidebar.radio("📊 시각화 선택", ["막대그래프", "선그래프", "파이차트"])

    st.header("♻️ 폐농약용기 재활용량 분석 (연도별 추이)")

    tabs = st.tabs(selected)
    for i, item in enumerate(selected):
        with tabs[i]:
            view_df = df_long[df_long["구분"] == item].dropna()
            styled_df = view_df.copy()
            styled_df["재활용량"] = styled_df["재활용량"].apply(lambda x: f"{x:,.0f}")
            st.dataframe(styled_df[["연도", "재활용량"]])

            if chart_type == "막대그래프":
                fig = px.bar(view_df, x="연도", y="재활용량", title=f"{item} 연도별 재활용량")
            elif chart_type == "선그래프":
                fig = px.line(view_df, x="연도", y="재활용량", markers=True, title=f"{item} 재활용 추이")
            else:
                fig = px.pie(view_df, names="연도", values="재활용량", title=f"{item} 연도별 재활용 비율")

            fig.update_layout(yaxis_tickformat=",")
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
