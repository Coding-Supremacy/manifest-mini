import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from PIL import Image
import yfinance as yf
import matplotlib.colors as mcolors

st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
        padding: 2rem;
    }
    .tab-button-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
        gap: 1rem;
    }
    .tab-button {
        padding: 1rem 2rem;
        border-radius: 8px;
        border: none;
        background-color: #e9ecef;
        transition: all 0.3s ease;
        cursor: pointer;
        font-weight: normal;
        text-align: center;
        width: 100%;
        font-size: 1rem;
    }
    .tab-button:hover {
        background-color: #dee2e6;
    }
    .tab-button.active {
        background-color: #4a6fa5;
        color: white;
        font-weight: bold;
    }
    .highlight-box {
        background-color: #f0f7ff;
        border: 2px solid #2a3f5f;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    .metric-container {
        border-radius: 10px;
        padding: 1.5rem;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .metric-title {
        font-size: 1rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2a3f5f;
    }
    .metric-change {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 0.5rem;
    }
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }
    .neutral {
        color: #ffc107;
    }
    .chart-guide {
        background-color: #f5f5f5;
        padding: 1.2rem;
        border-radius: 10px;
        margin-top: 1rem;
        font-size: 0.9rem;
        color: #333;
        line-height: 1.6;
        border-left: 4px solid #6c757d;
    }
    .country-info-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .summary-box {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
    }
    .summary-item {
        background-color: white;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .map-info-container {
        display: flex;
        gap: 2rem;
        margin-bottom: 2rem;
    }
    .map-container {
        flex: 1;
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .info-container {
        flex: 1;
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .reason-box-positive {
        background-color: #e6f7e6;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #28a745;
    }
    .reason-box-negative {
        background-color: #fce8e8;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #dc3545;
    }
    .reason-box-neutral {
        background-color: #fff8e1;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #ffc107;
    }
    .key-metrics-box {
        background-color: #f0f7ff;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4a6fa5;
    }
    .chart-columns {
        display: flex;
        gap: 2rem;
        margin-bottom: 2rem;
    }
    .chart-column {
        flex: 1;
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #4a6fa5;
        color: white;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background-color: #3a5f95;
        color: white;
    }
    .section-title {
        font-size: 1.5rem;
        color: #2a3f5f;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e6e6e6;
    }
    .feature-description {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid #4a6fa5;
    }
    .flag-img {
        width: 40px;
        height: 25px;
        object-fit: cover;
        border: 1px solid #ddd;
        margin-right: 10px;
    }
    .country-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def reset_form():
    st.session_state.clear()

def get_country_flag(country_name):
    """국가명으로 국기 이미지 URL 가져오기"""
    flag_mapping = {
        '미국': 'https://flagcdn.com/w320/us.png',
        '중국': 'https://flagcdn.com/w320/cn.png',
        '일본': 'https://flagcdn.com/w320/jp.png',
        '독일': 'https://flagcdn.com/w320/de.png',
        '영국': 'https://flagcdn.com/w320/gb.png',
        '프랑스': 'https://flagcdn.com/w320/fr.png',
        '한국': 'https://flagcdn.com/w320/kr.png',
        '인도': 'https://flagcdn.com/w320/in.png',
        '브라질': 'https://flagcdn.com/w320/br.png',
        '캐나다': 'https://flagcdn.com/w320/ca.png',
        '호주': 'https://flagcdn.com/w320/au.png',
        '이탈리아': 'https://flagcdn.com/w320/it.png',
        '스페인': 'https://flagcdn.com/w320/es.png',
        '멕시코': 'https://flagcdn.com/w320/mx.png',
        '인도네시아': 'https://flagcdn.com/w320/id.png',
        '터키': 'https://flagcdn.com/w320/tr.png',
        '네덜란드': 'https://flagcdn.com/w320/nl.png',
        '스위스': 'https://flagcdn.com/w320/ch.png',
        '사우디아라비아': 'https://flagcdn.com/w320/sa.png',
        '아르헨티나': 'https://flagcdn.com/w320/ar.png'
    }
    return flag_mapping.get(country_name, None)

def fetch_country_info(country_name):
    """국가 정보 가져오기 (수정된 버전)"""
    country_unions = {
        '미국': '북미자유무역협정(NAFTA), G7, G20',
        '중국': 'G20, BRICS, 상하이협력기구',
        '일본': 'G7, G20, 아시아태평양경제협력체(APEC)',
        '독일': '유럽연합(EU), G7, G20',
        '영국': 'G7, G20, 유럽연합(탈퇴)',
        '프랑스': '유럽연합(EU), G7, G20',
        '한국': 'G20, 아시아태평양경제협력체(APEC)',
        '인도': 'G20, BRICS, 상하이협력기구',
        '브라질': 'G20, BRICS, 남미국가연합',
        '캐나다': '북미자유무역협정(NAFTA), G7, G20',
        '호주': 'G20, 아시아태평양경제협력체(APEC)',
        '이탈리아': '유럽연합(EU), G7, G20',
        '스페인': '유럽연합(EU), G20',
        '멕시코': '북미자유무역협정(NAFTA), G20',
        '인도네시아': 'G20, 아세안(ASEAN)',
        '터키': 'G20',
        '네덜란드': '유럽연합(EU)',
        '스위스': '유럽자유무역연합(EFTA)',
        '사우디아라비아': 'G20, OPEC',
        '아르헨티나': 'G20, 남미국가연합'
    }
    
    return {
        'union': country_unions.get(country_name, '정보 없음'),
        'flag': get_country_flag(country_name)
    }

def fetch_gdp_data(country_name):
    """World Bank API에서 GDP 데이터 가져오기"""
    country_code_map = {
        '미국': 'USA',
        '중국': 'CHN',
        '일본': 'JPN',
        '독일': 'DEU',
        '영국': 'GBR',
        '프랑스': 'FRA',
        '한국': 'KOR',
        '인도': 'IND',
        '브라질': 'BRA',
        '캐나다': 'CAN',
        '호주': 'AUS',
        '이탈리아': 'ITA',
        '스페인': 'ESP',
        '멕시코': 'MEX',
        '인도네시아': 'IDN',
        '터키': 'TUR',
        '네덜란드': 'NLD',
        '스위스': 'CHE',
        '사우디아라비아': 'SAU',
        '아르헨티나': 'ARG'
    }
    
    country_code = country_code_map.get(country_name, None)
    if country_code:
        try:
            url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.MKTP.CD?format=json&date=2022"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and data[1]:
                    return data[1][0]['value'] / 1e9  # 10억 달러 단위
        except:
            pass
    return None

def get_change_reason(change_rate):
    """변화율에 따른 원인 분석 반환 (더 세분화된 분석)"""
    if change_rate > 30:
        return {
            "text": "📈 급격한 증가 (30% 초과)",
            "reason": [
                "✅ 신규 시장 진출 성공: 현지 딜러 네트워크 확장 및 마케팅 효과",
                "✅ 경쟁사 제품 리콜: 경쟁사의 주요 모델 문제로 인한 수요 전환",
                "✅ 현지 통화 강세: 수입차 구매력 증가",
                "✅ 정부 인센티브: 전기차 보조금 확대 등 정책 지원 효과",
                "✅ 신제품 출시: 현지 시장 맞춤형 신모델 인기"
            ],
            "suggestion": [
                "📌 생산량 확대를 고려하세요",
                "📌 현지 서비스 네트워크 강화 필요",
                "📌 가격 인상 가능성 검토"
            ],
            "color": "#2e7d32",
            "box_class": "reason-box-positive"
        }
    elif 15 < change_rate <= 30:
        return {
            "text": "📈 강한 증가 (15%~30%)",
            "reason": [
                "✅ 현지 경제 호황: 소비자 구매력 증가",
                "✅ 브랜드 인지도 상승: 광고 및 마케팅 효과",
                "✅ 모델 라인업 강화: 현지 취향에 맞는 차종 추가",
                "✅ 환율 영향: 현지 통화 대비 원화 약세",
                "✅ 계절적 수요 증가: 휴가철 또는 세금 환급 시기"
            ],
            "suggestion": [
                "📌 재고 관리 강화",
                "📌 지속적인 마케팅 투자 유지",
                "📌 고객 만족도 조사 실시"
            ],
            "color": "#4caf50",
            "box_class": "reason-box-positive"
        }
    elif 5 < change_rate <= 15:
        return {
            "text": "📈 안정적 증가 (5%~15%)",
            "reason": [
                "✅ 꾸준한 마케팅 효과: 브랜드 충성도 형성",
                "✅ 소폭의 가격 경쟁력 향상",
                "✅ 경쟁사 대비 품질 인식 개선",
                "✅ 소비자 신뢰도 점진적 상승",
                "✅ 부분 모델 변경 효과"
            ],
            "suggestion": [
                "📌 현재 전략 유지",
                "📌 고객 피드백 수집 강화",
                "📌 경쟁사 동향 모니터링"
            ],
            "color": "#8bc34a",
            "box_class": "reason-box-positive"
        }
    elif -5 <= change_rate <= 5:
        return {
            "text": "➡️ 안정 유지 (-5%~5%)",
            "reason": [
                "⚖️ 시장 상황 유지: 특별한 변동 요인 없음",
                "⚖️ 경쟁사와 유사한 성과",
                "⚖️ 계절적 영향이 없는 시기",
                "⚖️ 경제 상황 중립적",
                "⚖️ 마케팅 활동 효과 중립적"
            ],
            "suggestion": [
                "📌 시장 변화 모니터링",
                "📌 고객 설문조사를 통한 만족도 점검",
                "📌 마케팅 전략 재검토"
            ],
            "color": "#ffc107",
            "box_class": "reason-box-neutral"
        }
    elif -15 <= change_rate < -5:
        return {
            "text": "📉 감소 추세 (-15%~-5%)",
            "reason": [
                "⚠️ 현지 경제 불황: 소비자 구매력 감소",
                "⚠️ 경쟁사 제품 강세: 신기술 적용 또는 가격 인하",
                "⚠️ 환율 영향: 현지 통화 대비 원화 강세",
                "⚠️ 부분 모델 노후화",
                "⚠️ 계절적 수요 감소"
            ],
            "suggestion": [
                "📌 프로모션 강화 검토",
                "📌 가격 경쟁력 분석 필요",
                "📌 모델 업데이트 계획 수립"
            ],
            "color": "#ff9800",
            "box_class": "reason-box-neutral"
        }
    elif -30 <= change_rate < -15:
        return {
            "text": "📉 급격한 감소 (-30%~-15%)",
            "reason": [
                "❌ 현지 규제 강화: 배출가스 기준 강화 또는 수입 제한",
                "❌ 정치적 불안정: 수입 장벽 증가 또는 반한 감정",
                "❌ 주요 딜러 파산: 판매 채널 축소",
                "❌ 경쟁사 대폭 할인 공세",
                "❌ 제품 품질 이슈 발생"
            ],
            "suggestion": [
                "📌 현지 사정 긴급 점검",
                "📌 위기 대응 팀 구성",
                "📌 긴급 마케팅 전략 수립",
                "📌 본사 지원 필요"
            ],
            "color": "#f44336",
            "box_class": "reason-box-negative"
        }
    else:
        return {
            "text": "📉 위험한 감소 (-30% 미만)",
            "reason": [
                "🆘 현지 법인/딜러 운영 위기",
                "🆘 주요 모델 판매 중단",
                "🆘 경제 위기 또는 전쟁 등 특별한 사정",
                "🆘 경쟁사 시장 점유율 급증",
                "🆘 브랜드 이미지 심각한 손상"
            ],
            "suggestion": [
                "📌 긴급 대책 회의 소집",
                "📌 현지 실사 파견",
                "📌 본사 차원의 구조 조정 검토",
                "📌 시장 철수 가능성 검토"
            ],
            "color": "#b71c1c",
            "box_class": "reason-box-negative"
        }

def create_tab_buttons():
    """탭 버튼 생성 함수"""
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
    """GDP 대비 수출량 분석을 위한 버블차트 생성 함수"""
    latest_year = df['날짜'].dt.year.max()
    data = df[df['날짜'].dt.year == latest_year].groupby('국가명')['수출량'].sum().reset_index()
    data['GDP'] = data['국가명'].apply(lambda x: fetch_gdp_data(x) or 0)
    # 버블 차트: 수출량을 버블 크기로 표시
    fig = px.scatter(data, x='GDP', y='수출량', size='수출량', color='국가명', 
                     title="GDP 대비 수출량 분석 (버블 차트)",
                     labels={'GDP': 'GDP (10억$)', '수출량': '총 수출량'},
                     size_max=60)
    return fig

def run_ho():
    # 모델 및 데이터 로드
    model = joblib.load("hoyeon/lgbm_tuned_model.pkl")
    scaler = joblib.load("hoyeon/scaler.pkl")
    model_columns = joblib.load("hoyeon/model_columns.pkl")  
    df = pd.read_csv("hoyeon/기아.csv")
    
    # 대시보드 제목 (st.title로 단순하게 표시)
    st.title("기아 자동차 수출량 분석 대시보드")
    
    # 데이터 전처리
    id_vars = ['국가명', '연도', '기후대', 'GDP', '차종 구분', '차량 구분']
    month_cols = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
    df_long = pd.melt(df, id_vars=id_vars, value_vars=month_cols, var_name='월', value_name='수출량')
    df_long['월'] = df_long['월'].str.replace('월', '').astype(int)
    df_long['날짜'] = pd.to_datetime(df_long['연도'].astype(str) + '-' + df_long['월'].astype(str) + '-01')
    df_long = df_long.sort_values(by=['국가명', '날짜'])
    
    # 최신 연도 데이터
    latest_year = df_long["날짜"].dt.year.max()
    
    # 탭 버튼 생성
    current_tab = create_tab_buttons()
    
    # 세션 상태 관리
    if 'prediction_made' not in st.session_state:
        st.session_state.prediction_made = False
    if 'comparison_made' not in st.session_state:
        st.session_state.comparison_made = False
    
    if current_tab == "📊 단일 국가 예측":
        st.header("📊 단일 국가 수출량 예측")
        
        # 기능 설명 추가
        with st.container():
            st.markdown("""
            <div class="feature-description">
                <h4>📌 단일 국가 예측 기능 사용 방법</h4>
                <p>이 기능은 특정 국가의 특정 차종에 대한 수출량을 예측합니다. 다음과 같은 경우에 유용합니다:</p>
                <ul>
                    <li>특정 국가의 수출 전략 수립 전 예측이 필요할 때</li>
                    <li>특정 차종의 수요 예측이 필요할 때</li>
                    <li>전년 대비 성장률 분석이 필요할 때</li>
                    <li>새로운 유입 국가 추가시 수출모델 예측이 필요할 때</li>
                </ul>
                <p><b>사용 방법:</b> 왼쪽에서 국가, 차종, 예측 연도/월을 선택한 후 "예측 실행" 버튼을 클릭하세요.</p>
                <p><b>결과 해석:</b> 예측 결과는 차트와 수치로 표시되며, 전년 대비 변화율과 원인 분석도 제공합니다.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("🔍 분석 조건 설정", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_climate = st.selectbox("🌍 기후대", sorted(df["기후대"].unique()), key='climate_select')
                filtered_countries = sorted(df[df["기후대"] == selected_climate]["국가명"].unique())
                selected_country = st.selectbox("🏳️ 국가명", filtered_countries, key='country_select')
                
                # 예측 연도 입력
                target_year = st.number_input("📅 예측 연도", 
                                           min_value=2000, 
                                           max_value=datetime.now().year+5, 
                                           value=datetime.now().year,
                                           key='year_select')
                
                # 예측 월 입력
                target_month = st.number_input("📆 예측 월", 
                                            min_value=1, 
                                            max_value=12, 
                                            value=datetime.now().month,
                                            key='month_select')
                
            with col2:
                selected_car_type = st.selectbox("🚘 차종 구분", sorted(df["차종 구분"].unique()), key='car_type_select')
                
                if "차종" in df.columns:
                    filtered_car_options = sorted(df[df["차종 구분"] == selected_car_type]["차종"].unique())
                else:
                    filtered_car_options = sorted(df[df["차종 구분"] == selected_car_type]["차량 구분"].unique())
                selected_car = st.selectbox("🚗 차량 구분", filtered_car_options, key='car_select')
        
        # 버튼 영역
        col1, col2 = st.columns([4,1])
        with col1:
            predict_btn = st.button("🔮 예측 실행", type="primary", use_container_width=True)
        with col2:
            reset_btn = st.button("🔄 초기화", on_click=reset_form, use_container_width=True)
        
        if predict_btn:
            st.session_state.prediction_made = True
        
        if st.session_state.prediction_made or ('prediction_result' in st.session_state and not reset_btn):
            # 국가 데이터 추출
            country_data = df_long[
                (df_long["국가명"] == selected_country) |
                ((df_long["차종 구분"] == selected_car_type) & (df_long["차량 구분"] == selected_car))
            ].sort_values(by="날짜", ascending=False)
            
            if country_data.empty:
                st.warning("⚠️ 선택한 조건에 맞는 데이터가 없습니다. 다른 조건을 선택해주세요.")
                st.session_state.prediction_made = False
                return
            
            if predict_btn or 'prediction_result' in st.session_state:
                if predict_btn:
                    # 데이터 준비
                    auto_current_export = country_data["수출량"].iloc[0] if not country_data.empty else 0
                    auto_prev_export = country_data["수출량"].iloc[1] if len(country_data) >= 2 else 0.0
                    
                    # 전년 동월 데이터 찾기
                    prev_year_data = df_long[
                        (df_long["국가명"] == selected_country) |
                        ((df_long["차종 구분"] == selected_car_type) & (df_long["차량 구분"] == selected_car)) &
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
                    
                    # 인코딩 및 스케일링
                    input_encoded = pd.get_dummies(input_df, columns=["국가명", "기후대", "차종 구분", "차량 구분"])
                    input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)
                    input_scaled = scaler.transform(input_encoded)
                    
                    # 예측 실행
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
                
                yearly_change = ((prediction - prev_year_export) / prev_year_export * 100) if prev_year_export != 0 else 0
                gdp_value = fetch_gdp_data(selected_country) or df[df["국가명"] == selected_country]["GDP"].iloc[0]
                country_info = fetch_country_info(selected_country)
                
                # 상단 3열 레이아웃
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### 🌦️ 기후대별 차량 수출량 분석")
                    with st.container():
                        climate_data = df_long[
                            ((df_long["차종 구분"] == selected_car_type) | (df_long["차량 구분"] == selected_car)) &
                            (df_long["날짜"].dt.year == target_year-1)
                        ].groupby("기후대")["수출량"].sum().reset_index()
                        
                        if not climate_data.empty:
                            fig_climate = px.bar(
                                climate_data,
                                x="기후대",
                                y="수출량",
                                title=f"{selected_car_type} - {selected_car} 기후대별 총 수출량 ({target_year-1}년)",
                                labels={"수출량": "총 수출량", "기후대": "기후대"},
                                height=500,
                                color="기후대",
                                color_discrete_sequence=px.colors.qualitative.Pastel
                            )
                            fig_climate.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                xaxis=dict(gridcolor='lightgray'),
                                yaxis=dict(gridcolor='lightgray'),
                                showlegend=False,
                                margin=dict(l=20, r=20, t=40, b=20)
                            )
                            st.plotly_chart(fig_climate, use_container_width=True)
                        else:
                            st.warning(f"{target_year-1}년도 {selected_car_type} - {selected_car} 모델의 기후대별 데이터가 없습니다.")
                    
                    st.markdown("### 💰 GDP 대비 수출량 (버블 차트)")
                    bubble_fig = create_gdp_export_scatter(df_long, selected_country)
                    st.plotly_chart(bubble_fig, use_container_width=True)
                
                with col2:
                    with st.container():
                        st.markdown(f"""
                        <div style="background-color:{'#e6f7e6' if yearly_change >=5 else ('#fce8e8' if yearly_change <=-5 else '#fff8e1')}; 
                                    border-radius:12px; padding:1.5rem; margin-bottom:1.5rem; 
                                    border-left: 4px solid {'#28a745' if yearly_change >=5 else ('#dc3545' if yearly_change <=-5 else '#ffc107')};">
                            <div style="font-size:1.2rem; font-weight:bold; color:#2a3f5f; margin-bottom:1rem;">
                                {selected_country} {target_year}년 {target_month}월 예측 수출량
                            </div>
                            <div style="font-size:2.5rem; font-weight:bold; text-align:center; margin:1rem 0; color:#2a3f5f;">
                                {prediction:,.2f}
                            </div>
                            <div style="font-size:1.1rem; text-align:center; margin-bottom:1rem;">
                                전년 동월 대비 <span class="{ 'positive' if yearly_change >= 5 else ('negative' if yearly_change <= -5 else 'neutral') }" style="font-weight:bold;">{abs(yearly_change):.2f}% {"증가" if yearly_change >= 5 else ("감소" if yearly_change <= -5 else "유지")}</span> {"📈" if yearly_change >= 5 else ("📉" if yearly_change <= -5 else "➡️")}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("""
                        <div class="key-metrics-box">
                            <div style="font-size:1.1rem; font-weight:bold; color:#2a3f5f; margin-bottom:1rem;">
                                주요 지표
                            </div>
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
                                <div>
                                    <div style="color:#666; font-size:0.9rem;">차종/차량</div>
                                    <div style="font-weight:bold; font-size:1rem;">{} - {}</div>
                                </div>
                                <div>
                                    <div style="color:#666; font-size:0.9rem;">기후대</div>
                                    <div style="font-weight:bold; font-size:1rem;">{}</div>
                                </div>
                                <div>
                                    <div style="color:#666; font-size:0.9rem;">국가 GDP</div>
                                    <div style="font-weight:bold; font-size:1rem;">{:,.2f} (10억 달러)</div>
                                </div>
                                <div>
                                    <div style="color:#666; font-size:0.9rem;">전월 수출량</div>
                                    <div style="font-weight:bold; font-size:1rem;">{:,.2f}</div>
                                </div>
                                <div>
                                    <div style="color:#666; font-size:0.9rem;">전년 동월 수출량</div>
                                    <div style="font-weight:bold; font-size:1rem;">{:,.2f}</div>
                                </div>
                                <div>
                                    <div style="color:#666; font-size:0.9rem;">최근 수출량</div>
                                    <div style="font-weight:bold; font-size:1rem;">{:,.2f}</div>
                                </div>
                            </div>
                        </div>
                        """.format(
                            selected_car_type, selected_car, 
                            selected_climate, 
                            gdp_value, 
                            auto_prev_export,
                            prev_year_export,
                            auto_current_export
                        ), unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class="{ get_change_reason(yearly_change)['box_class'] }">
                            <div style="font-size:1.1rem; font-weight:bold; color:#2a3f5f; margin-bottom:1rem;">
                                📌 변화 원인 분석 ({ get_change_reason(yearly_change)['text'] })
                            </div>
                            <div style="font-size:0.95rem; margin-bottom:1rem;">
                                <b>주요 원인:</b><br>
                                {''.join([f'• {reason}<br>' for reason in get_change_reason(yearly_change)['reason']])}
                            </div>
                            <div style="font-size:0.95rem;">
                                <b>제안 사항:</b><br>
                                {''.join([f'• {suggestion}<br>' for suggestion in get_change_reason(yearly_change)['suggestion']])}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    with st.container():
                        st.markdown("### 🚗 차량 종류별 수출량 비율")
                        country_car_data = df_long[
                            (df_long["국가명"] == selected_country) &
                            (df_long["날짜"].dt.year == latest_year)
                        ].groupby(["차종 구분", "차량 구분"])["수출량"].sum().reset_index()
                         
                        if not country_car_data.empty:
                            country_car_data = country_car_data.sort_values("수출량", ascending=False).head(10)
                             
                            fig3 = px.pie(
                                country_car_data,
                                names="차량 구분",
                                values="수출량",
                                title=f"{selected_country}의 차량 종류별 수출량 비율 (최근 1년)",
                                height=500,
                                color_discrete_sequence=px.colors.qualitative.Pastel
                            )
                             
                            fig3.update_traces(textposition='inside', textinfo='percent+label')
                            fig3.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                showlegend=False,
                                margin=dict(l=20, r=20, t=40, b=20)
                            )
                            st.plotly_chart(fig3, use_container_width=True)
                             
                            st.markdown("""
                            <div class="chart-guide">
                                <b>🥧 차트 해석 방법:</b><br>
                                - 전체 원은 선택한 국가의 총 수출량을 나타냅니다.<br>
                                - 각 조각은 차량 종류별 수출량 비율을 나타냅니다.<br>
                                - 상위 10개 차량만 표시됩니다.<br>
                                - 마우스를 조각 위에 올리면 차량명과 정확한 비율을 확인할 수 있습니다.
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning(f"{selected_country}의 차량 수출량 데이터가 없습니다.")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.write("")
                st.markdown("### 📊 추가 분석 차트")
                
                st.subheader("국가별 수출량 비교")
                car_data = df_long[
                    ((df_long["차종 구분"] == selected_car_type) | (df_long["차량 구분"] == selected_car)) &
                    (df_long["날짜"].dt.year == latest_year)
                ].groupby("국가명")["수출량"].sum().reset_index()
                
                if not car_data.empty:
                    fig = px.bar(
                        car_data,
                        x="국가명",
                        y="수출량",
                        title=f"{selected_car_type} - {selected_car} 국가별 수출량 비교 (최근 1년)",
                        labels={"수출량": "총 수출량", "국가명": "국가명"},
                        height=500,
                        color="국가명",
                        color_discrete_sequence=px.colors.qualitative.Vivid
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(gridcolor='lightgray'),
                        yaxis=dict(gridcolor='lightgray'),
                        showlegend=False,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("""
                    <div class="chart-guide">
                        <b>📊 차트 해석 방법:</b><br>
                        - 가로축은 국가명을, 세로축은 수출량을 나타냅니다.<br>
                        - 각 막대의 높이는 해당 국가의 총 수출량을 나타냅니다.<br>
                        - 색상이 다르게 표시되어 국가별로 쉽게 구분할 수 있습니다.<br>
                        - 마우스를 막대 위에 올리면 정확한 수치를 확인할 수 있습니다.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("선택한 차량의 수출량 데이터가 없습니다.")
                st.markdown('</div>', unsafe_allow_html=True)
        
                
                   
    
    elif current_tab == "🌍 다중 국가 비교":
        st.header("🌍 다중 국가 비교 분석")
        
        with st.container():
            st.markdown("""
            <div class="feature-description">
                <h4>📌 다중 국가 비교 기능 사용 방법</h4>
                <p>이 기능은 여러 국가의 수출량을 비교 분석합니다. 다음과 같은 경우에 유용합니다:</p>
                <ul>
                    <li>여러 국가 간 수출 성과 비교가 필요할 때</li>
                    <li>시장별 성장 추세 분석이 필요할 때</li>
                    <li>차종별 국가별 선호도 비교가 필요할 때</li>
                </ul>
                <p><b>사용 방법:</b> 왼쪽에서 비교할 국가와 차종을 선택한 후 "비교하기" 버튼을 클릭하세요.</p>
                <p><b>결과 해석:</b> 비교 결과는 라인 차트, 막대 차트, 히트맵 등 다양한 시각화로 제공되며, 국가 간 차이를 쉽게 파악할 수 있습니다.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("🔍 비교 조건 설정", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_countries = st.multiselect(
                    "비교할 국가 선택",
                    sorted(df["국가명"].unique()),
                    default=sorted(df["국가명"].unique())[:3],
                    key='multi_country_select'
                )
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
        
        # 재할당: 위젯에서 설정된 값을 session_state에서 가져옴
        selected_countries = st.session_state.get('multi_country_select', sorted(df["국가명"].unique())[:3])
        selected_car_type = st.session_state.get('multi_car_type_select', sorted(df["차종 구분"].unique())[0])
        selected_car = st.session_state.get('multi_car_select', filtered_car_options[0] if filtered_car_options else None)
        
        if compare_btn:
            st.session_state.comparison_made = True
        
        if st.session_state.comparison_made or ('multi_comparison_result' in st.session_state and not reset_btn):
            if compare_btn:
                filtered_data = df_long[
                    (df_long["국가명"].isin(selected_countries)) | ((df_long["차종 구분"] == selected_car_type) & (df_long["차량 구분"] == selected_car) & (df_long["날짜"].dt.year == latest_year))
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
            
            st.write("")
            col1, col2 = st.columns(2)
            
            with col1:
                with st.container():
                    st.subheader("연간 수출량 비교")
                    current_year = datetime.now().year
                    past_years = sorted([y for y in df_long["날짜"].dt.year.unique() if y < current_year], reverse=True)[:3]
                    
                    annual_data = df_long[
                        (df_long["국가명"].isin(selected_countries)) | ((df_long["차종 구분"] == selected_car_type) & (df_long["차량 구분"] == selected_car)) &
                        (df_long["날짜"].dt.year.isin(past_years))
                    ].groupby(["국가명", df_long["날짜"].dt.year])["수출량"].sum().reset_index()
                    
                    if not annual_data.empty:
                        fig_annual = px.bar(
                            annual_data,
                            x="날짜",
                            y="수출량",
                            color="국가명",
                            barmode="group",
                            title=f"{selected_car_type} - {selected_car} 국가별 연간 총 수출량 비교 ({past_years[-1]}~{past_years[0]}년)",
                            labels={"날짜": "연도", "수출량": "총 수출량"},
                            height=500,
                            color_discrete_sequence=px.colors.qualitative.Plotly
                        )
                        fig_annual.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(gridcolor='lightgray'),
                            yaxis=dict(gridcolor='lightgray'),
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig_annual, use_container_width=True)
                        
                        st.markdown("""
                        <div class="chart-guide">
                            <b>📅 연간 비교 차트 해석 방법:</b><br>
                            - 가로축은 연도를, 세로축은 수출량을 나타냅니다.<br>
                            - 색상별로 다른 국가를 구분할 수 있습니다.<br>
                            - 각 연도별로 국가 간 수출량을 비교할 수 있습니다.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("연간 수출량 데이터가 없습니다.")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                with st.container():
                    st.subheader("차량 종류별 수출량 비교")
                    heatmap_data = df_long[
                        (df_long["국가명"].isin(selected_countries)) &
                        (df_long["날짜"].dt.year == latest_year)
                    ].groupby(["국가명", "차량 구분"])["수출량"].sum().reset_index()
                    
                    if not heatmap_data.empty:
                        fig_heatmap = px.density_heatmap(
                            heatmap_data,
                            x="국가명",
                            y="차량 구분",
                            z="수출량",
                            title=f"국가별 차량 종류별 수출량 비교 (최근 1년)",
                            height=500,
                            color_continuous_scale='Viridis'
                        )
                        fig_heatmap.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(gridcolor='lightgray'),
                            yaxis=dict(gridcolor='lightgray'),
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig_heatmap, use_container_width=True)
                        
                        st.markdown("""
                        <div class="chart-guide">
                            <b>🔥 히트맵 해석 방법:</b><br>
                            - 가로축은 국가명을, 세로축은 차량 종류를 나타냅니다.<br>
                            - 색상이 진할수록 해당 국가에서 해당 차량의 수출량이 많습니다.<br>
                            - 마우스를 셀 위에 올리면 정확한 수치를 확인할 수 있습니다.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("히트맵 생성에 필요한 데이터가 없습니다.")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.write("")
            st.markdown("### 📈 국가별 월별 수출량 추이")
            with st.container():
                monthly_data = filtered_data.groupby(['국가명', '월'])['수출량'].mean().reset_index()
                fig_line = px.line(
                    monthly_data,
                    x="월",
                    y="수출량",
                    color="국가명",
                    title=f"{selected_car_type} - {selected_car} 국가별 월별 수출량 추이 (최근 1년)",
                    labels={"수출량": "평균 수출량", "월": "월"},
                    height=500,
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                fig_line.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(gridcolor='lightgray'),
                    yaxis=dict(gridcolor='lightgray'),
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_line, use_container_width=True)
                
                st.markdown("""
                <div class="chart-guide">
                    <b>📈 라인 차트 해석 방법:</b><br>
                    - 가로축은 월을, 세로축은 수출량을 나타냅니다.<br>
                    - 색상별로 다른 국가를 구분할 수 있습니다.<br>
                    - 선의 기울기로 증가/감소 추세를 파악할 수 있습니다.<br>
                    - 마우스를 선 위에 올리면 정확한 수치를 확인할 수 있습니다.
                </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    run_ho()
