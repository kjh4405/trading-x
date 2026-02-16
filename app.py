import streamlit as st
import pandas as pd
import time

# 1. 전산 DB 및 세션 초기화
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame([
        {"ID": "user01", "PW": "1234", "이름": "홍길동", "이메일": "hong@test.com", "연락처": "010-1234-5678", "추천인": "admin", "위치": "Left", "직추천": 12, "소실적": 65, "수익($)": 1520.50}
    ])

if 'page' not in st.session_state:
    st.session_state.page = "login"

# --- [공통 CSS 디자인] ---
st.markdown("""
    <style>
    .main { background-color: #0A0E21; }
    .stMetric { background-color: #161B33; padding: 15px; border-radius: 10px; border: 1px solid #2E344E; }
    .profit-card { 
        background: linear-gradient(135deg, #00F0FF 0%, #0072FF 100%); 
        padding: 30px; border-radius: 20px; color: white; text-align: center; margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,240,255,0.2);
    }
    .custom-card {
        background-color: #161B33; padding: 20px; border-radius: 15px; border-left: 5px solid #00F0FF; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [기능: 비밀번호 찾기 & 변경] ---
def password_management():
    st.subheader("🔐 비밀번호 관리")
    tab1, tab2 = st.tabs(["비밀번호 찾기", "비밀번호 변경"])
    
    with tab1:
        st.write("등록된 이메일과 아이디를 입력하세요.")
        find_id = st.text_input("아이디 확인")
        find_email = st.text_input("이메일 확인")
        if st.button("임시 비밀번호 발송"):
            user_exists = st.session_state.db[(st.session_state.db['ID'] == find_id) & (st.session_state.db['이메일'] == find_email)]
            if not user_exists.empty:
                st.success(f"{find_email}로 임시 안내가 전송되었습니다. (기능 구현 중)")
            else:
                st.error("일치하는 정보가 없습니다.")

    with tab2:
        if 'current_user' in st.session_state:
            old_pw = st.text_input("기존 비밀번호", type="password")
            new_pw = st.text_input("새 비밀번호", type="password")
            if st.button("변경하기"):
                idx = st.session_state.db[st.session_state.db['ID'] == st.session_state.current_user].index
                if st.session_state.db.loc[idx, 'PW'].values[0] == old_pw:
                    st.session_state.db.at[idx[0], 'PW'] = new_pw
                    st.success("비밀번호가 안전하게 변경되었습니다.")
                else:
                    st.error("기존 비밀번호가 틀립니다.")
        else:
            st.warning("로그인 후 이용 가능합니다.")

# --- [페이지: 로그인 후 회원 대시보드] ---
def user_dashboard():
    user_info = st.session_state.db[st.session_state.db['ID'] == st.session_state.current_user].iloc[0]
    
    st.title(f"📊 Trading X Dashboard")
    st.write(f"Welcome back, **{user_info['이름']}**님")

    # 메인 수익 카드
    st.markdown(f"""
        <div class="profit-card">
            <p style="margin:0; font-size:16px; opacity:0.8;">Total Accumulated Profit</p>
            <h1 style="margin:0; font-size:48px;">${user_info['수익($)']:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    # 지표 분석 섹션
    col1, col2, col3 = st.columns(3)
    col1.metric("Direct Referrals", f"{user_info['직추천']}명", "+2 this week")
    col2.metric("Small Leg", f"{user_info['소실적']}명", "Level 3")
    col3.metric("Current Rebate", "17.5%", "Active")

    st.write("---")
    
    # 2단 구성 (조직 현황 & 설정)
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        st.subheader("📈 실적 통계 (최근 7일)")
        # 샘플 그래프
        chart_data = pd.DataFrame([120, 150, 180, 220, 200, 250, 310], columns=['Daily Profit'])
        st.area_chart(chart_data)
        
        st.subheader("📂 최근 정산 내역")
        st.write("2026-02-16 | $120.00 | Trading Rebate")
        st.write("2026-02-15 | $500.00 | Subscription Bonus")

    with right_col:
        st.subheader("⚙️ Account Settings")
        if st.button("비밀번호 변경하기"):
            st.session_state.sub_page = "pw_change"
        
        st.markdown("""
            <div class="custom-card">
                <p style="margin:0; font-size:12px;">Rank Status</p>
                <b style="color:#00F0FF;">Diamond Partner</b>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("로그아웃", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

# --- [메인 실행 제어] ---
# (상태에 따라 login_page, signup_page, password_management 호출 로직 포함)
# ... 중략 (이전의 로그인/회원가입 로직과 동일) ...

if st.session_state.page == "user":
    if 'sub_page' in st.session_state and st.session_state.sub_page == "pw_change":
        if st.button("← 대시보드로 돌아가기"):
            del st.session_state.sub_page
            st.rerun()
        password_management()
    else:
        user_dashboard()
elif st.session_state.page == "login":
    # 로그인 화면 내에 '비번 잊으셨나요?' 버튼 추가
    st.title("💎 TRADING X")
    # ... (로그인 입력창)
    if st.button("비밀번호를 잊으셨나요?"):
        st.session_state.page = "find_pw"
        st.rerun()
elif st.session_state.page == "find_pw":
    if st.button("← 로그인으로 돌아가기"):
        st.session_state.page = "login"
        st.rerun()
    password_management()
