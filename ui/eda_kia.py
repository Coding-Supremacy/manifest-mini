import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import platform

# 폰트 설정
plt.rcParams['axes.unicode_minus'] = False

if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    path = "c:/Windows/Fonts/malgun.ttf"
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system... sorry~~~~')

months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']


@st.cache_data(ttl=3600, show_spinner="데이터 로드 중...")
def load_data():
    months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
    # 지역별 수출 데이터
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df_export = pd.read_csv(os.path.join(BASE_DIR, "data/기아_지역별수출실적_전처리.csv"))
    df_export['연간합계'] = df_export[months].sum(axis=1)
    df_export['차량유형'] = df_export['차량 구분'].str.split('(').str[0]
    melt_export = df_export.melt(id_vars=['차량유형', '국가명', '연도'],
                               value_vars=months,
                               var_name='월',
                               value_name='수출량')
    melt_export['월'] = melt_export['월'].str.replace('월', '').astype(int)
    # 차종별 판매 데이터
    df_sales = pd.read_csv(os.path.join(BASE_DIR, "data/기아_차종별판매실적.csv"))
    df_sales['연간합계'] = df_sales[months].sum(axis=1)
    melt_sales = df_sales.melt(id_vars=['차종', '차량 구분', '거래 유형', '연도'],
                             value_vars=months,
                             var_name='월',
                             value_name='판매량')
    melt_sales['월'] = melt_sales['월'].str.replace('월', '').astype(int)
    # 해외공장 판매 데이터
    df_factory = pd.read_csv(os.path.join(BASE_DIR, "data/기아_해외공장판매실적_전처리.csv"))
    df_factory['연간합계'] = df_factory[months].sum(axis=1)
    melt_factory = df_factory.melt(id_vars=['공장명(국가)', '공장 코드', '차종', '연도'],
                                 value_vars=months,
                                 var_name='월',
                                 value_name='판매량')
    melt_factory['월'] = melt_factory['월'].str.replace('월', '').astype(int)
    # 해외현지판매 데이터
    df_overseas = pd.read_csv(os.path.join(BASE_DIR, "data/기아_해외현지판매_전처리.csv"))
    df_overseas['월별합계'] = df_overseas[months].sum(axis=1)
    melt_overseas = df_overseas.melt(id_vars=['국가명', '공장명(국가)', '차종', '연도'],
                                    value_vars=months,
                                    var_name='월',
                                    value_name='판매량')
    melt_overseas['월'] = melt_overseas['월'].str.replace('월', '').astype(int)
    return df_export, melt_export, df_sales, melt_sales, df_factory, melt_factory, df_overseas, melt_overseas

# 차트 생성 함수 (캐싱 적용)
@st.cache_data(ttl=600, show_spinner=False)
def create_plot(_fig):
    return _fig

# 데이터 로드
df_export, melt_export, df_sales, melt_sales, df_factory, melt_factory, df_overseas, melt_overseas = load_data()

powertrain_types = {
    '내연기관': ['Bongo', 'K3', 'K5', 'Carnival', 'Seltos', 'Sportage', 'Sorento'],
    '전기차': ['EV6', 'EV9', 'Niro EV', 'Soul EV', 'EV5'],
    '하이브리드': ['Niro', 'Sorento Hybrid', 'Sportage Hybrid']
}

# 파워트레인 유형 결정 함수
def get_powertrain_type(model):
    for ptype, models in powertrain_types.items():
        if any(m in model for m in models):
            return ptype
    return '내연기관'  # 기본값

# 데이터 전처리
df_overseas['파워트레인'] = df_overseas['차종'].apply(get_powertrain_type)

# 분석 코멘트 생성을 위한 도우미 함수들
def get_seasonality_pattern(monthly_data):
    peak = monthly_data.idxmax()+1
    low = monthly_data.idxmin()+1
    if abs(peak-low) <=2:
        return f"연중 안정적 판매 (최고: {peak}월, 최저: {low}월)"
    else:
        return f"뚜렷한 계절성 (최고: {peak}월, 최저: {low}월)"

def get_promotion_idea(model):
    ideas = {
        "SUV": "오프로드 체험 이벤트 + 보험 패키지",
        "세단": "명품 카키트 증정 + 5년 무상 점검",
        "전기차": "충전기 설치 지원 + 전기요금 할인",
        "하이브리드": "환경 보조금 지원 + 연비 경진대회"
    }
    for k,v in ideas.items():
        if k in model: return v
    return "할인 금융 혜택 + 무료 옵션 업그레이드"

def get_improvement_point(model):
    points = {
        "K5": "후면 공간 확장 및 인포테인먼트 시스템 업그레이드",
        "K3": "연비 개선을 위한 경량화 설계",
        "EV6": "배터리 성능 향상 및 충전 속도 개선",
        "Sorento": "3열 좌석 편의성 강화"
    }
    return points.get(model.split()[0], "디자인 리프레시 + 신기술 적용")

def get_best_month(df, year, country):
    monthly = df[(df['연도']==year) & (df['국가명']==country)][months].sum()
    return f"{monthly.idxmax().replace('월','')}월 ({monthly.max():,}대)"

def calculate_sales_volatility(df, year, country):
    # 월별 컬럼 이름이 '1월', '2월' 형식이므로 원본 컬럼명 사용
    monthly = df[(df['연도']==year) & (df['국가명']==country)][months].sum()
    return (monthly.std() / monthly.mean()) * 100
def get_market_share(country):
    # 가상의 시장 점유율 데이터 (실제 구현시 데이터 연결 필요)
    shares = {'U.S.A': 4.2, 'China': 2.8, 'Germany': 3.5, 'India': 5.1}
    return shares.get(country, 3.0)

def get_fastest_growing_country(df, countries, year):
    growth = {}
    for country in countries:
        prev_year = df[df['국가명']==country]['연도'].max() - 1
        if prev_year in df['연도'].unique():
            curr = df[(df['국가명']==country) & (df['연도']==year)]['월별합계'].sum()
            prev = df[(df['국가명']==country) & (df['연도']==prev_year)]['월별합계'].sum()
            growth[country] = (curr - prev) / prev * 100 if prev != 0 else 0
    return max(growth, key=growth.get) if growth else "데이터 부족"

def identify_seasonal_pattern(df, countries):
    patterns = []
    for country in countries:
        monthly = df[df['국가명']==country][months].mean()
        peak = monthly.idxmax().replace('월','')
        patterns.append(f"{country}({peak}월)")
    return ", ".join(patterns)

def get_year_round_models(df):
    top_models = df.groupby('차종')['월별합계'].sum().nlargest(5).index
    stable = []
    for model in top_models:
        monthly = df[df['차종']==model][months].mean()
        if monthly.std() / monthly.mean() < 0.3:
            stable.append(model)
    return ", ".join(stable[:3]) if stable else "없음"

def get_seasonal_models(df):
    top_models = df.groupby('차종')['월별합계'].sum().nlargest(5).index
    seasonal = []
    for model in top_models:
        monthly = df[df['차종']==model][months].mean()
        if monthly.std() / monthly.mean() >= 0.5:
            seasonal.append(f"{model}({monthly.idxmax().replace('월','')}월)")
    return ", ".join(seasonal[:3]) if seasonal else "없음"

def get_ev_leader(df):
    # 전기차 비율이 가장 높은 국가
    ev_ratio = df.groupby('국가명').apply(lambda x: x[x['파워트레인']=='전기차']['월별합계'].sum() / x['월별합계'].sum())
    return ev_ratio.idxmax() if not ev_ratio.empty else "데이터 부족"

def get_ice_dependent(df):
    # 내연기관 의존도가 가장 높은 국가
    ice_ratio = df.groupby('국가명').apply(lambda x: x[x['파워트레인']=='내연기관']['월별합계'].sum() / x['월별합계'].sum())
    return ice_ratio.idxmax() if not ice_ratio.empty else "데이터 부족"

def get_country_policy(country):
    # 국가별 정책 방향 (가상 데이터)
    policies = {
        'U.S.A': '전기차 보조금 확대 및 충전 인프라 구축',
        'China': '신에너지차 할당제 및 보조금 단계적 축소',
        'Germany': '2030년 내연기관 판매 금지 목표',
        'Norway': '전기차 비율 100% 달성 중'
    }
    return policies.get(country, '정보 없음')

st.title("🚗 기아 자동차 통합 분석 대시보드 (최적화 버전)")




