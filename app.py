import streamlit as st
from streamlit_option_menu import option_menu

# 페이지 설정
st.set_page_config(
    page_title="🚗 현대 & 기아 판매현황 관리 자동화 및 추천 시스템",
    layout="wide"
)

# 각 페이지 함수 불러오기
from ui.home import run_home
from ui.description import run_description
from ui.eda_kia import run_eda_기아
from ui.eda_hyundai import run_eda_현대
from ui.prediction_hyundai import run_prediction_hyundai



def run_app():
    with st.sidebar:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Hyundai_Motor_Company_logo.svg/320px-Hyundai_Motor_Company_logo.svg.png",
            width=200
        )
        st.markdown("### 📂 메뉴 선택")

        menu = option_menu(
            menu_title=None,
            options=[
                "홈", "개발 과정",
                "기아 자동차 분석", "현대 자동차 분석",
                "현대 자동차 판매량 예측", "수출 및 생산량 분석"
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

    elif menu == "현대 자동차 판매량 예측":
        run_prediction_hyundai()

    elif menu == "수출 및 생산량 분석":
        st.warning("📦 수출 및 생산량 분석 페이지는 아직 준비 중입니다.")

if __name__ == "__main__":
    run_app()
