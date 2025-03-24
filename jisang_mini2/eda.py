import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Streamlit 앱 설정 (전역 범위)
st.set_page_config(
    page_title="기아 수출 실적 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 폰트 설정 (Windows 환경 고려)
try:
    font_path = "C:/Windows/Fonts/NanumGothic.ttf"  # Windows 환경에서 NanumGothic 폰트 경로
    font_name = fm.FontProperties(fname=font_path).get_name()
    plt.rc('font', family=font_name)
except:
    st.warning("NanumGothic 폰트를 찾을 수 없습니다. 시스템에 설치되어 있는지 확인해주세요.")

# 함수 정의
def run_eda():
    # 데이터 불러오기
    try:
        df = pd.read_csv("기아_지역별수출실적_전처리.csv")
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

    # 국가 선택 (사이드바)
    selected_countries = st.sidebar.multiselect("국가를 선택하세요:", list(countries), default=countries.tolist())

    # 그래프 생성
    fig, ax = plt.subplots(figsize=(15, 8))

    for country in selected_countries:
        country_data = df[df['국가명'] == country].copy()

        # 연도별 월별 판매량 데이터를 하나의 Series로 만들기
        monthly_sales = []
        years = country_data['연도'].unique()

        for year in years:
            year_data = country_data[country_data['연도'] == year]

            # 각 월별 판매량 컬럼 이름
            month_cols = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']

            # 해당 연도의 월별 판매량을 리스트에 추가
            for month in month_cols:
                if month in year_data.columns:  # 해당 월이 데이터프레임에 있는지 확인
                    sales = year_data[month].values
                    if len(sales) > 0:
                        monthly_sales.append(sales[0])
                    else:
                        monthly_sales.append(None)  # 데이터가 없는 경우 None 추가
                else:
                    monthly_sales.append(None)  # 해당 월이 없는 경우 None 추가

        # x축 날짜 생성
        dates = pd.date_range(start='2023-01-01', periods=len(monthly_sales), freq='M')

        # 2025년 3월까지만 그래프에 표시
        dates = dates[dates <= pd.to_datetime('2025-03-01')]
        monthly_sales = monthly_sales[:len(dates)]

        # NaN 값을 제외한 데이터만 플롯
        valid_indices = [i for i, x in enumerate(monthly_sales) if pd.notna(x)]
        valid_dates = dates[valid_indices]
        valid_sales = [monthly_sales[i] for i in valid_indices]

        ax.plot(valid_dates, valid_sales, marker='o', linestyle='-', label=country)

    ax.set_title('주요 시장별 수출량 변화', fontsize=16)
    ax.set_xlabel('날짜', fontsize=12)
    ax.set_ylabel('판매량', fontsize=12)
    plt.xticks(rotation=45)
    ax.grid(True)
    ax.legend()
    plt.tight_layout()

    # Streamlit에 그래프 표시
    st.pyplot(fig)
    st.markdown("Made by Your Name")

# Streamlit 앱 실행
if __name__ == "__main__":
    run_eda()
