# pages/1_시각화.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="판매 시각화", layout="wide")
st.title("📊 판매 데이터 시각화")

# 🔄 세션에 저장된 파일 불러오기
uploaded_file = st.session_state.get("uploaded_file")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ 업로드한 데이터:")
    st.dataframe(df.head())

    시각화 = st.button("📈 시각화 시작")
    if 시각화:
        plt.rcParams["font.family"] = "Malgun Gothic"
        plt.rcParams["axes.unicode_minus"] = False
        sns.set(style="whitegrid")

        # melt 예제 (데이터 구조에 맞게 수정 가능)
        df_melted = df.melt(
            id_vars=["공장명(국가)", "차량 모델", "판매 구분", "연도"],
            value_vars=[f"{i}월" for i in range(1, 13)],
            var_name="월", value_name="판매량"
        )
        df_melted["월_숫자"] = df_melted["월"].str.replace("월", "").astype(int)
        df_melted["날짜"] = pd.to_datetime(df_melted["연도"].astype(str) + df_melted["월_숫자"].astype(str), format="%Y%m")

        df_group = df_melted.groupby(["날짜", "공장명(국가)"])["판매량"].sum().reset_index()

        plt.figure(figsize=(12, 5))
        sns.lineplot(data=df_group, x="날짜", y="판매량", hue="공장명(국가)", marker="o")
        plt.title("공장별 판매량 추이")
        plt.xticks(rotation=45)
        st.pyplot(plt)

else:
    st.warning("⚠️ 먼저 메인 페이지에서 파일을 업로드해주세요.")
