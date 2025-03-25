import streamlit as st
import pandas as pd

from home import run_home
from Sales_analysis import run_analysis


def main():
    
    st.sidebar.title('Navigation')
    menu = ['🏠 홈', '📊 판매 분석', '🔮 수요 예측', '📍 마케팅 추천', '📈 경영진 리포트']
    page = st.sidebar.radio('메뉴', menu)
    
    if page == '🏠 홈' :
        run_home()
    if page == '📊 판매 분석':
        run_analysis()
    


if __name__ == '__main__':
    main()