import streamlit as st
from streamlit_option_menu import option_menu

from eda_기아 import run_eda_기아
from eda_현대 import run_eda_현대
from home import run_home

# 페이지 설정
st.set_page_config(page_title="홈 | 판매현황 분석 시스템", layout="wide")

def run_app():
    with st.sidebar:
        st.markdown("### 전체 메뉴")

        # 전체 메뉴를 한 번에 통합
        active_page = option_menu(
            menu_title=None,
            options=[
                "🏠 홈", "⚙️ 개발 과정",
                "🚗 기아 자동차 분석", "🚙 현대 자동차 분석"
            ],
            default_index=0
        )

    # 페이지 선택 분기
    if active_page == "🏠 홈":
        run_home()

    elif active_page == "⚙️ 개발 과정":
        st.title("개발 과정 페이지")
        # 개발 과정 내용

    elif active_page == "🚗 기아 자동차 분석":
        run_eda_기아()

    elif active_page == "🚙 현대 자동차 분석":
        run_eda_현대()     

if __name__ == "__main__":
    run_app()