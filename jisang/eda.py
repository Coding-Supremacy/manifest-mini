import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Streamlit 앱 설정 (전역 범위)
st.set_page_config(
    page_title="기아 수출 실적 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 함수 정의
def run_eda():
    # 데이터 불러오기
    try:
        df = pd.read_csv("C:/ground/Github/manifest-mini/jisang/data/기아_지역별수출실적_전처리.csv")
    except FileNotFoundError:
        st.error("기아_지역별수출실적_전처리.csv 파일을 찾을 수 없습니다. 올바른 경로에 파일이 있는지 확인해주세요.")
        st.stop()

    # 데이터 전처리
    df = df[df['차량 구분'] == '총합']
    df = df.drop(columns=['차량 구분'])
    countries = df['국가명'].unique()

    # Streamlit 레이아웃 구성
    st.title("📈 기아 수출 실적 대시보드")
    st.markdown("2023년 - 2025년 지역별 수출 실적 변화")

     # 데이터 분석 이유와 장점 설명 추가
    st.subheader("데이터 분석의 목적과 장점")
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

    # 국가 선택 (웹페이지 내에서)
    selected_countries = st.multiselect(
        "국가를 선택하세요:",  # 라벨
        options=list(countries),  # 선택 가능한 옵션 리스트
        default=list(countries)  # 기본값으로 모든 국가 선택
    )

    if not selected_countries:
        st.warning("최소 하나의 국가를 선택해야 합니다.")
        return

    # Plotly 그래프 생성
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for country in selected_countries:
        country_data = df[df['국가명'] == country].copy()

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

    fig.update_layout(
        title='주요 시장별 수출량 변화',
        xaxis_title='날짜',
        yaxis_title='판매량',
        legend_title='국가',
        hovermode="closest"  # 마우스를 올린 그래프에만 값 표시
    )

    # Streamlit에 그래프 표시
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("Made by Your Name")

# Streamlit 앱 실행
if __name__ == "__main__":
    run_eda()
