import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

@st.cache_data(ttl=3600, show_spinner="데이터 로드 중...")
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
    
    # 해외현지판매 데이터
    df_overseas = pd.read_csv("eungmin/기아_해외현지판매_전처리.CSV")
    df_overseas['월별합계'] = df_overseas[months].sum(axis=1)
    
    melt_overseas = df_overseas.melt(id_vars=['국가명', '공장명(국가)', '차종', '연도'],
                                    value_vars=months,
                                    var_name='월',
                                    value_name='판매량')
    melt_overseas['월'] = melt_overseas['월'].str.replace('월', '').astype(int)
    
    return df_export, melt_export, df_sales, melt_sales, df_factory, melt_factory, df_overseas, melt_overseas

# 차트 생성 함수 (캐싱 적용)
@st.cache_data(ttl=600, show_spinner=False)
def create_plot(_fig):
    return _fig

# 데이터 로드
df_export, melt_export, df_sales, melt_sales, df_factory, melt_factory, df_overseas, melt_overseas = load_data()


powertrain_types = {
    '내연기관': ['Bongo', 'K3', 'K5', 'Carnival', 'Seltos', 'Sportage', 'Sorento'],
    '전기차': ['EV6', 'EV9', 'Niro EV', 'Soul EV', 'EV5'],
    '하이브리드': ['Niro', 'Sorento Hybrid', 'Sportage Hybrid']
}

# 파워트레인 유형 결정 함수
def get_powertrain_type(model):
    for ptype, models in powertrain_types.items():
        if any(m in model for m in models):
            return ptype
    return '내연기관'  # 기본값

# 데이터 전처리
df_overseas['파워트레인'] = df_overseas['차종'].apply(get_powertrain_type)

st.title("🚗 기아 자동차 통합 분석 대시보드 (최적화 버전)")

# 세션 상태 초기화 (추가)
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "🌍 지역별 수출 분석"

# 탭 변경 감지 함수
def on_tab_change():
    st.session_state.current_tab = st.session_state.tab_key

# 메인 탭 구성 (수정)
main_tabs = st.tabs(["🌍 지역별 수출 분석", "🚘 차종별 판매 분석", "🏭 해외공장 판매 분석", "📊 해외현지 판매 분석"])

# 현재 활성 탭 확인
current_tab = st.session_state.current_tab

