import os
import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go
import requests
from prophet import Prophet
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def load_model(channel, selected_market, model_dir):
    channel_key_map = {
        "현대": "hyundai",
        "기아": "kia"
    }
    channel_key = channel_key_map[channel]  # "hyundai" or "kia"
    filename = f"{channel_key}_{selected_market}_prophet.pkl"
    model_path = os.path.join(model_dir, filename)
    
    if not os.path.exists(model_path):
        st.error(f"❌ 해당 모델 파일이 존재하지 않습니다: {filename}")
        return None

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model

def load_sales_data(csv_path, selected_market):
    df = pd.read_csv(csv_path)
    df["ds"] = pd.to_datetime(df["ds"])
    df = df[df["국가"] == selected_market][["ds", "y"]].copy()
    return df

def create_forecast(model, periods=18, freq="ME"):
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    return forecast

def plot_forecast(df_actual, forecast, selected_market):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=forecast["ds"], y=forecast["yhat"],
        mode='lines+markers', name='예측값', line=dict(color='blue')
    ))

    fig.add_trace(go.Scatter(
        x=df_actual["ds"], y=df_actual["y"],
        mode='lines', name='실제값', line=dict(color='orange', dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=forecast["ds"].tolist() + forecast["ds"][::-1].tolist(),
        y=forecast["yhat_upper"].tolist() + forecast["yhat_lower"][::-1].tolist(),
        fill='toself', fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip", showlegend=True, name='신뢰구간'
    ))

    fig.update_layout(
        title=f"[{selected_market}] 수출 실적 예측",
        xaxis_title="날짜",
        yaxis_title="수출량",
        legend=dict(x=0.01, y=0.99),
        template="plotly_white"
    )
    fig.update_xaxes(
        tickformat="%Y-%m", dtick="M1", tickangle=45,
        range=["2024-10-01", forecast["ds"].max().strftime("%Y-%m-%d")]
    )

    return fig

def fetch_news(query, display=5):
    headers = {
        "X-Naver-Client-Id": st.secrets["X-Naver-Client-Id"],
        "X-Naver-Client-Secret": st.secrets["X-Naver-Client-Secret"],
    }
    params = {"query": query, "display": display, "sort": "date"}
    url = "https://openapi.naver.com/v1/search/news.json"
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        return []

def run_prediction_region():
    CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
    MODEL_DIR = os.path.join(CURRENT_DIR, "..", "models")
    CSV_PATH_MAP = {
        "현대": os.path.join(CURRENT_DIR, "..", "data", "현대_시장구분별_수출실적.csv"),
        "기아": os.path.join(CURRENT_DIR, "..", "data", "기아_시장구분별_수출실적.csv")
    }
    st.write("")
    st.write("")
    channel = st.selectbox("분석할 채널을 선택하세요", ["현대", "기아"])

    market_label_map = {
        "미국": "북미-미국",
        "캐나다": "북미-캐나다",
        "멕시코": "북미-멕시코",
        "동유럽": "동유럽",
        "서유럽": "서유럽",
        "아시아": "아시아",
        "중남미": "중남미",
        "중동·아프리카": "중동·아프리카"
    }
    market_labels = list(market_label_map.keys())
    selected_label = st.selectbox("국가를 선택하세요", market_labels)
    selected_market = market_label_map[selected_label]

    st.title(f"{channel} - 국가별 수출실적 예측")
    st.markdown(f"""
### 📈 수출 실적 예측 대시보드
이 페이지는 {channel}차의 **2021년~2025년 1월 까지의 국가별 수출 실적** 데이터를 기반으로,  
**향후 18개월간 예측된 수출 추세**를 시각화하고,
**관련 뉴스 기사**를 통해 최근 이슈와 전망을 함께 제공합니다.
""")

    if selected_market:
        model = load_model(channel, selected_market, MODEL_DIR)
        if model is None:
            return

        forecast = create_forecast(model, periods=18, freq="ME")
        df_actual = load_sales_data(CSV_PATH_MAP[channel], selected_market)
        fig = plot_forecast(df_actual, forecast, selected_market)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🔍 그래프 해석 가이드")
        st.info("""
        **파란 선**: Prophet 모델이 예측한 향후 수출량입니다.  
        **주황 점선**: 2025년 1월까지의 실제 수출 실적입니다.  
        **연한 녹색 영역**: 예측의 신뢰 구간을 의미합니다.
        """)

        st.subheader(f"📰 [{selected_market}] 관련 최신 뉴스")
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

        st.subheader("🧐 AI 분석가의 시장 해석")
        if st.button("AI 예측실행"):
            try:
                forecast_start = forecast["yhat"].iloc[0]
                forecast_end = forecast["yhat"].iloc[-1]
                forecast_trend = "증가세" if forecast_end > forecast_start else "감소세"
                news_keywords = ", ".join([n["title"].replace("<b>", "").replace("</b>", "") for n in news_items[:3]])

                # 최근 12개월 실제 수출 데이터 추출
                recent_actual = df_actual.sort_values('ds').tail(12)
                actual_trend_str = ", ".join([
                    f"{row['ds'].strftime('%Y-%m')}: {int(row['y'])}" for _, row in recent_actual.iterrows()
                ])

                prompt = f"""
                당신은 자동차 수출 시장을 분석하는 전문 보고서 작성자입니다. 아래 정보를 바탕으로, [시장 분석 보고서]를 작성해주세요.

                - 브랜드: {channel}
                - 시장명: {selected_market}
                - 최근 12개월간 실제 수출 실적: {actual_trend_str}
                - 향후 18개월 예측: {forecast_trend}
                - 최근 뉴스 키워드: {news_keywords}

                보고서 형식은 다음과 같이 작성해주세요:

                1. **{selected_market} 시장 예측 분석**  
                {selected_market} 시장의 특징과 현재 상황을 분석 합니다.

                2. **최근 동향 요약**  
                뉴스 키워드를 바탕으로 최근 이슈 및 자동차 수출과 관련된 주요 변화 사항을 서술합니다.

                3. **수출 예측 분석**  
                Prophet 모델 예측 결과를 바탕으로 수출량의 변화를 분석합니다.  
                특히 최근 12개월간 실제 수출 실적 흐름과 비교하여 예측의 신뢰도와 특이사항을 설명해주세요.

                4. **전략적 제언**  
                자동차 제조업체 또는 관련 산업이 향후 어떻게 대응하면 좋을지 구체적이고 현실적인 전략을 제시해주세요.

                보고서는 **전문적이지만 이해하기 쉽게**, **한글로** 작성해주세요.
                """

                with st.spinner("GPT-4 Turbo가 분석 중입니다..."):
                    response = client.chat.completions.create(
                        model="gpt-4-0125-preview",
                        messages=[
                            {"role": "system", "content": "당신은 자동차 수출 시장 전문 보고서를 작성하는 전문가입니다."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1024
                    )
                st.success(response.choices[0].message.content.strip())
            except Exception as e:
                st.warning("AI 해석 생성 실패")
                st.text(f"에러: {e}")