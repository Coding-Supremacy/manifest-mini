import streamlit as st
import pandas as pd
import numpy as np
import joblib
<<<<<<< Updated upstream
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from PIL import Image
import yfinance as yf
import matplotlib.colors as mcolors

# CSS 스타일 (간결한 버전)
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
        padding: 2rem;
    }
    .highlight-box {
        background-color: #f0f7ff;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4a6fa5;
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .positive {
        color: #28a745;
        font-weight: bold;
    }
    .negative {
        color: #dc3545;
        font-weight: bold;
    }
    .neutral {
        color: #ffc107;
        font-weight: bold;
    }
    .section-title {
        font-size: 1.5rem;
        color: #2a3f5f;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e6e6e6;
    }
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def reset_form():
    st.session_state.clear()

def get_country_flag(country_name):
    flag_mapping = {
        '미국': '🇺🇸', '중국': '🇨🇳', '일본': '🇯🇵', '독일': '🇩🇪',
        '영국': '🇬🇧', '프랑스': '🇫🇷', '한국': '🇰🇷', '인도': '🇮🇳',
        '브라질': '🇧🇷', '캐나다': '🇨🇦', '호주': '🇦🇺', '이탈리아': '🇮🇹',
        '스페인': '🇪🇸', '멕시코': '🇲🇽', '인도네시아': '🇮🇩', '터키': '🇹🇷',
        '네덜란드': '🇳🇱', '스위스': '🇨🇭', '사우디아라비아': '🇸🇦', '아르헨티나': '🇦🇷'
    }
    return flag_mapping.get(country_name, '')

def fetch_gdp_data(country_name):
    country_code_map = {
        '미국': 'USA', '중국': 'CHN', '일본': 'JPN', '독일': 'DEU',
        '영국': 'GBR', '프랑스': 'FRA', '한국': 'KOR', '인도': 'IND',
        '브라질': 'BRA', '캐나다': 'CAN', '호주': 'AUS', '이탈리아': 'ITA',
        '스페인': 'ESP', '멕시코': 'MEX', '인도네시아': 'IDN', '터키': 'TUR',
        '네덜란드': 'NLD', '스위스': 'CHE', '사우디아라비아': 'SAU', '아르헨티나': 'ARG'
    }
    country_code = country_code_map.get(country_name, None)
    if country_code:
        try:
            url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.MKTP.CD?format=json&date=2022"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and data[1]:
                    return data[1][0]['value'] / 1e9  # 단위: 10억 달러
        except:
            pass
    return None

def get_change_reason(change_rate):
    if change_rate > 30:
        return {
            "text": "📈 급격한 증가 (30% 초과)",
            "reason": "신규 시장 진출 성공, 경쟁사 제품 리콜, 현지 통화 강세, 정부 인센티브 확대, 신제품 출시",
            "suggestion": "생산량 확대 고려, 서비스 네트워크 강화, 가격 인상 검토",
            "class": "positive"
        }
    elif 15 < change_rate <= 30:
        return {
            "text": "📈 강한 증가 (15%~30%)",
            "reason": "현지 경제 호황, 브랜드 인지도 상승, 모델 라인업 강화, 환율 영향 (원화 약세), 계절적 수요 증가",
            "suggestion": "재고 관리 강화, 마케팅 투자 유지, 고객 만족도 조사 실시",
            "class": "positive"
        }
    elif 5 < change_rate <= 15:
        return {
            "text": "📈 안정적 증가 (5%~15%)",
            "reason": "꾸준한 마케팅 효과, 소폭 가격 경쟁력 향상, 품질 인식 개선, 소비자 신뢰 상승, 부분 모델 변경 효과",
            "suggestion": "현재 전략 유지, 고객 피드백 수집, 경쟁사 동향 모니터링",
            "class": "positive"
        }
    elif -5 <= change_rate <= 5:
        return {
            "text": "➡️ 안정 유지 (-5%~5%)",
            "reason": "시장 상황 유지, 경쟁사 유사 성과, 계절 영향 없음, 경제 상황 중립, 마케팅 효과 중립",
            "suggestion": "시장 변화 모니터링, 고객 설문 실시, 전략 재검토",
            "class": "neutral"
        }
    elif -15 <= change_rate < -5:
        return {
            "text": "📉 감소 추세 (-15%~-5%)",
            "reason": "경제 불황, 경쟁사 강세, 환율 영향, 모델 노후화, 수요 감소",
            "suggestion": "프로모션 강화, 가격 경쟁력 분석, 모델 업데이트 계획 수립",
            "class": "negative"
        }
    elif -30 <= change_rate < -15:
        return {
            "text": "📉 급격한 감소 (-30%~-15%)",
            "reason": "규제 강화, 정치 불안, 딜러 파산, 경쟁사 할인, 품질 문제 발생",
            "suggestion": "사정 긴급 점검, 위기 대응 팀 구성, 긴급 마케팅 전략 수립, 본사 지원 검토",
            "class": "negative"
        }
    else:
        return {
            "text": "📉 위험한 감소 (-30% 미만)",
            "reason": "운영 위기, 모델 판매 중단, 경제 위기/전쟁, 시장 점유율 급증, 브랜드 이미지 손상",
            "suggestion": "긴급 대책 회의 소집, 현지 실사 파견, 구조 조정 검토, 시장 철수 검토",
            "class": "negative"
        }

def create_tab_buttons():
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "📊 단일 국가 예측"
    cols = st.columns(2)
    tabs = ["📊 단일 국가 예측", "🌍 다중 국가 비교"]
    for i, tab in enumerate(tabs):
        with cols[i]:
            if st.button(tab, key=f"tab_{i}",
                         type="primary" if st.session_state.current_tab == tab else "secondary",
                         use_container_width=True):
                st.session_state.current_tab = tab
    return st.session_state.current_tab

def create_gdp_export_scatter(df, selected_country):
    latest_year = df['날짜'].dt.year.max()
    data = df[df['날짜'].dt.year == latest_year].groupby('국가명')['수출량'].sum().reset_index()
    data['GDP'] = data['국가명'].apply(lambda x: fetch_gdp_data(x) or 0)
    fig = px.scatter(data, x='GDP', y='수출량', size='수출량', color='국가명',
                     title="GDP 대비 수출량 분석",
                     labels={'GDP': 'GDP (10억$)', '수출량': '총 수출량'},
                     size_max=60)
    fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(hovermode="closest")
    return fig

def run_ho():
    # 모델 및 데이터 로드
    model = joblib.load("hoyeon/lgbm_tuned_model.pkl")
    scaler = joblib.load("hoyeon/scaler.pkl")
    model_columns = joblib.load("hoyeon/model_columns.pkl")
    df = pd.read_csv("hoyeon/기아.csv")
    
    st.title("🚗 기아 자동차 수출량 분석 대시보드")
    st.markdown("""
    <div style="margin-bottom: 2rem; color: #666;">
        기아 자동차의 글로벌 수출량을 분석하고 예측하는 대시보드입니다. 단일 국가 예측과 다중 국가 비교 기능을 제공합니다.
    </div>
    """, unsafe_allow_html=True)
    
    # 데이터 전처리
    id_vars = ['국가명', '연도', '기후대', 'GDP', '차종 구분', '차량 구분']
    month_cols = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']
    df_long = pd.melt(df, id_vars=id_vars, value_vars=month_cols, var_name='월', value_name='수출량')
    df_long['월'] = df_long['월'].str.replace('월','').astype(int)
    df_long['날짜'] = pd.to_datetime(df_long['연도'].astype(str) + '-' + df_long['월'].astype(str) + '-01')
    df_long = df_long.sort_values(by=['국가명','날짜'])
    latest_year = df_long["날짜"].dt.year.max()
    
    current_tab = create_tab_buttons()
    
    if 'prediction_made' not in st.session_state:
        st.session_state.prediction_made = False
    if 'comparison_made' not in st.session_state:
        st.session_state.comparison_made = False
    
    if current_tab == "📊 단일 국가 예측":
        st.markdown("### 📊 단일 국가 수출량 예측")
        
        with st.expander("🔍 분석 조건 설정", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_climate = st.selectbox("🌍 기후대", sorted(df["기후대"].unique()), key='climate_select')
                filtered_countries = sorted(df[df["기후대"] == selected_climate]["국가명"].unique())
                selected_country = st.selectbox("🏳️ 국가명", filtered_countries, key='country_select')
                target_year = st.number_input("📅 예측 연도", min_value=2000, max_value=datetime.now().year+5,
                                              value=datetime.now().year, key='year_select')
                target_month = st.number_input("📆 예측 월", min_value=1, max_value=12,
                                               value=datetime.now().month, key='month_select')
            with col2:
                selected_car_type = st.selectbox("🚘 차종 구분", sorted(df["차종 구분"].unique()), key='car_type_select')
                if "차종" in df.columns:
                    filtered_car_options = sorted(df[df["차종 구분"] == selected_car_type]["차종"].unique())
                else:
                    filtered_car_options = sorted(df[df["차종 구분"] == selected_car_type]["차량 구분"].unique())
                selected_car = st.selectbox("🚗 차량 구분", filtered_car_options, key='car_select')
        
        col1, col2 = st.columns([4,1])
        with col1:
            predict_btn = st.button("🔮 예측 실행", type="primary", use_container_width=True)
        with col2:
            reset_btn = st.button("🔄 초기화", on_click=reset_form, use_container_width=True)
        
        if predict_btn:
            st.session_state.prediction_made = True
        
        if st.session_state.prediction_made or ('prediction_result' in st.session_state and not reset_btn):
            # 단일 국가 데이터 (AND 조건)
            country_data = df_long[
                (df_long["국가명"] == selected_country) |
                (df_long["차종 구분"] == selected_car_type) &
                (df_long["차량 구분"] == selected_car)
            ].sort_values(by="날짜", ascending=False)
            
            if country_data.empty:
                st.warning("⚠️ 선택한 조건에 맞는 데이터가 없습니다. 다른 조건을 선택해주세요.")
                st.session_state.prediction_made = False
                return
            
            if predict_btn:
                auto_current_export = country_data["수출량"].iloc[0]
                auto_prev_export = country_data["수출량"].iloc[1] if len(country_data) >= 2 else 0.0
                prev_year_data = df_long[
                    (df_long["국가명"] == selected_country) |
                    (df_long["차종 구분"] == selected_car_type) &
                    (df_long["차량 구분"] == selected_car) &
                    (df_long["날짜"].dt.year == target_year-1) &
                    (df_long["날짜"].dt.month == target_month)
                ]
                prev_year_export = prev_year_data["수출량"].values[0] if not prev_year_data.empty else 0
                input_data = {
                    "수출량": [auto_current_export],
                    "전월_수출량": [auto_prev_export],
                    "연도": [target_year],
                    "월": [target_month],
                    "GDP": [df[df["국가명"] == selected_country]["GDP"].iloc[0]],
                    "국가명": [selected_country],
                    "기후대": [selected_climate],
                    "차종 구분": [selected_car_type],
                    "차량 구분": [selected_car]
                }
                input_df = pd.DataFrame(input_data)
                input_encoded = pd.get_dummies(input_df, columns=["국가명", "기후대", "차종 구분", "차량 구분"])
                input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)
                input_scaled = scaler.transform(input_encoded)
                prediction = model.predict(input_scaled)[0]
                st.session_state.prediction_result = {
                    'selected_country': selected_country,
                    'selected_car_type': selected_car_type,
                    'selected_car': selected_car,
                    'auto_current_export': auto_current_export,
                    'auto_prev_export': auto_prev_export,
                    'prev_year_export': prev_year_export,
                    'prediction': prediction,
                    'target_year': target_year,
                    'target_month': target_month,
                    'selected_climate': selected_climate
                }
            else:
                result = st.session_state.prediction_result
                selected_country = result['selected_country']
                selected_car_type = result['selected_car_type']
                selected_car = result['selected_car']
                auto_current_export = result['auto_current_export']
                auto_prev_export = result['auto_prev_export']
                prev_year_export = result['prev_year_export']
                prediction = result['prediction']
                target_year = result['target_year']
                target_month = result['target_month']
                selected_climate = result['selected_climate']
            
            # 예측 결과 계산
            yearly_change = ((prediction - prev_year_export) / prev_year_export * 100) if prev_year_export != 0 else 0
            change_info = get_change_reason(yearly_change)
            gdp_value = fetch_gdp_data(selected_country) or df[df["국가명"] == selected_country]["GDP"].iloc[0]
            st.write("")
            st.write("")
            # 예측 결과 표시
            st.markdown("### 📌 예측 결과 요약")

            st.markdown("""
    <div style="background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%); 
                border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0;
                border-left: 5px solid #4a6fa5;">
        <h3 style="color: #2a3f5f; margin-top: 0;">✨ 핵심 예측 지표</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
            <div style="background: white; border-radius: 10px; padding: 1.5rem; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;">
                <div style="font-size: 1rem; color: #666; margin-bottom: 0.5rem;">예상 수출량</div>
                <div style="font-size: 2.5rem; font-weight: bold; color: #2a3f5f;">
                    {prediction:,.0f}
                </div>
                <div style="font-size: 0.9rem; color: #666;">
                    {target_year}년 {target_month}월 예측
                </div>
            </div>
            <div style="background: white; border-radius: 10px; padding: 1.5rem; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;">
                <div style="font-size: 1rem; color: #666; margin-bottom: 0.5rem;">전년 동월 대비</div>
                <div style="font-size: 2.5rem; font-weight: bold; color: {color};">
                    {yearly_change:+.1f}%
                </div>
                <div style="font-size: 0.9rem; color: #666;">
                    {prev_year_export:,.0f} → {prediction:,.0f}
                </div>
            </div>
        </div>
    </div>
    """.format(
        prediction=prediction,
        target_year=target_year,
        target_month=target_month,
        yearly_change=yearly_change,
        prev_year_export=prev_year_export,
        color="green" if yearly_change >= 5 else ("red" if yearly_change <= -5 else "orange")
    ), unsafe_allow_html=True)






            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.9rem; color:#666;">예측 국가</div>
                    <div style="font-size:1.2rem; font-weight:bold;">{get_country_flag(selected_country)} {selected_country}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.9rem; color:#666;">예측 차량</div>
                    <div style="font-size:1.2rem; font-weight:bold;">{selected_car_type} - {selected_car}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.9rem; color:#666;">예측 기후대</div>
                    <div style="font-size:1.2rem; font-weight:bold;">{selected_climate}</div>
                </div>
                """, unsafe_allow_html=True)

            st.write("")   
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.9rem; color:#666;">예측 수출량</div>
                    <div style="font-size:1.5rem; font-weight:bold;">{prediction:,.0f}</div>
                    <div style="font-size:0.9rem;">{target_year}년 {target_month}월</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.9rem; color:#666;">전년 동월 대비</div>
                    <div style="font-size:1.5rem; font-weight:bold; class="{change_info['class']}">{yearly_change:.1f}%</div>
                    <div style="font-size:0.9rem;">{change_info['text']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.9rem; color:#666;">국가 GDP</div>
                    <div style="font-size:1.5rem; font-weight:bold;">{gdp_value:,.1f}</div>
                    <div style="font-size:0.9rem;">10억 달러 (2022년 기준)</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            # 분석 인사이트 섹션
            st.markdown("### 🔍 분석 인사이트")
            with st.container():
                st.markdown(f"""
                <div class="highlight-box">
                    <h4>📈 변화 원인 분석</h4>
                    <p><strong>{change_info['text']}</strong></p>
                    <p><strong>주요 원인:</strong> {change_info['reason']}</p>
                    <p><strong>제안 사항:</strong> {change_info['suggestion']}</p>
                </div>
                """, unsafe_allow_html=True)
            st.write("")
            st.write("")
            # 차트 분석 섹션
            st.write("")
            st.write("")
            st.markdown("### 📊 차트 분석")
            
            # 첫 번째 행 차트
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 기후대별 수출량 비교")
                climate_data = df_long[
                    (df_long["국가명"] == selected_country) |
                    (df_long["차종 구분"] == selected_car_type) |
                    (df_long["차량 구분"] == selected_car) &
                    (df_long["날짜"].dt.year == target_year-1)
                ].groupby("기후대")["수출량"].sum().reset_index()
                
                if not climate_data.empty:
                    fig_climate = px.bar(
                        climate_data,
                        x="기후대",
                        y="수출량",
                        title=f"{selected_car_type} - {selected_car} 기후대별 총 수출량",
                        labels={"수출량": "총 수출량", "기후대": "기후대"},
                        height=400,
                        color="기후대",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_climate.update_layout(showlegend=False)
                    st.plotly_chart(fig_climate, use_container_width=True)
                    st.caption("""
                    **해석 방법:**  
                    - 각 기후대에서 선택한 차량의 총 수출량을 비교  
                    - 높은 막대는 해당 기후대에서 수출이 활발함을 의미  
                    - 기후 특성에 따른 수출 패턴 파악 가능
                    """)
                else:
                    st.warning("기후대별 데이터가 없습니다.")
            
            with col2:
                st.markdown("#### GDP 대비 수출량")
                bubble_fig = create_gdp_export_scatter(df_long, selected_country)
                st.plotly_chart(bubble_fig, use_container_width=True)
                st.caption("""
                    **해석 방법:**  
                    - X축: 국가 GDP (10억 달러)  
                    - Y축: 총 수출량  
                    - 버블 크기: 수출량 규모  
                    - 선택 국가는 강조 표시됨  
                    - GDP 대비 수출 효율성 분석 가능
                    """)
            
            # 두 번째 행 차트
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 차량 종류별 수출 비중")
                country_car_data = df_long[
                    (df_long["국가명"] == selected_country) &
                    (df_long["날짜"].dt.year == latest_year)
                ].groupby(["차종 구분", "차량 구분"])["수출량"].sum().reset_index()
                
                if not country_car_data.empty:
                    country_car_data = country_car_data.sort_values("수출량", ascending=False).head(10)
                    fig_pie = px.pie(country_car_data, names="차량 구분", values="수출량",
                                     title=f"{selected_country}의 차량 종류별 수출량 비중",
                                     height=400, color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pie.update_layout(showlegend=False)
                    st.plotly_chart(fig_pie, use_container_width=True)
                    st.caption("""
                    **해석 방법:**  
                    - 선택 국가에서 어떤 차량이 많이 수출되는지 비중 확인  
                    - 전체 판매에서 차량별 점유율 파악  
                    - 주력 모델과 마이너 모델 식별 가능
                    """)
                else:
                    st.warning("차량 종류별 데이터가 없습니다.")
            
            with col2:
                st.markdown("#### 국가별 수출량 순위")
                car_data = df_long[
                    ((df_long["차종 구분"] == selected_car_type) | (df_long["차량 구분"] == selected_car)) &
                    (df_long["날짜"].dt.year == latest_year)
                ].groupby("국가명")["수출량"].sum().reset_index()
                
                if not car_data.empty:
                    fig_bar = px.bar(
                        car_data,
                        x="국가명",
                        y="수출량",
                        title=f"{selected_car_type} - {selected_car} 국가별 수출량",
                        labels={"수출량": "총 수출량", "국가명": "국가명"},
                        height=400,
                        color="국가명",
                        color_discrete_sequence=px.colors.qualitative.Vivid
                    )
                    fig_bar.update_layout(showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)
                    st.caption("""
                    **해석 방법:**  
                    - 선택 차량의 국가별 수출량 순위  
                    - 글로벌 시장에서의 상대적 위치 파악  
                    - 경쟁 국가와의 비교 가능  
                    - 높은 막대는 주요 시장을 의미
                    """)
                else:
                    st.warning("국가별 데이터가 없습니다.")
    
    elif current_tab == "🌍 다중 국가 비교":
        st.markdown("### 🌍 다중 국가 비교 분석")
        
        with st.expander("🔍 비교 조건 설정", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_countries = st.multiselect("비교할 국가 선택",
                                                    sorted(df["국가명"].unique()),
                                                    default=sorted(df["국가명"].unique())[:3],
                                                    key='multi_country_select')
                if len(selected_countries) < 2:
                    st.warning("최소 2개 국가를 선택해주세요.")
                    st.stop()
            with col2:
                selected_car_type = st.selectbox("🚘 차종 구분", sorted(df["차종 구분"].unique()), key='multi_car_type_select')
                if "차종" in df.columns:
                    filtered_car_options = sorted(df[df["차종 구분"] == selected_car_type]["차종"].unique())
                else:
                    filtered_car_options = sorted(df[df["차종 구분"] == selected_car_type]["차량 구분"].unique())
                selected_car = st.selectbox("🚗 차량 구분", filtered_car_options, key='multi_car_select')
            
            col1, col2 = st.columns([4,1])
            with col1:
                compare_btn = st.button("🔍 비교하기", type="primary", use_container_width=True)
            with col2:
                reset_btn = st.button("🔄 초기화", on_click=reset_form, use_container_width=True)
        
        if compare_btn:
            st.session_state.comparison_made = True
        

           



        if st.session_state.comparison_made or ('multi_comparison_result' in st.session_state and not reset_btn):
            if compare_btn:
                filtered_data = df_long[
                    (df_long["국가명"].isin(selected_countries)) |
                    ((df_long["차종 구분"] == selected_car_type) & (df_long["차량 구분"] == selected_car)) &
                    (df_long["날짜"].dt.year == latest_year)
                ]
                if filtered_data.empty:
                    st.warning("⚠️ 선택한 조건에 맞는 데이터가 없습니다. 다른 조건을 선택해주세요.")
                    st.stop()
                st.session_state.multi_comparison_result = {
                    'filtered_data': filtered_data,
                    'selected_countries': selected_countries,
                    'selected_car_type': selected_car_type,
                    'selected_car': selected_car
                }
            else:
                result = st.session_state.multi_comparison_result
                filtered_data = result['filtered_data']
                selected_countries = result['selected_countries']
                selected_car_type = result['selected_car_type']
                selected_car = result['selected_car']
            
            # 요약 정보 표시
            st.markdown("### 📌 비교 요약")

    

            summary_data = filtered_data.groupby("국가명")["수출량"].sum().reset_index().sort_values("수출량", ascending=False)
            
            cols = st.columns(len(selected_countries))
            for idx, (_, row) in enumerate(summary_data.iterrows()):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size:1rem; font-weight:bold;">{get_country_flag(row['국가명'])} {row['국가명']}</div>
                        <div style="font-size:1.2rem;">{row['수출량']:,.0f}</div>
                        <div style="font-size:0.8rem;">총 수출량</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 차트 분석 섹션
            st.markdown("### 📊 비교 차트")
            
            # 첫 번째 행 차트
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 국가별 수출량 비교")
                fig_bar = px.bar(summary_data,
                                 x="국가명", y="수출량",
                                 title=f"{selected_car_type} - {selected_car} 국가별 수출량",
                                 labels={"수출량": "총 수출량", "국가명": "국가명"},
                                 height=400, color="국가명",
                                 color_discrete_sequence=px.colors.qualitative.Vivid)
                fig_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
                st.caption("""
                **해석 방법:**  
                - 선택 국가들의 총 수출량을 직관적으로 비교  
                - 막대 높이로 시장 규모 파악  
                - 상대적 순위와 격차 확인 가능  
                - 주요 시장 식별에 유용
                """)
            
            with col2:
                st.markdown("#### 차량 종류별 수출 분포")
                heatmap_data = df_long[
                    (df_long["국가명"].isin(selected_countries)) &
                    (df_long["날짜"].dt.year == latest_year)
                ].groupby(["국가명", "차량 구분"])["수출량"].sum().reset_index()
                
                if not heatmap_data.empty:
                    fig_heat = px.density_heatmap(heatmap_data,
                                                  x="국가명",
                                                  y="차량 구분",
                                                  z="수출량",
                                                  title=f"국가별 차량 종류별 수출량",
                                                  height=400,
                                                  color_continuous_scale='Viridis')
                    st.plotly_chart(fig_heat, use_container_width=True)
                    st.caption("""
                    **해석 방법:**  
                    - 국가별로 어떤 차량이 많이 수출되는지 시각화  
                    - 진한 색상은 높은 수출량을 의미  
                    - 국가별 선호 차량 패턴 파악 가능  
                    - 제품 포트폴리오 전략 수립에 활용
                    """)
                else:
                    st.warning("히트맵 생성에 필요한 데이터가 없습니다.")
            
            # 두 번째 행 차트
            st.markdown("#### 월별 수출량 추이 비교")
            monthly_data = filtered_data.groupby(['국가명', '월'])['수출량'].mean().reset_index()
            fig_line = px.line(monthly_data,
                               x="월", y="수출량", color="국가명",
                               title=f"{selected_car_type} - {selected_car} 국가별 월별 수출량 추이",
                               labels={"수출량": "평균 수출량", "월": "월"},
                               height=400, color_discrete_sequence=px.colors.qualitative.Plotly)
            st.plotly_chart(fig_line, use_container_width=True)
            st.caption("""
            **해석 방법:**  
            - 국가별 월별 수출 패턴 비교  
            - 계절적 변동성 분석  
            - 추세선을 통해 성장/감소 추세 파악  
            - 특정 시기의 급변동 포인트 확인  
            - 마케팅 캠페인 효과 측정에 활용
            """)

if __name__ == "__main__":
    run_ho()
=======
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import LabelEncoder

# ---------------------------
# 1) 경로 정의
# ---------------------------
RAW_DATA_PATH = r"D:/manifest-mini/hoyeon/기아.csv"  # 실제 파일 경로로 수정 필요

# ---------------------------
# 2) CSS 스타일 적용
# ---------------------------
st.markdown(
    """
    <style>
    /* 전체 배경 및 컨테이너 */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
    }
    /* 상단 헤더 */
    .header {
        background-color: #FFFFFF;
        padding: 2rem;
        border-bottom: 1px solid #ddd;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .header h2 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        color: #4B4B8F;
    }
    /* 섹션 타이틀 */
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        color: #333;
        border-left: 4px solid #6c6cff;
        padding-left: 12px;
    }
    /* 버튼 스타일 */
    .stButton>button {
        background-color: #6c6cff;
        color: white;
        border-radius: 5px;
        padding: 0.75rem 1.5rem;
        border: none;
        font-weight: 600;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background-color: #5a5ae0;
    }
    /* 차트 설명 */
    .chart-description {
        background-color: #F0F0F0;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    /* 입력 필드 스타일 */
    .stSelectbox, .stMultiselect {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# 3) 상단 헤더
# ---------------------------
st.markdown(
    """
    <div class="header">
        <h2>수출량 예측</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# 4) 국가명 영문 <-> 한글 매핑
# ---------------------------
country_kor_map = {
    "US": "미국",
    "Canada": "캐나다",
    "Mexico": "멕시코",
    "EU+EFTA": "유럽연합+EFTA",
    "E.Europe/CIS": "동유럽/CIS",
    "Latin America": "라틴아메리카",
    "Middle East/Africa": "중동/아프리카",
    "Asia / Pacific": "아시아/태평양",
    "China": "중국",
    "India": "인도"
}

def get_english_country(kor_name):
    for eng, kor in country_kor_map.items():
        if kor_name == kor:
            return eng
    return eng

# ---------------------------
# 5) 국가 GDP 데이터 정의
# ---------------------------
country_gdp = {
    "US": 21000,
    "Canada": 1700,
    "Mexico": 1200,
    "EU+EFTA": 30000,
    "E.Europe/CIS": 5000,
    "Latin America": 4000,
    "Middle East/Africa": 2500,
    "Asia / Pacific": 15000,
    "China": 14000,
    "India": 2900
}

def get_climate_for_country(country):
    climate_mapping = {
        "US": "온대",
        "Canada": "한랭",
        "Mexico": "열대",
        "EU+EFTA": "온대",
        "E.Europe/CIS": "한랭",
        "Latin America": "열대",
        "Middle East/Africa": "건조",
        "Asia / Pacific": "열대",
        "China": "온대",
        "India": "열대"
    }
    return climate_mapping.get(country, "Unknown")

# ---------------------------
# 5-1) 국가 연합
# ---------------------------
coalition_members = {
    "EU+EFTA": ["Austria", "Belgium", "Finland", "France", "Germany", "Iceland", "Ireland", "Italy", "Luxembourg", "Netherlands", "Norway", "Portugal", "Spain", "Sweden", "Switzerland"],
    "E.Europe/CIS": ["Russia", "Belarus", "Kazakhstan", "Ukraine", "Armenia", "Azerbaijan", "Uzbekistan"],
    "Latin America": ["Brazil", "Argentina", "Chile", "Colombia", "Mexico", "Peru"],
    "Middle East/Africa": ["South Africa", "Egypt", "Nigeria", "Israel", "UAE"],
    "Asia / Pacific": ["China", "Japan", "South Korea", "India", "Australia", "New Zealand"]
}

# ---------------------------
# 6) 기아.csv에서 차종 필터링
# ---------------------------
def filter_car_model_by_category(car_type_category):
    """차량 구분에 따른 차종 필터링"""
    df = pd.read_csv(RAW_DATA_PATH)
    
    # '차량 구분' 컬럼을 '차종'에 맞게 매핑하여 필터링
    filtered_data = df[df["차량 구분"] == car_type_category]
    
    return sorted(filtered_data["차종"].unique())

country_iso = {
    "US": "USA", "Canada": "CAN", "Mexico": "MEX",
    "EU+EFTA": "FRA", "E.Europe/CIS": "RUS", "Latin America": "BRA",
    "Middle East/Africa": "ZAF", "Asia / Pacific": "CHN",
    "China": "CHN", "India": "IND", "South Africa": "ZAF",
    "Egypt": "EGY", "Nigeria": "NGA", "Israel": "ISR", "UAE": "ARE",
    "Austria": "AUT", "Belgium": "BEL", "Finland": "FIN", "France": "FRA",
    "Germany": "DEU", "Iceland": "ISL", "Ireland": "IRL", "Italy": "ITA",
    "Luxembourg": "LUX", "Netherlands": "NLD", "Norway": "NOR", "Portugal": "PRT",
    "Spain": "ESP", "Sw Sweden": "SWE", "Switzerland": "CHE", "Russia": "RUS",
    "Belarus": "BLR", "Kazakhstan": "KAZ", "Ukraine": "UKR", "Armenia": "ARM",
    "Azerbaijan": "AZE", "Uzbekistan": "UZB", "Brazil": "BRA", "Argentina": "ARG",
    "Chile": "CHL", "Colombia": "COL", "Peru": "PER", "Japan": "JPN",
    "South Korea": "KOR", "Australia": "AUS", "New Zealand": "NZL"
}

# ---------------------------
# 7) 모델 로딩, 예측 함수
# ---------------------------
def load_models():
    model = joblib.load('hoyeon/rf_model.pkl')
    scaler = joblib.load('hoyeon/scaler.pkl')
    le_country = joblib.load('hoyeon/le_country.pkl')
    le_climate = joblib.load('hoyeon/le_climate.pkl')
    le_car_type = joblib.load('hoyeon/le_car_type.pkl')
    le_model = joblib.load('hoyeon/le_model.pkl')
    return model, scaler, le_country, le_climate, le_car_type, le_model

def predict(model, scaler, le_country, le_climate, le_car_type, le_model,
            country, climate, car_type, car_model, year, month, gdp, real_country):
    try:
        # 새로운 값 처리 (차량 구분 및 차종)
        if car_type not in le_car_type.classes_:
            le_car_type.classes_ = np.append(le_car_type.classes_, car_type)
            le_car_type.fit(le_car_type.classes_)  # fit을 다시 시도
        if car_model not in le_model.classes_:
            le_model.classes_ = np.append(le_model.classes_, car_model)
            le_model.fit(le_model.classes_)  # fit을 다시 시도

        # 예측에 사용할 데이터 준비
        row = pd.DataFrame([{
            '국가명': le_country.transform([country])[0],
            '기후대': le_climate.transform([climate])[0],
            '차량 구분': le_car_type.transform([car_type])[0],
            '차종': le_model.transform([car_model])[0],
            '연도': year,
            '월': month,
            'GDP': gdp
        }])

        # 차종_기후대 상호작용 피처 추가
        row['차종_기후대'] = row['차종'] * row['기후대']

        # 예측에 필요한 모든 피처를 포함합니다.
        FEATURES = ['국가명', '기후대', '차량 구분', '차종', '연도', '월', 'GDP', '차종_기후대']

        row_scaled = pd.DataFrame(scaler.transform(row), columns=FEATURES)
        
        # 모델을 사용하여 예측
        pred = model.predict(row_scaled)[0]

        return np.maximum(0, pred), {
            '국가명': real_country,
            '기후대': climate,
            '차량 구분': car_type,
            '차종': car_model,
            '연도': year,
            '월': month,
            'GDP': gdp,
            '예측 수출량': float(round( pred, 2))
        }
    except Exception as e:
        return f"❌ 예측 중 오류 발생: {e}", None

df = pd.read_csv(RAW_DATA_PATH)  
climate_to_countries = df.groupby('기후대')['국가명'].unique().to_dict()
car_type_to_models = df.groupby('차량 구분')['차종'].unique().to_dict()
country_gdp = df.groupby('국가명')['GDP'].mean().to_dict()

def expand_coalition_rows(df_map):
    rows = []
    for idx, row in df_map.iterrows():
        country = row["국가명"]
        if country in coalition_members:
            members = [m.strip() for m in coalition_members[country]]
            export_per_member = row["예측 수출량"] / len(members)
            for member in members:
                new_row = row.copy()
                new_row["국가명"] = member
                new_row["예측 수출량"] = export_per_member
                new_row["인기 차종"] = row["인기 차종"]
                new_row["구성 국가"] = member
                new_row["iso_alpha"] = country_iso.get(member, None)
                rows.append(new_row)
        else:
            rows.append(row)
    return pd.DataFrame(rows)

# ---------------------------
# 8) 메인 앱 함수
# ---------------------------
def run_ho():
    # 세션 상태 변수 초기화
    if 'results_country' not in st.session_state:
        st.session_state.results_country = []
    if 'results_car' not in st.session_state:
        st.session_state.results_car = []
    if 'results_heatmap' not in st.session_state:
        st.session_state.results_heatmap = []
    if 'results_trend' not in st.session_state:
        st.session_state.results_trend = []

    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    
    # 1. 보고 싶은 차트 선택 (selectbox)
    chart_options = [
        "국가별 예측 수출량 비교",
        "차량 구분 vs 기후대별 평균 수출량 히트맵",
    ]
    selected_chart = st.selectbox("보고 싶은 차트를 선택하세요:", chart_options, index=0)

    # ---------------------------
    # 6. 사용 방법 (보고 싶은 차트 선택하세요 밑에 위치)
    # ---------------------------
    st.markdown("<div class='section-title'>사용 방법</div>", unsafe_allow_html=True)
    st.write(
        """
        1. **보고 싶한 차트 선택**: '보고 싶은 차트를 선택하세요:'에서 원하는 차트를 선택합니다.
        2. **차트별 조건 입력 및 예측**: 선택한 차트에 따라 필요한 예측 조건을 입력하고 '예측하기' 버튼을 클릭합니다.
        3. **결과 확인**: '예측 결과' 섹션에서 예측 결과를 확인하고, 선택한 차트 아래에서 시각화된 결과를 확인합니다.
        4. **초기화**: 다른 차트를 선택하기 위해 '초기화' 버튼을 클릭하여 기존 예측 결과를 초기화합니다.
        """
    )

    # ---------------------------
    # 2. 차트별 예측 조건 입력 및 시각화
    # ---------------------------
    if selected_chart == "국가별 예측 수출량 비교":
        st.markdown("<div class='section-title'>국가별 예측 수출량 비교</div>", unsafe_allow_html=True)

        # 국가별 예측을 저장할 리스트
        country_predictions = []

        # 예측 조건 입력
        st.markdown("여러 나라를 선택해 비교해보세요.")
        
        col1, col2 = st.columns(2)
        with col1:
            all_countries = sorted(set(country for countries in climate_to_countries.values() for country in countries))
            display_countries = [country_kor_map.get(c, c) for c in all_countries]
            selected_display_countries = st.multiselect("국가 선택 (한글)", display_countries, key="country_country")
            real_countries = [get_english_country(c) for c in selected_display_countries]
        with col2:
            year = st.selectbox("연도 선택", list(range(2020, 2031)), index=5, key="year_country")  # 기본 2025
            month = st.selectbox("월 선택", list(range(1, 13)), format_func=lambda m: f"{m}월", key="month_country")

        vehicle_types = sorted(df["차량 구분"].unique())
        vehicle_type = st.selectbox("차량 구분", vehicle_types, key="vehicle_country")

        available_models = filter_car_model_by_category(vehicle_type)  # 필터링된 차종
        car_model = st.selectbox("차종", available_models, key="car_country")

        # 예측 실행 및 결과 저장
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("예측하기", key="button_country"):
                st.session_state.results_country = []
                for real_country in real_countries:
                    model, scaler, le_country, le_climate, le_car_type, le_model = load_models()
                    default_gdp = country_gdp.get(real_country, 2000.0)
                    climate = get_climate_for_country(real_country)
                    result, detail = predict(
                        model, scaler, le_country, le_climate, le_car_type, le_model,
                        real_country, climate, vehicle_type, car_model, year, month, default_gdp, real_country
                    )
                    if isinstance(result, str):
                        st.error(result)
                    else:
                        st.session_state.results_country.append(detail)
                        country_predictions.append({
                            "국가명": real_country,
                            "예측 수출량": result
                        })
                        st.success(f"{real_country} 예측 수출량: {result:,.2f} 대")
        with col2:
            if st.button("초기화", key="reset_country"):
                st.session_state.results_country = []

        # 그래프 및 지도 표시
        if st.session_state.results_country:
            df_result = pd.DataFrame(st.session_state.results_country)

            # 3-1. 국가별 예측 수출량 지도
            st.markdown("<div class='section-title'>예측 수출량 지도</div>", unsafe_allow_html=True)

            # 국가별 집계
            df_map = df_result.groupby("국가명")["예측 수출량"].sum().reset_index()
            pop_df = df_result.groupby(["국가명", "차종"])["예측 수출량"].sum().reset_index()
            pop_df = pop_df.loc[pop_df.groupby("국가명")["예측 수출량"].idxmax()]
            df_map = pd.merge(df_map, pop_df[["국가명", "차종"]], on="국가명", how="left")
            df_map.rename(columns={"차종": "인기 차종"}, inplace=True)
            df_map["구성 국가"] = df_map["국가명"].apply(lambda x: coalition_members.get(x, x))
            df_map["iso_alpha"] = df_map["국가명"].map(country_iso)

            # 구간화
            bins = [0, 100, 500, 1000, 5000, 10000]
            labels = ["~100", "100~500", "500~1천", "1천~5천", "5천~1만"]
            df_map["구간"] = pd.cut(df_map["예측 수출량"], bins=bins, labels=labels, right=False)

            # 확장 (연합)
            df_map_expanded = expand_coalition_rows(df_map)

            fig_map = px.choropleth(
                df_map_expanded,
                locations="iso_alpha",
                color="구간",
                hover_name="국가명",
                hover_data=["예측 수출량", "인기 차종", "구성 국가"],
                color_discrete_sequence=px.colors.qualitative.Set1,
                title="국가별 예측 수출량 (구간별)",
                projection="natural earth",
                template="plotly_white"
            )
            fig_map.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))
            fig_map.update_geos(showframe=False, showcoastlines=True, coastlinecolor="LightGray")
            st.plotly_chart(fig_map, use_container_width=True)

            # 차트 설명
            st.markdown(
                """
                <div class='chart-description'>
                    <h4>차트 보는 방법</h4>
                    <p>이 지도는 국가별 예측 수출량을 구간별로 시각화한 것입니다. 색상이 진할수록 수출량이 높습니다.</p>
                    <h4>차트를 보면 얻을 수 있는 장점</h4>
                    <p>특정 국가의 수출량을 쉽게 파악할 수 있으며, 전 세계적으로 어느 지역에서 더 많이 팔리는지 알 수 있습니다.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # 3-2. 국가별 수출량 비교 (막대 그래프)
            st.markdown("<div class='section-title'>국가별 예측 수출량 비교</div>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                country_export = df_result.groupby("국가명")["예측 수출량"].sum().reset_index()
                color_map = {country: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)] for i, country in enumerate(country_export["국가명"].unique())}
                country_export["색상"] = country_export["국가명"].map(color_map)

                fig_country = px.bar(
                    country_export,
                    x="국가명",
                    y="예측 수출량",
                    color="국가명",
                    color_discrete_map=color_map,
                    title="국가별 예측 수출량 비교 (막대 그래프)",
                    range_y=[0, 5000]  # y축 범위 조정
                )
                st.plotly_chart(fig_country, use_container_width=True)

                # 차트 설명
                st.markdown(
                    """
                    <div class='chart-description'>
                        <h4>차트 보는 방법</h4>
                        <p>이 막대 그래프는 국가별 예측 수출량을 비교한 것입니다. 각 막대는 국가를 나타내며, 높이가 수출량을 의미합니다.</p>
                        <h4>차트를 보면 얻을 수 있는 장점</h4>
                        <p>특정 국가의 수출량을 쉽게 비교할 수 있으며, 어느 국가가 더 많이 팔리는지 한눈에 파악할 수 있습니다.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col2:
                fig_pie = px.pie(
                    country_export,
                    names="국가명",
                    values="예측 수출량",
                    title="국가별 예측 수출량 비율 (파이 차트)",
                    color="국가명",
                    color_discrete_map=color_map
                )
                st.plotly_chart(fig_pie, use_container_width=True)

                # 차트 설명
                st.markdown(
                    """
                    <div class='chart-description'>
                        <h4>차트 보는 방법</h4>
                        <p>이 파이 차트는 국가별 예측 수출량의 비율을 시각화한 것입니다. 각 조각은 국가를 나타내며, 크기는 수출량 비율을 의미합니다.</p>
                        <h4>차트를 보면 얻을 수 있는 장점</h4>
                        <p>전체 수출량 중 특정 국가의 비중을 쉽게 파악할 수 있습니다.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # 3-3. 예측 결과 데이터프레임으로 표시
            st.markdown("<div class='section-title'>예측 결과</div>", unsafe_allow_html=True)
            st.dataframe(df_result)

        else:
            st.info("예측 결과가 없습니다. '예측하기' 버튼을 눌러 예측을 실행해주세요.")

    elif selected_chart == "차량 구분 vs 기후대별 평균 수출량 히트맵":
        st.markdown("<div class='section-title'>차량 구분 vs 기후대별 평균 수출량 히트맵</div>", unsafe_allow_html=True)

        # 사용자 입력 칸
        col1, col2 = st.columns(2)
        with col1:
            selected_climates = st.multiselect("기후대 선택 (복수 선택 가능)", sorted(climate_to_countries.keys()), key="climate_heatmap")
        with col2:
            vehicle_types = sorted(df["차량 구분"].unique())
            selected_vehicle_types = st.multiselect("차량 구분 선택 (복수 선택 가능)", vehicle_types, key="vehicle_heatmap")

        # 나라 선택 및 기후대 표시
        all_countries = sorted(set(country for countries in climate_to_countries.values() for country in countries))
        display_countries = [country_kor_map.get(c, c) for c in all_countries]
        selected_display_countries = st.multiselect("나라 선택 (복수 선택 가능)", display_countries, key="country_heatmap")
        real_countries = [get_english_country(c) for c in selected_display_countries]

        # 선택한 나라의 기후대 표시
        if selected_display_countries:
            st.markdown("<div class='section-title'>선택한 나라의 기후대</div>", unsafe_allow_html=True)
            country_climate_info = []
            for country in real_countries:
                climate = get_climate_for_country(country)
                country_climate_info.append(f"{country_kor_map.get(country, country)}: {climate}")
            st.write(", ".join(country_climate_info))

        # 차종 중복 선택
        selected_car_models = []
        if selected_vehicle_types:
            for vehicle_type in selected_vehicle_types:
                available_models = filter_car_model_by_category(vehicle_type)
                selected_car_models.extend(st.multiselect(f"{vehicle_type} 차종 선택", available_models, key=f"car_models_{vehicle_type}"))

        # 연도 및 월 선택 (예측하기 바로 위로 이동)
        col3, col4 = st.columns(2)
        with col3:
            year = st.selectbox("연도 선택", list(range(2020, 2031)), index=5, key="year_heatmap")  # 기본 2025
        with col4:
            month = st.selectbox("월 선택", list(range(1, 13)), format_func=lambda m: f"{m}월", key="month_heatmap")

        # 예측 실행 및 결과 저장
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("예측하기", key="button_heatmap"):
                st.session_state.results_heatmap = []  # 결과 초기화
                model, scaler, le_country, le_climate, le_car_type, le_model = load_models()

                for climate in selected_climates:
                    for vehicle_type in selected_vehicle_types:
                        for car_model in selected_car_models:
                            for real_country in real_countries:  # 선택한 나라별로 예측 실행
                                default_gdp = country_gdp.get(real_country, 2000.0)
                                result, detail = predict(
                                    model, scaler, le_country, le_climate, le_car_type, le_model,
                                    real_country, climate, vehicle_type, car_model, year, month, default_gdp, real_country
                                )
                                if isinstance(result, str):
                                    st.error(result)
                                else:
                                    st.session_state.results_heatmap.append(detail)
        with col2:
            if st.button("초기화", key="reset_heatmap"):
                st.session_state.results_heatmap = []

        if st.session_state.results_heatmap:
            df_result = pd.DataFrame(st.session_state.results_heatmap)
            # 차종과 차량 구분을 함께 표시하기 위해 새로운 컬럼 추가
            df_result["차종_차량구분"] = df_result["차종"] + " (" + df_result["차량 구분"] + ")"

            # 1. 차종 vs 기후대 히트맵 (Viridis 색상 팔레트)
            heatmap_data_climate = df_result.groupby(["차종_차량구분", "기후대"])["예측 수출량"].mean().unstack()
            fig_heatmap_climate = px.imshow(
                heatmap_data_climate,
                labels=dict(x="기후대", y="차종 (차량 구분)", color="평균 수출량"),
                color_continuous_scale="viridis",
                title="<b>차종별 기후대 적합성 분석</b><br><sub>차량 유형별로 다른 기후대에서의 예상 판매량</sub>",
                aspect="auto"
            )
            fig_heatmap_climate.update_layout(
                height=600,
                width=900,
                xaxis=dict(title="기후대", tickangle=45, tickfont=dict(size=12)),
                yaxis=dict(title="차종 (차량 구분)", tickfont=dict(size=10)),
                font=dict(family="Arial", size=12, color="#333"),
                margin=dict(l=100, r=50, b=100, t=100),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                coloraxis_colorbar=dict(
                    title="수출량(대)",
                    thickness=20,
                    len=0.75,
                    yanchor="middle",
                    y=0.5
                )
            )
            # 값 주석 추가
            fig_heatmap_climate.update_traces(
                text=np.round(heatmap_data_climate.values, 1),
                texttemplate="%{text}",
                hovertemplate="<b>차종</b>: %{y}<br><b>기후대</b>: %{x}<br><b>수출량</b>: %{z:.1f}대<extra></extra>"
            )

            # 2. 차종 vs 국가 히트맵 (Plasma 색상 팔레트)
            heatmap_data_country = df_result.groupby(["차종_차량구분", "국가명"])["예측 수출량"].mean().unstack()
            fig_heatmap_country = px.imshow(
                heatmap_data_country,
                labels=dict(x="국가", y="차종 (차량 구분)", color="평균 수출량"),
                color_continuous_scale="plasma",
                title="<b>국가별 차종 선호도 분석</b><br><sub>각 국가에서 가장 잘 팔릴 것으로 예상되는 차량 유형</sub>",
                aspect="auto"
            )
            fig_heatmap_country.update_layout(
                height=600,
                width=900,
                xaxis=dict(title="국가", tickangle=45, tickfont=dict(size=10)),
                yaxis=dict(title="차종 (차량 구분)", tickfont=dict(size=10)),
                font=dict(family="Arial", size=12, color="#333"),
                margin=dict(l=100, r=50, b=150, t=100),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                coloraxis_colorbar=dict(
                    title="수출량(대)",
                    thickness=20,
                    len=0.75,
                    yanchor="middle",
                    y=0.5
                )
            )
            # 값 주석 추가
            fig_heatmap_country.update_traces(
                text=np.round(heatmap_data_country.values, 1),
                texttemplate="%{text}",
                hovertemplate="<b>차종</b>: %{y}<br><b>국가</b>: %{x}<br><b>수출량</b>: %{z:.1f}대<extra></extra>"
            )

            # 3. 탭으로 구분하여 표시
            tab1, tab2 = st.tabs(["기후대별 분석", "국가별 분석"])
            with tab1:
                st.plotly_chart(fig_heatmap_climate, use_container_width=True)
                st.markdown("""
                <div style="background-color:#f8f9fa;padding:15px;border-radius:10px;margin-top:20px;">
                    <h4 style="color:#2c3e50;">📊 분석 가이드</h4>
                    <ul style="color:#34495e;">
                        <li>열대 기후에서는 소형차와 SUV의 수요가 높은 경향</li>
                        <li>한랭 기후에서는 4WD와 대형차의 선호도가 두드러짐</li>
                        <li>건조 기후 지역에서는 내구성이 뛰어난 모델이 인기</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with tab2:
                st.plotly_chart(fig_heatmap_country, use_container_width=True)
                st.markdown("""
                <div style="background-color:#f8f9fa;padding:15px;border-radius:10px;margin-top:20px;">
                    <h4 style="color:#2c3e50;">🌍 지역별 인기 차종</h4>
                    <ul style="color:#34495e;">
                        <li>유럽 국가: 디젤 엔진과 친환경 차량 선호</li>
                        <li>아시아/태평양: 소형차와 하이브리드 모델 수요 높음</li>
                        <li>북미 지역: 대형 SUV와 픽업트럭 시장이 활발</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            # 차트 설명
            st.markdown(
                """
                <div class='chart-description'>
                    <h4>📌 차트 활용 팁</h4>
                    <p>1. <b>색상 강도</b>: 진한 색상일수록 해당 조합에서의 예상 수출량이 높음을 의미</p>
                    <p>2. <b>상호작용 분석</b>: 특정 차종이 특정 국가/기후대에서 두드러지게 잘 팔리는 패턴 발견 가능</p>
                    <p>3. <b>전략 수립</b>: 이 분석을 통해 특정 지역에 맞는 마케팅 전략과 차량 라인업 최적화 가능</p>
                    
                    <h4 style='margin-top:20px;'>🔍 색상 범례 해석</h4>
                    <div style='display:flex; gap:15px; margin-top:10px;'>
                        <div style='width:20px;height:20px;background-color:#440154;'></div>
                        <span>낮은 수출량 (0~20%)</span>
                    </div>
                    <div style='display:flex; gap:15px; margin-top:5px;'>
                        <div style='width:20px;height:20px;background-color:#21918c;'></div>
                        <span>중간 수출량 (40~60%)</span>
                    </div>
                    <div style='display:flex; gap:15px; margin-top:5px;'>
                        <div style='width:20px;height:20px;background-color:#fde725;'></div>
                        <span>높은 수출량 (80~100%)</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


run_ho()
>>>>>>> Stashed changes