with main_tabs[0] if current_tab == "🌍 지역별 수출 분석" else main_tabs[0]:
    sub_tab1, sub_tab2 = st.tabs(["📌 핵심 지표", "🗓️ 월별 분석"])
    
    with sub_tab1:
        # 1. KPI 지표 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_kpi_metrics():
            total_export = df_export['연간합계'].sum()
            avg_export = df_export['연간합계'].mean()
            top_region = df_export.groupby('국가명')['연간합계'].sum().idxmax()
            return total_export, avg_export, top_region

        total_export, avg_export, top_region = get_kpi_metrics()
        
        st.subheader("주요 수출 지표")
        col1, col2, col3 = st.columns(3)
        col1.metric("총 수출량", f"{total_export:,}대")
        col2.metric("평균 수출량", f"{avg_export:,.0f}대/년")
        col3.metric("최다 수출 지역", top_region)

        # 2. 지역별 총합 차트 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_region_chart():
            region_data = df_export.groupby('국가명')['연간합계'].sum().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x=region_data.values, y=region_data.index, palette='viridis')
            for i, v in enumerate(region_data.values):
                ax.text(v + 100, i, f"{v:,}", va='center', fontsize=10)
            plt.tight_layout()
            return fig

        st.subheader("지역별 총 수출량")
        fig1 = get_region_chart()
        st.pyplot(fig1)

        # 3. 지역별 월간 패턴 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_region_heatmap():
            region_month = melt_export.pivot_table(index='국가명', columns='월', 
                                                 values='수출량', aggfunc='mean')
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.heatmap(region_month, cmap="Blues", annot=True, fmt=',.0f',
                        linewidths=.5, cbar_kws={'label': '평균 수출량 (대)'})
            plt.tight_layout()
            return fig

        st.subheader("지역-월별 수출 현황")
        fig4 = get_region_heatmap()
        st.pyplot(fig4)

    with sub_tab2:
        # 4. 월별 수출 추이 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_monthly_trend():
            palette = sns.color_palette("husl", len(df_export['연도'].unique()))
            fig, ax = plt.subplots(figsize=(12, 6))
            for idx, year in enumerate(sorted(df_export['연도'].unique())):
                monthly_data = melt_export[melt_export['연도'] == year].groupby('월')['수출량'].sum()
                sns.lineplot(x=monthly_data.index, y=monthly_data.values, 
                             label=str(year), color=palette[idx], 
                             marker='o', linewidth=2.5, ax=ax)
            plt.xticks(range(1, 13))
            plt.grid(True, alpha=0.3)
            plt.legend(title="연도", bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            return fig

        st.subheader("월별 수출 추이 (연도별 비교)")
        fig2 = get_monthly_trend()
        st.pyplot(fig2)
        
        # 5. 차량유형별 월별 패턴 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_vehicle_heatmap():
            vehicle_month = melt_export.groupby(['차량유형', '월'])['수출량'].mean().unstack()
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.heatmap(vehicle_month, cmap="YlGnBu", annot=True, fmt=',.0f', 
                        linewidths=.5, cbar_kws={'label': '평균 수출량 (대)'})
            plt.tight_layout()
            return fig

        st.subheader("차량유형-월별 수출 패턴")
        fig3 = get_vehicle_heatmap()
        st.pyplot(fig3)

with main_tabs[1] if current_tab == "🚘 차종별 판매 분석" else main_tabs[1]:
    sub_tab1, sub_tab2 = st.tabs(["📊 판매 현황", "📈 트렌드 분석"])
    
    selected_year = st.selectbox(
        "연도 선택",
        options=sorted(df_sales['연도'].unique()),
        index=len(df_sales['연도'].unique())-1,
        key='sales_year'
    )
    
    # 캐싱 적용된 상위 차종 추출
    @st.cache_data(ttl=300)
    def get_top_models(_df, year, n=10):
        return _df[_df['연도'] == year]\
               .groupby('차종')['연간합계'].sum()\
               .nlargest(n).index.tolist()

    top_models = get_top_models(df_sales, selected_year)
    
    with sub_tab1:
        # 1. 차종별 연간 판매량 Top 10 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_top_models_chart(_df, year, models):
            top_data = _df[
                (_df['연도'] == year) & 
                (_df['차종'].isin(models))
            ].groupby('차종')['연간합계'].sum().sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x=top_data.values, y=top_data.index, palette='rocket')
            for i, v in enumerate(top_data.values):
                ax.text(v + 50, i, f"{v:,}", va='center')
            plt.title(f"{year}년 Top 10 차종", fontsize=14)
            plt.tight_layout()
            return fig

        st.subheader("차종별 연간 판매량 Top 10")
        fig1 = get_top_models_chart(df_sales, selected_year, top_models)
        st.pyplot(fig1)
        
        # 2. 상위 차종 거래 유형 비중 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_sales_composition(_df, year, models):
            top_type = _df[
                (_df['연도'] == year) &
                (_df['차종'].isin(models))
            ].groupby(['차종', '거래 유형'])['연간합계'].sum().unstack()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            top_type.plot(kind='barh', stacked=True, ax=ax)
            plt.legend(title="거래 유형", bbox_to_anchor=(1.05, 1))
            plt.title("국내/수출 비율", fontsize=14)
            plt.tight_layout()
            return fig

        st.subheader("상위 차종별 거래 유형")
        fig2 = get_sales_composition(df_sales, selected_year, top_models)
        st.pyplot(fig2)
    
    with sub_tab2:
        # 3. 상위 차종 월별 추이 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_monthly_trend_top5(_melt, year, models, n=5):
            top5 = models[:n]
            monthly_top5 = _melt[
                (_melt['연도'] == year) & 
                (_melt['차종'].isin(top5))
            ].groupby(['차종', '월'])['판매량'].sum().unstack().T
            
            fig, ax = plt.subplots(figsize=(12, 6))
            for model in top5:
                sns.lineplot(x=monthly_top5.index, y=monthly_top5[model], 
                             label=model, marker='o', linewidth=2.5)
            plt.title("월별 판매 동향", fontsize=14)
            plt.xticks(range(1, 13))
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            return fig

        st.subheader("상위 5개 차종 월별 추이")
        fig3 = get_monthly_trend_top5(melt_sales, selected_year, top_models)
        st.pyplot(fig3)
        
        # 4. 상위 차종 비교 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_model_comparison(_melt, year, model1, model2):
            compare = _melt[
                (_melt['차종'].isin([model1, model2])) &
                (_melt['연도'] == year)
            ].pivot_table(index='월', columns='차종', values='판매량', aggfunc='sum')
            
            fig, ax = plt.subplots(figsize=(10, 5))
            compare.plot(kind='bar', ax=ax, width=0.8)
            plt.title(f"{model1} vs {model2}", fontsize=14)
            plt.xlabel("월")
            plt.tight_layout()
            return fig

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
        
        fig4 = get_model_comparison(melt_sales, selected_year, model1, model2)
        st.pyplot(fig4)

