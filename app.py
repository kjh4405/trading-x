import streamlit as st
import pandas as pd

# 1. 전산 데이터 초기화 (실제 운영 시 구글 시트 등과 연결 가능)
if 'member_db' not in st.session_state:
    st.session_state.member_db = pd.DataFrame([
        {"ID": "user01", "이름": "홍길동", "직추천": 12, "소실적": 65, "수익($)": 1500.0},
        {"ID": "user02", "이름": "김철수", "직추천": 5, "소실적": 10, "수익($)": 450.0}
    ])

# 2. 화면 구성
st.set_page_config(page_title="Trading X 전산관리", layout="wide")

st.sidebar.title("🛠️ 전산 메뉴")
menu = st.sidebar.radio("이동할 화면", ["관리자 대시보드", "회원 실적 제어", "신규 회원 등록"])

# --- [화면 1: 관리자 대시보드] ---
if menu == "관리자 대시보드":
    st.title("📊 전체 전산 현황")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("총 등록 인원", f"{len(st.session_state.member_db)} 명")
    col2.metric("총 발생 리베이트", f"${st.session_state.member_db['수익($)'].sum():,.2f}")
    col3.metric("이번 달 신규", "2 명")

    st.subheader("회원 목록 전체 보기")
    st.dataframe(st.session_state.member_db, use_container_width=True)

# --- [화면 2: 회원 실적 제어] ---
elif menu == "회원 실적 제어":
    st.title("⚙️ 실적 수동 제어")
    st.write("회원의 실적(직추천, 소실적)을 직접 수정하여 리베이트를 조정합니다.")
    
    # 데이터 수정 에디터
    edited_df = st.data_editor(st.session_state.member_db, num_rows="dynamic")
    
    if st.button("전산 수정사항 반영하기"):
        st.session_state.member_db = edited_df
        st.success("회원 데이터가 성공적으로 업데이트되었습니다!")

# --- [화면 3: 신규 회원 등록] ---
elif menu == "신규 회원 등록":
    st.title("👤 신규 회원 등록")
    with st.form("add_user"):
        new_id = st.text_input("아이디(ID)")
        new_name = st.text_input("이름")
        new_direct = st.number_input("직추천 수", min_value=0, step=1)
        new_weak = st.number_input("소실적 인원", min_value=0, step=1)
        
        if st.form_submit_button("등록 실행"):
            new_row = {"ID": new_id, "이름": new_name, "직추천": new_direct, "소실적": new_weak, "수익($)": 0.0}
            st.session_state.member_db = pd.concat([st.session_state.member_db, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"{new_name} 님이 전산에 등록되었습니다.")
