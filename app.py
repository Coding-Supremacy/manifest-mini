import streamlit as st
from streamlit_option_menu import option_menu

from ui.prediction_region import run_prediction_region

# 페이지 설정
st.set_page_config(
    page_icon="🚗",
    page_title="현대 & 기아 판매현황 관리 자동화 및 추천 시스템",
    layout="wide"
)

# 각 페이지 함수 불러오기
from ui.home import run_home
from ui.description import run_description
from ui.eda_kia import run_eda_기아
from ui.eda_hyundai import run_eda_현대
st.markdown(
    """
    <style>
    
        /* 배경색 설정 */
        .stApp {
            background-color: #ffffff; 
        }
        /* 컨텐츠 정렬 */
        .block-container {
            max-width: 1100px; /* 중앙 정렬을 위한 최대 너비 */
            margin: auto;
            padding: 2rem;
            border-radius: 10px;
            background-color: #F8F9FA; /* 컨텐츠 부분만 흰색 */
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1); /* 살짝 그림자 효과 */
        }

        /* 제목 스타일 */
        h1, h2, h3 {
            color: #343a40; /* 다크 그레이 */
        }
    </style>
    """,
    unsafe_allow_html=True
)


def run_app():
    with st.sidebar:
        st.markdown("### 📂 메뉴 선택")

        menu = option_menu(
            menu_title=None,
            options=[
                "홈", "개발 과정",
                "기아 자동차 분석", "현대 자동차 분석",
                "국가별 자동차 판매량 예측", "기후별 자동차 판매량 예측"
            ],
            icons=[
                "house", "code-slash",
                "car-front", "car-front-fill",
                "bi bi-bar-chart-line", "bi bi-bar-chart-line-fill"
            ],
            default_index=0,
            key="main_menu"
        )

    # 페이지 매핑
    if menu == "홈":
        run_home()

    elif menu == "개발 과정":
        run_description()

    elif menu == "기아 자동차 분석":
        run_eda_기아()

    elif menu == "현대 자동차 분석":
        run_eda_현대()

    elif menu == "국가별 자동차 판매량 예측":
        run_prediction_region()

    elif menu == "기후별 자동차 판매량 예측":
        st.warning("📦 수출 및 생산량 분석 페이지는 아직 준비 중입니다.")

if __name__ == "__main__":
    run_app()
