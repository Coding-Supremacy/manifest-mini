import os
import streamlit as st
import pandas as pd
import requests
from transformers import pipeline
from fpdf import FPDF
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# Hugging Face 감성 분석 파이프라인 초기화
sentiment_pipeline = pipeline("sentiment-analysis")

# NewsAPI.org API 키 (자신의 API 키로 교체)
news_api_key = ""

# 주가 API 키 (API Ninjas)
stock_api_key = ""

# 현대기아차 관련 키워드 목록
hyundai_kia_keywords = ["현대", "기아", "현대자동차", "기아자동차", "전기차", "SUV"]

# 한글 폰트 설정 (Matplotlib)
font_path = "C:/Windows/Fonts/malgun.ttf"  # Windows에서는 맑은 고딕 사용
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 감성 분석 함수 (Hugging Face + 키워드 필터링)
def sentiment_analysis_with_keywords(text):
    negative_keywords = ["사기", "체포", "혐의", "부패", "비리", "문제", "위기", "논란"]
    for keyword in negative_keywords:
        if keyword in text:
            return "부정"
    # Hugging Face 감성 분석 수행
    result = sentiment_pipeline(text)
    label = result[0]['label']
    if label == "NEGATIVE":
        return "부정"
    else:
        return "긍정"

# 현대기아차 관련 여부 판단 함수
def is_related_to_hyundai_kia(text):
    for keyword in hyundai_kia_keywords:
        if keyword in text:
            return True
    return False

# 뉴스 데이터 가져오기 함수 (캐싱 적용)
@st.cache_data
def fetch_auto_news_cached():
    url = f"https://newsapi.org/v2/everything?q=자동차&apiKey={news_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data['articles']
        news_data = pd.DataFrame({
            'title': [article['title'] for article in articles],
            'content': [article['description'] for article in articles]
        })
        return news_data
    else:
        return pd.DataFrame()

# 주가 데이터 가져오기 함수 (캐싱 적용)
@st.cache_data
def get_stock_price_cached(ticker):
    url = f"https://api.api-ninjas.com/v1/stockprice?ticker={ticker}"
    headers = {'X-Api-Key': stock_api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# PDF 보고서 생성 함수
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.add_font('DejaVu', '', 'eungmin/font/DejaVuSans.ttf', uni=True)  # Unicode 폰트 추가
        self.set_font('DejaVu', size=12)

    def add_title(self, title):
        self.set_font('DejaVu', size=16)
        self.cell(200, 10, txt=title, ln=True, align='C')

    def add_text(self, text):
        self.set_font('DejaVu', size=12)
        self.multi_cell(0, 10, txt=text)

def generate_pdf_report(news_data, stock_data):
    pdf = PDF()
    
    # 뉴스 섹션 추가
    pdf.add_title("현대/기아차 관련 뉴스")
    for index, row in news_data.iterrows():
        pdf.add_text(f"{row['title']} - {row['sentiment']}")
    
    # 주가 섹션 추가
    pdf.add_title("현대/기아차 주가 현황")
    for ticker, data in stock_data.items():
        pdf.add_text(
            f"{data['name']}: 현재 주가 {data['current_price']}원 "
            f"(변동 {data['change_percent']:.2f}%)"
        )
    
    # PDF 저장 경로 설정 및 반환
    pdf_file_path = "report.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path

# Streamlit 앱 시작
def main():
    st.title("자동차 관련 뉴스 및 현대/기아 기업 영향 분석")

    # 뉴스 데이터 가져오기 및 분석
    news_data = fetch_auto_news_cached()

    if not news_data.empty:
        # 현대/기아 관련 여부 판단 및 감성 분석 적용
        news_data['related_to_hyundai_kia'] = news_data['content'].apply(is_related_to_hyundai_kia)
        news_data['sentiment'] = news_data['content'].apply(sentiment_analysis_with_keywords)

        # 현대/기아와 관련된 기사만 필터링하여 출력
        related_news = news_data[news_data['related_to_hyundai_kia']]
        
        st.write("현대/기아와 관련된 뉴스 감성 분석 결과:")
        st.write(related_news)

        # 감성 분석 결과 시각화 (파이 차트)
        sentiment_counts = related_news['sentiment'].value_counts()
        
        fig_pie = px.pie(
            names=sentiment_counts.index,
            values=sentiment_counts.values,
            title="현대/기아차 관련 뉴스 감성 비율"
        )
        
        fig_pie.update_layout(
            font=dict(family="Malgun Gothic", size=14)  # 한글 폰트 설정 및 크기 조정
        )
        
        st.plotly_chart(fig_pie)

        # CSV 다운로드 버튼 추가
        csv = related_news.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="뉴스 데이터 다운로드 (CSV)",
            data=csv,
            file_name='news_data.csv',
            mime='text/csv',
        )

    else:
        st.error("뉴스 데이터를 가져오는 데 실패했습니다.")

    # 주식 종목 티커 설정 (현대자동차와 기아자동차 기본값 사용)
    tickers = ["005380.KS", "000270.KS"]
    
    stock_results = {}
    
    for ticker in tickers:
        stock_data = get_stock_price_cached(ticker)
        
        if stock_data:
            current_price = stock_data.get('price')
            previous_price = current_price * 0.98  # 전날 주가는 현재 주가의 98%로 가정
            
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100

            stock_results[ticker] = {
                'name': stock_data.get('name'),
                'current_price': current_price,
                'previous_price': previous_price,
                'change': change,
                'change_percent': change_percent,
            }

            st.write(f"**종목명:** {stock_results[ticker]['name']}")
            st.write(f"**현재 주가:** {stock_results[ticker]['current_price']:.2f}원")
            st.write(f"**전날 주가:** {stock_results[ticker]['previous_price']:.2f}원")
            st.write(f"**변동:** {stock_results[ticker]['change']:.2f}원 ({stock_results[ticker]['change_percent']:.2f}%)")

            # 변동 시각화 (막대 그래프)
            fig_bar = plt.figure(figsize=(6, 4))
            plt.bar(['전날', '현재'], [previous_price, current_price], color=['blue', 'green'])
            plt.title(f"{stock_results[ticker]['name']} 주가 변동")
            plt.ylabel('주가 (원)')
            plt.xlabel('기간')
            st.pyplot(fig_bar)

    if stock_results and not news_data.empty:
        pdf_path = generate_pdf_report(related_news, stock_results)
        
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="PDF 보고서 다운로드",
                data=pdf_file,
                file_name="report.pdf",
                mime="application/pdf",
            )

if __name__ == "__main__":
    main()
