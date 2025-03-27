import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드 함수
@st.cache_data
def load_data():
    months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
    
    # 지역별 수출 데이터
    df_export = pd.read_csv("eungmin/기아_지역별수출실적_전처리.csv")
    df_export['연간합계'] = df_export[months].sum(axis=1)
    df_export['차량유형'] = df_export['차량 구분'].str.split('(').str[0]
    
    melt_export = df_export.melt(id_vars=['차량유형', '국가명', '연도'], 
                               value_vars=months,
                               var_name='월', 
                               value_name='수출량')
    melt_export['월'] = melt_export['월'].str.replace('월', '').astype(int)
    
    # 차종별 판매 데이터
    df_sales = pd.read_csv("eungmin/기아_차종별판매실적.csv")
    df_sales['연간합계'] = df_sales[months].sum(axis=1)
    
    melt_sales = df_sales.melt(id_vars=['차종', '차량 구분', '거래 유형', '연도'],
                             value_vars=months,
                             var_name='월',
                             value_name='판매량')
    melt_sales['월'] = melt_sales['월'].str.replace('월', '').astype(int)
    
    # 해외공장 판매 데이터
    df_factory = pd.read_csv("eungmin/기아_해외공장판매실적_전처리.csv")
    df_factory['연간합계'] = df_factory[months].sum(axis=1)
    
    melt_factory = df_factory.melt(id_vars=['공장명(국가)', '공장 코드', '차종', '연도'],
                                 value_vars=months,
                                 var_name='월',
                                 value_name='판매량')
    melt_factory['월'] = melt_factory['월'].str.replace('월', '').astype(int)
    
    return df_export, melt_export, df_sales, melt_sales, df_factory, melt_factory

df_export, melt_export, df_sales, melt_sales, df_factory, melt_factory = load_data()

st.title("🚗 기아 자동차 통합 분석 대시보드")

# 세션 상태 초기화
if 'selected_year' not in st.session_state:
    st.session_state.selected_year = max(df_sales['연도'].unique())
if 'selected_year_factory' not in st.session_state:
    st.session_state.selected_year_factory = max(df_factory['연도'].unique())

# 1. 메인 탭 구성
main_tab1, main_tab2, main_tab3 = st.tabs(["🌍 지역별 수출 분석", "🚘 차종별 판매 분석", "🏭 해외공장 판매 분석"])

with main_tab1:
    # 지역별 분석 내부 서브 탭 구성
    sub_tab1, sub_tab2 = st.tabs(["📌 핵심 지표", "🗓️ 월별 분석"])
    
    with sub_tab1:
        # 1. KPI 지표
        st.subheader("주요 수출 지표")
        col1, col2, col3 = st.columns(3)
        col1.metric("총 수출량", f"{df_export['연간합계'].sum():,}대")
        col2.metric("평균 수출량", f"{df_export['연간합계'].mean():,.0f}대/년")
        col3.metric("최다 수출 지역", df_export.groupby('국가명')['연간합계'].sum().idxmax())

        # 2. 지역별 총합 차트
        st.subheader("지역별 총 수출량")
        region_data = df_export.groupby('국가명')['연간합계'].sum().sort_values(ascending=False)
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.barplot(x=region_data.values, y=region_data.index, palette='viridis')
        for i, v in enumerate(region_data.values):
            ax1.text(v + 100, i, f"{v:,}", va='center', fontsize=10)
        st.pyplot(fig1)

        # 3. 지역별 월간 패턴
        st.subheader("지역-월별 수출 현황")
        region_month = melt_export.pivot_table(index='국가명', columns='월', 
                                             values='수출량', aggfunc='mean')
        fig4, ax4 = plt.subplots(figsize=(12, 6))
        sns.heatmap(region_month, cmap="Blues", annot=True, fmt=',.0f',
                    linewidths=.5, cbar_kws={'label': '평균 수출량 (대)'})
        st.pyplot(fig4)

    with sub_tab2:
        # 4. 월별 수출 추이
        st.subheader("월별 수출 추이 (연도별 비교)")
        palette = sns.color_palette("husl", len(df_export['연도'].unique()))
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        for idx, year in enumerate(sorted(df_export['연도'].unique())):
            monthly_data = melt_export[melt_export['연도'] == year].groupby('월')['수출량'].sum()
            sns.lineplot(x=monthly_data.index, y=monthly_data.values, 
                         label=str(year), color=palette[idx], 
                         marker='o', linewidth=2.5, ax=ax2)
        plt.xticks(range(1, 13))
        plt.grid(True, alpha=0.3)
        plt.legend(title="연도", bbox_to_anchor=(1.05, 1), loc='upper left')
        st.pyplot(fig2)
        
        # 5. 차량유형별 월별 패턴
        st.subheader("차량유형-월별 수출 패턴")
        vehicle_month = melt_export.groupby(['차량유형', '월'])['수출량'].mean().unstack()
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        sns.heatmap(vehicle_month, cmap="YlGnBu", annot=True, fmt=',.0f', 
                    linewidths=.5, cbar_kws={'label': '평균 수출량 (대)'})
        st.pyplot(fig3)

