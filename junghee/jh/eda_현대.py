import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu






# CSS 스타일링 (이전 스타일 코드 그대로 사용)
st.markdown("""
<style>
    /* CSS 스타일 코드 (이전 예시와 동일) */
    /* 이 부분은 현대차 대시보드 스타일을 그대로 가져와서 사용하시면 됩니다. */
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<h1 style='text-align: center; color: #2E86C1;'>🚗 현대 수출실적 대시보드</h1>
<h4 style='text-align: center;'>지역별 수출 실적 및 차종별 판매 분석</h4>
<hr>
""", unsafe_allow_html=True)

# 데이터 로드 함수
@st.cache_data
def load_data():
    df_export = pd.read_csv("junghee/data/현대_지역별수출실적.csv")
    df_sales = pd.read_csv("junghee/data/현대_차종별판매실적.csv")
    return df_export, df_sales

df_export, df_sales = load_data()

# 메인 함수
def run_eda_현대():
    st.markdown("<h1 style='text-align: center;'>🚗 현대 수출실적 대시보드</h1>", unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["🌍 지역별 수출 분석", "🚙 차종별 판매 분석", "🏭 공장별 판매실적"],
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
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

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
            <div style='background-color:#FFEBCD; padding:20px; border-radius:8px;'>
                <h4 style='font-size:20px;'>📌 주요 시장별 수출량 변화 분석</h4>
                <ul>
                    <li><b>북미·미국</b> 지역의 수출량이 압도적으로 많으며, 전체 수출 전략에서 중심 역할을 하고 있습니다.</li>
                    <li>중남미, 중동·아프리카 등 신흥시장도 점차 성장하는 추세를 보입니다.</li>
                    <li>글로벌 트렌드 및 지역 정책 변화에 따라 수출 비중 조정이 필요한 시점입니다.</li>
                </ul>
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
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

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

        # 국내 차트 출력
        st.plotly_chart(fig_domestic, use_container_width=True)

        # 차트별 분석 내용
        if selected_type == '세단':
            st.markdown("""
            <div style='background-color:#eefaf1; padding:20px; border-radius:8px;'>
            <span style="font-size:20px; font-weight:bold;">📌 세단 차종별 국내 월별 판매량 분석</span><br>
            
            - **그랜저(GN7)** 모델이 국내 시장에서 뚜렷한 우위를 보이며 베스트셀러로 자리잡고 있습니다.
            - 쏘나타(DN8)는 점진적인 감소세를 보여 리디자인 또는 마케팅 강화가 필요한 상황입니다.
            - Avante와 G80은 안정적인 판매 흐름을 보이고 있으나 경쟁 차종에 대한 전략이 필요합니다.
            </div>
            """, unsafe_allow_html=True)
        elif selected_type == 'SUV':
            st.markdown("""
            <div style='background-color:#fff8e7; padding:20px; border-radius:8px;'>
            <span style="font-size:20px; font-weight:bold;">📌 SUV 차종별 국내 월별 판매량 분석</span><br>
                        
            - **투싼(NX4)**, **싼타페** 계열 모델이 국내 시장에서 꾸준한 인기를 보이고 있습니다.
            - 전기차인 **IONIQ 5** 및 **NEXO**의 판매량은 제한적이나, 성장 가능성은 있습니다.
            - 다양한 SUV 라인업이 존재하지만, 특정 월에만 급등하는 모델은 프로모션 영향 가능성이 있습니다.
            </div>
            """, unsafe_allow_html=True)
        elif selected_type == '기타':
            st.markdown("""
            <div style='background-color:#fdf2f8; padding:20px; border-radius:8px;'>
            <span style="font-size:20px; font-weight:bold;">📌 기타 차종별 국내 월별 판매량 분석</span><br>
                    
            - **캐스퍼** 모델이 기타 차종 중 국내 시장에서 가장 안정적인 판매 실적을 기록하고 있습니다.
            - **경상용차 및 버스** 계열은 계절성 수요나 정책 변화에 따라 변화가 큽니다.
            - 일부 모델은 특정 시기에 집중 판매되며, 이는 계약형 납품 또는 기관 수요로 추정됩니다.
            </div>
            """, unsafe_allow_html=True)



        # 해외 차트 출력    
        st.plotly_chart(fig_international, use_container_width=True)

        # 차트별 분석 내용
        if selected_type == '세단':
            st.markdown("""
            <div style='background-color:#eaf4fc; padding:20px; border-radius:8px;'>
            <span style="font-size:20px; font-weight:bold;">📌 세단 차종별 국내 월별 판매량 분석</span><br>
                
            - **Avante (CN7)** 모델이 글로벌 세단 수출의 중심으로, 유럽/중남미에서 강세를 보입니다.
            - 그랜저 및 쏘나타 계열은 일부 지역에서 지속적인 수요가 있으나, 지역별 편차가 큽니다.
            - 친환경 모델의 수요는 아직 제한적이며, 전동화 모델 확대 전략이 필요합니다.
            </div>
            """, unsafe_allow_html=True)

        elif selected_type == 'SUV':
            st.markdown("""
            <div style='background-color:#f0f9ff; padding:20px; border-radius:8px;'>
            <span style="font-size:20px; font-weight:bold;">📌 SUV 차종별 국내 월별 판매량 분석</span><br>
    
            - **Kona** 시리즈와 <b>투싼</b>은 북미 및 유럽 시장에서 높은 수출 실적을 기록하고 있습니다.
            - **전기차 모델(Kona EV, IONIQ 5)**는 점진적 확산을 보이며 전략적 확대가 필요합니다.
            - HEV 및 PHEV 하위 모델도 고르게 분포되어 있어 친환경 차량 포트폴리오 강화에 유리한 구조입니다.
            </div>
            """, unsafe_allow_html=True)

        elif selected_type == '기타':
            st.markdown("""
            <div style='background-color:#f0fff0; padding:20px; border-radius:8px;'>
            <span style="font-size:20px; font-weight:bold;">📌 기타 차종별 국내 월별 판매량 분석</span><br>
                
            - **i10, Xcent** 등 소형차 중심 모델이 아시아/남미 등 신흥국 시장에서 선전하고 있습니다.
            - 상용차 및 트럭 계열 모델들은 소수 지역에 집중 분포하며, 틈새 시장 전략으로 접근할 필요가 있습니다.
            - 복수 모델이 고르게 분산된 구조로, 지역 맞춤형 전략이 유효할 수 있습니다.
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
        
    elif selected == "🏭 공장별 판매실적":

        df = pd.read_csv('junghee/현대_공장별_판매실적_합계제거.csv')

        df_melted = df.melt(
            id_vars=['공장명(국가)', '차량 모델', '판매 구분', '연도'],
            value_vars=["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"],
            var_name='월', value_name='판매량'
        )

        # 날짜 변환
        월_매핑 = {f"{i}월": i for i in range(1, 13)}
        df_melted['월_숫자'] = df_melted['월'].map(월_매핑)
        df_melted['날짜'] = pd.to_datetime(df_melted['연도'].astype(str) + df_melted['월_숫자'].astype(str), format='%Y%m')

        st.subheader("🏭 공장별 판매 실적 추이")
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

        # 선택 옵션: 공장 선택
        factories = df_melted['공장명(국가)'].unique()
        selected_factories = st.multiselect("공장을 선택하세요", factories, default=list(factories))

        if selected_factories:
            df_filtered = df_melted[df_melted['공장명(국가)'].isin(selected_factories)]

            # 차트
            fig = px.line(
                df_filtered.groupby(['날짜', '공장명(국가)'])['판매량'].sum().reset_index(),
                x='날짜', y='판매량', color='공장명(국가)',
                title="공장별 월별 판매량 추이",
                markers=True,
                labels={"날짜": "날짜", "판매량": "판매량", "공장명(국가)": "공장"}
            )
            fig.update_layout(xaxis_title="날짜", yaxis_title="판매량", legend_title="공장", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)


        st.markdown("""
        <div style='background-color:#f0f8ff; padding:20px; border-radius:8px;'>
            <h4 style='font-size:20px;'>📌 공장별 월별 판매량 분석</h4>
            <ul>
                <li><b>HMI</b> 공장의 판매량이 타 공장에 비해 매우 높은 수준을 유지하며 전체 실적을 견인하고 있습니다.</li>
                <li>동남아 및 유럽 공장들은 꾸준한 흐름을 보이고 있으며, 일부 공장은 계절성 영향이 큽니다.</li>
                <li>급감하거나 급등한 구간은 공급 차질이나 글로벌 이벤트에 따른 영향일 수 있습니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
if __name__ == "__main__":
    run_eda_현대()
