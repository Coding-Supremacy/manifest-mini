import streamlit as st


def run_home():
    st.markdown("<h1 style='text-align: center;'>🚗 글로벌 자동차 판매 분석 플랫폼</h1>", unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    ### 프로젝트 개요
    본 애플리케이션은 현대자동차와 기아자동차의 **2023년 1월부터 2025년 1월까지**의 글로벌 판매 데이터를 기반으로, 
    차량 판매 흐름과 수출 실적을 분석하고, <br> 외부 요인을 고려한 예측 정보를 제공합니다.
    """, unsafe_allow_html=True)
    st.image('image/home.png', width=1000)

        # 📦 3개의 카드 형태로 주요 기능 소개
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("#### 📊 차종별, 지역별 수출 실적 분석")
        st.info("""
        - 브랜드별 / 차종별 / 글로벌 별  
                판매 트렌드 시각화  
        - 월별 판매량, 연간 누적 판매량 비교  
        """)

    with col2:
        st.write("#### 🤖  예측")
        st.success("""Prophet 시계열 모델과  
        최신 글로벌 이슈를 반영한 LLM 분석을 결합하여  
        향후 **판매량 예측 및 트렌드 인사이트**를 제공합니다.""")

    with col3:
        st.write("#### 🎯 활용 대상")
        st.warning("""전략 기획팀  
                   마케팅팀  
                   생산기획팀  
                   글로벌 비즈니스 담당자""")
    st.markdown("""
    ### 📌 목표
    > 세계 경제 트랜드와 계절성까지 고려한 정밀 판매 예측과 경쟁사 동향까지 제공하는 통합 분석 플랫폼 구축

    ---
    """)