with main_tab2:
    # 차종별 분석 내부 서브 탭 구성
    sub_tab1, sub_tab2 = st.tabs(["📊 판매 현황", "📈 트렌드 분석"])
    
    # 연도 선택 (세션 상태 사용)
    selected_year = st.selectbox(
        "연도 선택",
        options=sorted(df_sales['연도'].unique()),
        index=len(df_sales['연도'].unique())-1,
        key='sales_year'
    )
    st.session_state.selected_year = selected_year
    
    # 해당 연도 상위 10개 차종 추출
    top_models = df_sales[df_sales['연도'] == selected_year]\
                .groupby('차종')['연간합계'].sum()\
                .nlargest(10).index.tolist()
    
    with sub_tab1:
        # 1. 차종별 연간 판매량 Top 10
        st.subheader("차종별 연간 판매량 Top 10")
        top_data = df_sales[
            (df_sales['연도'] == selected_year) & 
            (df_sales['차종'].isin(top_models))
        ].groupby('차종')['연간합계'].sum().sort_values(ascending=False)
        
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.barplot(x=top_data.values, y=top_data.index, palette='rocket')
        for i, v in enumerate(top_data.values):
            ax1.text(v + 50, i, f"{v:,}", va='center')
        plt.title(f"{selected_year}년 Top 10 차종", fontsize=14)
        st.pyplot(fig1)
        
        # 2. 상위 차종 거래 유형 비중
        st.subheader("상위 차종별 거래 유형")
        top_type = df_sales[
            (df_sales['연도'] == selected_year) &
            (df_sales['차종'].isin(top_models))
        ].groupby(['차종', '거래 유형'])['연간합계'].sum().unstack()
        
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        top_type.plot(kind='barh', stacked=True, ax=ax2)
        plt.legend(title="거래 유형", bbox_to_anchor=(1.05, 1))
        plt.title("국내/수출 비율", fontsize=14)
        st.pyplot(fig2)
    
    with sub_tab2:
        # 3. 상위 차종 월별 추이 (Top 5)
        st.subheader("상위 5개 차종 월별 추이")
        top5 = top_models[:5]
        monthly_top5 = melt_sales[
            (melt_sales['연도'] == selected_year) & 
            (melt_sales['차종'].isin(top5))
        ].groupby(['차종', '월'])['판매량'].sum().unstack().T
        
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        for model in top5:
            sns.lineplot(x=monthly_top5.index, y=monthly_top5[model], 
                         label=model, marker='o', linewidth=2.5)
        plt.title("월별 판매 동향", fontsize=14)
        plt.xticks(range(1, 13))
        plt.grid(True, alpha=0.3)
        st.pyplot(fig3)
        
        # 4. 상위 차종 비교
        st.subheader("상위 차종 직접 비교")
        
        col1, col2 = st.columns(2)
        with col1:
            model1 = st.selectbox(
                "첫 번째 차종",
                options=top_models,
                index=0,
                key='model1'
            )
        with col2:
            model2 = st.selectbox(
                "두 번째 차종", 
                options=[m for m in top_models if m != model1],
                index=1 if len(top_models) > 1 else 0,
                key='model2'
            )
        
        compare = melt_sales[
            (melt_sales['차종'].isin([model1, model2])) &
            (melt_sales['연도'] == selected_year)
        ].pivot_table(index='월', columns='차종', values='판매량', aggfunc='sum')
        
        fig4, ax4 = plt.subplots(figsize=(10, 5))
        compare.plot(kind='bar', ax=ax4, width=0.8)
        plt.title(f"{model1} vs {model2}", fontsize=14)
        plt.xlabel("월")
        st.pyplot(fig4)

