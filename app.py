import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="Trading X Admin", layout="wide")

# 세션 관리 (로그인 상태 및 데이터 저장)
if 'db' not in st.session_state:
    # 샘플 데이터베이스 (실제 운영 시 구글 시트나 DB 연결 가능)
    st.session_state.db = pd.DataFrame([
        {"ID": "user01", "Name": "홍길동", "Left": 10, "Right": 5, "Rebate": 120.0},
        {"ID": "user02", "Name": "김철수", "Left": 2, "Right": 8, "Rebate": 45.0}
    ])

if 'role' not in st.session_state:
    st.session_state.role = None

# --- 로그인 로직 ---
def login():
    st.title("🔐 TRADING X 시스템 접속")
    user = st.text_input("아이디")
    pw = st.text_input("비밀번호", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("사용자 로그인"):
            st.session_state.role = "User"
            st.rerun()
    with col2:
        if st.button("관리자 로그인"):
            # 관리자 전용 비밀번호 예시 (admin123)
            if pw == "admin123":
                st.session_state.role = "Admin"
                st.rerun()
            else:
                st.error("관리자 비밀번호가 틀렸습니다.")

# --- 관리자 전산 화면 ---
def admin_panel():
    st.title("🛠️ 관리자 전산 제어판")
    
    # 1. 회원 등록 섹션
    with st.expander("👤 신규 회원 등록"):
        new_id = st.text_input("회원 ID")
        new_name = st.text_input("회원 성함")
        if st.button("등록 완료"):
            new_data = {"ID": new_id, "Name": new_name, "Left": 0, "Right": 0, "Rebate": 0.0}
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_data])], ignore_index=True)
            st.success(f"{new_name} 님이 등록되었습니다.")

    # 2. 전산 데이터 제어
    st.subheader("📊 전체 회원 실적 관리")
    edited_db = st.data_editor(st.session_state.db) # 표에서 직접 수정 가능
    
    if st.button("수정사항 저장"):
        st.session_state.db = edited_db
        st.success("전산 데이터가 업데이트되었습니다.")

    # 3. 리베이트 일괄 계산 기능 (예시)
    if st.button("🚀 전체 리베이트 정산 실행"):
        # 1랏당 $6 분배 로직 등을 여기에 코딩
        st.info("오늘자 거래 내역에 따른 리베이트 정산이 완료되었습니다.")

# --- 메인 실행 흐름 ---
if st.session_state.role == "Admin":
    admin_panel()
    if st.button("로그아웃"):
        st.session_state.role = None
        st.rerun()
elif st.session_state.role == "User":
    st.write("사용자 화면입니다 (기존 대시보드 코드 연결)")
    if st.button("로그아웃"):
        st.session_state.role = None
        st.rerun()
else:
    login()
