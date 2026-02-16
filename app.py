import streamlit as st
import pandas as pd

# =========================
# 1) 세션 초기화 + DB 초기화
# =========================
def init_state():
    if "db" not in st.session_state or "PW" not in st.session_state.db.columns:
        st.session_state.db = pd.DataFrame(
            [
                {
                    "ID": "admin",
                    "PW": "admin123",
                    "이름": "관리자",
                    "이메일": "admin@tradingx.com",
                    "연락처": "010-0000-0000",
                    "추천인": "-",
                    "위치": "-",
                    "직추천": 0,
                    "소실적": 0,
                    "수익($)": 0.0,
                },
                {
                    "ID": "user01",
                    "PW": "1234",
                    "이름": "홍길동",
                    "이메일": "hong@test.com",
                    "연락처": "010-1234-5678",
                    "추천인": "admin",
                    "위치": "Left",
                    "직추천": 12,
                    "소실적": 65,
                    "수익($)": 1520.50,
                },
            ]
        )

    if "page" not in st.session_state:
        st.session_state.page = "login"


init_state()

# =========================
# 2) CSS (밝은 테마)
# =========================
st.markdown(
    """
<style>
.stApp { background-color: #F8FAFC; color: #1E293B; }

/* 메인 수익 카드 */
.main-card {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
    padding: 40px;
    border-radius: 20px;
    text-align: center;
    color: white;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
}

/* 흰색 정보 박스 */
.info-box {
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    border: 1px solid #E2E8F0;
    margin-bottom: 10px;
}

/* 입력창/버튼 */
.stTextInput>div>div>input {
    background-color: white !important;
    color: black !important;
    border: 1px solid #CBD5E1 !important;
}
.stButton>button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s;
}

/* 메트릭 값 색상 */
[data-testid="stMetricValue"] { color: #2563EB !important; }
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# 3) 유틸 함수
# =========================
def goto(page: str):
    st.session_state.page = page
    st.rerun()


def get_user_row(user_id: str):
    df = st.session_state.db
    user = df[df["ID"] == user_id]
    if user.empty:
        return None
    return user.iloc[0]


# =========================
# 4) 페이지: 대시보드
# =========================
def user_dashboard():
    user_info = get_user_row(st.session_state.current_user)
    if user_info is None:
        st.error("사용자 정보를 찾을 수 없습니다.")
        goto("login")

    st.title("🚀 My Trading X")
    st.write(f"오늘도 좋은 하루 되세요, **{user_info['이름']}**님!")

    st.markdown(
        f"""
<div class="main-card">
    <p style="font-size:16px; opacity:0.9;">Total Accumulated Profit</p>
    <h1 style="font-size:48px; font-weight:800; margin:10px 0;">
        ${user_info['수익($)']:,.2f}
    </h1>
    <div style="display:inline-block; padding:5px 15px; background:rgba(255,255,255,0.2);
                border-radius:20px; font-size:12px;">
        Rank: Diamond Partner
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("👥 **Direct Referrals**")
        st.subheader(f"{int(user_info['직추천'])} 명")
    with c2:
        st.success("📉 **Weak Leg Members**")
        st.subheader(f"{int(user_info['소실적'])} 명")
    with c3:
        st.warning("💰 **Commission Rate**")
        st.subheader("17.5 %")

    st.write("---")

    l_col, r_col = st.columns([2, 1])

    with l_col:
        st.subheader("📊 수익 리포트")
        st.area_chart([200, 450, 300, 600, 800, 750, 1100])

    with r_col:
        st.subheader("⚙️ Quick Menu")
        if st.button("🔐 비밀번호 변경", use_container_width=True):
            goto("pw_manage")
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.pop("current_user", None)
            goto("login")


# =========================
# 5) 페이지: 로그인
# =========================
def login_page():
    st.markdown(
        "<h1 style='text-align: center; color: #2563EB;'>💎 TRADING X</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #64748B;'>정산 관리 시스템에 접속하세요</p>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    l_id = st.text_input("아이디 (ID)")
    l_pw = st.text_input("비밀번호 (Password)", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("로그인", use_container_width=True, type="primary"):
            df = st.session_state.db
            user = df[(df["ID"] == l_id) & (df["PW"] == l_pw)]
            if not user.empty:
                st.session_state.current_user = l_id
                goto("user")
            else:
                st.error("정보가 일치하지 않습니다.")
    with col2:
        if st.button("회원가입", use_container_width=True):
            goto("signup")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 6) 페이지: 회원가입 (✅ 입력 즉시 아이디 중복 체크 + 버튼 비활성화)
# =========================
def signup_page():
    st.title("📝 회원가입")

    st.markdown('<div class="info-box">', unsafe_allow_html=True)

    new_id = st.text_input("아이디 (ID)")
    new_pw = st.text_input("비밀번호 (Password)", type="password")
    name = st.text_input("이름")
    email = st.text_input("이메일")
    phone = st.text_input("연락처")
    recommender = st.text_input("추천인(ID) (없으면 -)")

    df = st.session_state.db

    # ✅ 실시간 아이디 중복 체크
    id_exists = bool(new_id) and (df["ID"] == new_id).any()
    if id_exists:
        st.error("이미 존재하는 아이디입니다. 다른 아이디를 입력하세요.")

    # ✅ (선택) 추천인 실시간 체크
    recommender_invalid = (
        bool(recommender) and recommender != "-" and not (df["ID"] == recommender).any()
    )
    if recommender_invalid:
        st.warning("추천인 ID가 존재하지 않습니다. '-' 로 입력하거나 정확히 입력하세요.")

    # ✅ 가입 버튼 활성 조건
    can_submit = (not id_exists) and bool(new_id) and bool(new_pw) and (not recommender_invalid)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "가입하기",
            type="primary",
            use_container_width=True,
            disabled=not can_submit,
        ):
            st.session_state.db = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        [
                            {
                                "ID": new_id,
                                "PW": new_pw,
                                "이름": name if name else new_id,
                                "이메일": email,
                                "연락처": phone,
                                "추천인": recommender if recommender else "-",
                                "위치": "-",
                                "직추천": 0,
                                "소실적": 0,
                                "수익($)": 0.0,
                            }
                        ]
                    ),
                ],
                ignore_index=True,
            )

            st.success("회원가입 완료! 로그인 해주세요.")
            goto("login")

    with col2:
        if st.button("취소", use_container_width=True):
            goto("login")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 7) 페이지: 비밀번호 변경
