import streamlit as st
import pandas as pd

# [핵심] 기존 세션에 'PW' 열이 없으면 강제로 초기화하여 에러를 방지합니다.
if 'db' not in st.session_state or 'PW' not in st.session_state.db.columns:
    st.session_state.db = pd.DataFrame([
        {
            "ID": "admin", "PW": "admin123", "이름": "관리자", 
            "이메일": "admin@tradingx.com", "연락처": "010-0000-0000", 
            "추천인": "-", "위치": "-", "직추천": 0, "소실적": 0, "수익($)": 0.0
        },
        {
            "ID": "user01", "PW": "1234", "이름": "홍길동", 
            "이메일": "hong@test.com", "연락처": "010-1234-5678", 
            "추천인": "admin", "위치": "Left", "직추천": 12, "소실적": 65, "수익($)": 1520.50
        }
    ])

if 'page' not in st.session_state:
    st.session_state.page = "login"

# --- [디자인: 커스텀 CSS] ---
st.markdown("""
    <style>
    .stApp { background-color: #0A0E21; color: #FFFFFF; }
    .main-card {
        background: linear-gradient(135deg, #00F0FF 0%, #0072FF 100%);
        padding: 40px; border-radius: 25px; text-align: center; color: white;
        box-shadow: 0 15px 35px rgba(0,240,255,0.25); margin-bottom: 30px;
    }
    .stMetric { background-color: #161B33 !important; border-radius: 15px !important; padding: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- [기능: 비밀번호 관리] ---
def password_management():
    st.title("🔐 보안 설정")
    tab1, tab2 = st.tabs(["비밀번호 찾기", "비밀번호 변경"])
    
    with tab1:
        f_id = st.text_input("아이디 확인")
        f_email = st.text_input("가입 이메일 확인")
        if st.button("임시 비밀번호 요청"):
            user = st.session_state.db[(st.session_state.db['ID'] == f_id) & (st.session_state.db['이메일'] == f_email)]
            if not user.empty:
                st.info(f"등록된 이메일({f_email})로 안내 메일을 발송했습니다.")
            else:
                st.error("일치하는 정보를 찾을 수 없습니다.")

    with tab2:
        if 'current_user' in st.session_state:
            curr_pw = st.text_input("현재 비밀번호", type="password")
            new_pw = st.text_input("변경할 비밀번호", type="password")
            if st.button("비밀번호 업데이트"):
                idx = st.session_state.db[st.session_state.db['ID'] == st.session_state.current_user].index
                if not idx.empty and st.session_state.db.at[idx[0], 'PW'] == curr_pw:
                    st.session_state.db.at[idx[0], 'PW'] = new_pw
                    st.success("비밀번호가 안전하게 변경되었습니다.")
                else:
                    st.error("비밀번호가 일치하지 않거나 오류가 발생했습니다.")
        else:
            st.warning("로그인이 필요한 서비스입니다.")

# --- [페이지: 대시보드] ---
def user_dashboard():
    user_info = st.session_state.db[st.session_state.db['ID'] == st.session_state.current_user].iloc[0]
    st.title("📊 My Trading Status")
    
    st.markdown(f"""
        <div class="main-card">
            <p style="font-size:18px; opacity:0.9; margin-bottom:10px;">Total Trading Profit</p>
            <h1 style="font-size:56px; font-weight:800;">${user_info['수익($)']:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Direct referrals", f"{user_info['직추천']}명")
    c2.metric("Weak leg members", f"{user_info['소실적']}명")
    c3.metric("Level Status", "Diamond")

    st.write("---")
    l_col, r_col = st.columns([2, 1])
    with l_col:
        st.subheader("📈 실적 추이")
        st.area_chart([20, 35, 45, 80, 60, 90, 110])
    with r_col:
        st.subheader("⚙️ Quick Menu")
        if st.button("비밀번호 변경", use_container_width=True):
            st.session_state.page = "pw_manage"
            st.rerun()
        if st.button("로그아웃", use_container_width=True):
            del st.session_state.current_user
            st.session_state.page = "login"
            st.rerun()

# --- [페이지: 로그인] ---
def login_page():
    st.title("💎 TRADING X")
    l_id = st.text_input("ID")
    l_pw = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", use_container_width=True):
            user = st.session_state.db[(st.session_state.db['ID'] == l_id) & (st.session_state.db['PW'] == l_pw)]
            if not user.empty:
                st.session_state.current_user = l_id
                st.session_state.page = "user"
                st.rerun()
            else:
                st.error("계정 정보를 확인하세요.")
    with col2:
        if st.button("Sign Up", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()
    
    if st.button("Forgot Password?", type="secondary"):
        st.session_state.page = "pw_manage"
        st.rerun()

# --- 메인 제어 로직 ---
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "user":
    user_dashboard()
elif st.session_state.page == "pw_manage":
    if st.button("← Back"):
        st.session_state.page = "user" if 'current_user' in st.session_state else "login"
        st.rerun()
    password_management()
elif st.session_state.page == "signup":
    st.title("📝 회원가입")
    # 간단한 가입 폼
    s_id = st.text_input("희망 ID")
    s_pw = st.text_input("희망 Password", type="password")
    s_name = st.text_input("성함")
    if st.button("가입신청"):
        new_user = {"ID": s_id, "PW": s_pw, "이름": s_name, "이메일": "", "연락처": "", "추천인": "admin", "위치": "Left", "직추천": 0, "소실적": 0, "수익($)": 0.0}
        st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_user])], ignore_index=True)
        st.success("가입 완료! 로그인 해주세요.")
        st.session_state.page = "login"
    if st.button("← Back to Login"):
        st.session_state.page = "login"
        st.rerun()
