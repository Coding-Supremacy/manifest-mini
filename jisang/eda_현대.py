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
<h1 style='text-align: center; color: #2E86C1;'>🏎️ 현대 수출실적 대시보드</h1>
<h4 style='text-align: center;'>지역별 수출 실적 및 차종별 판매 분석</h4>
<hr>
""", unsafe_allow_html=True)

# 데이터 로드 함수
@st.cache_data
def load_data():
    df_export = pd.read_csv("../jisang/data/현대_지역별수출실적.csv")
    df_sales = pd.read_csv("../jisang/data/현대_차종별판매실적.csv")
    return df_export, df_sales

df_export, df_sales = load_data()

# 메인 함수
def run_eda_현대():

    st.markdown("<h1 style='text-align: center;'>🏎️ 현대 수출실적 대시보드</h1>", unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["📊 지역별 수출 분석", "🏎️ 차종별 판매 분석"],
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
        df_export_filtered = df_export.copy()
        countries = df_export_filtered['국가'].unique()

        selected_countries = st.multiselect("국가를 선택하세요:", options=list(countries), default=list(countries))

        if selected_countries:
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            all_dates = []  # 모든 날짜를 저장할 리스트

            for country in selected_countries:
                country_data = df_export_filtered[df_export_filtered['국가'] == country].copy()
                
                dates = []
                sales_values = []
                
                # 연도와 월 정보를 조합해 실제 날짜 생성
                for idx, row in country_data.iterrows():
                    year = row['연도']
                    for month in range(1, 13):
                        month_col = f"{month}월"
                        if month_col in row:
                            date = pd.to_datetime(f"{year}-{month}-01")
                            dates.append(date)
                            sales_values.append(row[month_col])

                # 2025-03-01 이후 데이터 필터링
                df_plot = pd.DataFrame({'date': dates, 'sales': sales_values})
                df_plot = df_plot[df_plot['date'] <= pd.to_datetime('2025-03-01')]

                # NaN 제거
                df_plot = df_plot.dropna()
                
                all_dates.extend(df_plot['date'])  # 모든 날짜 저장
                
                if not df_plot.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=df_plot['date'], 
                            y=df_plot['sales'], 
                            mode='lines+markers', 
                            name=country,
                            hovertemplate='%{x|%Y-%m}<br>판매량: %{y:,.0f}<extra></extra>'
                        )
                    )

            # x축 범위 설정
            if all_dates:
                min_date = min(all_dates)
                max_date = max(all_dates)
            else:
                min_date = pd.to_datetime('2023-01-01')
                max_date = pd.to_datetime('2025-03-01')

            # 레이아웃 설정
            fig.update_layout(
                title='주요 시장별 수출량 변화',
                xaxis_title='날짜',
                yaxis_title='판매량',
                legend_title='국가',
                hovermode="closest",
                xaxis=dict(
                    range=[min_date, max_date],
                    type="date"
                ),
                margin=dict(l=50, r=50, t=50, b=50),  # 마진 조정
                width=800,  # 그래프 너비 설정
                height=500  # 그래프 높이 설정
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(""" 
            ### 분석 목적
            1. **시장 동향 파악**: 현대의 글로벌 시장에서의 성과를 시각화하여 전반적인 수출 동향을 파악합니다.
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

    elif selected == "🏎️ 차종별 판매 분석":
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.subheader("🏎️ 차종별 판매 실적")

        car_types = {
            '세단': [
                'Avante (CN7)', 'Avante (CN7 HEV)', 'Avante (CN7 N)', 
                'Sonata (LF)', 'Sonata (DN8)', 'Sonata (DN8 HEV)', 
                'Grandeur (IG)', 'Grandeur (IG HEV)', 'Grandeur (GN7)', 
                'Grandeur (GN7 HEV)', 'G70 (IK)', 'G70 S/B (IK S/B)', 
                'G80 (RG3)', 'G80 (RG3 EV)', 'G90 (HI)', 'G90 (RS4)', 
                'i30 (PD)', 'i20 (BI3 5DR)', 'i20 N (BC3 N)', 'Elantra (CN7)', 
                'Elantra (CN7c)', 'Elantra (CN7a)', 'Elantra (CN7v)'
            ],
            'SUV': [
                'Kona (OS)', 'Kona (OS HEV)', 'Kona (OS EV)', 'Kona (OS N)', 
                'Kona (SX2)', 'Kona (SX2 HEV)', 'Kona (SX2 EV)', 'Tucson (TL)', 
                'Tucson (NX4)', 'Tucson (NX4 HEV)', 'NEXO (FE)', 'IONIQ 5 (NE)', 
                'IONIQ 5 N (NE N)', 'Santa-Fe (TM)', 'Santa-Fe (TM HEV)', 
                'Santa-Fe (MX5)', 'Santa-Fe (MX5 HEV)', 'Palisade (LX2)', 
                'GV60 (JW)', 'GV70 (JK)', 'GV70 (JK EV)', 'GV80 (JX)', 
                'GV70 (JKa)', 'GV70 EV (Jka EV)', 'Kona EV (OSi EV)', 
                'Kona EV (SX2e EV)', 'Santa-Fe (MX5c)', 'Santa-Fe (TMc)', 
                'Santa-Fe (TMa)', 'Santa-Fe HEV (TMa HEV)', 'Santa-Fe (MX5a)', 
                'Santa-Fe (MX5a HEV)', 'Kona EV (OSe EV)', 'IONIQ5 (NE)', 
                'IONIQ5 (NEid N)', 'Santa-Fe (TMid)', 'Santa-Fe (MX5id)', 
                'Santa-Fe (MX5id HEV)', 'Creta (SU2i)', 'Creta (SU2i LWB)', 
                'Creta (SU2r)', 'Creta (GSb)', 'Creta (SU2b)', 'Creta (SU2id)', 
                'Exter (AI3 SUV)', 'Venue (QXi)', 'Venue (QX)', 'Bayon (BC3 CUV)', 
                'Stargazer (KS)', 'Tucson (NX4 PHEV)', 'Santa-Fe (MX5 PHEV)', 
                'Santa-Fe (TM PHEV)'
            ],
            '기타': [
                'Casper (AX)', 'Casper (AX EV)', 'Mighty (LTv)', 'Mighty (VTv)', 
                'Mighty (QTv)', 'Mighty (QTc)', 'Porter (HRv)', 'Truck', 
                'CV', 'HB20 (BR2)', 'Xcent (AI3 4DR)', 'Grand i10 (AI3 5DR)', 
                'Verna (Hci)', 'Verna (BN7i)', 'Exter(AI3 SUV)', 'IONIQ New Car (ME)', 
                'HTBC', 'NX4m', 'HCm', 'Others', 'i10 (AC3)', 'i10 (AI3v 4DR)', 
                'i10 (AI3v 5DR)', 'Accent (HCv)', 'Accent (BN7v)', 'Elantra (CN7v)', 
                'Santa Fe (TMv)', 'Santa Fe HEV (TMv HEV)', 'Palisade (LX2v)', 
                'IONIQ5 (NEv)', 'Palisade (LX3)', 'Palisade (LX3 HEV)', 
                'GV80 Coupe (JX Coupe)', 'Casper EV (AX EV)', 'IONIQ6 (CE)', 
                'IONIQ5 Robotaxi (NE R)', 'PV', 'G90', 'Casper (AX EV)', 
                'Palisade (LX3)', 'Palisade (LX3 HEV)', 'GV80 Coupe (JX Coupe)'
            ]
        }

        selected_type = st.selectbox('차종 카테고리 선택', list(car_types.keys()))

        df_filtered = df_sales[df_sales['차량 모델'].isin(car_types[selected_type])]

        # 거래유형을 기준으로 데이터 분리
        df_domestic = df_filtered[df_filtered['판매 구분'] == '내수용']
        df_international = df_filtered[df_filtered['판매 구분'] != '내수용']

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
                        temp_df = year_data[['차량 모델', month]].copy()
                        temp_df.rename(columns={month: '판매량'}, inplace=True)
                        temp_df['연도'] = year
                        temp_df['월'] = month
                        df_melted = pd.concat([df_melted, temp_df], ignore_index=True)

            # "월" 컬럼을 숫자로 변환
            df_melted['월'] = df_melted['월'].map(month_mapping)

            # "연도-월"을 datetime 객체로 변환
            df_melted['연도-월'] = pd.to_datetime(df_melted['연도'].astype(str) + '-' + df_melted['월'].astype(str), format='%Y-%m')

            # 2025년 1월까지만 필터링
            df_melted = df_melted[df_melted['연도-월'] <= pd.to_datetime('2025-01')]

            return df_melted

        # 국내와 해외 데이터프레임 생성
        df_melted_domestic = create_melted_dataframe(df_domestic)
        df_melted_international = create_melted_dataframe(df_international)

        # 그래프 그리기
        fig_domestic = px.line(df_melted_domestic, x='연도-월', y='판매량', color='차량 모델', 
                                title=f'{selected_type} 차량 모델별 국내 월별 판매량',
                                labels={'연도-월': '연도-월 (Year-Month)', '판매량': '판매량 (Sales Volume)'})

        fig_international = px.line(df_melted_international, x='연도-월', y='판매량', color='차량 모델', 
                                        title=f'{selected_type} 차량 모델별 해외 월별 판매량',
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
        3. **차종별 판매 성과 평가**: 각 차종의 성과를
        """)

        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    run_eda_현대()
