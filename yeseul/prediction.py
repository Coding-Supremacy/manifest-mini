import os
from openai import OpenAI
import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go
import requests

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def main():
    CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
    MODEL_DIR = os.path.join(CURRENT_DIR, "models")

    available_markets = [
        '동유럽', '북미-멕시코', '북미-미국', '북미-캐나다',
        '서유럽', '아시아', '중남미', '중동·아프리카'
    ]

    st.title("현대 - 시장구분별 수출실적 예측")
    st.markdown("""
### 📈 수출 실적 예측 대시보드
이 페이지는 현대차의 **시장구분별 수출 실적** 데이터를 기반으로,  
**향후 18개월간 예측된 수출 추세**를 시각화하고,
**관련 뉴스 기사**를 통해 최근 이슈와 전망을 함께 제공합니다.
""")

    selected_market = st.selectbox("시장 구분을 선택하세요", available_markets)
    model_path = os.path.join(MODEL_DIR, f"{selected_market}_prophet.pkl")

    if selected_market:
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)

            future = model.make_future_dataframe(periods=18, freq="ME")
            forecast = model.predict(future)

            CSV_PATH = os.path.join(CURRENT_DIR, "현대_시장구분별_수출실적.csv")
            df = pd.read_csv(CSV_PATH)
            df = df[df["국가"] == selected_market][["ds", "y"]].copy()
            df["ds"] = pd.to_datetime(df["ds"])

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["ds"], y=df["y"], mode='lines+markers', name='실제값', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"], mode='lines', name='예측값', line=dict(color='orange', dash='dash')))
            fig.add_trace(go.Scatter(
                x=forecast["ds"].tolist() + forecast["ds"][::-1].tolist(),
                y=forecast["yhat_upper"].tolist() + forecast["yhat_lower"][::-1].tolist(),
                fill='toself',
                fillcolor='rgba(0,100,80,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=True,
                name='신뢰구간'
            ))

            fig.update_layout(
                title=f"[{selected_market}] 수출 실적 예측",
                xaxis_title="날짜",
                yaxis_title="수출량",
                legend=dict(x=0.01, y=0.99),
                template="plotly_white"
            )
            fig.update_xaxes(
                range=["2024-11-01", forecast["ds"].max().strftime("%Y-%m-%d")],
                tickformat="%Y-%m", dtick="M1", tickangle=45
            )
            st.plotly_chart(fig, use_container_width=True)

        except FileNotFoundError:
            st.error("❌ 해당 시장의 모델 파일이 존재하지 않습니다.")
        except Exception as e:
            st.error(f"❌ 예외 발생: {e}")

        st.markdown("#### 🔍 그래프 해석 가이드")
        st.info("""
        **파란 선**: 2025년 1월까지의 실제 수출 실적을 나타냅니다.  
        **주황 점선**: Prophet 모델이 예측한 향후 수출량입니다.  
        **연한 녹색 영역**: 예측치의 신뢰 구간입니다.
        """)

        st.subheader(f"📰 [{selected_market}] 관련 최신 뉴스")

    def fetch_news(query, display=5):
        headers = {
            "X-Naver-Client-Id": st.secrets["X-Naver-Client-Id"],
            "X-Naver-Client-Secret": st.secrets["X-Naver-Client-Secret"],
        }
        params = {"query": query, "display": display, "sort": "date"}
        url = "https://openapi.naver.com/v1/search/news.json"
        response = requests.get(url, headers=headers, params=params)
        return response.json().get("items", []) if response.status_code == 200 else []

    query = f"{selected_market} 자동차 수출"
    news_items = fetch_news(query)

    if news_items:
        cols = st.columns(len(news_items))
        for i, news in enumerate(news_items):
            with cols[i]:
                title = news["title"].replace("<b>", "").replace("</b>", "")
                description = news.get("description", "").replace("<b>", "").replace("</b>", "")
                link = news["link"]
                st.markdown(f"""
                <div style="border:1px solid #ddd; border-radius:10px; padding:10px; text-align:center; height: 300px; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden;">
                    <div style="flex-grow: 1;">
                        <a href="{link}" target="_blank" style="text-decoration:none;"><strong>{title}</strong></a>
                        <hr style="border: 0; height: 1px; background-color: #ccc; margin: 10px 0;">
                        <p style="font-size:14px; color:#555; margin-top:10px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 6; -webkit-box-orient: vertical;">{description}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("뉴스 데이터를 불러올 수 없습니다.")

    st.subheader("🧠 AI 분석가의 시장 해석")
    try:
        forecast_start = forecast["yhat"].iloc[0]
        forecast_end = forecast["yhat"].iloc[-1]
        forecast_trend = "증가세" if forecast_end > forecast_start else "감소세"
        news_keywords = ", ".join([n["title"].replace("<b>", "").replace("</b>", "") for n in news_items[:3]])

        prompt = f"""
당신은 자동차 수출 시장 분석가입니다.
- 시장명: {selected_market}
- 향후 18개월 예측: {forecast_trend}
- 최근 이슈: {news_keywords}
위 정보를 바탕으로 수출 동향을 분석하고 전략 방향을 제안해주세요.
"""

        with st.spinner("GPT-3.5가 분석 중입니다..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 자동차 수출 시장 전문가입니다. 결과를 전문적이면서도 쉽게 설명해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )

        st.success(response.choices[0].message.content.strip())

    except Exception as e:
        st.warning("AI 해석 생성 실패")
        st.text(f"에러: {e}")


if __name__ == '__main__':
    main()
