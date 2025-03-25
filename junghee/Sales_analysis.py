from matplotlib import pyplot as plt
import streamlit as st
import pandas as pd
import seaborn as sns




# 자동 melt 및 날짜 처리 함수
def auto_melt_month_columns(df):
    month_cols = [f"{i}월" for i in range(1, 13)]
    existing_month_cols = [col for col in month_cols if col in df.columns]

    if len(existing_month_cols) < 2:
        return None

    id_vars = [col for col in df.columns if col not in existing_month_cols]

    df_melted = df.melt(id_vars=id_vars, value_vars=existing_month_cols,
                        var_name="월", value_name="판매량")
    df_melted["월_숫자"] = df_melted["월"].str.replace("월", "").astype(int)

    if "연도" in df_melted.columns:
        df_melted["날짜"] = pd.to_datetime(
            df_melted["연도"].astype(str) + df_melted["월_숫자"].astype(str), format="%Y%m"
        )
    else:
        df_melted["연도"] = 2023
        df_melted["날짜"] = pd.to_datetime(
            df_melted["연도"].astype(str) + df_melted["월_숫자"].astype(str), format="%Y%m"
        )

    return df_melted


def run_analysis():
    st.title('📊 판매 분석 시스템')

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(['판매 데이터 업로드', '판매 데이터 분석', '판매 데이터 시각화'])

    # TAB 1 - 업로드
    with tab1:
        uploaded_file = st.file_uploader('판매 데이터 업로드 (CSV)', type='csv')
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.session_state["uploaded_df"] = df
            st.success("✅ 업로드 완료! 시각화 탭으로 이동하세요.")

    # TAB 2 - 분석 (추후 확장)
    with tab2:
        st.info("📌 분석 기능은 여기에 추가할 수 있어요!")

    # TAB 3 - 시각화
    with tab3:
        df = st.session_state.get("uploaded_df", None)
        if df is not None:
            st.subheader("✅ 업로드된 원본 데이터")
            st.dataframe(df.head())

            df_melted = auto_melt_month_columns(df)

            if df_melted is not None:
                st.subheader("✅ melt + 날짜 변환된 데이터")
                st.dataframe(df_melted.head())

                group_col = st.selectbox("📌 기준 컬럼 선택 (라인별)", [
                    col for col in df_melted.columns if col not in ["월", "월_숫자", "판매량", "날짜"]
                ])

                시각화 = st.button('📈 시각화 시작')
                if 시각화:
                    plt.rcParams['font.family'] = 'Malgun Gothic'
                    plt.rcParams['axes.unicode_minus'] = False
                    sns.set(style="whitegrid")

                    df_group = df_melted.groupby(["날짜", group_col])["판매량"].sum().reset_index()

                    plt.figure(figsize=(12, 5))
                    sns.lineplot(data=df_group, x="날짜", y="판매량", hue=group_col, marker="o")
                    plt.title(f"{group_col}별 월별 판매량 추이")
                    plt.xlabel("날짜")
                    plt.ylabel("판매량")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(plt)
            else:
                st.error("⚠️ '1월'~'12월' 컬럼이 포함된 파일만 분석할 수 있어요.")
        else:
            st.warning("📂 먼저 파일을 업로드해주세요.")