
import streamlit as st
import joblib
import pandas as pd

# 스트림릿 앱
st.title("국가별 차량 판매량 예측")

country_list = ['Africa', 'Asia Pacific', 'Canada', 'China', 'Eastern Europe', 'Europe', 'India', 'Latin America', 'Mexico', 'Middle East', 'U.S.A']
selected_country = st.selectbox("국가를 선택하세요", country_list)

if selected_country:
    # 모델 불러오기
    model = joblib.load(f"{selected_country}_model.joblib")
    
    # 새로운 데이터 예측
    new_economic_data = pd.DataFrame({
        'GDP': [3.1],
        '소비자 신뢰지수': [92],
        '환율': [1.32]
    })
    predicted_sales = model.predict(new_economic_data)
    st.write(f"{selected_country}의 예측 판매량: {predicted_sales}")
