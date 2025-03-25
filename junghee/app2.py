import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
from streamlit.components.v1 import html
import pdfkit

# 1. 파일 업로드
uploaded_file = st.file_uploader("CSV 파일 업로드", type='csv')
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("📄 데이터 미리보기", df.head())

    # 2. 프로파일링 리포트 생성
    profile = ProfileReport(df, title="📊 자동 데이터 분석 리포트", explorative=True)

    # 3. HTML 삽입
    profile_html = profile.to_html()
    html(profile_html, height=800, scrolling=True)

    profile.to_file("report.html")

    # HTML → PDF 변환 (pdfkit or weasyprint 사용)
    
    pdfkit.from_file("report.html", "report.pdf")