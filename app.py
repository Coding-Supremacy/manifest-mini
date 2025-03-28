import streamlit as st

from ui.raw_data import run_raw_data

# set_page_config는 반드시 첫 번째 Streamlit 명령이어야 함
st.set_page_config(
    page_title="자동차 판매 분석 시스템",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 나머지 임포트
from streamlit_option_menu import option_menu
import warnings

# 경고 메시지 무시
warnings.filterwarnings("ignore")

# 페이지 모듈 임포트
from ui.home import run_home
from ui.description import run_description
from ui.eda_kia import run_eda_kia
from ui.eda_hyundai import run_eda_hyundai
from ui.trend import run_trend
from ui.prediction_region import run_prediction_region
from ui.ho import run_ho

def configure_page():
    """스트림릿 페이지 기본 설정"""
    # CSS 스타일 적용
    st.markdown("""
    <style>
        .main { padding: 2rem; }
        .sidebar .sidebar-content { padding: 1rem; }
        div[data-testid="stSidebarUserContent"] { padding: 1rem; }
        .stButton>button { width: 100%; }
        .stDownloadButton>button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

def main_menu():
    """사이드바 메뉴 구성"""
    with st.sidebar:
        st.markdown("## 메뉴 선택")
        
        return option_menu(
            menu_title=None,
            options=["홈","지역별 예측", "기후별 예측", "기아 분석", "현대 분석","시장 트렌드", "프로젝트 개발과정","원본 데이터 확인"],
            icons=["house", "file-earmark-text",
                  "car-front", "car-front",
                  "graph-up", "globe"],
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {"font-size": "14px", "margin": "5px 0"},
            }
        )

def route_pages(selected_page):
    """페이지 라우팅 처리"""
    page_functions = {
        "홈": run_home,
        "기아 분석": run_eda_kia,
        "현대 분석": run_eda_hyundai,
        "시장 트렌드": run_trend,
        "지역별 예측": run_prediction_region,
        "기후별 예측": run_ho,
        "프로젝트 개발과정": run_description,
        "원본 데이터 확인":run_raw_data
    }
    
    if selected_page in page_functions:
        page_functions[selected_page]()
    else:
        st.warning("페이지를 찾을 수 없습니다")

# 데이터 로딩 캐싱 설정
@st.cache_data(ttl=3600)
def load_all_data():
    # 모든 데이터 로딩 함수 통합
    return True

def main():
    """메인 애플리케션 실행"""
    load_all_data()
    configure_page()
    selected_page = main_menu()
    route_pages(selected_page)

if __name__ == "__main__":
    main()