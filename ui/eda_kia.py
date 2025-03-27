import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
import os

# CSS 스타일링
st.markdown("""
<style>
    /* CSS 스타일 코드 (이전 예시와 동일) */
    /* 이 부분은 현대차 대시보드 스타일을 그대로 가져와서 사용하시면 됩니다. */
</style>
""", unsafe_allow_html=True)

# 데이터 로드 함수
@st.cache_data
def load_data():
    df_export = pd.read_csv("data/기아_지역별수출실적_전처리.csv")
    df_sales = pd.read_csv("data/기아_차종별판매실적.csv")
    return df_export, df_sales

df_export, df_sales = load_data()

# 메인 함수
def run_eda_기아():

    st.markdown("<h1 style='text-align: center;'>🚙 기아 수출실적 대시보드</h1>", unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["🌍 지역별 수출 분석", "🚙 차종별 판매 분석"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f9f9f9"},
            "icon": {"color": "#2E86C1", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "padding": "10px"},
            "nav-link-selected": {"background-color": "#2E86C1", "color": "white"},
        }
    )

    if selected == "🌍 지역별 수출 분석":
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.subheader("🌍 지역별 수출 실적 변화")
        
        # 데이터 전처리 (차량 구분을 고려하지 않고 모든 데이터를 사용)
        df_export_filtered = df_export.copy()  # 차량 구분 없이 전체 데이터를 사용
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
                xaxis=dict(
                    tickformat='%b %Y',  # 월, 연도 형식으로 표시 (예: Jan 2023)
                    dtick="M3",  # 3개월 간격으로 눈금 표시
                ),
                xaxis_range=[min(valid_dates), max(valid_dates)] if valid_dates else None  # 데이터가 있는 경우에만 범위 설정
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

    elif selected == "🚙 차종별 판매 분석":
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.subheader("🚙 차종별 판매 실적")

        car_types = {
            '세단': ['Morning', 'Ray', 'K3', 'K5', 'Stinger', 'K7 / K8', 'K9', "Morning / Picanto", "K5 / Optima", 'K7 / K8 / Cadenza'],
            'SUV': ['Seltos', 'Niro', 'Sportage', 'Sorento', 'Mohave', 'EV6', 'EV9', "Mohave / Borrego"],
            '기타': ['Bongo', 'Carnival', 'Bus', "Carnival / Sedona", "Millitary", "Bongo (특수)", "Bus (특수)"]
        }

        selected_type = st.selectbox('차종 카테고리 선택', list(car_types.keys()))

        df_filtered = df_sales[df_sales['차종'].isin(car_types[selected_type])]

        # 데이터 확인 코드 추가 (디버깅용, 필요에 따라 주석 처리)
        # st.write("df_sales:", df_sales.head())
        # st.write("df_filtered:", df_filtered.head())

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

            # 데이터 확인 코드 추가 (디버깅용, 필요에 따라 주석 처리)
            # st.write("df_melted:", df_melted.head())

            return df_melted

        # 국내와 해외 데이터프레임 생성
        df_melted_domestic = create_melted_dataframe(df_domestic)
        df_melted_international = create_melted_dataframe(df_international)

        # 그래프 그리기
        fig_domestic = px.line(df_melted_domestic, x='연도-월', y='판매량', color='차종',
                                title=f'{selected_type} 차종별 국내 월별 판매량',
                                labels={'연도-월': '연도-월 (Year-Month)', '판매량': '판매량 (Sales Volume)'})
        fig_domestic.update_xaxes(
            range=['2023-01-01', '2025-03-01'],
            dtick="M3",  # 3개월 간격으로 틱 표시
            tickformat="%Y-%m"  # 틱 레이블 형식 지정
        )

        fig_international = px.line(df_melted_international, x='연도-월', y='판매량', color='차종',
                                        title=f'{selected_type} 차종별 해외 월별 판매량',
                                        labels={'연도-월': '연도-월 (Year-Month)', '판매량': '판매량 (Sales Volume)'})
        fig_international.update_xaxes(
            range=['2023-01-01', '2025-03-01'],
            dtick="M3",  # 3개월 간격으로 틱 표시
            tickformat="%Y-%m"  # 틱 레이블 형식 지정
        )

        # 국내 차트 출력
        st.plotly_chart(fig_domestic, use_container_width=True)

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

        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

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

if __name__ == "__main__":
    run_eda_기아()