# =========================
def pw_manage_page():
    st.title("🔐 비밀번호 변경")

    if "current_user" not in st.session_state:
        st.warning("로그인이 필요합니다.")
        goto("login")

    user_id = st.session_state.current_user
    user_info = get_user_row(user_id)
    if user_info is None:
        goto("login")

    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    old_pw = st.text_input("현재 비밀번호", type="password")
    new_pw = st.text_input("새 비밀번호", type="password")
    new_pw2 = st.text_input("새 비밀번호 확인", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("변경하기", type="primary", use_container_width=True):
            if old_pw != user_info["PW"]:
                st.error("현재 비밀번호가 틀립니다.")
                return
            if not new_pw:
                st.error("새 비밀번호를 입력하세요.")
                return
            if new_pw != new_pw2:
                st.error("새 비밀번호가 일치하지 않습니다.")
                return

            idx = st.session_state.db.index[st.session_state.db["ID"] == user_id][0]
            st.session_state.db.at[idx, "PW"] = new_pw
            st.success("비밀번호가 변경되었습니다.")
            goto("user")

    with col2:
        if st.button("뒤로", use_container_width=True):
            goto("user")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 8) 실행 라우팅
# =========================
page = st.session_state.page

if page == "login":
    login_page()
elif page == "signup":
    signup_page()
elif page == "pw_manage":
    pw_manage_page()
elif page == "user":
    if "current_user" not in st.session_state:
        goto("login")
    user_dashboard()
else:
    st.error("알 수 없는 페이지입니다.")
    goto("login")