with main_tabs[2] if current_tab == "🏭 해외공장 판매 분석" else main_tabs[2]:
    sub_tab1, sub_tab2 = st.tabs(["🏗️ 공장별 분석", "🚙 차종별 분석"])
    
    selected_year_factory = st.selectbox(
        "연도 선택",
        options=sorted(df_factory['연도'].unique()),
        index=len(df_factory['연도'].unique())-1,
        key='factory_year'
    )
    
    with sub_tab1:
        # 1. 공장별 총 판매량 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_factory_total(_df, year):
            factory_total = _df[_df['연도'] == year]\
                          .groupby('공장명(국가)')['연간합계'].sum().sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x=factory_total.values, y=factory_total.index, palette='mako')
            for i, v in enumerate(factory_total.values):
                ax.text(v + 100, i, f"{v:,}", va='center')
            plt.title(f"{year}년 공장별 총 판매량", fontsize=14)
            plt.tight_layout()
            return fig

        st.subheader("공장별 연간 총 판매량")
        fig1 = get_factory_total(df_factory, selected_year_factory)
        st.pyplot(fig1)
        
        # 2. 공장별 월별 판매 추이 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_factory_monthly(_melt, year):
            factory_monthly = _melt[_melt['연도'] == year]\
                            .groupby(['공장명(국가)', '월'])['판매량'].sum().unstack()
            
            fig, ax = plt.subplots(figsize=(12, 6))
            for factory in factory_monthly.index:
                sns.lineplot(x=factory_monthly.columns, y=factory_monthly.loc[factory], 
                             label=factory, marker='o', linewidth=2.5)
            plt.title("월별 판매 추이", fontsize=14)
            plt.xticks(range(1, 13))
            plt.grid(True, alpha=0.3)
            plt.legend(title="공장명", bbox_to_anchor=(1.05, 1))
            plt.tight_layout()
            return fig

        st.subheader("공장별 월별 판매 추이")
        fig2 = get_factory_monthly(melt_factory, selected_year_factory)
        st.pyplot(fig2)
    
    with sub_tab2:
        # 3. 차종별 공장 분포 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_model_factory(_df, year, n=10):
            top_models = _df[_df['연도'] == year]\
                       .groupby('차종')['연간합계'].sum()\
                       .nlargest(n).index.tolist()
            
            model_factory = _df[
                (_df['연도'] == year) &
                (_df['차종'].isin(top_models))
            ].groupby(['차종', '공장명(국가)'])['연간합계'].sum().unstack()
            
            fig, ax = plt.subplots(figsize=(12, 6))
            model_factory.plot(kind='barh', stacked=True, ax=ax)
            plt.title("차종별 생산 공장 분포", fontsize=14)
            plt.legend(title="공장명", bbox_to_anchor=(1.05, 1))
            plt.tight_layout()
            return fig

        st.subheader("차종별 생산 공장 분포 (Top 10)")
        fig3 = get_model_factory(df_factory, selected_year_factory)
        st.pyplot(fig3)
        
        # 4. 차종 선택 상세 분석 (캐싱 적용)
        @st.cache_data(ttl=300)
        def get_model_detail(_melt, year):
            available_models = _melt[_melt['연도'] == year]\
                              .groupby('차종')['판매량'].sum()
            available_models = available_models[available_models > 0].index.tolist()
            return available_models

        available_models = get_model_detail(melt_factory, selected_year_factory)
        
        selected_model = st.selectbox(
            "차종 선택",
            options=available_models,
            index=0,
            key='model_select'
        )
        
        @st.cache_data(ttl=300)
        def get_model_trend(_melt, year, model):
            model_data = _melt[
                (_melt['차종'] == model) &
                (_melt['연도'] == year)
            ]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.lineplot(data=model_data, x='월', y='판매량', hue='공장명(국가)', 
                         marker='o', linewidth=2.5)
            plt.title(f"{model} 월별 판매 추이 ({year}년)", fontsize=14)
            plt.xticks(range(1, 13))
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            return fig

        st.subheader("차종 상세 분석")
        fig4 = get_model_trend(melt_factory, selected_year_factory, selected_model)
        st.pyplot(fig4)

