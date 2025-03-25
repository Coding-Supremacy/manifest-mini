# streamlit_app.py
import streamlit as st

st.set_page_config(page_title="판매 데이터 업로드", layout="wide")

st.title("📂 판매 데이터 업로드 페이지")

uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type="csv")

if uploaded_file:
    # 파일을 세션에 저장
    st.session_state.uploaded_file = uploaded_file
    st.success("✅ 업로드 완료! 시각화 페이지로 이동합니다...")

    # ✅ 페이지 이동
    st.switch_page("pages/시각화.py")
