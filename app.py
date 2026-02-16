import streamlit as st
import pandas as pd

# 1. 전산 DB 초기화
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame([
        {"ID": "admin", "이름": "관리자", "이메일": "admin@test.com", "추천인": "-", "위치": "-", "직추천": 0, "소실적": 0, "수익($)": 0.0}
    ])

if 'page' not in st.session_state:
    st.session_state.page = "login"

# --- [페이지: 회원가입] ---
def signup_page():
    st.title("📝 TRADING X 회원가입")
    with st.form("signup_form"):
        new_id = st.text_input("아이디 (ID)")
        new_pw = st.text_input("비밀번호", type="password")
        new_name = st.text_input("성함 (Full Name)")
        new_email = st.text_input("이메일 (Email)")
        new_phone = st.text_input("연락처 (Phone)")
        ref_id = st.text_input("추천인 ID (Referral ID)")
        position = st.radio("배치 방향 (Position)", ["Left (좌)", "Right (우)"])
        
        if st.form_submit_button("가입 완료"):
            if new_id in st.session_state.db['ID'].values:
                st.error("이미 존재하는 아이디입니다.")
            elif not ref_id:
                st.error("추천인 ID는 필수입니다.")
            else:
                # DB에 신규 회원 추가
                new_user = {
                    "ID": new_id, "이름": new_name, "이메일": new_email, 
                    "추천인": ref_id, "위치": position, 
                    "직추천": 0, "소실적": 0, "수익($)": 0.0
                }
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_user])], ignore_index=True)
                st.success("가입이 완료되었습니다! 로그인을 해주세요.")
                st.session_state.page = "login"
    
    if st.button("이미 계정이 있나요? 로그인하기"):
        st.session_state.page = "login"
        st.rerun()

# --- [페이지: 로그인] ---
def login_page():
    st.title("💎 TRADING X 접속")
    login_id = st.text_input("아이디")
    login_pw = st.text_input("비밀번호", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("로그인"):
            if login_id == "admin" and login_pw == "admin123":
                st.session_state.page = "admin"
                st.rerun()
            elif login_id in st.session_state.db['ID'].values:
                st.session_state.current_user = login_id
                st.session_state.page = "user"
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호를 확인하세요.")
    with col2:
        if st.button("회원가입하러 가기"):
            st.session_state.page = "signup"
            st.rerun()

# --- [관리자 및 사용자 화면은 이전과 동일하되 DB 연동 유지] ---
def admin_page():
    st.title("🛠️ 관리자 총괄 전산")
    st.subheader("👥 전체 회원 가입 정보")
    st.dataframe(st.session_state.db, use_container_width=True)
    if st.button("로그아웃"):
        st.session_state.page = "login"
        st.rerun()

def user_page():
    user_info = st.session_state.db[st.session_state.db['ID'] == st.session_state.current_user].iloc[0]
    st.title(f"👋 {user_info['이름']}님 환영합니다.")
    st.write(f"추천인: {user_info['추천인']} | 배치방향: {user_info['위치']}")
    st.metric("나의 수익", f"${user_info['수익($)']:,.2f}")
    if st.button("로그아웃"):
        st.session_state.page = "login"
        st.rerun()

# --- 메인 실행 ---
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "admin":
    admin_page()
elif st.session_state.page == "user":
    user_page()
