import streamlit as st
import pandas as pd
import os
import re
import hashlib
import secrets
from datetime import datetime

# =========================================================
# TRADING X  (Single-file Streamlit App)
# - CSV 영구저장
# - 비밀번호 해시(PBKDF2)
# - 회원가입 실시간 ID 중복 체크 + 버튼 비활성화
# - 추천인 유효성 체크
# - 직추천 자동 집계
# - 관리자 운영 기능(대시보드/회원 추가/인라인 편집/삭제/정산기록/리포트/조직 점검)
# =========================================================

DB_FILE = "tradingx_db.csv"
LEDGER_FILE = "tradingx_ledger.csv"

COLUMNS = ["ID", "PW", "이름", "이메일", "연락처", "추천인", "위치", "직추천", "소실적", "수익($)", "Role"]
LEDGER_COLS = ["ts", "admin_id", "target_id", "type", "amount", "note"]

DEFAULT_ROWS = [
    {
        "ID": "admin",
        "PW": "",  # init에서 해시로 채움
        "이름": "관리자",
        "이메일": "admin@tradingx.com",
        "연락처": "010-0000-0000",
        "추천인": "-",
        "위치": "-",
        "직추천": 0,
        "소실적": 0,
        "수익($)": 0.0,
        "Role": "admin",
    },
    {
        "ID": "user01",
        "PW": "",
        "이름": "홍길동",
        "이메일": "hong@test.com",
        "연락처": "010-1234-5678",
        "추천인": "admin",
        "위치": "Left",
        "직추천": 0,
        "소실적": 65,
        "수익($)": 1520.50,
        "Role": "user",
    },
]

# =========================
# 0) 보안 유틸: 비밀번호 해시(PBKDF2)
# =========================
def hash_password(password: str, salt_hex: str | None = None) -> str:
    if salt_hex is None:
        salt_hex = secrets.token_hex(16)
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"pbkdf2${salt_hex}${dk.hex()}"

def verify_password(password: str, stored: str) -> bool:
    if isinstance(stored, str) and stored.startswith("pbkdf2$"):
        try:
            _, salt_hex, _hash_hex = stored.split("$", 2)
            return hash_password(password, salt_hex) == stored
        except Exception:
            return False
    return password == stored  # legacy plain-text fallback


# =========================
# 1) DB / Ledger 로드/세이브
# =========================
def load_db() -> pd.DataFrame:
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE, dtype=str)
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = ""
        df = df[COLUMNS].copy()

        df["직추천"] = pd.to_numeric(df["직추천"], errors="coerce").fillna(0).astype(int)
        df["소실적"] = pd.to_numeric(df["소실적"], errors="coerce").fillna(0).astype(int)
        df["수익($)"] = pd.to_numeric(df["수익($)"], errors="coerce").fillna(0.0).astype(float)
        df["Role"] = df["Role"].fillna("user")
        df["추천인"] = df["추천인"].fillna("-")
        df["위치"] = df["위치"].fillna("-")
        return df

    df = pd.DataFrame(DEFAULT_ROWS)
    df.loc[df["ID"] == "admin", "PW"] = hash_password("admin123")
    df.loc[df["ID"] == "user01", "PW"] = hash_password("1234")
    df = df[COLUMNS].copy()
    save_db(df)
    return df

def save_db(df: pd.DataFrame) -> None:
    df = df.copy()
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = ""
    df = df[COLUMNS]
    df.to_csv(DB_FILE, index=False)

def load_ledger() -> pd.DataFrame:
    if os.path.exists(LEDGER_FILE):
        lg = pd.read_csv(LEDGER_FILE, dtype=str)
        for c in LEDGER_COLS:
            if c not in lg.columns:
                lg[c] = ""
        lg = lg[LEDGER_COLS].copy()
        lg["amount"] = pd.to_numeric(lg["amount"], errors="coerce").fillna(0.0).astype(float)
        return lg
    lg = pd.DataFrame(columns=LEDGER_COLS)
    save_ledger(lg)
    return lg

def save_ledger(lg: pd.DataFrame) -> None:
    lg = lg.copy()
    for c in LEDGER_COLS:
        if c not in lg.columns:
            lg[c] = ""
    lg = lg[LEDGER_COLS]
    lg.to_csv(LEDGER_FILE, index=False)

