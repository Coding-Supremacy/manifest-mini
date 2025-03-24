import streamlit as st
from streamlit_option_menu import option_menu

from jisang_mini2.eda import run_eda

def run_app():

    menu = ['홈', '고객정보 입력', '고객 분석', '개발 과정']

    with st.sidebar:
        selected = option_menu("메뉴", menu, 
            icons=['house'], menu_icon="cast", default_index=0)
        
    if selected == '홈' :
        pass

    if selected == '개발 과정' :
        pass 
    
    if selected == '고객 분석' :
        run_eda()
     

if __name__ == "__main__":
    run_app()