import streamlit as st
import joblib
import pandas as pd

# 스트림릿 앱
st.title("국가별 차량 판매량 예측")

country_list = ['Africa', 'Asia Pacific', 'Canada', 'China', 'Eastern Europe', 'Europe', 'India', 'Latin America', 'Mexico', 'Middle East', 'U.S.A']
selected_country = st.selectbox("국가를 선택하세요", country_list)

if selected_country:
    # 모델 불러오기
    model = joblib.load(f"eungmin/{selected_country}_model.pkl")
    print(model)
    
    # 각 국가의 경제 지표 데이터
    new_economic_data_dict = {
        'Africa': pd.DataFrame({
            'GDP': [2.5],
            '소비자 신뢰지수': [80],
            '환율': [1.15]
        }),
        'Asia Pacific': pd.DataFrame({
            'GDP': [4.5],
            '소비자 신뢰지수': [93],
            '환율': [6.9]
        }),
        'Canada': pd.DataFrame({
            'GDP': [2.1],
            '소비자 신뢰지수': [90],
            '환율': [1.37]
        }),
        'China': pd.DataFrame({
            'GDP': [5.5],
            '소비자 신뢰지수': [103],
            '환율': [7.0]
        }),
        'Eastern Europe': pd.DataFrame({
            'GDP': [2.8],
            '소비자 신뢰지수': [83],
            '환율': [1.25]
        }),
        'Europe': pd.DataFrame({
            'GDP': [1.9],
            '소비자 신뢰지수': [88],
            '환율': [0.97]
        }),
        'India': pd.DataFrame({
            'GDP': [7.0],
            '소비자 신뢰지수': [94],
            '환율': [85]
        }),
        'Latin America': pd.DataFrame({
            'GDP': [2.5],
            '소비자 신뢰지수': [78],
            '환율': [1.25]
        }),
        'Mexico': pd.DataFrame({
            'GDP': [2.8],
            '소비자 신뢰지수': [83],
            '환율': [22.5]
        }),
        'Middle East': pd.DataFrame({
            'GDP': [3.5],
            '소비자 신뢰지수': [88],
            '환율': [4.1]
        }),
        'U.S.A': pd.DataFrame({
            'GDP': [2.5],
            '소비자 신뢰지수': [98],
            '환율': [1.075]
        })
    }
    
    # 선택한 국가의 경제 지표 데이터 사용
    new_economic_data = new_economic_data_dict[selected_country]
    
    # 예측
    predicted_sales = model.predict(new_economic_data)
    st.write(f"{selected_country}의 예측 판매량: {round(predicted_sales[0], 0)}")
