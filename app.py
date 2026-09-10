import streamlit as st
from datetime import datetime, date

# 페이지 기본 설정
st.set_page_config(
    page_title="통신 회선 및 요금제 통합 관리 프로그램",
    page_icon="📱",
    layout="wide"
)

# 다크모드 및 사이드바 입력창(date_input 포함) 스타일 일치화 CSS
st.markdown("""
    <style>
    /* 다른 입력칸들과 동일한 배경 및 테두리 로직 적용 */
    [data-testid="stSidebar"] div[data-baseweb="input"] input {
        background-color: inherit !important;
        color: inherit !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="base-input"] {
        background-color: inherit !important;
    }
    </style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "lines" not in st.session_state:
    st.session_state.lines = []
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "다크 모드"

# 상단 테마 설정 및 헤더
col_title, col_theme = st.columns([3, 1])

with col_title:
    st.markdown("### 📱 통신 회선 및 요금제 통합 관리 프로그램")
    st.markdown("회선별 상세 정보 및 의무기간, 요금제 변경일, 해지 가능일, 부가서비스 일정을 관리하세요.")

with col_theme:
    st.markdown("🎨 테마 설정")
    theme_choice = st.selectbox(
        "테마 선택", 
        ["다크 모드", "라이트 모드"], 
        label_visibility="collapsed",
        key="theme_mode"
    )

st.markdown("---")
st.markdown("### 📋 회선 세부 관리 목록")

# 사이드바 입력 폼
with st.sidebar:
    st.markdown("### ➕ 새 회선 추가")
    
    phone_number = st.text_input("전화번호", "010-0000-0000")
    carrier = st.selectbox("통신사", ["SKT", "KT", "LGU+", "알뜰폰(SKT)", "알뜰폰(KT)", "알뜰폰(LGU+)"])
    
    # [수정된 부분] 날짜 입력창 (다른 입력칸과 동일하게 다크모드 배경 스타일 적용됨)
    join_date = st.date_input("가입일", value=date(2026, 9, 10))
    
    col_a, col_b = st.columns(2)
    with col_a:
        contract_period = st.number_input("의무기간(일)", value=185, step=30)
    with col_b:
        plan_change_period = st.number_input("요금제변경(일)", value=120, step=30)
        
    owner = st.text_input("명의", "홍길동")
    phone_model = st.text_input("폰모델", "Galaxy S24")
    
    col_c, col_d = st.columns(2)
    with col_c:
        activation_fee = st.text_input("가입비", "0원")
    with col_d:
        purchase_type = st.text_input("구입", "신규/번이/기변")
        
    carrier_id = st.text_input("통신사 계정 ID", "아이디 입력")
    payment_info = st.text_input("납부정보", "카드/계좌 정보")
    memo = st.text_area("상세 참고사항 / 비고", "- 혜택/상품권 관련 메모\n- 결합할인 정보 및 고객센터 안내 내용 등 자유 작성")

    if st.button("새 회선 추가", type="primary", use_container_width=True):
        new_line = {
            "phone": phone_number,
            "carrier": carrier,
            "join_date": join_date,
            "contract": contract_period,
            "plan_change": plan_change_period,
            "owner": owner,
            "model": phone_model,
            "activation_fee": activation_fee,
            "purchase_type": purchase_type,
            "carrier_id": carrier_id,
            "payment_info": payment_info,
            "memo": memo
        }
        st.session_state.lines.append(new_line)
        st.success("새 회선이 추가되었습니다!")
        st.rerun()

# 메인 화면 회선 목록 표시 영역
if not st.session_state.lines:
    col_add_btn, col_memo_toggle = st.columns([1, 1])
    with col_add_btn:
        if st.button("➕ 새 회선 추가"):
            pass
    with col_memo_toggle:
        show_memo = st.checkbox("🔍 상세 메모 숨기기", value=True)
        
    st.markdown("---")
    st.info("👉 왼쪽 사이드바 또는 상단의 '➕ 새 회선 추가' 버튼을 눌러 회선 정보를 입력해 주세요.")
    
    st.markdown("### 📌 의무 부가서비스 일정")
    st.info("등록된 의무 부가서비스 일정이 없습니다. 각 회선의 수정(✏️) 버튼을 눌러 부가서비스를 추가해 주세요.")
    
    if st.button("🚨 전체 목록 초기화"):
        st.session_state.lines = []
        st.rerun()
else:
    for idx, line in enumerate(st.session_state.lines):
        st.markdown(f"**회선 {idx+1}: {line['phone']} ({line['carrier']} / {line['model']})** - 명의: {line['owner']} / 가입일: {line['join_date']}")
    
    if st.button("🚨 전체 목록 초기화"):
        st.session_state.lines = []
        st.rerun()
