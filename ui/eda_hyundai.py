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



# 데이터 로드 함수
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df_export = pd.read_csv(os.path.join(BASE_DIR, "data/현대_지역별수출실적.csv"))
    df_export = pd.read_csv("data/현대_지역별수출실적.csv")
    df_sales = pd.read_csv(os.path.join(BASE_DIR, "data/현대_차종별판매실적.csv"))
    return df_export, df_sales

df_export, df_sales = load_data()

# 메인 함수
def run_eda_hyundai():

    st.markdown("<h1 style='text-align: center;'>🏎️ 현대 수출실적 대시보드</h1>", unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["📊 지역별 수출 분석", "🏎️ 차종별 판매 분석"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f9f9f9"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "padding": "10px"},
            "nav-link-selected": {"background-color": "#2E86C1", "color": "white"},
        }
    )

    if selected == "📊 지역별 수출 분석":
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.subheader("📊 지역별 수출 실적 변화")

        # 데이터 전처리 (차량 구분을 고려하지 않고 모든 데이터를 사용)
        df_export_filtered = df_export.copy()  # 차량 구분 없이 전체 데이터를 사용
        countries = df_export_filtered['국가'].unique()

        selected_countries = st.multiselect("국가를 선택하세요:", options=list(countries), default=list(countries))

        if selected_countries:
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            for country in selected_countries:
                country_data = df_export_filtered[df_export_filtered['국가'] == country].copy()

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
                dates = pd.date_range(start='2023-01-01', periods=len(monthly_sales), freq='M')
                dates = dates[dates <= pd.to_datetime('2025-03-01')]
                monthly_sales = monthly_sales[:len(dates)]

                # NaN 값을 제외한 데이터만 플롯
                valid_indices = [i for i, x in enumerate(monthly_sales) if pd.notna(x)]
                valid_dates = [dates[i] for i in valid_indices]  # Use list comprehension
                valid_sales = [monthly_sales[i] for i in valid_indices]  # Use list comprehension

                fig.add_trace(
                    go.Scatter(x=valid_dates, y=valid_sales, mode='lines+markers', name=country,
                            hovertemplate='%{x|%Y-%m-%d}<br>판매량: %{y:,.0f}<extra></extra>')
                )
            
            # x축 범위를 데이터에 맞게 조정
            fig.update_layout(
                title='주요 시장별 수출량 변화', 
                xaxis_title='날짜', 
                yaxis_title='판매량', 
                legend_title='국가', 
                hovermode="closest",
                xaxis_range=[min(valid_dates), max(valid_dates)] if valid_dates else None  # 데이터가 있는 경우에만 범위 설정
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
            '세단 내연기관': [
                'Avante (CN7)', 'Sonata (LF)', 'Sonata (DN8)',
                'Grandeur (IG)', 'Grandeur (GN7)', 'G70 (IK)',
                'G80 (RG3)', 'G90 (HI)',  'Verna (Hci)', 'Verna (BN7i)',
                'Elantra (CN7c)', 'La festa (SQ)', 'Verna (YC)',
                'Celesta (ID)', 'Mistra (DU2)', 'Elantra (CN7a)',
                'Sonata (DN8a)', 'Solaris (HCr)', 'Accent (HCv)',
                'Accent (BN7v)', 'Elantra (CN7v)'
            ],
            '세단 하이브리드': [
                'Avante (CN7 HEV)', 'IONIQ (AE HEV)', 'Sonata (DN8 HEV)',
                'Grandeur (IG HEV)', 'Grandeur (GN7 HEV)'
            ],
            '세단 전기차': [
                'IONIQ (AE EV)', 'IONIQ 6 (CE)', 'G80 (RG3 EV)'
            ],
            'SUV 내연기관': [
                'Venue (QX)', 'Kona (OS)',  'Kona (SX2)', 'Tucson (TL)',
                'Tucson (NX4)', 'Santa-Fe (TM)', 'Santa-Fe (MX5)',
                'Palisade (LX2)', 'GV80 (JX)', 'Exter (AI3 SUV)', 'Venue (QXi)',
                'Creta (SU2i)', 'Creta(SU2i)', 'Bayon (BC3 CUV)',
                'Mufasa (NU2)', 'Tucson (NX4c)', 'ix35 (NU)',
                'Santa Fe (MX5c)', 'Santa Fe (TMc)', 'Tucson (NX4a)',
                'Tucson OB (NX4a OB)', 'Santa-Fe (TMa)', 'GV70 (JKa)',
                'Tucson (TLe)', 'Tucson (NX4e)',  'Creta (SU2r)',
                'Creta (GSb)', 'Creta (SU2b)', 'Santa-Fe (TMid)',
                'Santa-Fe (MX5id)',  'Creta (SU2id)',
                'Creta (SU2v)', 'Tucson (NX4v)', 'Santa Fe (TMv)',
                'Santa Fe (MX5v)', 'Palisade (LX3)',
                'GV80 Coupe (JX Coupe)'
            ],
            'SUV 하이브리드': [
                'Kona (OS HEV)', 'Kona (SX2 HEV)', 'Tucson (NX4 HEV)',
                'Santa-Fe (TM HEV)', 'Santa-Fe (MX5 HEV)',
                'Santa Fe HEV (TMa HEV)', 'Tucson HEV (NX4c HEV)',
                'Santa-Fe HEV (MX5a HEV)',  'Tucson HEV (NX4e HEV)',
                'Santa Fe HEV (TMv HEV)', 'Santa-Fe (MX5id HEV)'
            ],
            'SUV 전기차': [
                'Kona (OS EV)', 'Kona (OS N)', 'Kona (SX2 EV)', 'NEXO (FE)',
                'IONIQ 5 (NE)', 'IONIQ 5 N (NE N)', 'Kona N (OS N)',
                'Tucson (NX4 PHEV)', 'Santa-Fe (TM PHEV)',
                'Santa-Fe (MX5 PHEV)', 'GV70 EV (JK EV)',
                'Kona EV (OSi EV)', 'IONIQ5 (NEi)', 'Tucson (NX4i)',
                'Exter(AI3 SUV)', 'Venue(QXi)', 'Creta(SU2i)',
                'Creta(SU2i LWB)', 'Tucson OB (NX4a OB)',  'Ioniq5 (NEa)',
                'Kona EV (OSe EV)', 'Kona EV (SX2e EV)',
                'Tucson PHEV (NX4e PHEV)',  'Kona EV (SX2id EV)',
                'IONIQ5 (NE)', 'IONIQ5 (NEid N)', 'GV70 (JKa)',
                'GV70 EV (Jka EV)', 'IONIQ5 (NEv)', 'GV60 (JW)',
                'Palisade (LX3 HEV)', 'Palisade (LX2v)', 'Santa Fe (TMv)'
            ],
            '기타': [
                'Veloster (JS N)', 'G70 S/B (IK S/B)', 'Casper (AX)', 'LCV',
                'HCV', 'i30 (PD)', 'Grand i10 (AI3 5DR)', 'i20 (BI3 5DR)',
                'i10 (AC3)', 'i20 (BC3)', 'i20 N (BC3 N)', 'Custo (KU)',
                'BHMC', 'i30 (PDe)', 'i30 (Pde N)', 'HB20 (BR2)',
                'Stargazer (KS)', 'HTBC', 'NX4m', 'HCm', 'Others', 'CV',
                'i10(AI3v 4DR)', 'i10(AI3v 5DR)', 'Kusto (KUv)', 'Porter (HRv)',
                'Mighty (LTv)', 'Mighty (VTv)', 'Mighty (QTv)',
                'Mighty (QTc)', 'Truck',  'IONIQ5 Robotaxi (NE R)',
                'PV', 'G90', 'Casper (AX EV)', 'Casper EV (AX EV)',
                'IONIQ New Car (ME)', 'Palisade (LX3 HEV)', 'Santa Fe (TMv)', 'Santa Fe (MX5v)'
            ]
                   
        }

        # 연도 선택 UI
        year_filter = st.radio(
            "연도 선택",
            ["2023년", "2024년", "전체"],
            horizontal=True,
            key="year_selection"
        )

        # 데이터 필터링 로직 (수정된 부분)
        if year_filter == '2023년':
            available_models = df_sales[df_sales['연도'] == 2023]['차량 모델'].unique()
            df_filtered = df_sales[df_sales['연도'] == 2023].copy()
            max_date = pd.to_datetime('2023-12')  # 2023년 12월까지만 표시
        elif year_filter == '2024년':
            available_models = df_sales[df_sales['연도'] == 2024]['차량 모델'].unique()
            df_filtered = df_sales[df_sales['연도'] == 2024].copy()
            max_date = pd.to_datetime('2024-12')  # 2024년 12월까지만 표시
        else:
            available_models = df_sales['차량 모델'].unique()
            df_filtered = df_sales.copy()
            max_date = pd.to_datetime('2025-01')  # 전체 선택 시 2025-01까지

        # 차종 카테고리 필터링
        filtered_car_types = {
            category: [model for model in models if model in available_models]
            for category, models in car_types.items()
        }
        selectable_categories = [category for category, models in filtered_car_types.items() if models]

        # 선택 가능한 카테고리가 없는 경우
        if not selectable_categories:
            st.warning(f"{year_filter}에는 해당 데이터가 없습니다.")
        else:
            selected_type = st.selectbox('차종 카테고리 선택', selectable_categories)
            df_filtered = df_filtered[df_filtered['차량 모델'].isin(filtered_car_types[selected_type])].copy()

            # 내수용/수출용 분리
            df_domestic = df_filtered[df_filtered['판매 구분'] == '내수용']
            df_international = df_filtered[df_filtered['판매 구분'] != '내수용']

            # 월별 데이터 변환 (수정된 함수)
            months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
            month_mapping = {month: idx + 1 for idx, month in enumerate(months)}

            def create_melted_dataframe(df, max_date):
                df_melted = pd.DataFrame()
                for year in df['연도'].unique():
                    year_data = df[df['연도'] == year]
                    for month in months:
                        if month in year_data.columns:
                            temp_df = year_data[['차량 모델', month]].copy()
                            temp_df.rename(columns={month: '판매량'}, inplace=True)
                            temp_df['연도'] = year
                            temp_df['월'] = month
                            df_melted = pd.concat([df_melted, temp_df], ignore_index=True)
                
                df_melted['월'] = df_melted['월'].map(month_mapping)
                df_melted['연도-월'] = pd.to_datetime(
                    df_melted['연도'].astype(str) + '-' + df_melted['월'].astype(str), 
                    format='%Y-%m'
                )
                df_melted = df_melted[df_melted['연도-월'] <= max_date]  # 핵심 수정 부분
                return df_melted

            df_melted_domestic = create_melted_dataframe(df_domestic, max_date)
            df_melted_international = create_melted_dataframe(df_international, max_date)

            # 그래프 생성
            if df_melted_domestic.empty and df_melted_international.empty:
                st.warning(f"{year_filter}에는 {selected_type} 카테고리의 판매 데이터가 없습니다.")
            else:
                # 국내 판매량 그래프
                fig_domestic = px.line(
                    df_melted_domestic,
                    x='연도-월',
                    y='판매량',
                    color='차량 모델',
                    title=f'{selected_type} 국내 월별 판매량 ({year_filter})',
                    labels={'판매량': '판매량 (대)'}
                )
                fig_domestic.update_layout(xaxis_title='연도-월', yaxis_title='판매량')

                # 해외 판매량 그래프
                fig_international = px.line(
                    df_melted_international,
                    x='연도-월',
                    y='판매량',
                    color='차량 모델',
                    title=f'{selected_type} 해외 월별 판매량 ({year_filter})',
                    labels={'판매량': '판매량 (대)'}
                )
                fig_international.update_layout(xaxis_title='연도-월', yaxis_title='판매량')

                # 그래프 표시
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
    run_eda_hyundai()