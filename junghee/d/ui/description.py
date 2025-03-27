import streamlit as st
import pandas as pd

def run_description():

    st.title('데이터 전처리')
    df1=pd.read_csv('data/원본2024년_차종별판매실적.csv')
    df2=pd.read_csv('data/원본hmc-export-by-region-december-y2023.csv')

    st.subheader('원본 데이터 확인')
    col1, col2 = st.columns(2)
    with col1:
        st.write('기아 2024년 차종별 판매실적')
        st.dataframe(df1.head(),hide_index=True)
    with col2:
        st.write('현대 2023년 지역별 판매 실적')
        st.dataframe(df2.head(),hide_index=True)
    st.markdown("""
기아차와 현대차의 차종별, 지역별, 해외공장별 판매 실적 데이터를 수집하였으며,
이 중 기아차는 해외 현지 판매 실적, 현대차는 EU 및 미국 내 판매 실적 데이터를 포함하고 있습니다.
모든 데이터는 **2023년, 2024년, 2025년 연도별로 제공**받았습니다.
    """)


