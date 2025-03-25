import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
import os

# 페이지 설정
st.set_page_config(page_title="🚗 기아 수출실적 대시보드", layout="wide")

# CSS 스타일링 (이전 스타일 코드 그대로 사용)
st.markdown("""
<style>
    /* CSS 스타일 코드 (이전 예시와 동일) */
    /* 이 부분은 현대차 대시보드 스타일을 그대로 가져와서 사용하시면 됩니다. */
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<h1 style='text-align: center; color: #2E86C1;'>🚗 기아 수출실적 대시보드</h1>
<h4 style='text-align: center;'>지역별 수출 실적 및 차종별 판매 분석</h4>
<hr>
""", unsafe_allow_html=True)

# 데이터 로드 함수
@st.cache_data
def load_data():
    df_export = pd.read_csv("../jisang/data/기아_지역별수출실적_전처리.csv")
    df_sales = pd.read_csv("../jisang/data/기아_차종별판매실적_전처리.csv")
    return df_export, df_sales

df_export, df_sales = load_data()

# 메인 함수
def run_eda_기아():
    selected = option_menu(
        menu_title=None,
        options=["📊 지역별 수출 분석", "🚙 차종별 판매 분석"],
        icons=["globe", "car-front"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f9f9f9"},
            "icon": {"color": "#2E86C1", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "padding": "10px"},
            "nav-link-selected": {"background-color": "#2E86C1", "color": "white"},
        }
    )

    if selected == "📊 지역별 수출 분석":
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.subheader("📊 지역별 수출 실적 변화")
        
        # 데이터 전처리
        df_export_filtered = df_export[df_export['차량 구분'] == '총합'].drop(columns=['차량 구분'])
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

                # x축 날짜 생성
                dates = pd.date_range(start='2023-01-01', periods=len(monthly_sales), freq='M')
                dates = dates[dates <= pd.to_datetime('2025-03-01')]
                monthly_sales = monthly_sales[:len(dates)]

                # NaN 값을 제외한 데이터만 플롯
                valid_indices = [i for i, x in enumerate(monthly_sales) if pd.notna(x)]
                valid_dates = dates[valid_indices]
                valid_sales = [monthly_sales[i] for i in valid_indices]

                fig.add_trace(
                    go.Scatter(x=valid_dates, y=valid_sales, mode='lines+markers', name=country,
                               hovertemplate='%{x|%Y-%m-%d}<br>판매량: %{y:,.0f}<extra></extra>')
                )
            
            fig.update_layout(title='주요 시장별 수출량 변화', xaxis_title='날짜', yaxis_title='판매량', legend_title='국가', hovermode="closest")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            ### 분석 목적
            1. **시장 동향 파악**: 기아의 글로벌 시장에서의 성과를 시각화하여 전반적인 수출 동향을 파악합니다.
            2. **지역별 성과 비교**: 다양한 국가 및 지역의 수출 실적을 비교 분석하여 지역별 전략의 효과성을 평가합니다.
            3. **미래 전략 수립**: 과거와 현재의 데이터를 바탕으로 향후 수출 전략 수립에 필요한 인사이트를 도출합니다.

            ### 분석의 장점
            1. **데이터 기반 의사결정**: 객관적인 데이터를 통해 보다 정확하고 신뢰성 있는 의사결정이 가능해집니다.
            2. **트렌드 예측**: 시계열 데이터 분석을 통해 향후 시장 트렌드를 예측할 수 있습니다.
            3. **경쟁력 강화**: 지역별, 시기별 성과 분석을 통해 기업의 강점과 약점을 파악하고 경쟁력을 강화할 수 있습니다.
            4. **리소스 최적화**: 데이터에 기반한 성과 분석으로 마케팅 및 생산 리소스의 효율적 배분이 가능해집니다.
            5. **이해관계자 커뮤니케이션**: 시각화된 데이터를 통해 경영진, 투자자, 직원들과 효과적으로 성과를 공유할 수 있습니다.
            """)
        
        st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "🚙 차종별 판매 분석":
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.subheader("🚙 차종별 판매 실적")

        car_types = {
            '세단': ['Morning', 'Ray', 'K3', 'K5', 'Stinger', 'K7 / K8', 'K9'],
            'SUV': ['Seltos', 'Niro', 'Sportage', 'Sorento', 'Mohave', 'EV6', 'EV9'],
            '기타': ['Bongo', 'Carnival', 'Bus']
        }

        selected_type = st.selectbox('차종 카테고리 선택', list(car_types.keys()))

        df_filtered = df_sales[df_sales['차종'].isin(car_types[selected_type])]

        # 거래유형을 기준으로 데이터 분리
        df_domestic = df_filtered[df_filtered['거래 유형'] == '국내']
        df_international = df_filtered[df_filtered['거래 유형'] != '국내']

        # 연도 및 월 컬럼 추가
        years = range(2023, 2026)
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

            return df_melted

        # 국내와 해외 데이터프레임 생성
        df_melted_domestic = create_melted_dataframe(df_domestic)
        df_melted_international = create_melted_dataframe(df_international)

        # 그래프 그리기
        fig_domestic = px.line(df_melted_domestic, x='연도-월', y='판매량', color='차종', 
                            title=f'{selected_type} 차종의 국내 월별 판매량',
                            labels={'연도-월': '연도-월 (Year-Month)', '판매량': '판매량 (Sales Volume)'})

        fig_international = px.line(df_melted_international, x='연도-월', y='판매량', color='차종', 
                                    title=f'{selected_type} 차종의 해외 월별 판매량',
                                    labels={'연도-월': '연도-월 (Year-Month)', '판매량': '판매량 (Sales Volume)'})

        # 차트 출력
        st.plotly_chart(fig_domestic, use_container_width=True)
        st.plotly_chart(fig_international, use_container_width=True)

        st.markdown("""
        ### 분석 내용:
                    
        - 선택한 차종 카테고리 내 각 모델의 국내 및 해외 판매 추이를 확인할 수 있습니다.
        - 국내와 해외 판매 추이를 비교하여 전략을 수립하는 데 도움을 줄 수 있습니다.
        - 특정 차종이 국내 및 해외 시장에서 어떻게 성과를 내고 있는지, 그리고 어떤 차종이 글로벌 트렌드에 따라 더 유망한지 확인할 수 있습니다.

        ### 분석 목적:
        1. **국내외 판매 추이 비교**: 각 차종의 국내 및 해외 판매 실적을 비교하여 지역별 시장의 성과 차이를 파악합니다.
        2. **글로벌 시장 전략 수립**: 국내외 판매 실적을 기반으로 향후 글로벌 시장에서의 판매 전략을 수립할 수 있습니다.
        3. **차종별 판매 동향 분석**: 각 차종의 월별 판매 추이를 분석하여 인기 모델과 부진한 모델을 파악하고, 판매 전략을 최적화할 수 있습니다.

        ### 분석 장점:
        1. **시장 맞춤 전략 수립**: 국내외 시장에 맞는 차종별 전략을 세우고, 각 시장에 최적화된 판매 전략을 강화할 수 있습니다.
        2. **시기별 판매 변화 분석**: 월별 판매 추이를 통해 시즌별, 프로모션 및 이벤트에 따른 판매 변화를 확인하고, 적절한 시점에 마케팅 전략을 세울 수 있습니다.
        3. **차종별 판매 성과 평가**: 각 차종의 성과를 평가하여, 강점을 극대화하고, 개선이 필요한 차종에 대해 집중할 수 있습니다.
        4. **국내외 판매 비교**: 국내와 해외의 판매 성과를 비교함으로써, 각 지역에서 어떤 차종이 인기가 있는지, 각 시장의 특성을 반영한 전략을 수립할 수 있습니다.
    """)

        st.markdown("</div>", unsafe_allow_html=True)
if __name__ == "__main__":
    run_eda_기아()