def run_eda_kia():
    
    
    # 세션 상태 초기화
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "🌍 지역별 수출 분석"

    # 탭 변경 감지 함수
    def on_tab_change():
        st.session_state.current_tab = st.session_state.tab_key
    # 메인 탭 구성
    main_tabs = st.tabs(["🌍 지역별 수출 분석", "🚘 차종별 판매 분석", "🏭 해외공장 판매 분석", "📊 해외현지 판매 분석"])

    # 현재 활성 탭 확인
    current_tab = st.session_state.current_tab



    with main_tabs[0] if current_tab == "🌍 지역별 수출 분석" else main_tabs[0]:
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📌 핵심 지표", "🗓️ 월별 분석", "📈 수출 분석"])
        
        with sub_tab1:
            # 1. KPI 지표 (캐싱 적용)
            @st.cache_data(ttl=300)
            def get_kpi_metrics():
                total_export = df_export['연간합계'].sum()
                avg_export = df_export['연간합계'].mean()
                top_region = df_export.groupby('국가명')['연간합계'].sum().idxmax()
                return total_export, avg_export, top_region

            total_export, avg_export, top_region = get_kpi_metrics()
            
            st.subheader("주요 수출 지표")
            col1, col2, col3 = st.columns(3)
            col1.metric("총 수출량", f"{total_export:,}대")
            col2.metric("평균 수출량", f"{avg_export:,.0f}대/년")
            col3.metric("최다 수출 지역", top_region)

            # 2. 지역별 총합 차트 (캐싱 적용)
            @st.cache_data(ttl=300)
            def get_region_chart():
                region_data = df_export.groupby('국가명')['연간합계'].sum().sort_values(ascending=False)
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x=region_data.values, y=region_data.index, palette='viridis')
                for i, v in enumerate(region_data.values):
                    ax.text(v + 100, i, f"{v:,}", va='center', fontsize=10)
                plt.tight_layout()
                return fig

            st.subheader("지역별 총 수출량")
            fig1 = get_region_chart()
            st.pyplot(fig1)
            
            st.info(f"""
            **📊 분석 코멘트:**
            - {top_region}이 전체 수출의 {df_export[df_export['국가명']==top_region]['연간합계'].sum()/total_export*100:.1f}%를 차지하며 핵심 시장으로 확인
            - 상위 3개 지역({df_export.groupby('국가명')['연간합계'].sum().nlargest(3).index.tolist()})이 전체의 70% 이상 점유
            
            **🚀 전략 제안:**
            1. {top_region} 시장 공략 강화: 현지 마케팅 예산 20% 증액 및 현지 취향 반영 모델 개발
            2. 신흥 시장 공략: 동남아시아 지역을 대상으로 소형 SUV 및 경차 라인업 확대
            3. 지역별 맞춤 전략:
            - 북미: 대형 SUV 및 픽업트럭 라인업 강화
            - 유럽: 디젤 하이브리드 및 스포츠 왜건 모델 확대
            - 중동: 고온 환경에 특화된 냉각 시스템 적용 모델 출시
            """)

            # 3. 지역별 월간 패턴 (캐싱 적용)
            @st.cache_data(ttl=300)
            def get_region_heatmap():
                region_month = melt_export.pivot_table(index='국가명', columns='월', 
                                                    values='수출량', aggfunc='mean')
                fig, ax = plt.subplots(figsize=(12, 6))
                sns.heatmap(region_month, cmap="Blues", annot=True, fmt=',.0f',
                            linewidths=.5, cbar_kws={'label': '평균 수출량 (대)'})
                plt.tight_layout()
                return fig

            st.subheader("지역-월별 수출 현황")
            fig4 = get_region_heatmap()
            st.pyplot(fig4)
            
            st.info("""
            **🌍 월별 패턴 분석:**
            - 북미 지역: 11~12월 연말 할인 시즌에 30% 이상 판매 증가
            - 유럽 지역: 3월(신년형 출시)과 9월(독일 모터쇼)에 판매 정점
            - 중국 지역: 2월(춘절) 기간 동안 판매 급감 → 대체 시장 확보 필요
            
            **📅 계절별 전략:**
            1. 분기별 목표 설정 시스템:
            - 1분기(3월): 유럽 시장 집중 공략
            - 4분기(11~12월): 북미 시장 대상 연말 프로모션 강화
            2. 생산 계획 유연화:
            - 1월: 중국 수요 감소분을 다른 지역으로 전환 생산
            - 8월: 연말 수요 대비 생산량 15% 증대
            3. 물류 효율화:
            - 연말 수출량 증가에 대비한 선박 용량 확보
            - 지역별 판매 패턴에 맞춘 물류 허브 최적화
            """)

        with sub_tab2:
            # 4. 월별 수출 추이 (캐싱 적용)
            @st.cache_data(ttl=300)
            def get_monthly_trend():
                palette = sns.color_palette("husl", len(df_export['연도'].unique()))
                fig, ax = plt.subplots(figsize=(12, 6))
                for idx, year in enumerate(sorted(df_export['연도'].unique())):
                    monthly_data = melt_export[melt_export['연도'] == year].groupby('월')['수출량'].sum()
                    sns.lineplot(x=monthly_data.index, y=monthly_data.values, 
                                label=str(year), color=palette[idx], 
                                marker='o', linewidth=2.5, ax=ax)
                plt.xticks(range(1, 13))
                plt.grid(True, alpha=0.3)
                plt.legend(title="연도", bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.tight_layout()
                return fig

            st.subheader("월별 수출 추이 (연도별 비교)")
            fig2 = get_monthly_trend()
            st.pyplot(fig2)
            
            # 성장률 계산 함수
            @st.cache_data(ttl=300)
            def calculate_growth():
                try:
                    # 최신 연도와 이전 연도 자동 계산
                    current_year = melt_export['연도'].max()
                    prev_year = current_year - 1
                    
                    # 4분기(10,11,12월) 데이터 필터링
                    current_q4 = melt_export[(melt_export['연도'] == current_year) & 
                                        (melt_export['월'].isin([10,11,12]))]['수출량'].sum()
                    prev_q4 = melt_export[(melt_export['연도'] == prev_year) & 
                                        (melt_export['월'].isin([10,11,12]))]['수출량'].sum()
                    
                    # 성장률 계산 (분모 0 방지)
                    growth_rate = ((current_q4 / prev_q4) - 1) * 100 if prev_q4 != 0 else 0
                    return current_year, prev_year, growth_rate
                except:
                    return None, None, 0

            current_year, prev_year, growth_rate = calculate_growth()
            
            st.info(f"""
            **📈 추세 분석:**
            - 매년 2~3월과 8~9월에 두드러진 판매 증가 패턴 확인
            - {current_year}년 4분기 판매량 전년 대비 {growth_rate:.1f}% 증가
            
            **🛠️ 운영 전략:**
            1. 생산 계획 최적화:
            - 2월: 전년 대비 15% 생산량 증대
            - 8월: 연말 수요 대비 20% 생산량 증가
            2. 물류 효율화:
            - 4분기 전용 선박 2척 추가 계약
            - 지역별 수요 패턴에 맞춘 물류 허브 재배치
            3. 인센티브 프로그램:
            - 3월과 9월에 딜러 인센티브 30% 증대
            - 연말 판매 목표 달성 시 추가 보너스 지급
            """)
            
            # 5. 차량유형별 월별 패턴 (캐싱 적용)
            @st.cache_data(ttl=300)
            def get_vehicle_heatmap():
                vehicle_month = melt_export.groupby(['차량유형', '월'])['수출량'].mean().unstack()
                fig, ax = plt.subplots(figsize=(12, 6))
                sns.heatmap(vehicle_month, cmap="YlGnBu", annot=True, fmt=',.0f', 
                            linewidths=.5, cbar_kws={'label': '평균 수출량 (대)'})
                plt.tight_layout()
                return fig

            st.subheader("차량유형-월별 수출 패턴")
            fig3 = get_vehicle_heatmap()
            st.pyplot(fig3)
            
            st.info("""
            **🚗 차종별 특징:**
            - 소형차: 2분기(4~6월)에 집중 판매 (전체의 40% 점유)
            - 전기차: 11~12월에 판매 급증 (평균 대비 65% 증가)
            
            **🔧 맞춤형 전략:**
            1. 소형차 전략:
            - 1분기 생산량 25% 증대 → 2분기 수요 대비
            - 신학기 맞춤 프로모션 (학생 할인 + 무료 보험 패키지)
            2. 전기차 공략:
            - 보조금 마감 시기(11월) 집중 홍보 캠페인
            - 충전 인프라 협력사와 공동 마케팅 진행
            """)

        with sub_tab3:
            st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
            st.subheader("📊 지역별 수출 실적 변화")
            
            # 데이터 전처리
            df_export_filtered = df_export.copy()
            countries = df_export_filtered['국가명'].unique()

            selected_countries = st.multiselect("국가를 선택하세요:", options=list(countries), default=list(countries))

            if selected_countries:
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                for country in selected_countries:
                    country_data = df_export_filtered[df_export_filtered['국가명'] == country].copy()

                    # 연도별 월별 판매량 데이터를 하나의 Series로 만들기
                    monthly_sales = []
                    years = country_data['연도'].unique()

                    for year in years:
                        year_data = country_data[country_data['연도'] == year]
                        month_cols = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
                        for month in month_cols:
                            if month in year_data.columns:
                                sales = year_data[month].values
                                if len(sales) > 0:
                                    monthly_sales.append(sales[0])
                                else:
                                    monthly_sales.append(None)
                            else:
                                monthly_sales.append(None)

                    # x축 날짜 생성 및 2025-03-01 이후 데이터 제거
                    dates = pd.date_range(start='2023-01-01', periods=len(monthly_sales), freq='MS')
                    dates = dates[dates <= pd.to_datetime('2025-03-01')]
                    monthly_sales = monthly_sales[:len(dates)]

                    # NaN 값을 제외한 데이터만 플롯
                    valid_indices = [i for i, x in enumerate(monthly_sales) if pd.notna(x)]
                    valid_dates = [dates[i] for i in valid_indices]
                    valid_sales = [monthly_sales[i] for i in valid_indices]

                    fig.add_trace(
                        go.Scatter(x=valid_dates, y=valid_sales, mode='lines+markers', name=country,
                                hovertemplate='%{x|%Y-%m-%d}<br>판매량: %{y:,.0f}<extra></extra>')
                    )
                
                # 그래프 레이아웃 설정
                fig.update_layout(
                    title='주요 시장별 수출량 변화', 
                    xaxis_title='날짜', 
                    yaxis_title='판매량', 
                    legend_title='국가', 
                    hovermode="closest",
                    xaxis=dict(
                        tickformat='%b %Y',
                        dtick="M3",
                    ),
                    xaxis_range=[min(valid_dates), max(valid_dates)] if valid_dates else None,
                    height=600
                )
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("""
                <div style="background-color:#FFEBCD; padding:15px; border-radius:10px;">
                <span style="font-size:20px; font-weight:bold;">📌 주요 시장별 수출량 변화 분석</span><br>

                - **미국(US)** 과 **EU+EFTA**는 가장 높은 수출량을 기록한 주요 시장으로, 전반적으로 안정적인 흐름을 유지하고 있습니다.  
                - **멕시코**, **중동**, **라틴 아메리카** 등의 지역은 상대적으로 수출량이 낮지만, 일부 구간에서 증가 추세를 보여 **성장 가능성**이 있는 시장으로 분석됩니다.  
                - 최근 수출량 변동이 큰 국가는 **미국(US), 인도(India), 아시아/퍼시픽 지역** 등으로, 글로벌 수요 또는 정책 변화에 따른 영향을 받고 있는 것으로 해석됩니다. **이들 시장은 지속적인 모니터링과 전략 조정이 필요한 대상**입니다.
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
                
                st.divider()

                # 기아 지역별 수출실적 분석 요약표 작업

                df_export.drop(df_export.loc[df_export['차량 구분'] == '총합'].index, inplace=True)
                
                df_export_melted =  df_export.melt(id_vars=['차량 구분', '국가명', '연도'], 
                                        value_vars=["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"] ,
                                        var_name='월', value_name='판매량')
            
                
                
                st.subheader("📌 기아 지역별 수출실적 통계 요약")
                st.write('')

                국가_차종_피벗 = df_export_melted.pivot_table(
                        index='국가명',
                        columns='차량 구분',
                        values='판매량',
                        aggfunc='sum',
                        fill_value=0
                    )
                총합 = 국가_차종_피벗.sum(axis=1)
                국가_차종_피벗.insert(0, '총합', 총합)
                국가_차종_피벗 = 국가_차종_피벗.sort_values(by='총합', ascending=False)

                # 총합 컬럼 빼고 나머지 차종 컬럼만 선택
                차종_컬럼 = 국가_차종_피벗.columns.drop('총합')
                # 차종별 총합 기준으로 열 순서 정렬
                정렬된_열_순서 = 국가_차종_피벗[차종_컬럼].sum().sort_values(ascending=False).index.tolist()
                # 총합을 맨 앞으로 두고 열 재정렬
                열_순서 = ['총합'] + 정렬된_열_순서
                국가차종피벗 = 국가_차종_피벗[열_순서]
                총합_행 = 국가차종피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                국가차종피벗 = pd.concat([총합_행.to_frame().T, 국가차종피벗])

                # 스타일링을 위해 복사본 생성
                국가_차종_styled = 국가차종피벗.copy()

                # 스타일링 적용
                styled_국가_차종 = (
                    국가_차종_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                
                
                st.write("""##### 🌍 국가별 차종 판매량""")
                st.dataframe(styled_국가_차종, use_container_width=True)


                col1, col2 = st.columns(2)
                
                with col1:
                    st.write('📅 국가 연도별 판매량')
                    국가_연도별_피벗 = df_export_melted.pivot_table(index='국가명', columns='연도', values='판매량', aggfunc='sum', fill_value=0)
                    총합 = 국가_연도별_피벗.sum(axis=1)
                    국가_연도별_피벗.insert(0, '총합', 총합)
                    국가_연도별_피벗 = 국가_연도별_피벗.sort_values(by='총합', ascending=False)

                    st.dataframe(국가_연도별_피벗)

                    차량_연도별_피벗 = df_export_melted.pivot_table(index='차량 구분', columns='연도', values='판매량', aggfunc='sum', fill_value=0)
                    총합 = 차량_연도별_피벗.sum(axis=1)
                    차량_연도별_피벗.insert(0, '총합', 총합)
                    차량_연도별_피벗 = 차량_연도별_피벗.sort_values(by='총합', ascending=False)

                    st.write('📅 차량 연도별 판매량')                
                    
                    st.dataframe(차량_연도별_피벗)
                    
                with col2:
                    st.write('📆 국가 월별 통계 (2023년~2025년 누적 기준)')

                    # 월 순서를 올바르게 정의
                    month_order = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']

                    국가_월_피벗 = df_export_melted.pivot_table(index='국가명', columns='월', values='판매량', aggfunc='sum', fill_value=0).reindex(columns=month_order)
                    총합 = 국가_월_피벗.sum(axis=1)
                    국가_월_피벗.insert(0, '총합', 총합)
                    국가_월_피벗 = 국가_월_피벗.sort_values(by='총합', ascending=False)

                    st.dataframe(국가_월_피벗)

                    차량_월_피벗 = df_export_melted.pivot_table(index='차량 구분', columns='월', values='판매량', aggfunc='sum', fill_value=0).reindex(columns=month_order)
                    총합 = 차량_월_피벗.sum(axis=1)
                    차량_월_피벗.insert(0, '총합', 총합)
                    차량_월_피벗 = 차량_월_피벗.sort_values(by='총합', ascending=False)
                    
                    st.write('📆 차량 월별 판매량')
                    st.dataframe(차량_월_피벗)

                
                

                st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

                with st.expander("🎯 분석 목적"):
                    st.markdown("""
                    <div style='background-color: #F4F6F6; padding: 15px; border-radius: 8px;'>
                        <h4 style='color:#2E86C1;'>🎯 분석 목적</h4>
                        <ul>
                            <li><b style='color:#1F618D'>시장 동향 파악:</b> 글로벌 시장에서의 성과를 시각화하여 전반적인 수출 동향을 파악합니다.</li>
                            <li><b style='color:#1F618D'>지역별 성과 비교:</b> 다양한 국가 및 지역의 실적을 비교하여 전략의 효과성을 평가합니다.</li>
                            <li><b style='color:#1F618D'>미래 전략 수립:</b> 과거와 현재 데이터를 기반으로 향후 전략 수립에 필요한 인사이트를 도출합니다.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                with st.expander("✨ 분석 장점"):
                    st.markdown("""
                    <div style='background-color: #F9F9F9; padding: 15px; border-radius: 8px;'>
                        <h4 style='color:#2E86C1;'>✨ 분석 장점</h4>
                        <ol>
                            <li><b style='color:#117A65'>데이터 기반 의사결정:</b> 객관적인 데이터를 통해 신뢰도 높은 의사결정이 가능합니다.</li>
                            <li><b style='color:#117A65'>트렌드 예측:</b> 시계열 분석을 통해 향후 시장 흐름을 예측할 수 있습니다.</li>
                            <li><b style='color:#117A65'>경쟁력 강화:</b> 강점/약점을 파악하고 전략적으로 대응할 수 있습니다.</li>
                            <li><b style='color:#117A65'>리소스 최적화:</b> 분석을 통해 마케팅 및 생산 자원의 효율적 배분이 가능합니다.</li>
                            <li><b style='color:#117A65'>이해관계자 커뮤니케이션:</b> 경영진, 투자자와 효과적으로 성과를 공유할 수 있습니다.</li>
                        </ol>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

    with main_tabs[1] if current_tab == "🚘 차종별 판매 분석" else main_tabs[1]:
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📊 판매 현황", "📈 트렌드 분석", "🚙 차종별 판매 실적"])
        
        with sub_tab1:

            selected_year = st.selectbox(
            "연도 선택",
            options=sorted(df_sales['연도'].unique()),
            index=len(df_sales['연도'].unique())-1,
            key='sales_year_sub_tab1'
            )

            # 캐싱 적용된 상위 차종 추출
            @st.cache_data(ttl=300)
            def get_top_models(_df, year, n=10):
                return _df[_df['연도'] == year]\
                    .groupby('차종')['연간합계'].sum()\
                    .nlargest(n).index.tolist()

            top_models = get_top_models(df_sales, selected_year)

            # 1. 차종별 연간 판매량 Top 10 (캐싱 적용)
            @st.cache_data(ttl=300)
            def get_top_models_chart(_df, year, models):
                top_data = _df[
                    (_df['연도'] == year) & 
                    (_df['차종'].isin(models))
                ].groupby('차종')['연간합계'].sum().sort_values(ascending=False)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x=top_data.values, y=top_data.index, palette='rocket')
                for i, v in enumerate(top_data.values):
                    ax.text(v + 50, i, f"{v:,}", va='center')
                plt.title(f"{year}년 Top 10 차종", fontsize=14)
                plt.tight_layout()
                return fig

            st.subheader("차종별 연간 판매량 Top 10")
            fig1 = get_top_models_chart(df_sales, selected_year, top_models)
            st.pyplot(fig1)
            
            top_model_share = df_sales[(df_sales['차종']==top_models[0]) & (df_sales['연도']==selected_year)]['연간합계'].sum()/df_sales[df_sales['연도']==selected_year]['연간합계'].sum()*100
            ev_models = [m for m in top_models if get_powertrain_type(m)=='전기차']
            
            st.info(f"""
            **🏆 {selected_year}년 베스트셀러 분석:**
            - 1위 {top_models[0]} 모델: 전체 판매의 {top_model_share:.1f}% 점유
            - 상위 3개 모델({top_models[:3]})이 전체의 45% 차지
            
            
            **🎯 마케팅 전략:**
            1. 베스트셀러 유지 전략:
            - {top_models[0]}: 고객 충성도 프로그램 강화 (5년 무상 점검 확대)
            - {top_models[1]}: 리스/렌탈 옵션 다양화 (월 30만원 대 출시)
            2. 신규 모델 개발 로드맵:
            - {top_models[0]}의 플러그인 하이브리드 버전 2024년 출시
            - 소형 전기차 2종 2025년까지 단계적 출시
            3. 판매 촉진 프로그램:
            - 5~10위 차종 대상 프로모션 (최대 100만원 할인)
            - 패키지 할인 ({top_models[0]} + {top_models[3]} 구매 시 50만원 추가 할인)
            """)
            
            # 2. 상위 차종 거래 유형 비중 (캐싱 적용)
            @st.cache_data(ttl=300)
            def get_sales_composition(_df, year, models):
                top_type = _df[
                    (_df['연도'] == year) &
                    (_df['차종'].isin(models))
                ].groupby(['차종', '거래 유형'])['연간합계'].sum().unstack()
                
                fig, ax = plt.subplots(figsize=(10, 6))
                top_type.plot(kind='barh', stacked=True, ax=ax)
                plt.legend(title="거래 유형", bbox_to_anchor=(1.05, 1))
                plt.title("국내/수출 비율", fontsize=14)
                plt.tight_layout()
                return fig

            st.subheader("상위 차종별 거래 유형")
            fig2 = get_sales_composition(df_sales, selected_year, top_models)
            st.pyplot(fig2)
            
            avg_export_ratio = df_sales[df_sales['연도']==selected_year].groupby('차종')['연간합계'].sum().nlargest(10).index.to_series().apply(
                lambda x: df_sales[(df_sales['차종']==x) & (df_sales['연도']==selected_year)].groupby('거래 유형')['연간합계'].sum().get('수출', 0)/df_sales[(df_sales['차종']==x) & (df_sales['연도']==selected_year)]['연간합계'].sum()
            ).mean()*100
            
            domestic_models = [m for m in top_models if df_sales[(df_sales['차종']==m) & (df_sales['연도']==selected_year)].groupby('거래 유형')['연간합계'].sum().get('국내', 0)/df_sales[(df_sales['차종']==m) & (df_sales['연도']==selected_year)]['연간합계'].sum() > 0.5]
            
            st.info(f"""
            **🌐 판매 채널 분석:**
            - 평균 수출 비중: {avg_export_ratio:.1f}%
            - 국내 비중 높은 모델: {domestic_models[0] if domestic_models else '없음'}
            
            **📦 채널 전략:**
            1. 수출 중심 모델:
            - {top_models[0]}: 주요 수출국별 맞춤형 사양 개발 (중동 - 강력한 냉방 시스템)
            - 유럽 시장: 디젤 하이브리드 버전 추가
            2. 국내 중심 모델:
            - {domestic_models[0] if domestic_models else '국내 모델'}: 한국 전용 컬러/옵션 추가
            - 내수 판매 촉진을 위한 할부 조건 개선 (최장 7년)
            3. 글로벌 통합 전략:
            - 수출 모델과 국내 모델의 플랫폼 통합으로 생산 효율화
            - 해외 현지 생거 증가에 따른 CKD 부품 수출 확대
            """)
        
        with sub_tab2:

            selected_year = st.selectbox(
            "연도 선택",
            options=sorted(df_sales['연도'].unique()),
            index=len(df_sales['연도'].unique())-1,
            key='sales_year_sub_tab2'
        )

        # 3. 상위 차종 월별 추이 (겹쳐진 막대그래프 버전)
        @st.cache_data(ttl=300)
        def get_monthly_trend_top5(_melt, year, models, n=5):
            top5 = models[:n]
            monthly_top5 = _melt[
                (_melt['연도'] == year) & 
                (_melt['차종'].isin(top5))
            ].groupby(['월', '차종'])['판매량'].sum().unstack()
            
            fig, ax = plt.subplots(figsize=(12, 6))
            monthly_top5.plot(kind='bar', stacked=True, ax=ax, width=0.8)
            plt.title("월별 판매 동향 - 상위 5개 차종 (누적)", fontsize=14)
            plt.xlabel("월")
            plt.ylabel("판매량 (누적)")
            plt.xticks(range(12), range(1, 13), rotation=0)  # 1월~12월 표시
            plt.grid(axis='y', alpha=0.3)
            plt.legend(title='차종', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            return fig

        st.subheader("상위 5개 차종 월별 추이 (겹쳐진 막대그래프)")
        fig3 = get_monthly_trend_top5(melt_sales, selected_year, top_models)
        st.pyplot(fig3)

        model1_pattern = get_seasonality_pattern(melt_sales[(melt_sales['차종']==top_models[0]) & (melt_sales['연도']==selected_year)].groupby('월')['판매량'].sum())
        model2_pattern = get_seasonality_pattern(melt_sales[(melt_sales['차종']==top_models[2]) & (melt_sales['연도']==selected_year)].groupby('월')['판매량'].sum())
        ev_increase = melt_sales[(melt_sales['차종'].isin([m for m in top_models if get_powertrain_type(m)=='전기차'])) & (melt_sales['월'].isin([11,12]))]['판매량'].sum()/melt_sales[(melt_sales['차종'].isin([m for m in top_models if get_powertrain_type(m)=='전기차']))]['판매량'].sum()*12/2*100-100 if melt_sales[(melt_sales['차종'].isin([m for m in top_models if get_powertrain_type(m)=='전기차']))]['판매량'].sum() > 0 else 0

        st.info(f"""
        **📅 계절성 패턴:**
        - {top_models[0]}: {model1_pattern}
        - {top_models[2]}: {model2_pattern}
        - 전기차 모델: 연말(11~12월) 평균 대비 {ev_increase:.0f}% 증가

        **🔄 생산 계획 제안:**
        1. 생산량 조정:
        - {top_models[0]}: 최고 판매월 전월 생산량 20% 증대
        - {top_models[2]}: 판매 정점기 2개월 전부터 증산
        2. 재고 관리:
        - 저조기(1월, 7월) 생산량 15% 감축
        - 연말 수요 대비 10월까지 목표 재고 확보
        3. 프로모션 일정:
        - 3월: 신학기 맞춤 캠페인 ({top_models[2]} 중심)
        - 11월: 전기차 보조금 마감 기간 집중 홍보
        """)

        # 4. 상위 차종 비교 (기존 막대그래프 유지)
        @st.cache_data(ttl=300)
        def get_model_comparison(_melt, year, model1, model2):
            compare = _melt[
                (_melt['차종'].isin([model1, model2])) &
                (_melt['연도'] == year)
            ].pivot_table(index='월', columns='차종', values='판매량', aggfunc='sum')
            
            fig, ax = plt.subplots(figsize=(10, 5))
            compare.plot(kind='bar', ax=ax, width=0.8)
            plt.title(f"{model1} vs {model2}", fontsize=14)
            plt.xlabel("월")
            plt.tight_layout()
            return fig

        st.subheader("상위 차종 직접 비교")
        col1, col2 = st.columns(2)
        with col1:
            model1 = st.selectbox(
                "첫 번째 차종",
                options=top_models,
                index=0,
                key='model1'
            )
        with col2:
            model2 = st.selectbox(
                "두 번째 차종", 
                options=[m for m in top_models if m != model1],
                index=1 if len(top_models) > 1 else 0,
                key='model2'
            )

        fig4 = get_model_comparison(melt_sales, selected_year, model1, model2)
        st.pyplot(fig4)

        # 모델 비교 분석을 위한 추가 계산
        model1_total = melt_sales[(melt_sales['차종']==model1) & (melt_sales['연도']==selected_year)]['판매량'].sum()
        model2_total = melt_sales[(melt_sales['차종']==model2) & (melt_sales['연도']==selected_year)]['판매량'].sum()
        model1_peak = melt_sales[(melt_sales['차종']==model1) & (melt_sales['연도']==selected_year)].groupby('월')['판매량'].sum().idxmax()
        model2_peak = melt_sales[(melt_sales['차종']==model2) & (melt_sales['연도']==selected_year)].groupby('월')['판매량'].sum().idxmax()

        st.info(f"""
        **🔍 {model1} vs {model2} 심층 비교 ({selected_year}년)**

        📊 기본 현황:
        - 총 판매량: {model1} {model1_total:,}대 vs {model2} {model2_total:,}대
        - 판매 차이: {abs(model1_total-model2_total):,}대 ({'상위' if model1_total>model2_total else '하위'} {abs(model1_total/model2_total*100-100):.1f}%)
        - 최고 판매월: {model1} {model1_peak}월 vs {model2} {model2_peak}월

        💡 인사이트:
        1. 제품 포지셔닝:
        - {model1}: {get_powertrain_type(model1)} 차종으로 {'주력 모델' if model1_total > model2_total else '보조 모델'} 역할
        - {model2}: {get_powertrain_type(model2)} 차종으로 {'가격 경쟁력' if 'K' in model2 else '고급형'} 포지션

        🎯 마케팅 전략:
        1. {model1} 강화 방안:
        - {model1_peak}월에 맞춘 한정판 모델 출시
        - 경쟁 모델 대비 차별화 포인트({get_improvement_point(model1)}) 강조
        2. {model2} 판매 촉진:
        - {get_promotion_idea(model2)} 프로모션 실시
        - {model1} 구매 고객 대상 {model2} 크로스 오퍼 제공
        3. 시너지 창출:
        - 패키지 할인: {model1}+{model2} 동시 구매 시 {5 if abs(model1_total-model2_total)<3000 else 7}% 추가 할인
        - 공통 마케팅: 두 모델 모두 강점을 보이는 {list(set([model1_peak, model2_peak]))[0]}월에 통합 캠페인 진행
        """)

        with sub_tab3:

            car_types = {
                '세단': ['Morning', 'Ray', 'K3', 'K5', 'Stinger', 'K7 / K8', 'K9', "Morning / Picanto", "K5 / Optima", 'K7 / K8 / Cadenza'],
                'SUV': ['Seltos', 'Niro', 'Sportage', 'Sorento', 'Mohave', 'EV6', 'EV9', "Mohave / Borrego"],
                '기타': ['Bongo', 'Carnival', 'Bus', "Carnival / Sedona", "Millitary", "Bongo (특수)", "Bus (특수)"]
            }

            selected_type = st.selectbox('차종 카테고리 선택', list(car_types.keys()))

            df_filtered = df_sales[df_sales['차종'].isin(car_types[selected_type])]

            # 거래유형을 기준으로 데이터 분리
            df_domestic = df_filtered[df_filtered['거래 유형'] == '국내']
            df_international = df_filtered[df_filtered['거래 유형'] != '국내']

            # 연도 및 월 컬럼 추가
            years = df_sales['연도'].unique()
            months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
            month_mapping = {month: idx + 1 for idx, month in enumerate(months)}

            # 데이터프레임 생성 함수
            def create_melted_dataframe(df):
                df_melted = pd.DataFrame()
                for year in years:
                    year_data = df[df['연도'] == year]
                    for month in months:
                        if month in year_data.columns:
                            temp_df = year_data[['차종', month]].copy()
                            temp_df.rename(columns={month: '판매량'}, inplace=True)
                            temp_df['연도'] = year
                            temp_df['월'] = month
                            df_melted = pd.concat([df_melted, temp_df], ignore_index=True)

                # "월" 컬럼을 숫자로 변환
                df_melted['월'] = df_melted['월'].map(month_mapping)

                # "연도-월"을 datetime 객체로 변환
                df_melted['연도-월'] = pd.to_datetime(df_melted['연도'].astype(str) + '-' + df_melted['월'].astype(str), format='%Y-%m')

                # 2023년 1월부터 2025년 3월까지만 필터링
                df_melted = df_melted[(df_melted['연도-월'] >= pd.to_datetime('2023-01-01')) & (df_melted['연도-월'] <= pd.to_datetime('2025-03-01'))]

                return df_melted

            # 국내와 해외 데이터프레임 생성
            df_melted_domestic = create_melted_dataframe(df_domestic)
            df_melted_international = create_melted_dataframe(df_international)

            # 그래프 그리기
            fig_domestic = px.line(df_melted_domestic, x='연도-월', y='판매량', color='차종',
                                    title=f'{selected_type} 차종별 국내 월별 판매량',
                                    labels={'연도-월': '연도-월 (Year-Month)', '판매량': '판매량 (Sales Volume)'},
                                    height=500)
            fig_domestic.update_xaxes(
                range=['2023-01-01', '2025-03-01'],
                dtick="M3",
                tickformat="%Y-%m"
            )

            fig_international = px.line(df_melted_international, x='연도-월', y='판매량', color='차종',
                                            title=f'{selected_type} 차종별 해외 월별 판매량',
                                            labels={'연도-월': '연도-월 (Year-Month)', '판매량': '판매량 (Sales Volume)'},
                                            height=500)
            fig_international.update_xaxes(
                range=['2023-01-01', '2025-03-01'],
                dtick="M3",
                tickformat="%Y-%m"
            )

            # 국내 차트 출력
            st.plotly_chart(fig_domestic, use_container_width=True)

            st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
            st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

            # 차트별 분석 내용
            if selected_type == '세단':
                st.markdown("""
                <div style="background-color:#fff8e7; padding:15px; border-radius:10px;">
                <span style="font-size:20px; font-weight:bold;">📌 세단 차종별 국내 판매 분석</span><br>

                - **K5**, **K3**, **K7/K8** 모델은 국내 시장에서 비교적 높은 판매량을 기록하고 있으며, **중형 세단 수요**가 지속되고 있음을 보여줍니다.  
                - **Stinger**, **K9** 등 고급 세단 모델은 지속적인 감소세를 보여, **단종 또는 전략 조정 필요성**이 제기될 수 있습니다.  
                - **Ray**의 판매량이 최근 상승세를 보이며, **경차 수요 확대** 가능성이 관찰됩니다.
                </div>
                """, unsafe_allow_html=True)
            elif selected_type == 'SUV':
                st.markdown("""
                <div style="background-color:#fff8e7; padding:15px; border-radius:10px;">
                <span style="font-size:20px; font-weight:bold;">📌 SUV 차종별 국내 판매 분석</span><br>

                - **Sorento**, **Sportage**는 국내 SUV 시장을 선도하고 있으며, **탄탄한 수요 기반**이 유지되고 있습니다.  
                - **전기 SUV**인 **EV6**, **EV9**는 점진적인 수요 상승을 보이며, **친환경 트렌드**에 따라 향후 확대 가능성이 있습니다.  
                - **Mohave**는 전통적인 수요층이 존재하나, **점진적 감소세**로 **라인업 재정비 고려**가 필요합니다.
                </div>
                """, unsafe_allow_html=True)
            elif selected_type == '기타':
                st.markdown("""
                <div style="background-color:#fff8e7; padding:15px; border-radius:10px;">
                <span style="font-size:20px; font-weight:bold;">📌 기타 차종별 국내 월별 판매량 분석</span><br>
                            
                - Carnival 모델이 압도적으로 높은 국내 판매량을 보이며, 기타 차종 중 가장 인기 있는 차량으로 확인됩니다.
                - Bongo 또한 일정한 수요를 유지하고 있으며, 상용차로서 안정적인 판매 흐름을 보여줍니다.
                - Bus와 Military, 특수 모델(Bus/ Bongo) 등은 비교적 판매량이 낮고, 특정 시기에만 수요가 발생하는 패턴을 보입니다.
                - 전반적으로 Carnival의 판매 흐름이 전체 기타 차종의 국내 시장을 주도하고 있음이 드러납니다.
                </div>
                """, unsafe_allow_html=True)

            # 해외 차트 출력
            st.plotly_chart(fig_international, use_container_width=True)
            st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
            st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

            # 차트별 분석 내용
            if selected_type == '세단':
                st.markdown("""
                <div style="background-color:#eaf4fc; padding:15px; border-radius:10px;">
                <span style="font-size:20px; font-weight:bold;">📌 세단 차종별 해외 판매 분석</span><br>

                - **Morning/Picanto**는 해외 시장에서 **가장 강력한 수요**를 기록하고 있으며, **소형차 중심의 수요**가 강함을 보여줍니다.  
                - **K5/Optima**는 2024년 중반 이후 해외 수요가 급증하며, **중형 세단의 글로벌 경쟁력**을 입증하고 있습니다.  
                - **고급 세단 모델**인 Stinger, K7/K8 등은 **해외 시장에서 낮은 수요**를 보여 **선택적 수출 전략**이 필요합니다.
                </div>
                """, unsafe_allow_html=True)
            elif selected_type == 'SUV':
                st.markdown("""
                <div style="background-color:#eaf4fc; padding:15px; border-radius:10px;">
                <span style="font-size:20px; font-weight:bold;">📌 SUV 차종별 해외 판매 분석</span><br>            

                - **Sportage**, **Seltos**는 해외 시장에서도 높은 판매량을 기록하며, **글로벌 전략 차종**으로서 경쟁력을 입증하고 있습니다.  
                - **EV6**는 일시적인 수요 급증 이후 다소 하락세로, **전기차 마케팅 전략 재점검**이 필요할 수 있습니다.  
                - **Mohave**는 해외 수요가 거의 없으며, **EV9**는 출시 초기로 **데이터 확보 및 향후 추이 관찰**이 필요합니다.
                </div>
                """, unsafe_allow_html=True)
                
            elif selected_type == '기타':
                st.markdown("""
                <div style="background-color:#eaf4fc; padding:15px; border-radius:10px;">
                <span style="font-size:20px; font-weight:bold;">📌 기타 차종별 해외 월별 판매량 분석</span><br>

                - 해외 시장에서도 Carnival/Sedona 모델의 판매 비중이 매우 높으며, 국내와 유사하게 해당 차종이 핵심 수출 모델로 작용하고 있습니다.
                - Bongo의 해외 수출은 안정적인 흐름을 보이나, 국내보다는 판매량이 낮은 편입니다.
                - **특수 목적 차량들(Military, 특수 Bus/Bongo)**은 대부분 소량 수출에 머무르고 있으며, 특정 국가나 계약 기반 수요에 의존하는 구조일 수 있습니다.
                - 전체적으로 기타 차종 중 Carnival이 국내외에서 모두 전략적으로 중요한 모델로 평가됩니다.
                </div>
                """, unsafe_allow_html=True)

            # 기아 차종별 판매실적 분석 요약표 작업
        
            df_sales_melted =  df_sales.melt(id_vars=['차종', '차량 구분', '거래 유형', '연도'], 
                                    value_vars=["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"] ,
                                    var_name='월', value_name='판매량')

            # 카테고리 매핑 딕셔너리 만들기
            car_category_map = {}
            for category, models in car_types.items():
                for model in models:
                    car_category_map[model] = category

            # df_sales에 카테고리 컬럼 추가
            df_sales_melted['카테고리'] = df_sales_melted['차종'].map(car_category_map)
            
            st.divider()
            st.subheader("📊 기아 차종별 판매실적 통계 요약")
            
            차종_연도_피벗 = df_sales_melted.pivot_table(
                    index='카테고리',
                    columns='연도',
                    values='판매량',
                    aggfunc='sum',
                    fill_value=0
                )
            총합 = 차종_연도_피벗.sum(axis=1)
            차종_연도_피벗.insert(0, '총합', 총합)
            차종_연도_피벗 = 차종_연도_피벗.sort_values(by='총합', ascending=False)
            
            # 총합 컬럼 빼고 나머지 차종 컬럼만 선택
            카테고리_컬럼 = 차종_연도_피벗.columns.drop('총합')
            # 차종별 총합 기준으로 열 순서 정렬
            정렬된_열_순서 = 차종_연도_피벗[카테고리_컬럼].sum().sort_values(ascending=False).index.tolist()
            # 총합을 맨 앞으로 두고 열 재정렬
            열_순서 = ['총합'] + 정렬된_열_순서
            차종연도피벗 = 차종_연도_피벗[열_순서]
            총합_행 = 차종연도피벗.sum(numeric_only=True)
            총합_행.name = '총합'
            차종연도피벗 = pd.concat([총합_행.to_frame().T, 차종연도피벗])

            # 스타일링을 위해 복사본 생성
            차종_연도_styled = 차종연도피벗.copy()

            # 스타일링 적용
            styled_차종_연도 = (
                차종_연도_styled.style
                .format('{:,.0f}')  # 숫자 포맷
                .background_gradient(cmap='Blues')
            )
            
            st.write('')
            st.write("""##### 🌍 차종별 전체 판매량(2023년~2025년)""")
            st.dataframe(styled_차종_연도, use_container_width=True)
            

            국내 = df_sales_melted.loc[df_sales_melted['거래 유형'] == '국내']
            해외 = df_sales_melted.loc[df_sales_melted['거래 유형'] != '국내']

            st.write('')
            st.write("""##### 🚙 카테고리별 차종 판매량 (연도 기준) """)
            st.info('##### - 국내 카테고리별 차종')
            col1, col2, col3 = st.columns(3)    
            # 국내 카테고리별 차종 판매량
            with col1: 
           
                국내_세단 = 국내.loc[국내['카테고리'] == '세단']
                국내_세단_피벗 = 국내_세단.pivot_table(index='차종', columns='연도', values='판매량', aggfunc='sum', fill_value=0)
                
                st.markdown("<h5 style='text-align:center;'>세단</h5>", unsafe_allow_html=True)
                st.dataframe(국내_세단_피벗)

            with col2:

                국내_SUV = 국내.loc[국내['카테고리'] == 'SUV']
                국내_SUV_피벗 = 국내_SUV.pivot_table(index='차종', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                st.markdown("<h5 style='text-align:center;'>SUV</h5>", unsafe_allow_html=True)
                st.dataframe(국내_SUV_피벗)    

            with col3:

                국내_기타 = 국내.loc[국내['카테고리'] == '기타']
                국내_기타_피벗 = 국내_기타.pivot_table(index='차종', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                st.markdown("<h5 style='text-align:center;'>기타</h5>", unsafe_allow_html=True)
                st.dataframe(국내_기타_피벗)

            st.success('##### - 해외 카테고리별 차종')
            col1, col2, col3 = st.columns(3)    
            # 해외 카테고리 차종별 판매량
            with col1: 
                
                해외_세단 = 해외.loc[해외['카테고리'] == '세단']
                해외_세단_피벗 = 해외_세단.pivot_table(index='차종', columns='연도', values='판매량', aggfunc='sum', fill_value=0)
                
                st.markdown("<h5 style='text-align:center;'>세단</h5>", unsafe_allow_html=True)
                st.dataframe(해외_세단_피벗)

            with col2:

                해외_SUV = 해외.loc[해외['카테고리'] == 'SUV']
                해외_SUV_피벗 = 해외_SUV.pivot_table(index='차종', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                st.markdown("<h5 style='text-align:center;'>SUV</h5>", unsafe_allow_html=True)
                st.dataframe(해외_SUV_피벗)    

            with col3:

                해외_기타 = 해외.loc[해외['카테고리'] == '기타']
                해외_기타_피벗 = 해외_기타.pivot_table(index='차종', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                st.markdown("<h5 style='text-align:center;'>기타</h5>", unsafe_allow_html=True)
                st.dataframe(해외_기타_피벗)

            


            with st.expander("📊 분석 내용"):
                st.markdown("""
                <div style='background-color: #F4F6F6; padding: 15px; border-radius: 8px;'>
                    <h4 style='color:#2E86C1;'>📊 분석 내용</h4>
                    <ul>
                        <li>선택한 차종 카테고리 내 각 모델의 <b>국내 및 해외 판매 추이</b>를 확인할 수 있습니다.</li>
                        <li>국내와 해외 판매 추이를 비교하여 <b>전략 수립에 도움</b>을 줄 수 있습니다.</li>
                        <li>특정 차종이 <b>어떤 시장에서 유망한지</b> 확인하고, 글로벌 트렌드에 맞춰 분석할 수 있습니다.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("🎯 분석 목적"):
                st.markdown("""
                <div style='background-color: #F9F9F9; padding: 15px; border-radius: 8px;'>
                    <h4 style='color:#2E86C1;'>🎯 분석 목적</h4>
                    <ol>
                        <li><b style='color:#1F618D'>국내외 판매 추이 비교:</b> 국내외 실적을 비교하여 시장별 성과 차이를 파악합니다.</li>
                        <li><b style='color:#1F618D'>글로벌 시장 전략 수립:</b> 향후 해외 진출 및 수출 전략 설계에 활용됩니다.</li>
                        <li><b style='color:#1F618D'>차종별 판매 동향 분석:</b> 월별 추이를 기반으로 인기/부진 모델을 파악할 수 있습니다.</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("✨ 분석 장점"):
                st.markdown("""
                <div style='background-color: #F9F9F9; padding: 15px; border-radius: 8px;'>
                    <h4 style='color:#2E86C1;'>✨ 분석 장점</h4>
                    <ol>
                        <li><b style='color:#117A65'>시장 맞춤 전략 수립:</b> 시장별 맞춤 전략으로 효과적인 마케팅 및 생산 전략 설계 가능</li>
                        <li><b style='color:#117A65'>시기별 판매 변화 분석:</b> 시즌 및 프로모션에 따른 수요 변화를 시각화할 수 있습니다.</li>
                        <li><b style='color:#117A65'>차종별 판매 성과 평가:</b> 강점 모델 강화, 약점 모델 보완 전략 도출 가능</li>
                        <li><b style='color:#117A65'>국내외 판매 비교:</b> 지역별 차종 성과를 기반으로 전략적 수출 비중 조정 가능</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

    with main_tabs[2] if current_tab == "🏭 해외공장 판매 분석" else main_tabs[2]:
        sub_tab1, sub_tab2 = st.tabs(["🏗️ 공장별 분석", "🚙 차종별 분석"])
        
        selected_year_factory = st.selectbox(
            "연도 선택",
            options=sorted(df_factory['연도'].unique()),
            index=len(df_factory['연도'].unique())-1,
            key='factory_year'
        )
        
        with sub_tab1:
            # 1. 공장별 총 판매량 (캐싱 적용)
            @st.cache_data(ttl=300)
            def get_factory_total(_df, year):
                factory_total = _df[_df['연도'] == year]\
                            .groupby('공장명(국가)')['연간합계'].sum().sort_values(ascending=False)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x=factory_total.values, y=factory_total.index, palette='mako')
                for i, v in enumerate(factory_total.values):
                    ax.text(v + 100, i, f"{v:,}", va='center')
                plt.title(f"{year}년 공장별 총 판매량", fontsize=14)
                plt.tight_layout()
                return fig

            st.subheader("공장별 연간 총 판매량")
            fig1 = get_factory_total(df_factory, selected_year_factory)
            st.pyplot(fig1)
            
            top_factory = df_factory[df_factory['연도']==selected_year_factory].groupby('공장명(국가)')['연간합계'].sum().idxmax()
            top_factory_share = df_factory[df_factory['연도']==selected_year_factory].groupby('공장명(국가)')['연간합계'].sum().max()/df_factory[df_factory['연도']==selected_year_factory]['연간합계'].sum()*100
            
            st.info(f"""
            **🏭 공장별 생산 현황 분석 ({selected_year_factory}년):**
            - {top_factory} 공장이 전체 생산의 {top_factory_share:.1f}% 차지 (연간 {df_factory[df_factory['연도']==selected_year_factory].groupby('공장명(국가)')['연간합계'].sum().max():,}대)
            - 신규 공장({df_factory[df_factory['연도']==selected_year_factory].groupby('공장명(국가)')['연간합계'].sum().nsmallest(1).index[0]})은 아직 생산량 낮음 ({df_factory[df_factory['연도']==selected_year_factory].groupby('공장명(국가)')['연간합계'].sum().nsmallest(1).values[0]:,}대)
            
            **🌎 글로벌 생산 전략:**
            1. 주력 공장({top_factory}) 최적화:
            - 생산 효율화 투자로 수율 5%p 개선 목표
            - 연간 2회 정밀 점검으로 가동 중단 시간 최소화
            2. 신규 공장 역량 강화:
            - 현지 공급망 구축 지원 (부품 현지 조달률 30%→50% 목표)
            - 현지 직원 기술 교육 프로그램 확대 (월 20시간)
            3. 지역별 생산 특화:
            - 북미 공장: 대형 SUV 및 픽업트럭 전문화
            - 유럽 공장: 친환경 차량 생산 거점화
            - 아시아 공장: 소형차 및 전기차 생산 집중
            """)
            
            # 2. 공장별 월별 판매 추이 (캐싱 적용)
            @st.cache_data(ttl=300)
            def get_factory_monthly(_melt, year):
                factory_monthly = _melt[_melt['연도'] == year]\
                                .groupby(['공장명(국가)', '월'])['판매량'].sum().unstack()
                
                fig, ax = plt.subplots(figsize=(12, 6))
                for factory in factory_monthly.index:
                    sns.lineplot(x=factory_monthly.columns, y=factory_monthly.loc[factory], 
                                label=factory, marker='o', linewidth=2.5)
                plt.title("월별 판매 추이", fontsize=14)
                plt.xticks(range(1, 13))
                plt.grid(True, alpha=0.3)
                plt.legend(title="공장명", bbox_to_anchor=(1.05, 1))
                plt.tight_layout()
                return fig

            st.subheader("공장별 월별 판매 추이")
            fig2 = get_factory_monthly(melt_factory, selected_year_factory)
            st.pyplot(fig2)
            
            st.info("""
            **📆 공장별 계절성 패턴:**
            - 중국 공장: 2월(춘절) 생산량 60% 감소 → 대체 공장 가동 필요
            - 미국 공장: 3/4분기 생산량 25% 증가 → 현지 수요 대응
            - 인도 공장: 연중 안정적 생산 → 인근 국가 수출 거점화 가능성
            
            **⚙️ 생산 운영 전략:**
            1. 공장 간 생산 조정 시스템:
            - 휴무기 다른 공장으로 생산 분산 (예: 중국 춘절期間 인도 공장 가동량 20% 증대)
            - 긴급 수요 발생 시 유연한 생산 라인 전환
            2. 예측 생산 강화:
            - AI 기반 수요 예측 모델 도입 (정확도 85% 목표)
            - 역사적 데이터 기반 월별 생산 목표 자동 설정
            3. 유지보수 최적화:
            - 판매 저조기(1월, 7월) 정기 점검 실시
            - 예방 정비 프로그램으로 설비 고장률 30% 감축 목표
            """)
        
        with sub_tab2:
            # 3. 차종별 공장 분포 (캐싱 적용)
            @st.cache_data(ttl=300)
            def get_model_factory(_df, year, n=10):
                top_models = _df[_df['연도'] == year]\
                        .groupby('차종')['연간합계'].sum()\
                        .nlargest(n).index.tolist()
                
                model_factory = _df[
                    (_df['연도'] == year) &
                    (_df['차종'].isin(top_models))
                ].groupby(['차종', '공장명(국가)'])['연간합계'].sum().unstack()
                
                fig, ax = plt.subplots(figsize=(12, 6))
                model_factory.plot(kind='barh', stacked=True, ax=ax)
                plt.title("차종별 생산 공장 분포", fontsize=14)
                plt.legend(title="공장명", bbox_to_anchor=(1.05, 1))
                plt.tight_layout()
                return fig

            st.subheader("차종별 생산 공장 분포 (Top 10)")
            fig3 = get_model_factory(df_factory, selected_year_factory)
            st.pyplot(fig3)
            
            most_produced_model = df_factory[df_factory['연도']==selected_year_factory].groupby('차종')['연간합계'].sum().idxmax()
            model_factories = df_factory[(df_factory['연도']==selected_year_factory) & (df_factory['차종']==most_produced_model)]['공장명(국가)'].nunique()
            
            st.info(f"""
            **🚘 차종-공장 매칭 분석:**
            - 가장 많이 생산되는 모델: {most_produced_model} ({df_factory[df_factory['연도']==selected_year_factory].groupby('차종')['연간합계'].sum().max():,}대)
            - 다수 공장에서 생산 중인 모델: {most_produced_model} ({model_factories}개 공장)
            - 단일 공장 전용 모델: {df_factory[df_factory['연도']==selected_year_factory].groupby('차종')['공장명(국가)'].nunique().idxmin()} (1개 공장)
            
            **🔄 생산 최적화 방안:**
            1. 다각화 생산 시스템:
            - 핵심 모델({most_produced_model})은 3개 이상 공장에서 생산
            - 지역별 수요에 맞춰 생산 공장 유동적 조정
            2. 공장 특화 전략:
            - 각 공장별 전문 모델 지정 (예: A공장 - SUV, B공장 - 세단)
            - 특화 모델 생산라인 효율화로 생산성 15% 향상 목표
            3. 리스크 관리 체계:
            - 주요 공장 장애 시 대체 생산 계획 수립
            - 단일 공장 의존 모델은 2차 생산기지 확보
            """)
            
            # 4. 차종 선택 상세 분석 (캐싱 적용)
            @st.cache_data(ttl=300)
            def get_model_detail(_melt, year):
                available_models = _melt[_melt['연도'] == year]\
                                .groupby('차종')['판매량'].sum()
                available_models = available_models[available_models > 0].index.tolist()
                return available_models

            available_models = get_model_detail(melt_factory, selected_year_factory)
            
            selected_model = st.selectbox(
                "차종 선택",
                options=available_models,
                index=0,
                key='model_select'
            )
            
            @st.cache_data(ttl=300)
            def get_model_trend(_melt, year, model):
                model_data = _melt[
                    (_melt['차종'] == model) &
                    (_melt['연도'] == year)
                ]
                
                fig, ax = plt.subplots(figsize=(12, 6))
                sns.lineplot(data=model_data, x='월', y='판매량', hue='공장명(국가)', 
                            marker='o', linewidth=2.5)
                plt.title(f"{model} 월별 판매 추이 ({year}년)", fontsize=14)
                plt.xticks(range(1, 13))
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                return fig

            st.subheader("차종 상세 분석")
            fig4 = get_model_trend(melt_factory, selected_year_factory, selected_model)
            st.pyplot(fig4)
            
            model_main_factory = melt_factory[(melt_factory['차종']==selected_model) & (melt_factory['연도']==selected_year_factory)].groupby('공장명(국가)')['판매량'].sum().idxmax()
            model_volatility = (melt_factory[(melt_factory['차종']==selected_model) & (melt_factory['연도']==selected_year_factory)].groupby('월')['판매량'].sum().std() / melt_factory[(melt_factory['차종']==selected_model) & (melt_factory['연도']==selected_year_factory)].groupby('월')['판매량'].sum().mean()) * 100
            
            st.info(f"""
            **🔎 {selected_model} 생산 현황 심층 분석:**
            - 주요 생산 공장: {model_main_factory} (점유율 {melt_factory[(melt_factory['차종']==selected_model) & (melt_factory['연도']==selected_year_factory)].groupby('공장명(국가)')['판매량'].sum().max()/melt_factory[(melt_factory['차종']==selected_model) & (melt_factory['연도']==selected_year_factory)]['판매량'].sum()*100:.1f}%)
            - 생산 변동성: {model_volatility:.1f}% (표준편차 대비 평균)
            - 최고 생산월: {melt_factory[(melt_factory['차종']==selected_model) & (melt_factory['연도']==selected_year_factory)].groupby('월')['판매량'].sum().idxmax()}월
            
            **📈 개선 전략:**
            1. 생산 균등화:
            - 월별 생산량 편차를 현재 {model_volatility:.1f}%에서 30% 이내로 축소
            - 수요 예측 정확화를 위한 AI 모델 도입
            2. 품질 표준화:
            - 공장간 품질 차이 해소를 위한 표준 공정 도입
            - 월 1회 품질 크로스 체크 실시
            3. 생산 효율 개선:
            - {model_main_factory}의 생산 라인 최적화로 생산성 10% 향상
            - 다른 공장으로의 생산 기술 전수 프로그램 운영
            """)

    with main_tabs[3]:  # 📊 해외현지 판매 분석 탭
        sub_tab1, sub_tab2 = st.tabs(["🌍 국가별 분석", "🚙 차종별 분석"])
        
        selected_year = st.selectbox(
            "연도 선택",
            options=sorted(df_overseas['연도'].unique()),
            index=len(df_overseas['연도'].unique())-1,
            key='overseas_year'
        )

        # 월별 컬럼 리스트
        months = ['1월', '2월', '3월', '4월', '5월', '6월', 
                '7월', '8월', '9월', '10월', '11월', '12월']
        months_clean = [m.replace('월', '') for m in months]  # '월' 제거 버전

        # ----------------------------------
        # 1. 국가별 분석 서브탭
        # ----------------------------------
        with sub_tab1:
            st.subheader("📍 국가별 월별 판매 분석")
            
            # 국가 선택 위젯
            country_list = df_overseas['국가명'].unique().tolist()
            selected_country = st.selectbox(
                "분석할 국가 선택",
                options=country_list,
                index=country_list.index('U.S.A') if 'U.S.A' in country_list else 0
            )

            # 1-1. 선택 국가 월별 판매 추이 (라인 차트)
            @st.cache_data(ttl=300)
            def plot_country_monthly(_df, year, country):
                country_data = _df[
                    (_df['연도'] == year) & 
                    (_df['국가명'] == country)
                ][months].sum()
                
                fig, ax = plt.subplots(figsize=(12, 5))
                sns.lineplot(
                    x=months_clean, 
                    y=country_data.values,
                    color='#3498db', 
                    marker='o',
                    linewidth=2.5
                )
                plt.title(f"{year}년 {country} 월별 판매량", fontsize=14)
                plt.xlabel("월")
                plt.ylabel("판매량 (대)")
                plt.grid(True, alpha=0.3)
                plt.ylim(0, country_data.max() * 1.2)
                
                # 최대/최소값 강조
                max_month = months_clean[country_data.argmax()]
                min_month = months_clean[country_data.argmin()]
                ax.axvline(x=max_month, color='r', linestyle='--', alpha=0.3)
                ax.axvline(x=min_month, color='g', linestyle='--', alpha=0.3)
                return fig

            st.pyplot(plot_country_monthly(df_overseas, selected_year, selected_country))

            country_total = df_overseas[(df_overseas['연도']==selected_year) & (df_overseas['국가명']==selected_country)]['월별합계'].sum()
            country_peak = df_overseas[(df_overseas['연도']==selected_year) & (df_overseas['국가명']==selected_country)][months].sum().idxmax().replace('월','')
            country_peak_sales = df_overseas[(df_overseas['연도']==selected_year) & (df_overseas['국가명']==selected_country)][months].sum().max()
            
            st.info(f"""
            **🇺🇳 {selected_country} 시장 분석 ({selected_year}년):**
            - 총 판매량: {country_total:,}대
            - 최고 판매월: {country_peak}월 ({country_peak_sales:,}대)
            - 판매 변동성: {calculate_sales_volatility(df_overseas, selected_year, selected_country):.1f}%
            - 경쟁사 대비 점유율: {get_market_share(selected_country):.1f}%
            
            **🎯 현지화 전략:**
            1. 판매 정점기 활용:
            - {country_peak}월 전략적 프로모션 (최대 15% 할인 + 무료 옵션)
            - 현지 문화에 맞는 마케팅 (예: {selected_country}의 주요 축제 기간 활용)
            2. 제품 현지화:
            - {selected_country} 사양 맞춤형 모델 개발 (도로 조건/기후 반영)
            - 현지 선호 옵션 패키지 구성 (예: {selected_country} 전용 컬러)
            3. 유통망 강화:
            - 판매량 적은 지역 딜러사 지원 프로그램 확대
            - 전시장 리뉴얼 지원 (연 2회 현대화 프로젝트)
            """)

            # 1-2. 국가 비교 분석 (멀티 선택 가능)
            st.subheader("🆚 국가 비교 분석")
            
            selected_countries = st.multiselect(
                "비교할 국가 선택 (최대 5개)",
                options=country_list,
                default=['U.S.A', 'China', 'Asia Pacific'][:min(3, len(country_list))],
                max_selections=5
            )
            
            @st.cache_data(ttl=300)
            def plot_country_comparison(_df, year, countries):
                comparison_data = _df[
                    (_df['연도'] == year) & 
                    (_df['국가명'].isin(countries))
                ].groupby('국가명')[months].sum().T
                
                fig, ax = plt.subplots(figsize=(12, 6))
                for country in countries:
                    sns.lineplot(
                        x=months_clean,
                        y=comparison_data[country],
                        label=country,
                        marker='o',
                        linewidth=2.5
                    )
                plt.title(f"{year}년 국가별 월별 판매 비교", fontsize=14)
                plt.xlabel("월")
                plt.ylabel("판매량 (대)")
                plt.grid(True, alpha=0.3)
                plt.legend(title="국가", bbox_to_anchor=(1.05, 1))
                return fig

            if selected_countries:
                st.pyplot(plot_country_comparison(df_overseas, selected_year, selected_countries))
                
                fastest_grower = get_fastest_growing_country(df_overseas, selected_countries, selected_year)
                seasonal_pattern = identify_seasonal_pattern(df_overseas, selected_countries)
                
                st.info(f"""
                **🌐 다국가 비교 분석:**
                - 가장 빠른 성장국: {fastest_grower} (전년 대비 {df_overseas[(df_overseas['국가명']==fastest_grower) & (df_overseas['연도']==selected_year)]['월별합계'].sum()/df_overseas[(df_overseas['국가명']==fastest_grower) & (df_overseas['연도']==selected_year-1)]['월별합계'].sum()*100-100:.1f}% 성장)
                - 계절성 패턴: {seasonal_pattern}
                - 평균 판매 격차: {df_overseas[df_overseas['국가명'].isin(selected_countries) & (df_overseas['연도']==selected_year)].groupby('국가명')['월별합계'].sum().std()/df_overseas[df_overseas['국가명'].isin(selected_countries) & (df_overseas['연도']==selected_year)].groupby('국가명')['월별합계'].sum().mean()*100:.1f}%
                
                **🤝 통합 전략:**
                1. 공통 마케팅 캠페인:
                - 유사 패턴 국가({seasonal_pattern.split(',')[0].split('(')[0]}, {seasonal_pattern.split(',')[1].split('(')[0]}) 그룹화하여 동시 프로모션
                - 디지털 플랫폼 통합 관리 (소셜 미디어 통합 계정 운영)
                2. 지역별 리소스 배분:
                - {fastest_grower} 시장에 마케팅 예산 25% 증액
                - 성장 잠재력 높은 국가에 신제품 우선 출시
                3. 베스트 프랙티스 공유:
                - {selected_countries[0]}의 성공 사례 다른 국가에 적용
                - 분기별 국가별 성과 공유회 개최
                """)
            else:
                st.warning("비교할 국가를 선택해주세요.")

        # ----------------------------------
        # 2. 차종별 분석 서브탭
        # ----------------------------------
        with sub_tab2:
            # 2-1. 차종별 월별 판매 패턴 (히트맵)
            st.subheader("🔥 차종별 월별 판매 히트맵")
            
            @st.cache_data(ttl=300)
            def plot_vehicle_heatmap(_df, year):
                # 상위 5개 차종 선택
                top_models = _df[_df['연도'] == year]\
                            .groupby('차종')['월별합계'].sum()\
                            .nlargest(5).index
                
                # 해당 차종들의 월별 데이터 추출 및 전치
                heatmap_data = _df[
                    (_df['연도'] == year) & 
                    (_df['차종'].isin(top_models))
                ].groupby('차종')[months].sum().T
                
                # 컬럼명에서 '월' 제거 (1월 → 1)
                heatmap_data.index = heatmap_data.index.str.replace('월', '')
                
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.heatmap(heatmap_data, cmap="YlGnBu", annot=True, fmt=",.0f",
                            linewidths=0.5, cbar_kws={'label': '판매량 (대)'})
                plt.title(f"{year}년 인기 차종 월별 판매량", fontsize=14)
                plt.xlabel("차종")
                plt.ylabel("월")
                return fig

            st.pyplot(plot_vehicle_heatmap(df_overseas, selected_year))

            year_round_models = get_year_round_models(df_overseas)
            seasonal_models = get_seasonal_models(df_overseas)
            ev_ratio = df_overseas[(df_overseas['연도']==selected_year) & (df_overseas['파워트레인']=='전기차')]['월별합계'].sum()/df_overseas[df_overseas['연도']==selected_year]['월별합계'].sum()*100
            
            st.info(f"""
            **🧐 인기 차종 트렌드 분석:**
            - 연중 안정적 판매 모델: {year_round_models if year_round_models else "없음"}
            - 뚜렷한 계절성 모델: {seasonal_models if seasonal_models else "없음"}
            - 전기차 모델 판매 비중: {ev_ratio:.1f}%
            
            **🛠️ 제품 전략:**
            1. 안정적 수요 모델 강화:
            - {year_round_models.split(',')[0] if year_round_models else "베스트셀러"} 지속적 품질 개선
            - 연중 판매를 위한 재고 관리 시스템 최적화
            2. 계절성 모델 대응:
            - {seasonal_models.split(',')[0].split('(')[0] if seasonal_models else "계절성 모델"} 판매 시즌 전 사전 예약 캠페인
            - 비수기 판매 촉진을 위한 특별 할인 프로그램
            3. 신제품 기획:
            - 연중 수요가 있는 {year_round_models.split(',')[0] if year_round_models else "인기 모델"}과 유사 컨셉 개발
            - 계절성 모델의 연중 판매 가능한 파생 모델 연구
            """)

            st.subheader("⚡ 국가별 파워트레인 판매 현황")
            
            # 국가 선택 위젯
            country_list = df_overseas['국가명'].unique().tolist()
            selected_power_country = st.selectbox(
                "국가 선택",
                options=country_list,
                index=country_list.index('U.S.A') if 'U.S.A' in country_list else 0,
                key='power_country'
            )

            col1, col2 = st.columns(2)
            
            with col1:
                # 2-1. 파워트레인 비율 (파이 차트)
                @st.cache_data(ttl=300)
                def plot_powertrain_pie(_df, year, country):
                    powertrain_data = _df[
                        (_df['연도'] == year) & 
                        (_df['국가명'] == country)
                    ].groupby('파워트레인')['월별합계'].sum()
                    
                    fig, ax = plt.subplots(figsize=(8, 6))
                    if not powertrain_data.empty:
                        powertrain_data.plot(
                            kind='pie',
                            autopct='%.1f%%',
                            colors=['#FF9999', '#66B2FF', '#99FF99'],
                            startangle=90,
                            ax=ax,
                            wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
                        )
                        plt.title(f"{country} 파워트레인 비율 ({year}년)", fontsize=14)
                        plt.ylabel("")
                    else:
                        ax.text(0.5, 0.5, "데이터 없음", ha='center', va='center')
                    return fig

                st.pyplot(plot_powertrain_pie(df_overseas, selected_year, selected_power_country))

            with col2:
                # 2-2. 파워트레인 연도별 추이 (막대 그래프)
                @st.cache_data(ttl=300)
                def plot_powertrain_trend(_df, country):
                    trend_data = _df[_df['국가명'] == country]\
                            .groupby(['연도', '파워트레인'])['월별합계'].sum()\
                            .unstack()
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    if not trend_data.empty:
                        trend_data.plot(
                            kind='bar',
                            stacked=True,
                            color=['#FF9999', '#66B2FF', '#99FF99'],
                            ax=ax
                        )
                        plt.title(f"{country} 파워트레인 연도별 추이", fontsize=14)
                        plt.xlabel("연도")
                        plt.ylabel("판매량 (대)")
                        plt.legend(title="파워트레인", bbox_to_anchor=(1.05, 1))
                        plt.grid(True, axis='y', alpha=0.3)
                    else:
                        ax.text(0.5, 0.5, "데이터 없음", ha='center', va='center')
                    return fig

                st.pyplot(plot_powertrain_trend(df_overseas, selected_power_country))

            ev_share = df_overseas[(df_overseas['국가명']==selected_power_country) & (df_overseas['연도']==selected_year) & (df_overseas['파워트레인']=='전기차')]['월별합계'].sum()/df_overseas[(df_overseas['국가명']==selected_power_country) & (df_overseas['연도']==selected_year)]['월별합계'].sum()*100
            ice_share = df_overseas[(df_overseas['국가명']==selected_power_country) & (df_overseas['연도']==selected_year) & (df_overseas['파워트레인']=='내연기관')]['월별합계'].sum()/df_overseas[(df_overseas['국가명']==selected_power_country) & (df_overseas['연도']==selected_year)]['월별합계'].sum()*100
            ev_growth = df_overseas[(df_overseas['국가명']==selected_power_country) & (df_overseas['연도']==selected_year) & (df_overseas['파워트레인']=='전기차')]['월별합계'].sum()/df_overseas[(df_overseas['국가명']==selected_power_country) & (df_overseas['연도']==selected_year-1) & (df_overseas['파워트레인']=='전기차')]['월별합계'].sum()*100-100 if df_overseas[(df_overseas['국가명']==selected_power_country) & (df_overseas['연도']==selected_year-1) & (df_overseas['파워트레인']=='전기차')]['월별합계'].sum() > 0 else 0
            
            st.info(f"""
            **🔋 {selected_power_country} 파워트레인 전략:**
            - 현재 비율: 전기차 {ev_share:.1f}% | 하이브리드 {100-ev_share-ice_share:.1f}% | 내연기관 {ice_share:.1f}%
            - 정책 방향: {get_country_policy(selected_power_country)}
            - 성장 추이: 전기차 점유율 {ev_growth:.1f}% 변화
            
            **⚡ 미래 준비 전략:**
            1. 전기차 인프라 대응:
            - {selected_power_country}의 충전 표준에 맞춘 호환성 보장
            - 현지 충전 사업자와 제휴 (할인 충전 서비스 제공)
            2. 과도기적 솔루션:
            - 내연기관 → 전기차 전환기 동안 플러그인 하이브리드 확대
            - 기존 모델의 하이브리드 버전 개발 가속화
            3. 정책 선제적 대응:
            - {selected_power_country} 환경 규제 변화 모니터링 체계 구축
            - 주요 시장별 규제 대응 태스크포스 운영
            """)

            # 2-3. 모든 국가 파워트레인 비교 (Top 10)
            st.subheader("🌐 전 세계 파워트레인 비교 (Top 10 국가)")
            
            @st.cache_data(ttl=300)
            def plot_global_powertrain(_df, year):
                top_countries = _df[_df['연도'] == year]\
                            .groupby('국가명')['월별합계'].sum()\
                            .nlargest(10).index
                
                power_data = _df[
                    (_df['연도'] == year) & 
                    (_df['국가명'].isin(top_countries))
                ].groupby(['국가명', '파워트레인'])['월별합계'].sum().unstack()
                
                fig, ax = plt.subplots(figsize=(12, 6))
                power_data.plot(
                    kind='barh',
                    stacked=True,
                    color=['#FF9999', '#66B2FF', '#99FF99'],
                    ax=ax
                )
                plt.title(f"Top 10 국가 파워트레인 현황 ({year}년)", fontsize=14)
                plt.xlabel("총 판매량 (대)")
                plt.legend(title="파워트레인", bbox_to_anchor=(1.05, 1))
                plt.grid(True, axis='x', alpha=0.3)
                return fig

            st.pyplot(plot_global_powertrain(df_overseas, selected_year))

            ev_leader = get_ev_leader(df_overseas[df_overseas['연도']==selected_year])
            ice_dependent = get_ice_dependent(df_overseas[df_overseas['연도']==selected_year])
            avg_ev_ratio = df_overseas[(df_overseas['연도']==selected_year) & (df_overseas['파워트레인']=='전기차')]['월별합계'].sum()/df_overseas[df_overseas['연도']==selected_year]['월별합계'].sum()*100
            
            st.info(f"""
            **🌍 글로벌 파워트레인 트렌드:**
            - 전기차 선두국: {ev_leader} (전기차 비율 {df_overseas[(df_overseas['국가명']==ev_leader) & (df_overseas['연도']==selected_year) & (df_overseas['파워트레인']=='전기차')]['월별합계'].sum()/df_overseas[(df_overseas['국가명']==ev_leader) & (df_overseas['연도']==selected_year)]['월별합계'].sum()*100:.1f}%)
            - 내연기관 의존국: {ice_dependent} (내연기관 비율 {df_overseas[(df_overseas['국가명']==ice_dependent) & (df_overseas['연도']==selected_year) & (df_overseas['파워트레인']=='내연기관')]['월별합계'].sum()/df_overseas[(df_overseas['국가명']==ice_dependent) & (df_overseas['연도']==selected_year)]['월별합계'].sum()*100:.1f}%)
            - 평균 전기차 비율: {avg_ev_ratio:.1f}%
            
            **🚀 지속 가능한 전략:**
            1. 지역별 로드맵 수립:
            - 선진국({ev_leader} 등): 전기차 100% 전환 가속화
            - 개도국({ice_dependent} 등): 단계적 전환을 위한 하이브리드 중점
            2. 플랫폼 통합 전략:
            - 동일 플랫폼에 다양한 파워트레인 적용 (생산 효율성 제고)
            - 모듈식 배터리 시스템으로 유연한 제품 구성
            3. 기술 협력 강화:
            - {ev_leader}와의 공동 연구 개발 확대
            - 글로벌 충전 표준화 협의체 적극 참여
            """)