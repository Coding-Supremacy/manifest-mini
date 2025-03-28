import streamlit as st
import pandas as pd

def run_raw_data():
    st.title("📊 원본 데이터 보기")
    file_map = {
        "기아 2023년 해외공장 판매실적": "data/원본_기아_2023년 해외공장판매실적.CSV",
        "기아 2023년 해외현지 판매": "data/원본_기아_2023년 해외현지판매.CSV",
        "기아 2024년 지역별 수출실적": "data/원본_기아_2024년_지역별수출실적.csv",
        "기아 2024년 차종별 판매실적": "data/원본_기아_2024년_차종별판매실적.csv",
        "현대 2023년 해외공장 판매실적": "data/원본_hmc-global-plant-sales-december-y2023.csv",
        "현대 2024년 EU 소매 판매실적": "data/원본_hmc-eu-retail-sales-december-y2024.csv",
        "현대 2023년 지역별 수출실적": "data/원본hmc-export-by-region-december-y2023.csv",
        "현대 2023년 차종별 판매실적": "data/원본_hmc-sales-by-model-december-y2023.csv",
    }
    st.markdown("""
데이터는 해당 형식으로 2023, 2024, 2025년 년도별로 제공받았습니다.
                """)

    # 선택 박스
    selected_label = st.selectbox("확인할 원본 데이터를 선택하세요", list(file_map.keys()))
    file_path = file_map[selected_label]

    try:
        df = pd.read_csv(file_path)
        st.dataframe(df, use_container_width=True)
        st.write(f"🔢 데이터 크기: {df.shape[0]:,}행 × {df.shape[1]:,}열")
    except Exception as e:
        st.error(f"❌ 파일을 불러오는 중 오류 발생: {e}")

    # 하단 링크 정리
    st.markdown("---")
    st.markdown("""
**📌 데이터 출처**  
- [기아 공식 홈페이지](https://worldwide.kia.com/kr/company/ir/archive/sales-results)  
- [현대 공식 홈페이지](https://www.hyundai.com/worldwide/ko/company/ir/ir-resources/sales-results)  
- [협력사 제공 데이터](https://block-edu.s3.ap-northeast-2.amazonaws.com/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8+%EB%8D%B0%EC%9D%B4%ED%84%B0.zip)
""")