with main_tabs[3]:
    sub_tab1, sub_tab2 = st.tabs(["📈 판매 추이 분석", "🏭 공장 및 지역 분석"])

    selected_year = st.selectbox(
        "연도 선택",
        options=sorted(df_overseas['연도'].unique()),
        index=len(df_overseas['연도'].unique())-1,
        key='overseas_year'
    )

    # 첫 번째 서브탭
    with sub_tab1:
        st.subheader(f"{selected_year}년 지역별 차종 판매량 Top 10")
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        top_regions = df_overseas[df_overseas['연도'] == selected_year].groupby('국가명')['월별합계'].sum().nlargest(10)
        sns.barplot(x=top_regions.values, y=top_regions.index, ax=ax1)
        ax1.set_title(f"Top 10 Regions by Sales in {selected_year}")
        ax1.set_xlabel("Total Sales")
        ax1.set_ylabel("Region")
        st.pyplot(fig1)

        st.subheader(f"{selected_year}년 지역별 월별 판매량")
        fig2, ax2 = plt.subplots(figsize=(12, 8))
        monthly_sales = df_overseas[df_overseas['연도'] == selected_year].groupby('국가명')[['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']].sum()
        
        for country in monthly_sales.index:
            ax2.plot(monthly_sales.columns, monthly_sales.loc[country], label=country, marker='o')
        
        ax2.set_title(f"Monthly Sales by Region in {selected_year}")
        ax2.set_xlabel("Month")
        ax2.set_ylabel("Sales")
        ax2.legend(title="Region", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig2)

    # 두 번째 서브탭
    with sub_tab2:
        st.subheader("공장별 총 판매량")
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        factory_sales = df_overseas.groupby('공장명(국가)')['월별합계'].sum().sort_values(ascending=False)
        sns.barplot(x=factory_sales.values, y=factory_sales.index, ax=ax3)
        ax3.set_title("Total Sales by Factory")
        ax3.set_xlabel("Total Sales")
        ax3.set_ylabel("Factory")
        st.pyplot(fig3)

        selected_powertrain = st.selectbox(
            "파워트레인 유형 선택",
            options=['내연기관', '전기차', '하이브리드'],
            key='powertrain_type'
        )

        top_regions_powertrain = df_overseas[(df_overseas['파워트레인'] == selected_powertrain) & (df_overseas['연도'] == selected_year)].groupby('국가명')['월별합계'].sum().nlargest(5)

        if not top_regions_powertrain.empty:
            fig5, ax5 = plt.subplots(figsize=(10, 6))
            sns.barplot(x=top_regions_powertrain.values, y=top_regions_powertrain.index, ax=ax5)
            ax5.set_title(f"{selected_year}년 Top 5 Regions for {selected_powertrain} Vehicles")
            ax5.set_xlabel("Total Sales")
            ax5.set_ylabel("Region")
            st.pyplot(fig5)
        else:
            st.warning(f"{selected_powertrain} 차량의 판매 데이터가 없습니다.")



        
        

