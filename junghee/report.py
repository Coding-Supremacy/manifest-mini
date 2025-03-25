import streamlit as st
from PIL import Image
import io

# 리포트 요약 정보 (앞서 만든 report_summary 딕셔너리 사용)
# report_summary = {"총 판매량": ..., "전월 대비 증가율": ..., "해외 판매 비중": ..., "차트": ...}



st.header("📋 경영진 요약 리포트")

# 🔹 KPI 카드
col1, col2, col3 = st.columns(3)
col1.metric("📦 총 판매량", report_summary["총 판매량"])
col2.metric("📈 전월 대비 증가율", report_summary["전월 대비 증가율"])
col3.metric("🌍 해외 판매 비중", report_summary["해외 판매 비중"])

# 🔹 시각화 차트
st.subheader("📈 최근 6개월 판매 추이")
chart_image = Image.open(report_summary["차트"])
st.image(chart_image, use_column_width=True)

# 🔹 요약 인사이트
st.subheader("🔍 요약 인사이트")
st.markdown("""
- **전체 판매량은 지속적인 상승세**를 보이고 있으며, 특히 **해외 판매가 국내보다 빠르게 성장**하고 있습니다.
- 최근 해외 판매 비중이 54%를 넘어서며, **글로벌 전략 확대의 필요성**이 커지고 있습니다.
- 국내 판매는 정체 상태이므로, **내수 시장 활성화를 위한 마케팅 전략 보완**이 필요합니다.
""")

# 🔹 전략 제안
st.subheader("🎯 전략 제안")
st.markdown("""
- ✅ **전략 1**: 해외 수출 인기 차종 중심으로 생산 비중 확대  
- ✅ **전략 2**: 국내 시장 내 침체 차종에 대한 판촉 강화 또는 라인업 재조정  
- ✅ **전략 3**: 글로벌 수요 기반 차종 (ex. SUV) 중심의 물류/생산 전략 리디자인
""")
