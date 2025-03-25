import streamlit as st
import plotly.express as px
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def main():
    df = pd.read_csv('yeseul/현대_모델별_생산_판매.csv')

    # 1) 특정 모델(Santa-Fe (TMa), Santa-Fe (MX5a))만 별도 분류, 나머지는 '기타'
    df['특별모델'] = '기타'
    df.loc[df['차량 모델'] == 'Santa-Fe (TMa)', '특별모델'] = 'Santa-Fe (TMa)'
    df.loc[df['차량 모델'] == 'Santa-Fe (MX5a)', '특별모델'] = 'Santa-Fe (MX5a)'

    # 2) Plotly Scatter: color='특별모델'로 지정, color_discrete_map으로 색상 매핑
    fig = px.scatter(
        df,
        x="총생산량",
        y="총판매량",
        color='특별모델',  # 이 열을 기준으로 색이 달라짐
        color_discrete_map={
            'Santa-Fe (TMa)': 'red',     # 빨강
            'Santa-Fe (MX5a)': 'green', # 초록
            '기타': 'blue'               # 그 외 모델은 파랑
        },
        hover_name="차량 모델",
        hover_data={"총생산량": True, "총판매량": True, "특별모델": False},
        title="모델별 총생산량 vs 총판매량"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
### 모델별 공장 생산량 vs. 판매 실적 분석

이 산점도는 각 차량 모델의 <b>공장 생산량(가로축)</b>과 **판매 실적(세로축)** 간의 관계를 시각화한 그래프입니다.

- **양의 선형 관계**<br>
  대부분의 모델은 생산량이 증가할수록 판매량도 함께 증가하는 경향을 보여주어<br>**23년~24년간의 생산 계획이 시장 수요를 잘 반영**하고 있음을 시사합니다.

- **조정이 필요한 특이 모델(Outlier)**
  - **생산 대비 판매량이 극단적으로 낮은 모델**: 생산이 많음에도 판매가 저조해, **과잉 생산**이나 **시장 수요 부족** 등의 문제가 있을 수 있습니다. 예를 들어, Santa-Fe (TMa)가 이 범주에 속해 재고 누적 위험이 있을 수 있습니다.
  - **생산 대비 판매량이 예측보다 높은 모델**: 시장에서 좋은 반응을 얻어, **추가 생산 확대**나 **마케팅 지원**을 고려해볼 만한 모델입니다. Santa-Fe (MX5a)가 이 범주에 해당합니다.

                """, unsafe_allow_html=True)
    
    data = {
    '특징': ['세대', '출시 시기', '디자인', '플랫폼', '실내 공간', '주요 특징'],
    'Santa-Fe (TMa) (4세대)': [
        '4세대', 
        '2018년 ~ 2023년', 
        '곡선 위주', 
        '이전 세대 플랫폼', 
        '실용적', 
        '다양한 파워트레인, 첨단 안전/편의 사양'
    ],
    'Santa-Fe (MX5a) (5세대)': [
        '5세대', 
        '2023년 하반기 ~ 현재', 
        '각진 형태', 
        '현대 N3 플랫폼', 
        '넓음', 
        '넓은 공간, 최신 기술, 새로운 디자인'
    ]
}
    st.markdown(""" 
- **특이 모델(Outlier) 분석**
  - <b><span style="color: red;">Santa-Fe (TMa) (4세대)</b></span>: 생산량에 비해 판매량이 크게 낮은 모델이였습니다.
  - <b><span style="color: green;">Santa-Fe (MX5a) (5세대)</b></span>: 5세대 출시 이후 수요가 크게 늘어 생산량을 늘리는 것이 필요해 보입니다.
                <br> 고객에게 큰 인기를 끌고 있는 모델로, 4세대와의 차이점을 분석하여 다른 차종에도 적용가능한 포인트를 찾아보는 것이 좋을 것 같습니다.
                """, unsafe_allow_html=True)
    df_specs = pd.DataFrame(data)
    st.dataframe(df_specs,hide_index=True,use_container_width=True)
    st.markdown("""          
#### 시사점
1. **생산 계획 vs. 실제 판매**  
   - 생산이 지나치게 많은 모델은 재고 부담이 커지고 비용이 증가할 수 있어, 원인 분석 및 생산 조정이 필요합니다.
   - 생산 대비 판매가 좋은 모델은 생산 확대나 마케팅 투자를 통해 시장 점유율을 높일 기회를 갖습니다.


2. **전반적인 추세**  
   - 그래프 전반적으로, 생산량이 높아지면 판매량도 증가하는 **양의 상관관계**를 확인할 수 있습니다.  
   - 이 관계에서 크게 벗어나는 모델은 **데이터 오류** 또는 **시장 특수성**일 수도 있으니, 별도 검증이 필요합니다.

---
이러한 분석을 통해, **공장 생산량**과 **실제 판매 실적** 간의 간극을 파악하고, 모델별로 **과잉 생산** 혹은 **판매 호조** 현상의 원인을 심층적으로 조사할 수 있습니다.
""", unsafe_allow_html=True)



    domestic_ts =pd.read_csv('yeseul/현대_내수_판매실적.csv',index_col='기준일', parse_dates=True)
    export_ts = pd.read_csv('yeseul/현대_수출_판매실적.csv',index_col='기준일', parse_dates=True)
    total_ts = pd.read_csv('yeseul/현대_판매실적.csv',index_col='기준일', parse_dates=True)
    result_domestic = seasonal_decompose(domestic_ts, model='additive', period=12)
    result_export = seasonal_decompose(export_ts, model='additive', period=12)
    result_total = seasonal_decompose(total_ts, model='additive', period=12)
    

    # ----------------------------
    # Streamlit 앱: 채널 선택에 따른 시계열 분해 결과 Plotly 그래프
    # ----------------------------
    st.title("채널별 판매량 시계열 분해 분석")

    channel = st.selectbox("분석할 채널을 선택하세요", ["내수", "수출", "전체(내수+수출)"])

    if channel == "내수":
        result = result_domestic
        title = "내수 판매량 시계열 분해 결과"
    elif channel == "수출":
        result = result_export
        title = "수출 판매량 시계열 분해 결과"
    else:
        result = result_total
        title = "전체 판매량 시계열 분해 결과"

    # Plotly 서브플롯 생성 (4행 1열: 관측값, 추세, 계절성, 잔차)
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        subplot_titles=["관측값 (Observed)", "추세 (Trend)", "계절성 (Seasonal)", "잔차 (Residual)"]
    )

    fig.add_trace(
        go.Scatter(x=result.observed.index, y=result.observed.values, mode='lines', name='관측값'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=result.trend.index, y=result.trend.values, mode='lines', name='추세'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=result.seasonal.index, y=result.seasonal.values, mode='lines', name='계절성'),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=result.resid.index, y=result.resid.values, mode='lines', name='잔차'),
        row=4, col=1
    )

    # 모든 서브플롯의 x축 레이블 표시
    for i in range(1, 5):
        fig.update_xaxes(showticklabels=True, row=i, col=1)

    fig.update_layout(height=800, title_text=title)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    #### 그래프 해설
    - **관측값 (Observed):** 실제 측정된 월별 판매량을 나타냅니다.
    - **추세 (Trend):** 계절성과 단기 변동을 제거한 후, 장기적인 판매량의 증가/감소 추세를 보여줍니다.
    - **계절성 (Seasonal):** 1년 주기로 반복되는 계절적 패턴을 나타내며, 특정 달에 판매량이 높거나 낮은 경향을 파악할 수 있습니다.
    - **잔차 (Residual):** 추세와 계절성을 제거한 후의 불규칙 변동으로, 예상치 못한 이벤트나 외부 요인의 영향을 반영합니다.

    이 분석을 통해 각 채널(내수, 수출, 전체)의 판매 패턴을 심도 있게 이해하고, 마케팅 전략, 생산 계획, 그리고 전반적인 비즈니스 전략 수립에 활용할 수 있습니다.
    """)

    st.markdown("""
### 판매량 시계열 분해 결과

위 그래프는 **판매량**을 시계열로 분해하여 **관측값(Observed)**, **추세(Trend)**, **계절성(Seasonal)**, **잔차(Residual)**로 나눈 결과입니다.

---

### 시사점 및 활용 제안

- **마케팅팀**  
  - **계절성**을 확인하여, 판매가 상대적으로 낮은 달에 프로모션이나 이벤트를 집중할 수 있습니다.  
  - 2024년 중반부에 판매가 최고조에 달하는 추세가 보이므로, 해당 시점에 맞춰 **신차 출시** 또는 **마케팅 캠페인**을 강화하면 효과적일 수 있습니다.

- **생산기획팀**  
  - **장기 추세**가 2024년 중반까지 상승하다가 이후 완만히 내려가는 양상을 보이므로, **생산 계획**을 탄력적으로 조정할 필요가 있습니다.  
  - 계절성으로 인한 급격한 변동을 완충하기 위해, **재고 관리**와 **공장 라인 가동률**을 시즌별로 최적화해야 합니다.

- **CEO**  
  - **장기 추세**가 정점을 찍고 하강하는 흐름이 보이므로, **2024년 중반 이후** 시장 수요 감소에 대비한 전략 수립이 필요합니다.  
  - 계절적 변동이 크게 나타나는 시점(예: 연말·연초)에는 **예산 배분**과 **인력 운영**을 유연하게 가져가, 불필요한 비용을 줄이고 기회를 극대화할 수 있습니다.

---

이러한 시계열 분해 결과를 바탕으로, **계절 패턴**에 맞춘 프로모션 전략과 **장기 추세**를 고려한 생산·재고 계획을 수립하면, 시장에서의 판매 성과를 더욱 안정적으로 높일 수 있을 것으로 기대됩니다.
""")

if __name__ == '__main__':
    main()