def recalc_direct_referrals(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["추천인"].value_counts().to_dict()
    df = df.copy()
    df["직추천"] = df["ID"].map(lambda x: int(counts.get(x, 0)))
    return df


# =========================
# 2) 세션 초기화
# =========================
def init_state():
    if "db" not in st.session_state:
        st.session_state.db = load_db()
        st.session_state.db = recalc_direct_referrals(st.session_state.db)
        save_db(st.session_state.db)

    if "ledger" not in st.session_state:
        st.session_state.ledger = load_ledger()

    if "page" not in st.session_state:
        st.session_state.page = "login"

init_state()


# =========================
# 3) CSS
# =========================
st.markdown(
    """
<style>
.stApp { background-color: #F8FAFC; color: #1E293B; }

.main-card {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
    padding: 36px;
    border-radius: 18px;
    text-align: center;
    color: white;
    box-shadow: 0 10px 18px rgba(2,6,23,0.12);
    margin-bottom: 18px;
}

.info-box {
    background-color: #FFFFFF;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 6px 14px rgba(2,6,23,0.06);
    border: 1px solid #E2E8F0;
    margin-bottom: 10px;
}

.stTextInput>div>div>input {
    background-color: white !important;
    color: black !important;
    border: 1px solid #CBD5E1 !important;
}
.stButton>button { border-radius: 10px; font-weight: 700; }

[data-testid="stMetricValue"] { color: #2563EB !important; }

/* Admin UI */
.admin-wrap { display:flex; gap:14px; flex-wrap:wrap; margin: 8px 0 16px 0; }
.admin-card {
  background:#fff; border:1px solid #E2E8F0; border-radius:16px;
  padding:16px 16px; box-shadow:0 6px 14px rgba(2,6,23,0.06);
  min-width: 220px; flex:1;
}
.admin-card .label { color:#64748B; font-size:12px; margin-bottom:8px; }
.admin-card .value { color:#0F172A; font-size:26px; font-weight:900; line-height:1.1; }
.admin-card .sub { color:#2563EB; font-size:12px; margin-top:10px; font-weight:800; }
.badge {
  display:inline-block; padding:6px 12px; border-radius:999px;
  background: rgba(37,99,235,0.08); color:#2563EB; font-weight:900; font-size:12px;
  border:1px solid rgba(37,99,235,0.18);
}
.panel {
  background:#fff; border:1px solid #E2E8F0; border-radius:16px;
  padding:14px; box-shadow:0 6px 14px rgba(2,6,23,0.06);
}
.hr { height:1px; background:#E2E8F0; margin: 14px 0; }
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# 4) 유틸
# =========================
def goto(page: str):
    st.session_state.page = page
    st.rerun()

def get_user_row(user_id: str):
    df = st.session_state.db
    u = df[df["ID"] == user_id]
    return None if u.empty else u.iloc[0]

def is_admin(user_id: str) -> bool:
    u = get_user_row(user_id)
    return (u is not None) and (str(u.get("Role", "user")).lower() == "admin")

def now_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_ledger(admin_id: str, target_id: str, typ: str, amount: float = 0.0, note: str = ""):
    lg = st.session_state.ledger.copy()
    row = {"ts": now_ts(), "admin_id": admin_id, "target_id": target_id, "type": typ, "amount": float(amount), "note": note}
    lg = pd.concat([lg, pd.DataFrame([row])], ignore_index=True)
    st.session_state.ledger = lg
    save_ledger(lg)

def sanitize_user_df(df: pd.DataFrame) -> pd.DataFrame:
    # 타입 안정화 + 컬럼 유지
    df = df.copy()
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = ""
    df = df[COLUMNS]

    df["ID"] = df["ID"].astype(str)
    df["Role"] = df["Role"].fillna("user").astype(str)
    df["추천인"] = df["추천인"].fillna("-").astype(str)
    df["위치"] = df["위치"].fillna("-").astype(str)

    df["직추천"] = pd.to_numeric(df["직추천"], errors="coerce").fillna(0).astype(int)
    df["소실적"] = pd.to_numeric(df["소실적"], errors="coerce").fillna(0).astype(int)
    df["수익($)"] = pd.to_numeric(df["수익($)"], errors="coerce").fillna(0.0).astype(float)
    return df


# =========================
# 5) 로그인
# =========================
def login_page():
    st.markdown("<h1 style='text-align:center; color:#2563EB;'>💎 TRADING X</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748B;'>정산 관리 시스템에 접속하세요</p>", unsafe_allow_html=True)

    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    l_id = st.text_input("아이디 (ID)")
    l_pw = st.text_input("비밀번호 (Password)", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("로그인", use_container_width=True, type="primary"):
            df = st.session_state.db
            user = df[df["ID"] == l_id]
            if user.empty:
                st.error("정보가 일치하지 않습니다.")
            else:
                stored = user.iloc[0]["PW"]
                if verify_password(l_pw, stored):
                    # legacy plain-text → 자동 해시 마이그레이션
                    if not str(stored).startswith("pbkdf2$"):
                        idx = df.index[df["ID"] == l_id][0]
                        st.session_state.db.at[idx, "PW"] = hash_password(l_pw)
                        save_db(st.session_state.db)

                    st.session_state.current_user = l_id
                    goto("user")
                else:
                    st.error("정보가 일치하지 않습니다.")
    with col2:
        if st.button("회원가입", use_container_width=True):
            goto("signup")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 6) 회원가입 (실시간 중복 체크 + 버튼 비활성화)
# =========================
def signup_page():
    st.title("📝 회원가입")

    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    new_id = st.text_input("아이디 (ID) - 영문/숫자/언더바 4~20자", help="예: user_123")
    new_pw = st.text_input("비밀번호 (Password) - 4자 이상", type="password")
    name = st.text_input("이름")
    email = st.text_input("이메일")
    phone = st.text_input("연락처")
    recommender = st.text_input("추천인(ID) (없으면 -)")

    df = st.session_state.db

    id_format_ok = bool(re.fullmatch(r"[A-Za-z0-9_]{4,20}", new_id or ""))
    if new_id and not id_format_ok:
        st.warning("아이디는 영문/숫자/언더바만, 4~20자만 가능합니다.")

    id_exists = bool(new_id) and (df["ID"] == new_id).any()
    if id_exists:
        st.error("이미 존재하는 아이디입니다. 다른 아이디를 입력하세요.")

    pw_ok = bool(new_pw) and len(new_pw) >= 4
    if new_pw and not pw_ok:
        st.warning("비밀번호는 4자 이상 입력하세요.")

    recommender_invalid = bool(recommender) and recommender != "-" and not (df["ID"] == recommender).any()
    if recommender_invalid:
        st.warning("추천인 ID가 존재하지 않습니다. '-' 로 입력하거나 정확히 입력하세요.")

    can_submit = id_format_ok and (not id_exists) and pw_ok and (not recommender_invalid)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("가입하기", type="primary", use_container_width=True, disabled=not can_submit):
            new_row = {
                "ID": new_id,
                "PW": hash_password(new_pw),
                "이름": name if name else new_id,
                "이메일": email,
                "연락처": phone,
                "추천인": recommender if recommender else "-",
                "위치": "-",
                "직추천": 0,
                "소실적": 0,
                "수익($)": 0.0,
                "Role": "user",
            }
            df2 = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df2 = sanitize_user_df(df2)
            df2 = recalc_direct_referrals(df2)

            st.session_state.db = df2
            save_db(df2)

            st.success("회원가입 완료! 로그인 해주세요.")
            goto("login")

    with col2:
        if st.button("취소", use_container_width=True):
            goto("login")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 7) 유저 대시보드
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
  <p style="font-size:14px; opacity:0.9;">Total Accumulated Profit</p>
  <h1 style="font-size:44px; font-weight:900; margin:10px 0;">
    ${float(user_info['수익($)']):,.2f}
  </h1>
  <div style="display:inline-block; padding:6px 14px; background:rgba(255,255,255,0.18);
              border-radius:999px; font-size:12px; font-weight:800;">
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
        st.subheader("📊 수익 리포트(샘플)")
        st.area_chart([200, 450, 300, 600, 800, 750, 1100])

    with r_col:
        st.subheader("⚙️ Quick Menu")
        if st.button("🔐 비밀번호 변경", use_container_width=True):
            goto("pw_manage")
        if is_admin(st.session_state.current_user):
            if st.button("🛠️ 관리자 페이지", use_container_width=True):
                goto("admin")
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.pop("current_user", None)
            goto("login")


# =========================
# 8) 비밀번호 변경
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
            if not verify_password(old_pw, user_info["PW"]):
                st.error("현재 비밀번호가 틀립니다.")
                return
            if not new_pw or len(new_pw) < 4:
                st.error("새 비밀번호는 4자 이상 입력하세요.")
                return
            if new_pw != new_pw2:
                st.error("새 비밀번호가 일치하지 않습니다.")
                return

            df = st.session_state.db
            idx = df.index[df["ID"] == user_id][0]
            st.session_state.db.at[idx, "PW"] = hash_password(new_pw)
            save_db(st.session_state.db)

            st.success("비밀번호가 변경되었습니다.")
            goto("user")

    with col2:
        if st.button("뒤로", use_container_width=True):
            goto("user")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 9) 관리자 운영 페이지 (대시보드형 + 운영 기능)
# =========================
def admin_page():
    st.title("🛠️ Admin Dashboard")
    st.markdown("<span class='badge'>TRADING X • Operations</span>", unsafe_allow_html=True)

    if "current_user" not in st.session_state or not is_admin(st.session_state.current_user):
        st.error("관리자만 접근 가능합니다.")
        goto("user")

    admin_id = st.session_state.current_user
    df = st.session_state.db.copy()
    lg = st.session_state.ledger.copy()

    # ===== KPI =====
    total_users = int((df["Role"].str.lower() != "admin").sum())
    total_admin = int((df["Role"].str.lower() == "admin").sum())
    total_profit = float(df["수익($)"].sum())
    avg_profit = float(df[df["Role"].str.lower() != "admin"]["수익($)"].mean()) if total_users > 0 else 0.0
    top_user = df.sort_values("수익($)", ascending=False).iloc[0]
    orphan_cnt = int(((df["추천인"] != "-") & (~df["추천인"].isin(df["ID"]))).sum())

    st.markdown(
        f"""
<div class="admin-wrap">
  <div class="admin-card"><div class="label">Total Users</div><div class="value">{total_users:,}</div><div class="sub">Admins: {total_admin}</div></div>
  <div class="admin-card"><div class="label">Total Profit (All)</div><div class="value">${total_profit:,.2f}</div><div class="sub">Avg/User: ${avg_profit:,.2f}</div></div>
  <div class="admin-card"><div class="label">Top Performer</div><div class="value">{str(top_user["ID"])}</div><div class="sub">${float(top_user["수익($)"]):,.2f}</div></div>
  <div class="admin-card"><div class="label">Data Alerts</div><div class="value">{orphan_cnt}</div><div class="sub">Invalid recommender</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

    # 상단 액션
    colA, colB, colC, colD = st.columns([2.2, 1, 1, 1])
    with colA:
        q = st.text_input("🔎 Search (ID/이름/이메일/추천인)", "")
    with colB:
        if st.button("🔄 직추천 재계산", use_container_width=True):
            st.session_state.db = recalc_direct_referrals(st.session_state.db)
            save_db(st.session_state.db)
            log_ledger(admin_id, "-", "recalc_referrals", 0.0, "직추천 재계산")
            st.success("직추천 재계산 완료")
            st.rerun()
    with colC:
        st.download_button(
            "⬇️ DB Export",
            data=st.session_state.db.to_csv(index=False).encode("utf-8"),
            file_name="tradingx_db_export.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with colD:
        if st.button("⬅️ Back", use_container_width=True):
            goto("user")

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["👥 회원관리", "🧾 정산/기록", "📊 리포트", "⚠️ 데이터점검"])

    # -------------------
    # TAB 1: 회원관리
    # -------------------
    with tab1:
        left, right = st.columns([2.2, 1])

        # (A) 회원 테이블 + 인라인 편집
        with left:
            df_view = df.copy()
            if q.strip():
                mask = (
                    df_view["ID"].str.contains(q, case=False, na=False)
                    | df_view["이름"].str.contains(q, case=False, na=False)
                    | df_view["이메일"].str.contains(q, case=False, na=False)
                    | df_view["추천인"].str.contains(q, case=False, na=False)
                )
                df_view = df_view[mask].copy()

            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.subheader("회원 목록 (인라인 편집 가능)")
            st.caption("PW는 보안상 편집/표시하지 않습니다. 비번 변경은 오른쪽 패널 또는 '정산/기록' 탭에서.")
            edit_cols = ["ID", "이름", "이메일", "연락처", "추천인", "위치", "소실적", "수익($)", "Role"]
            editable = df_view[edit_cols].copy()

            edited = st.data_editor(
                editable,
                use_container_width=True,
                height=520,
                hide_index=True,
                num_rows="fixed",
                column_config={
                    "ID": st.column_config.TextColumn("ID", disabled=True),
                    "Role": st.column_config.SelectboxColumn("Role", options=["user", "admin"]),
                    "위치": st.column_config.SelectboxColumn("위치", options=["-", "Left", "Right"]),
                },
            )

            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("💾 변경 저장", use_container_width=True, type="primary"):
                    # 원본 df에 edited 반영
                    df2 = st.session_state.db.copy()

                    for _, row in edited.iterrows():
                        uid = str(row["ID"])
                        idxs = df2.index[df2["ID"] == uid].tolist()
                        if not idxs:
                            continue
                        idx = idxs[0]
                        for col in ["이름", "이메일", "연락처", "추천인", "위치", "소실적", "수익($)", "Role"]:
                            df2.at[idx, col] = row[col]

                    df2 = sanitize_user_df(df2)

                    # 추천인 유효성 전체 점검
                    bad = (df2["추천인"] != "-") & (~df2["추천인"].isin(df2["ID"]))
                    if bad.any():
                        st.error("저장 실패: 존재하지 않는 추천인이 포함되어 있습니다. (데이터점검 탭에서 확인)")
                    else:
                        df2 = recalc_direct_referrals(df2)
                        st.session_state.db = df2
                        save_db(df2)
                        log_ledger(admin_id, "-", "bulk_update_users", 0.0, "인라인 편집 저장")
                        st.success("저장 완료")
                        st.rerun()

            with c2:
                if st.button("↩️ 변경 취소(새로고침)", use_container_width=True):
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        # (B) 운영 패널: 회원 추가/삭제/비번리셋
        with right:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.subheader("운영 패널")

            st.markdown("**➕ 회원 추가(관리자용)**")
            add_id = st.text_input("새 ID", key="add_id")
            add_pw = st.text_input("임시 비밀번호", type="password", key="add_pw")
            add_name = st.text_input("이름", key="add_name")
            add_email = st.text_input("이메일", key="add_email")
            add_phone = st.text_input("연락처", key="add_phone")
            add_rec = st.text_input("추천인(- 가능)", value="-", key="add_rec")
            add_pos = st.selectbox("위치", ["-", "Left", "Right"], key="add_pos")
            add_role = st.selectbox("Role", ["user", "admin"], key="add_role")

            df0 = st.session_state.db
            add_id_ok = bool(re.fullmatch(r"[A-Za-z0-9_]{4,20}", add_id or ""))
            add_id_exists = bool(add_id) and (df0["ID"] == add_id).any()
            add_pw_ok = bool(add_pw) and len(add_pw) >= 4
            add_rec_ok = (add_rec == "-") or ((df0["ID"] == add_rec).any())

            if add_id and not add_id_ok:
                st.warning("ID 형식 오류(영문/숫자/언더바 4~20자)")
            if add_id_exists:
                st.error("이미 존재하는 ID")
            if add_pw and not add_pw_ok:
                st.warning("비밀번호는 4자 이상")
            if add_rec and not add_rec_ok:
                st.warning("추천인 ID가 존재하지 않음")

            can_add = add_id_ok and (not add_id_exists) and add_pw_ok and add_rec_ok

            if st.button("✅ 회원 생성", use_container_width=True, disabled=not can_add):
                new_row = {
                    "ID": add_id,
                    "PW": hash_password(add_pw),
                    "이름": add_name if add_name else add_id,
                    "이메일": add_email,
                    "연락처": add_phone,
                    "추천인": add_rec if add_rec else "-",
                    "위치": add_pos,
                    "직추천": 0,
                    "소실적": 0,
                    "수익($)": 0.0,
                    "Role": add_role,
                }
                df2 = pd.concat([df0, pd.DataFrame([new_row])], ignore_index=True)
                df2 = sanitize_user_df(df2)
                df2 = recalc_direct_referrals(df2)
                st.session_state.db = df2
                save_db(df2)
                log_ledger(admin_id, add_id, "create_user", 0.0, f"role={add_role}, rec={add_rec}, pos={add_pos}")
                st.success("회원 생성 완료")
                st.rerun()

            st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

            st.markdown("**🔐 비밀번호 리셋(선택 회원)**")
            target_id = st.selectbox("대상 선택", options=df0["ID"].tolist(), key="reset_target")
            reset_pw = st.text_input("새 비밀번호", type="password", key="reset_pw")
            if st.button("비번 리셋", use_container_width=True, disabled=(not reset_pw or len(reset_pw) < 4)):
                if target_id == "admin" and admin_id != "admin":
                    st.error("admin 비밀번호는 admin 계정만 변경 가능(안전장치)")
                else:
                    df2 = st.session_state.db.copy()
                    idx = df2.index[df2["ID"] == target_id][0]
                    df2.at[idx, "PW"] = hash_password(reset_pw)
                    st.session_state.db = df2
                    save_db(df2)
                    log_ledger(admin_id, target_id, "reset_password", 0.0, "관리자 리셋")
                    st.success("비밀번호 변경 완료")
                    st.rerun()

            st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

            st.markdown("**🗑️ 회원 삭제**")
            del_id = st.selectbox("삭제 대상", options=[x for x in df0["ID"].tolist()], key="del_target")
            if del_id == "admin":
                st.info("admin 계정은 삭제할 수 없습니다.")
            else:
                st.warning("삭제는 되돌릴 수 없습니다.")
                if st.button("삭제 실행", use_container_width=True):
                    df2 = st.session_state.db.copy()
                    df2 = df2[df2["ID"] != del_id].reset_index(drop=True)
                    df2 = recalc_direct_referrals(df2)
                    st.session_state.db = df2
                    save_db(df2)
                    log_ledger(admin_id, del_id, "delete_user", 0.0, "회원 삭제")
                    st.success("삭제 완료")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    # -------------------
    # TAB 2: 정산/기록
    # -------------------
    with tab2:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("🧾 정산 처리 (수익 누적 업데이트 + 기록 남김)")

        col1, col2 = st.columns([1.2, 1])
        with col1:
            target_id = st.selectbox("대상 회원", options=st.session_state.db["ID"].tolist(), key="settle_target")
            typ = st.selectbox("정산 타입", ["commission_add", "profit_adjust", "bonus_add", "manual_note"], key="settle_type")
            amount = st.number_input("금액($)", value=0.0, step=10.0, key="settle_amount")
            note = st.text_input("메모", key="settle_note")

            apply_to_profit = typ in ["commission_add", "profit_adjust", "bonus_add"]

            if st.button("정산 반영", type="primary", use_container_width=True):
                df2 = st.session_state.db.copy()
                if target_id not in df2["ID"].values:
                    st.error("대상 회원이 존재하지 않습니다.")
                else:
                    if apply_to_profit:
                        idx = df2.index[df2["ID"] == target_id][0]
                        df2.at[idx, "수익($)"] = float(df2.at[idx, "수익($)"]) + float(amount)
                        df2 = sanitize_user_df(df2)
                        st.session_state.db = df2
                        save_db(df2)

                    log_ledger(admin_id, target_id, typ, float(amount), note)
                    st.success("정산/기록 완료")
                    st.rerun()

        with col2:
            st.markdown("**최근 기록(상위 20)**")
            lg2 = st.session_state.ledger.copy()
            if not lg2.empty:
                view = lg2.sort_values("ts", ascending=False).head(20)
                st.dataframe(view, use_container_width=True, height=320)
            else:
                st.info("기록이 없습니다.")

            st.download_button(
                "⬇️ Ledger Export",
                data=st.session_state.ledger.to_csv(index=False).encode("utf-8"),
                file_name="tradingx_ledger_export.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
        st.subheader("📌 기록 필터")
        f1, f2, f3 = st.columns([1, 1, 1])
        with f1:
            fid = st.text_input("ID 필터(대상)", "")
        with f2:
            ftype = st.selectbox("타입", ["(전체)"] + sorted(st.session_state.ledger["type"].unique().tolist()) if not st.session_state.ledger.empty else ["(전체)"])
        with f3:
            limit = st.selectbox("표시 개수", [50, 100, 200, 500], index=0)

        lgf = st.session_state.ledger.copy()
        if not lgf.empty:
            if fid.strip():
                lgf = lgf[lgf["target_id"].str.contains(fid, case=False, na=False)]
            if ftype != "(전체)":
                lgf = lgf[lgf["type"] == ftype]
            lgf = lgf.sort_values("ts", ascending=False).head(int(limit))
            st.dataframe(lgf, use_container_width=True, height=420)
        else:
            st.info("기록이 없습니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    # -------------------
    # TAB 3: 리포트
    # -------------------
    with tab3:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("📊 리포트")

        # 수익 분포
        tmp = df[df["Role"].str.lower() != "admin"].copy()
        bins = [-1, 0, 100, 500, 1000, 3000, 10000, 10**18]
        labels = ["0", "0~100", "100~500", "500~1K", "1K~3K", "3K~10K", "10K+"]
        if not tmp.empty:
            tmp["bucket"] = pd.cut(tmp["수익($)"], bins=bins, labels=labels)
            dist = tmp["bucket"].value_counts().reindex(labels).fillna(0).astype(int)
            st.markdown("**수익 분포(회원 수)**")
            st.bar_chart(dist)

        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

        # Top lists
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Top 20 Profit**")
            st.dataframe(df.sort_values("수익($)", ascending=False).head(20)[["ID","이름","수익($)","직추천","소실적","추천인","위치","Role"]], use_container_width=True, height=360)
        with c2:
            st.markdown("**Top 20 Direct Referrals**")
            st.dataframe(df.sort_values("직추천", ascending=False).head(20)[["ID","이름","직추천","수익($)","소실적","추천인","위치","Role"]], use_container_width=True, height=360)

        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

        # Ledger 요약(타입별 합계)
        st.markdown("**정산/기록 타입별 합계(금액)**")
        if not lg.empty:
            lg_sum = lg.groupby("type", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
            st.dataframe(lg_sum, use_container_width=True, height=260)
        else:
            st.info("정산 기록이 없습니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    # -------------------
    # TAB 4: 데이터 점검
    # -------------------
    with tab4:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("⚠️ 데이터 점검")

        # 1) 잘못된 추천인
        bad_rec = df[(df["추천인"] != "-") & (~df["추천인"].isin(df["ID"]))][["ID","추천인","이름","Role"]]
        st.markdown("**1) 존재하지 않는 추천인**")
        if bad_rec.empty:
            st.success("이상 없음")
        else:
            st.warning(f"{len(bad_rec)}건")
            st.dataframe(bad_rec, use_container_width=True, height=220)

        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

        # 2) 자기 자신 추천인
        self_rec = df[df["추천인"] == df["ID"]][["ID","추천인","이름","Role"]]
        st.markdown("**2) 자기 자신을 추천인으로 설정**")
        if self_rec.empty:
            st.success("이상 없음")
        else:
            st.warning(f"{len(self_rec)}건")
            st.dataframe(self_rec, use_container_width=True, height=220)

        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

        # 3) Duplicate ID (방어)
        st.markdown("**3) 중복 ID 점검**")
        dup = df[df["ID"].duplicated(keep=False)][["ID","이름","이메일","Role"]]
        if dup.empty:
            st.success("이상 없음")
        else:
            st.error("중복 ID가 존재합니다(치명적).")
            st.dataframe(dup, use_container_width=True, height=220)

        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

        # 4) 자동 수정 도구
        st.markdown("**🔧 자동 수정 도구**")
        colx, coly = st.columns([1,1])
        with colx:
            if st.button("잘못된 추천인 → '-' 로 일괄 수정", use_container_width=True):
                df2 = st.session_state.db.copy()
                bad_mask = (df2["추천인"] != "-") & (~df2["추천인"].isin(df2["ID"]))
                df2.loc[bad_mask, "추천인"] = "-"
                df2 = recalc_direct_referrals(df2)
                st.session_state.db = df2
                save_db(df2)
                log_ledger(admin_id, "-", "fix_invalid_recommender", 0.0, "invalid recommender -> '-'")
                st.success("수정 완료")
                st.rerun()
        with coly:
            if st.button("직추천 재계산만 실행", use_container_width=True):
                st.session_state.db = recalc_direct_referrals(st.session_state.db)
                save_db(st.session_state.db)
                log_ledger(admin_id, "-", "recalc_referrals", 0.0, "직추천 재계산")
                st.success("재계산 완료")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 10) 라우팅
# =========================
page = st.session_state.page

if page == "login":
    login_page()
elif page == "signup":
    signup_page()
elif page == "pw_manage":
    pw_manage_page()
elif page == "admin":
    admin_page()
elif page == "user":
    if "current_user" not in st.session_state:
        goto("login")
    user_dashboard()
else:
    st.error("알 수 없는 페이지입니다.")
    goto("login")
