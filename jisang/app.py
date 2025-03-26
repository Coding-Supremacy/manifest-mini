import streamlit as st
from streamlit_option_menu import option_menu

from eda_kia import run_eda_기아
from eda_hyundai import run_eda_현대

# 페이지 설정
st.set_page_config(page_title="🚗 현대 & 기아 판매현황 관리 자동화 및 추천 시스템", layout="wide")

def run_app():

    with st.sidebar:
        
        st.markdown("### ⚙️ 시스템 메뉴")
        system_tab = option_menu(None, ['홈', '개발 과정'],
                                icons=['house', 'code-slash'], key='sys')

        st.markdown("### 🚗 브랜드 분석")
        selected = option_menu(None, ['기아 자동차 분석', '현대 자동차 분석'],
                            icons=['car-front', 'car-front-fill'], key='brand')

        
        
        
    if system_tab == '홈' :
        pass

    if system_tab == '개발 과정' :
        pass 
    
    if selected == '기아 자동차 분석' :
        run_eda_기아()

    if selected == '현대 자동차 분석' :
        run_eda_현대()     

if __name__ == "__main__":
    run_app()