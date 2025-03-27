import streamlit as st
import pandas as pd
import numpy as np
import joblib

def run_ho():
    # 모델, 스케일러, 컬럼 정보 불러오기
    model = joblib.load("hoyeon/lgbm_tuned_model.pkl")
    scaler = joblib.load("hoyeon/scaler.pkl")
    model_columns = joblib.load("hoyeon/model_columns.pkl")  # 학습 시 사용된 최종 컬럼 리스트

    st.title("다음달 수출량 예측 (LightGBM)")
    st.markdown("""
    이 애플리케이션은 학습된 LightGBM 모델을 이용하여  
    새로운 입력값에 따른 다음달 수출량을 예측합니다.
    """)

    # -------------------------------------------
    # 기아.csv 파일을 읽어 범주형 및 숫자형 옵션 추출
    # -------------------------------------------
    df = pd.read_csv("hoyeon/기아.csv")
    
    # 범주형 변수 옵션
    country_options = sorted(df["국가명"].unique())
    climate_options = sorted(df["기후대"].unique())
    car_type_options = sorted(df["차종 구분"].unique())
    vehicle_options = sorted(df["차량 구분"].unique())
    
    # "GDP"는 원본 파일에 있으므로 고유값 추출 (숫자형)
    gdp_options = sorted(df["GDP"].unique())
    
    # "전월 수출량"은 df를 Wide->Long 변환 후 계산
    id_vars = ['국가명', '연도', '기후대', 'GDP', '차종 구분', '차량 구분']
    month_cols = ['1월', '2월', '3월', '4월', '5월', '6월', 
                  '7월', '8월', '9월', '10월', '11월', '12월']
    df_long = pd.melt(df, id_vars=id_vars, value_vars=month_cols, 
                      var_name='월', value_name='수출량')
    df_long['월'] = df_long['월'].str.replace('월', '').astype(int)
    df_long['날짜'] = pd.to_datetime(df_long['연도'].astype(str) + '-' + df_long['월'].astype(str) + '-01')
    df_long = df_long.sort_values(by=['국가명', '날짜'])
    df_long['전월_수출량'] = df_long.groupby('국가명')['수출량'].shift(1)
    # 결측 제거 후 고유값 추출
    prev_export_options = sorted(df_long["전월_수출량"].dropna().unique())
    
    # -------------------------------------------
    # 사용자 입력 (메인 영역)
    # -------------------------------------------
    st.header("입력 변수")
    
   
    year         = st.number_input("연도", value=2023, step=1)
    month        = st.number_input("월", value=1, min_value=1, max_value=12, step=1)
    
    # 숫자 선택: "GDP" (기아.csv에서 추출한 옵션)
    gdp = st.selectbox("GDP", gdp_options)
    
    # 숫자 선택: "전월 수출량" (기아.csv에서 추출한 옵션)
    prev_export = st.selectbox("전월 수출량", prev_export_options)
    
    # 범주형 입력 (기아.csv의 고유값 사용)
    country  = st.selectbox("국가명", country_options)
    climate  = st.selectbox("기후대", climate_options)
    car_type = st.selectbox("차종 구분", car_type_options)
    vehicle  = st.selectbox("차량 구분", vehicle_options)
    
    # 입력 데이터를 DataFrame으로 구성 (한 행)
    input_data = {
        "수출량": [export_value],
        "전월_수출량": [prev_export],
        "연도": [year],
        "월": [month],
        "GDP": [gdp],
        "국가명": [country],
        "기후대": [climate],
        "차종 구분": [car_type],
        "차량 구분": [vehicle]
    }
    input_df = pd.DataFrame(input_data)
    
    st.subheader("입력 데이터")
    st.write(input_df)
    
    # -------------------------------
    # 전처리: One-Hot 인코딩 및 컬럼 재정렬
    # -------------------------------
    input_encoded = pd.get_dummies(input_df, columns=["국가명", "기후대", "차종 구분", "차량 구분"])
    input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)
    
    # 스케일링
    input_scaled = scaler.transform(input_encoded)
    
    # 예측
    prediction = model.predict(input_scaled)[0]
    
    st.subheader("예측 결과")
    st.write(f"예측된 다음달 수출량: {prediction:.2f}")

if __name__ == "__main__":
    run_ho()
