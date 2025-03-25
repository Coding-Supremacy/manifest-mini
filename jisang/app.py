import streamlit as st
from streamlit_option_menu import option_menu

from eda_기아 import run_eda_기아
from eda_현대 import run_eda_현대

def run_app():

    menu = ['홈', '기아 자동차 분석', "현대 자동차 분석",'개발 과정']

    with st.sidebar:
        selected = option_menu("메뉴", menu, 
            icons=['house'], menu_icon="cast", default_index=0)
        
    if selected == '홈' :
        pass

    if selected == '개발 과정' :
        pass 
    
    if selected == '기아 자동차 분석' :
        run_eda_기아()

    if selected == '현대 자동차 분석' :
        run_eda_현대()     

if __name__ == "__main__":
    run_app()