with main_tab3:
    # 해외공장 분석 내부 서브 탭 구성
    sub_tab1, sub_tab2 = st.tabs(["🏗️ 공장별 분석", "🚙 차종별 분석"])
    
    # 연도 선택 (세션 상태 사용)
    selected_year_factory = st.selectbox(
        "연도 선택",
        options=sorted(df_factory['연도'].unique()),
        index=len(df_factory['연도'].unique())-1,
        key='factory_year'
    )
    st.session_state.selected_year_factory = selected_year_factory
    
    with sub_tab1:
        # 1. 공장별 총 판매량
        st.subheader("공장별 연간 총 판매량")
        factory_total = df_factory[df_factory['연도'] == selected_year_factory]\
                      .groupby('공장명(국가)')['연간합계'].sum().sort_values(ascending=False)
        
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.barplot(x=factory_total.values, y=factory_total.index, palette='mako')
        for i, v in enumerate(factory_total.values):
            ax1.text(v + 100, i, f"{v:,}", va='center')
        plt.title(f"{selected_year_factory}년 공장별 총 판매량", fontsize=14)
        st.pyplot(fig1)
        
        # 2. 공장별 월별 판매 추이
        st.subheader("공장별 월별 판매 추이")
        factory_monthly = melt_factory[melt_factory['연도'] == selected_year_factory]\
                        .groupby(['공장명(국가)', '월'])['판매량'].sum().unstack()
        
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        for factory in factory_monthly.index:
            sns.lineplot(x=factory_monthly.columns, y=factory_monthly.loc[factory], 
                         label=factory, marker='o', linewidth=2.5)
        plt.title("월별 판매 추이", fontsize=14)
        plt.xticks(range(1, 13))
        plt.grid(True, alpha=0.3)
        plt.legend(title="공장명", bbox_to_anchor=(1.05, 1))
        st.pyplot(fig2)
    
    with sub_tab2:
        # 3. 차종별 공장 분포
        st.subheader("차종별 생산 공장 분포 (Top 10)")
        top_models_factory = df_factory[df_factory['연도'] == selected_year_factory]\
                           .groupby('차종')['연간합계'].sum()\
                           .nlargest(10).index.tolist()
        
        model_factory = df_factory[
            (df_factory['연도'] == selected_year_factory) &
            (df_factory['차종'].isin(top_models_factory))
        ].groupby(['차종', '공장명(국가)'])['연간합계'].sum().unstack()
        
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        model_factory.plot(kind='barh', stacked=True, ax=ax3)
        plt.title("차종별 생산 공장 분포", fontsize=14)
        plt.legend(title="공장명", bbox_to_anchor=(1.05, 1))
        st.pyplot(fig3)
        
        # 4. 차종 선택 상세 분석
        st.subheader("차종 상세 분석")
        
        # 선택된 연도에 데이터가 있는 차종만 필터링
        available_models = df_factory[df_factory['연도'] == selected_year_factory]\
                          .groupby('차종')['연간합계'].sum()
        available_models = available_models[available_models > 0].index.tolist()
        
        selected_model = st.selectbox(
            "차종 선택",
            options=available_models,
            index=0,
            key='model_select'
        )
        
        model_data = melt_factory[
            (melt_factory['차종'] == selected_model) &
            (melt_factory['연도'] == selected_year_factory)
        ]
        
        fig4, ax4 = plt.subplots(figsize=(12, 6))
        sns.lineplot(data=model_data, x='월', y='판매량', hue='공장명(국가)', 
                     marker='o', linewidth=2.5)
        plt.title(f"{selected_model} 월별 판매 추이 ({selected_year_factory}년)", fontsize=14)
        plt.xticks(range(1, 13))
        plt.grid(True, alpha=0.3)
        st.pyplot(fig4)

# 데이터 탐색기
st.sidebar.header("📁 데이터 탐색")
with st.sidebar.expander("수출 데이터 보기"):
    st.dataframe(df_export.head())

with st.sidebar.expander("판매 데이터 보기"):
    st.dataframe(df_sales.head())

with st.sidebar.expander("해외공장 데이터 보기"):
    st.dataframe(df_factory.head())

# 분석 팁
st.sidebar.caption("""
💡 분석 팁:
- 지역별 분석: 수출 전략 최적화
- 차종별 분석: 인기 모델 및 계절성 패턴 파악
- 해외공장 분석: 생산 현황 및 지역별 전략 분석
""")