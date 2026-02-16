import streamlit as st
import pandas as pd

# 1. 초기 데이터 설정 (전산 DB)
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame([
        {"ID": "user01", "이름": "홍길동", "직추천": 12, "소실적": 65, "수익($)": 1500.0, "상태": "활성"},
        {"ID": "user02", "이름": "김철수", "직추천": 5, "소실적": 10, "수익($)": 450.0, "상태": "활성"}
    ])

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

# --- 로그인 화면 ---
def login_page():
    st.title("💎 TRADING X SYSTEM")
    login_id = st.text_input("아이디")
    login_pw = st.text_input("비밀번호", type="password")
    
    if st.button("접속하기"):
        if login_id == "admin" and login_pw == "admin123": # 관리자 비번 설정
            st.session_state.logged_in = True
            st.session_state.user_role = "Admin"
            st.rerun()
        elif login_id in st.session_state.db['ID'].values:
            st.session_state.logged_in = True
            st.session_state.user_role = "User"
            st.session_state.current_user = login_id
            st.rerun()
        else:
            st.error("정보가 올바르지 않습니다.")

# --- 관리자 페이지 (Admin) ---
def admin_page():
    st.title("🛠️ 총괄 관리자 전산")
    menu = st.sidebar.radio("전산 메뉴", ["전체 현황", "회원 실적 제어", "신규 회원 등록"])

    if menu == "전체 현황":
        st.subheader("📊 플랫폼 통계")
        c1, c2 = st.columns(2)
        c1.metric("총 회원수", len(st.session_state.db))
        c2.metric("총 지급 수익", f"${st.session_state.db['수익($)'].sum():,.2(f)}")
        st.dataframe(st.session_state.db, use_container_width=True)

    elif menu == "회원 실적 제어":
        st.subheader("⚙️ 실적 수동 조정")
        st.write("랏(Lot) 수나 소실적 인원을 직접 수정하세요.")
        edited_db = st.data_editor(st.session_state.db)
        if st.button("전산 데이터 업데이트"):
            st.session_state.db = edited_db
            st.success("데이터가 반영되었습니다.")

    elif menu == "신규 회원 등록":
        st.subheader("👤 회원 강제 등록")
        with st.form("new_user"):
            n_id = st.text_input("새 ID")
            n_name = st.text_input("이름")
            if st.form_submit_button("등록"):
                new_data = {"ID": n_id, "이름": n_name, "직추천": 0, "소실적": 0, "수익($)": 0.0, "상태": "활성"}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_data])], ignore_index=True)
                st.rerun()

# --- 사용자 페이지 (User) ---
def user_page():
    user_info = st.session_state.db[st.session_state.db['ID'] == st.session_state.current_user].iloc[0]
    st.title(f"👋 {user_info['이름']}님, 반갑습니다.")
    
    st.markdown(f"""
        <div style="padding:20px; border-radius:15px; background-color:#1e293b; color:white;">
            <h3>나의 누적 리베이트</h3>
            <h1 style="color:#00F0FF;">${user_info['수익($)']:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    st.write("---")
    col1, col2 = st.columns(2)
    col1.metric("내 직추천", f"{user_info['직추천']}명")
    col2.metric("내 소실적", f"{user_info['소실적']}명")
    
    st.subheader("📢 공지사항")
    st.info("현재 15개월 구독 플랜($1,000) 이벤트 중입니다!")

# --- 메인 흐름 제어 ---
if not st.session_state.logged_in:
    login_page()
else:
    if st.sidebar.button("로그아웃"):
        st.session_state.logged_in = False
        st.rerun()
    
    if st.session_state.user_role == "Admin":
        admin_page()
    else:
        user_page()
