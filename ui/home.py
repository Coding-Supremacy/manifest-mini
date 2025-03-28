import streamlit as st 



def run_home():
    
    


    # 타이틀 및 소개
    st.markdown("""
    <h1 style='text-align: center; color: #2E86C1;'>🏠 현대 & 기아 판매현황 분석 시스템</h1>
    <h4 style='text-align: center;'>📊 공장, 지역, 차종별 판매 데이터 자동 분석 및 리포트 제공</h4>
    <hr>
    """, unsafe_allow_html=True)

    # KPI 카드
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📁 분석 항목", "3가지")
    with col2:
        st.metric("📅 분석 기간", "2023 ~ 2025")
    with col3:
        st.metric("🧾 리포트", "경영진 요약 포함")

    st.markdown("---")

    # 주요 기능
    st.markdown("### 🔧 주요 기능")
    st.markdown(""" 
    - ✅ **시각화 제공**: Plotly 기반 트렌드 분석 시각화  
    - ✅ **리포트 요약**: 경영진을 위한 요약 보고서 포함  
    - ✅ **향후 확장성**: 예측 기능 및 추천 시스템 연계 가능
    """)

    st.markdown("---")

    # 분석 항목
    st.markdown("### 🔍 분석 항목")
    st.info("🏭 **공장별 판매 분석**: 생산 공장 기준 월별 판매량 트렌드")
    st.success("🌍 **지역별 수출 분석**: 국가별 수출 변화 흐름")
    st.warning("🚙 **차종별 판매 분석**: 인기 차종 및 카테고리별 트렌드")

    st.markdown("---")

    # 사용 방법
    st.markdown("### 📌 사용 방법")
    st.markdown("""
    1️⃣ **왼쪽 메뉴에서 분석 항목 선택**  
    2️⃣ **자동 분석된 데이터 확인 또는 직접 업로드**  
    3️⃣ **시각화 및 전략 리포트 확인**  
    """)

    st.markdown("---")

    # 하단
    st.markdown("<p style='text-align: center;'>ⓒ 2025 판매현황 자동 분석 시스템 | Streamlit 기반 프로젝트</p>", unsafe_allow_html=True)

