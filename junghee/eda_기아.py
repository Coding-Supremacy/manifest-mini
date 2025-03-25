import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
import os



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
    df_export = pd.read_csv("junghee/data/기아_지역별수출실적_전처리.csv")
    df_sales = pd.read_csv("junghee/data/기아_차종별판매실적_전처리.csv")
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

        # 📌 분석 내용 (접힘 가능하게)
        with st.expander("🔍 분석 요약"):
            st.markdown("""
        - 선택한 차량 카테고리 내 모델들의 **국내 및 해외 판매 실적 추이를 비교**할 수 있습니다.
        - 국내외 지역 중 어떤 시장에서 선호도가 높은지 **데이터 기반으로 확인**할 수 있습니다.
        - 특정 차량이 **글로벌 시장에서 성장 중인지** 또는 **시장 대응이 필요한 상태인지** 판단할 수 있습니다.
        """)

        # 🎯 분석 목적
        with st.expander("🎯 분석 목적"):
            st.markdown("""
        1. **국내/해외 판매 비교**: 각 차종의 국내 및 해외 판매 실적을 비교하여 지역별 시장의 수요 차이를 파악합니다.  
        2. **모델별 시장 경쟁력 확인**: 차량별 수요 흐름을 분석하여 특정 지역에서의 경쟁력을 분석합니다.  
        3. **트렌드 기반 대응**: 차량별 수요 증가 또는 감소 트렌드를 분석하여, 타겟 시장에 따른 전략 수립에 활용할 수 있습니다.
        """)

        # ✨ 분석 장점
        with st.expander("✨ 분석 장점"):
            st.markdown("""
        - **시장 흐름 예측**: 국내/해외 시장의 변화를 빠르게 파악할 수 있고, 각 지역의 차종별 판매 현황을 트렌드로 확인할 수 있습니다.  
        - **신차 투입/단종 전략 수립**: 시기별 판매 흐름을 바탕으로 신차 투입 또는 단종 전략 수립 가능  
        - **시각적 비교 용이**: 라인차트를 통해 판매량 흐름을 명확히 비교할 수 있어 직관적인 전략 수립 가능  
        - **데이터 기반 마케팅**: 급등락 모델에 따른 마케팅 타이밍 도출
        """)

        # ✅ 요약 핵심 메시지
        st.info("📌 이 분석은 특정 차종의 수요 급증 또는 하락 패턴을 선제적으로 파악해 마케팅 전략 수립 및 생산 계획 조정에 활용할 수 있습니다.")

        with st.expander("📋 경영진 요약 리포트"):
            st.markdown("### 📦 KPI 요약")
            col1, col2, col3 = st.columns(3)
            col1.metric("총 판매량", "1,050,000대")
            col2.metric("전월 대비 증감률", "+6.1%")
            col3.metric("해외 판매 비중", "54.3%")

            st.markdown("### 🌍 지역별 수출 인사이트")
            st.markdown("- 유럽/인도 중심 수출 증가")
            st.markdown("- 러시아/중동 불안정… 다변화 필요")

            st.markdown("### 🚙 차종별 주요 이슈")
            st.markdown("- K3/K5 등 세단 약세, SUV·EV 강세")
            st.markdown("- EV6/EV9 글로벌 수요 증가")

            st.markdown("### 🎯 전략 제안")
            st.markdown("""
            - ✅ 생산라인 유연화로 수출 중심 차종 대응
            - ✅ 국내 세단 단종 or 리디자인 검토
            - ✅ 전기 SUV 물량 증대 및 마케팅 동시 강화
            """)


        st.markdown("</div>", unsafe_allow_html=True)
if __name__ == "__main__":
    run_eda_기아()
