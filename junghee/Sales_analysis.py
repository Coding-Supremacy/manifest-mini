from matplotlib import pyplot as plt
import streamlit as st
import pandas as pd
import seaborn as sns




def run_analysis():
    
    

    st.title('📊 판매 분석 시스템')

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(['판매 데이터 업로드', '판매 데이터 분석', '판매 데이터 시각화'])

    # 🔹 TAB 1 - 업로드
    with tab1:        
        uploaded_file = st.file_uploader('판매 데이터 업로드 (CSV)', type='csv')
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.session_state.uploaded_df = df
            st.success("✅ 업로드 완료! 시각화 탭으로 이동합니다.")
            
            

    # 🔹 TAB 2 - 분석 (추후 확장 가능)
    with tab2:
        st.write("여기에 분석 기능을 넣을 수 있어요!")

    # 🔹 TAB 3 - 시각화
    with tab3:
        df = st.session_state.uploaded_df
        if df is not None:
            st.write("✅ 업로드된 데이터 미리보기:")
            st.dataframe(df.head())

            # melt
            df_melted = df.melt(
                id_vars=['공장명(국가)', '차량 모델', '판매 구분', '연도'],
                value_vars=[f"{i}월" for i in range(1, 13)],
                var_name='월', value_name='판매량'
            )

            df_melted['월_숫자'] = df_melted['월'].map({f"{i}월": i for i in range(1, 13)})
            df_melted['날짜'] = pd.to_datetime(
                df_melted['연도'].astype(str) + df_melted['월_숫자'].astype(str),
                format='%Y%m'
            )


            # 컬럼 선택 UI
            x_col = st.selectbox("X축으로 사용할 컬럼 선택", df_melted.columns)
            y_col = st.selectbox("Y축으로 사용할 컬럼 선택", df_melted.columns)

            시각화 = st.button('📊 시각화 시작')
            if 시각화:
                # 🔧 한글 폰트 설정 (윈도우 기준)
                plt.rcParams['font.family'] = 'Malgun Gothic'
                plt.rcParams['axes.unicode_minus'] = False
                sns.set(style="whitegrid")

                
                # 시각화
                plt.figure(figsize=(12, 5))
                df_group1 = df_melted.groupby(["날짜", "공장명(국가)"])["판매량"].sum().reset_index()
                sns.lineplot(data=df_group1, x="날짜", y="판매량", hue="공장명(국가)", marker="o")
                plt.title("공장별 월별 판매량 추이")
                plt.xlabel("날짜")
                plt.ylabel("판매량")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(plt)
        else:
            st.warning("📂 먼저 파일을 업로드해주세요.")