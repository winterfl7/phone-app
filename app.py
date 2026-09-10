import datetime
import json
import os
import html
import requests
import streamlit as st
from dateutil.relativedelta import relativedelta

DATA_FILE = "data.json"

st.set_page_config(
    page_title="통신 회선 세부 대시보드", page_icon="📱", layout="wide"
)

# 세션 상태 초기화
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "라이트 모드"

if "lines" not in st.session_state:
    st.session_state.lines = []

if "vas_list" not in st.session_state:
    st.session_state.vas_list = []

if "editing_idx" not in st.session_state:
    st.session_state.editing_idx = None

if "editing_vas_idx" not in st.session_state:
    st.session_state.editing_vas_idx = None

if "show_top_add_form" not in st.session_state:
    st.session_state.show_top_add_form = False


# --- 라이트/다크 모드 강제 오버라이딩 CSS ---
theme_choice = st.session_state.get("theme_mode", "라이트 모드")

if theme_choice == "라이트 모드":
    theme_css = """
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #F8F9FA !important;
            color: #111827 !important;
            color-scheme: light !important;
        }

        hr, [data-testid="stDivider"] {
            border-color: #D1D5DB !important;
            background-color: #D1D5DB !important;
        }

        [data-testid="stSidebar"], [data-testid="stSidebar"] > div {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E5E7EB !important;
        }
        
        [data-testid="stSidebar"] *, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            color: #111827 !important;
        }

        [data-testid="stSidebarCollapseButton"], 
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarControl"],
        [data-testid="collapsedControl"] {
            opacity: 1 !important;
            visibility: visible !important;
            display: flex !important;
            z-index: 999999 !important;
            position: fixed !important;
            top: 0.8rem !important;
            left: 0.8rem !important;
        }
        
        [data-testid="stSidebarCollapseButton"] button, 
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebarControl"] button,
        [data-testid="collapsedControl"] button {
            color: #111827 !important;
            background-color: #E5E7EB !important;
            border: 1px solid #9CA3AF !important;
            border-radius: 6px !important;
            opacity: 1 !important;
            visibility: visible !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        [data-testid="stSidebarCollapseButton"] svg, 
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stSidebarControl"] svg,
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapseButton"] path, 
        [data-testid="stSidebarCollapsedControl"] path,
        [data-testid="stSidebarControl"] path,
        [data-testid="collapsedControl"] path {
            fill: #111827 !important;
            color: #111827 !important;
            stroke: #111827 !important;
            opacity: 1 !important;
        }

        div[data-testid="stForm"] label,
        div[data-testid="stForm"] p,
        div[data-testid="stForm"] span,
        div[data-testid="stForm"] div {
            color: #111827 !important;
        }

        input, textarea, select,
        div[data-baseweb="input"],
        div[data-baseweb="input"] *,
        div[data-baseweb="base-input"],
        div[data-baseweb="base-input"] *,
        div[data-baseweb="textarea"],
        div[data-baseweb="select"] > div,
        div[data-testid="stDateInput"],
        div[data-testid="stDateInput"] *,
        div[data-testid="stDateInput"] input,
        div[data-testid="stNumberInput"] input {
            background-color: #FFFFFF !important;
            color: #111827 !important;
            -webkit-text-fill-color: #111827 !important;
            border-color: #D1D5DB !important;
            color-scheme: light !important;
        }

        div[data-baseweb="input"],
        div[data-testid="stDateInput"] input,
        div[data-testid="stNumberInput"] input,
        input, textarea {
            border: 1px solid #D1D5DB !important;
            border-radius: 6px !important;
        }

        div[data-testid="stNumberInput"] button {
            background-color: #F3F4F6 !important;
            color: #111827 !important;
            border: 1px solid #D1D5DB !important;
        }
        div[data-testid="stNumberInput"] button:hover {
            background-color: #E5E7EB !important;
        }

        input::placeholder, textarea::placeholder {
            color: #6B7280 !important;
            -webkit-text-fill-color: #6B7280 !important;
        }

        div[data-baseweb="select"] * {
            background-color: #FFFFFF !important;
            color: #111827 !important;
        }
        div[data-baseweb="select"] svg {
            fill: #111827 !important;
        }
        div[data-baseweb="popover"] *, ul[role="listbox"] * {
            background-color: #FFFFFF !important;
            color: #111827 !important;
        }
        li[role="option"]:hover {
            background-color: #F3F4F6 !important;
        }

        div[data-testid="stExpander"], 
        div[data-testid="stExpander"] > details,
        div[data-testid="stExpander"] summary {
            background-color: #FFFFFF !important;
            color: #111827 !important;
            border: 1px solid #D1D5DB !important;
            border-radius: 8px !important;
        }
        div[data-testid="stExpander"] summary * {
            color: #111827 !important;
        }

        div[data-testid="stFileUploader"],
        div[data-testid="stFileUploader"] section,
        div[data-testid="stFileUploader"] section > div {
            background-color: #FFFFFF !important;
            color: #111827 !important;
            border: 1px dashed #D1D5DB !important;
            border-radius: 8px !important;
        }
        div[data-testid="stFileUploader"] * {
            color: #111827 !important;
        }

        .stButton > button,
        button[kind="primary"],
        button[kind="secondary"],
        div[data-testid="stForm"] button {
            background-color: #F3F4F6 !important;
            color: #111827 !important;
            border: 1px solid #D1D5DB !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
        }
        .stButton > button:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-testid="stForm"] button:hover {
            background-color: #E5E7EB !important;
            color: #000000 !important;
            border-color: #9CA3AF !important;
        }

        .memo-box {
            background-color: #F3F4F6 !important;
            border-left: 4px solid #16A34A !important;
        }
        .memo-title {
            color: #16A34A !important;
        }
        .memo-text {
            color: #111827 !important;
        }
    </style>
    """
elif theme_choice == "다크 모드":
    theme_css = """
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #0E1117 !important;
            color: #FAFAFA !important;
            color-scheme: dark !important;
        }
        
        hr, [data-testid="stDivider"] {
            border-color: #41444C !important;
            background-color: #41444C !important;
        }

        [data-testid="stSidebar"], [data-testid="stSidebar"] > div {
            background-color: #262730 !important;
        }

        [data-testid="stSidebarCollapseButton"], 
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarControl"],
        [data-testid="collapsedControl"] {
            opacity: 1 !important;
            visibility: visible !important;
            display: flex !important;
            z-index: 999999 !important;
            position: fixed !important;
            top: 0.8rem !important;
            left: 0.8rem !important;
        }
        [data-testid="stSidebarCollapseButton"] button, 
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebarControl"] button,
        [data-testid="collapsedControl"] button {
            color: #FAFAFA !important;
            background-color: #262730 !important;
            border: 1px solid #41444C !important;
            opacity: 1 !important;
            visibility: visible !important;
        }
        [data-testid="stSidebarCollapseButton"] svg, 
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stSidebarControl"] svg,
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapseButton"] path, 
        [data-testid="stSidebarCollapsedControl"] path,
        [data-testid="stSidebarControl"] path,
        [data-testid="collapsedControl"] path {
            fill: #FAFAFA !important;
            color: #FAFAFA !important;
            stroke: #FAFAFA !important;
            opacity: 1 !important;
        }

        input, textarea, select,
        div[data-baseweb="input"],
        div[data-baseweb="input"] *,
        div[data-baseweb="base-input"],
        div[data-baseweb="textarea"],
        div[data-baseweb="select"] > div,
        div[data-testid="stDateInput"] input,
        div[data-testid="stNumberInput"] input {
            background-color: #262730 !important;
            color: #FAFAFA !important;
            -webkit-text-fill-color: #FAFAFA !important;
            border: 1px solid #41444C !important;
            color-scheme: dark !important;
        }

        div[data-testid="stNumberInput"] button {
            background-color: #31333F !important;
            color: #FAFAFA !important;
            border: 1px solid #41444C !important;
        }

        input::placeholder, textarea::placeholder {
            color: #9CA3AF !important;
            -webkit-text-fill-color: #9CA3AF !important;
        }

        div[data-baseweb="select"] * {
            background-color: #262730 !important;
            color: #FAFAFA !important;
        }
        div[data-baseweb="select"] svg {
            fill: #FAFAFA !important;
        }

        div[data-baseweb="popover"] *, ul[role="listbox"] * {
            background-color: #262730 !important;
            color: #FAFAFA !important;
        }
        li[role="option"]:hover {
            background-color: #31333F !important;
        }

        div[data-testid="stExpander"], 
        div[data-testid="stExpander"] summary {
            background-color: #262730 !important;
            color: #FAFAFA !important;
            border: 1px solid #41444C !important;
        }

        div[data-testid="stFileUploader"],
        div[data-testid="stFileUploader"] section {
            background-color: #262730 !important;
            color: #FAFAFA !important;
            border: 1px dashed #41444C !important;
        }

        .stButton > button,
        button[kind="primary"],
        button[kind="secondary"],
        div[data-testid="stForm"] button {
            background-color: #262730 !important;
            color: #FAFAFA !important;
            border: 1px solid #41444C !important;
            border-radius: 6px !important;
        }
        .stButton > button:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-testid="stForm"] button:hover {
            background-color: #31333F !important;
            border-color: #6C757D !important;
        }

        .memo-box {
            background-color: #262730 !important;
            border-left: 4px solid #4CAF50 !important;
        }
        .memo-title {
            color: #4CAF50 !important;
        }
        .memo-text {
            color: #D0D0D0 !important;
        }
    </style>
    """
else:
    theme_css = """
    <style>
        [data-testid="stSidebarCollapseButton"], 
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarControl"],
        [data-testid="collapsedControl"] {
            opacity: 1 !important;
            visibility: visible !important;
            display: flex !important;
            z-index: 999999 !important;
            position: fixed !important;
            top: 0.8rem !important;
            left: 0.8rem !important;
        }
        @media (prefers-color-scheme: light) {
            .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #F8F9FA !important; color: #111827 !important; color-scheme: light !important; }
            hr, [data-testid="stDivider"] { border-color: #D1D5DB !important; background-color: #D1D5DB !important; }
            [data-testid="stSidebar"], [data-testid="stSidebar"] > div { background-color: #FFFFFF !important; border-right: 1px solid #E5E7EB !important; }
            [data-testid="stSidebar"] * { color: #111827 !important; }
            div[data-testid="stForm"] label, div[data-testid="stForm"] p, div[data-testid="stForm"] span { color: #111827 !important; }
            [data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebarCollapsedControl"] button, [data-testid="collapsedControl"] button { background-color: #E5E7EB !important; border: 1px solid #9CA3AF !important; }
            [data-testid="stSidebarCollapseButton"] svg, [data-testid="stSidebarCollapsedControl"] svg, [data-testid="collapsedControl"] svg, [data-testid="stSidebarCollapseButton"] path, [data-testid="stSidebarCollapsedControl"] path, [data-testid="collapsedControl"] path { fill: #111827 !important; stroke: #111827 !important; color: #111827 !important; }
            input, textarea, select, div[data-baseweb="input"], div[data-baseweb="input"] *, div[data-baseweb="textarea"], div[data-baseweb="select"] > div, div[data-testid="stDateInput"], div[data-testid="stDateInput"] *, div[data-testid="stNumberInput"] input { background-color: #FFFFFF !important; color: #111827 !important; -webkit-text-fill-color: #111827 !important; border: 1px solid #D1D5DB !important; color-scheme: light !important; }
            div[data-testid="stNumberInput"] button { background-color: #F3F4F6 !important; color: #111827 !important; }
            div[data-baseweb="select"] * { background-color: #FFFFFF !important; color: #111827 !important; }
            div[data-testid="stExpander"], div[data-testid="stExpander"] summary { background-color: #FFFFFF !important; color: #111827 !important; border: 1px solid #D1D5DB !important; }
            div[data-testid="stFileUploader"], div[data-testid="stFileUploader"] section { background-color: #FFFFFF !important; color: #111827 !important; }
            .stButton > button, div[data-testid="stForm"] button { background-color: #F3F4F6 !important; color: #111827 !important; border: 1px solid #D1D5DB !important; }
            .memo-box { background-color: #F3F4F6 !important; border-left: 4px solid #16A34A !important; }
            .memo-title { color: #16A34A !important; }
            .memo-text { color: #111827 !important; }
        }
        @media (prefers-color-scheme: dark) {
            .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #0E1117 !important; color: #FAFAFA !important; color-scheme: dark !important; }
            hr, [data-testid="stDivider"] { border-color: #41444C !important; background-color: #41444C !important; }
            [data-testid="stSidebar"], [data-testid="stSidebar"] > div { background-color: #262730 !important; }
            [data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebarCollapsedControl"] button, [data-testid="collapsedControl"] button { background-color: #262730 !important; border: 1px solid #41444C !important; }
            [data-testid="stSidebarCollapseButton"] svg, [data-testid="stSidebarCollapsedControl"] svg, [data-testid="collapsedControl"] svg, [data-testid="stSidebarCollapseButton"] path, [data-testid="stSidebarCollapsedControl"] path, [data-testid="collapsedControl"] path { fill: #FAFAFA !important; stroke: #FAFAFA !important; color: #FAFAFA !important; }
            input, textarea, select, div[data-baseweb="input"], div[data-baseweb="input"] *, div[data-baseweb="textarea"], div[data-baseweb="select"] > div, div[data-testid="stDateInput"], div[data-testid="stNumberInput"] input { background-color: #262730 !important; color: #FAFAFA !important; -webkit-text-fill-color: #FAFAFA !important; border: 1px solid #41444C !important; color-scheme: dark !important; }
            div[data-testid="stNumberInput"] button { background-color: #31333F !important; color: #FAFAFA !important; }
            div[data-baseweb="select"] * { background-color: #262730 !important; color: #FAFAFA !important; }
            div[data-testid="stExpander"], div[data-testid="stExpander"] summary { background-color: #262730 !important; color: #FAFAFA !important; border: 1px solid #41444C !important; }
            div[data-testid="stFileUploader"], div[data-testid="stFileUploader"] section { background-color: #262730 !important; color: #FAFAFA !important; }
            .stButton > button, div[data-testid="stForm"] button { background-color: #262730 !important; color: #FAFAFA !important; border: 1px solid #41444C !important; }
            .memo-box { background-color: #262730 !important; border-left: 4px solid #4CAF50 !important; }
            .memo-title { color: #4CAF50 !important; }
            .memo-text { color: #D0D0D0 !important; }
        }
    </style>
    """

st.markdown(f"""
    {theme_css}
    <style>
    html {{
        font-size: clamp(12px, 0.9vw, 15px) !important;
    }}
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stMarkdownContainer"] span,
    div[data-testid="stText"] {{
        font-size: 0.95rem !important;
        line-height: 1.25 !important;
        margin-bottom: 0px !important;
    }}
    [data-testid="stHorizontalBlock"] {{
        align-items: center;
        gap: 0.15rem !important;
        padding-top: 1px !important;
        padding-bottom: 1px !important;
    }}
    hr, [data-testid="stDivider"] {{
        margin-top: 0.35rem !important;
        margin-bottom: 0.35rem !important;
    }}
    .vas-section-container [data-testid="stHorizontalBlock"] {{
        margin-top: -0.3rem !important;
        margin-bottom: -0.3rem !important;
    }}
    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }}
    }}
    </style>
""", unsafe_allow_html=True)


# --- GitHub Gist 백업/불러오기 함수 ---
def get_gist_credentials():
    try:
        token = st.secrets["github"]["TOKEN"]
        gist_id = st.secrets["github"]["GIST_ID"]
        return token, gist_id
    except Exception:
        return "", ""

def save_data_to_gist():
    token, gist_id = get_gist_credentials()
    if not token or not gist_id:
        return False, "🔑 깃허브 연동 설정(Secrets)이 필요합니다."
    
    url = f"https://api.github.com/gists/{gist_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    backup_lines = []
    for line in st.session_state.lines:
        line_copy = line.copy()
        if isinstance(line_copy.get("join_date"), datetime.date):
            line_copy["join_date"] = line_copy["join_date"].isoformat()
        backup_lines.append(line_copy)

    backup_vas = []
    for vas in st.session_state.vas_list:
        vas_copy = vas.copy()
        if isinstance(vas_copy.get("start_date"), datetime.date):
            vas_copy["start_date"] = vas_copy["start_date"].isoformat()
        backup_vas.append(vas_copy)

    payload_data = {
        "lines": backup_lines,
        "vas_list": backup_vas
    }

    payload = {
        "description": "통신 회선 관리 자동 백업 데이터",
        "files": {"data.json": {"content": json.dumps(payload_data, ensure_ascii=False, indent=2)}}
    }
    
    try:
        res = requests.patch(url, headers=headers, json=payload, timeout=5)
        if res.status_code == 200:
            return True, "☁️ 깃허브 서버에 동기화 완료!"
        return False, f"연동 실패 (오류 코드: {res.status_code})"
    except Exception as e:
        return False, str(e)

def load_data_from_gist():
    token, gist_id = get_gist_credentials()
    if not token or not gist_id:
        return None, "🔑 깃허브 연동 설정(Secrets)이 필요합니다."
    
    url = f"https://api.github.com/gists/{gist_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            files = res.json().get("files", {})
            if "data.json" in files:
                content = json.loads(files["data.json"]["content"])
                if isinstance(content, list):
                    loaded_lines = content
                    loaded_vas = []
                else:
                    loaded_lines = content.get("lines", [])
                    loaded_vas = content.get("vas_list", [])
                
                processed_lines = [recalculate_dates(item) for item in loaded_lines]
                processed_vas = [recalculate_vas(item) for item in loaded_vas]
                return (processed_lines, processed_vas), "☁️ 깃허브 데이터 로드 완료!"
    except Exception as e:
        return None, str(e)
    return None, "백업 데이터를 찾을 수 없습니다."


def render_github_error_alert(message):
    target_url = "https://github.com/settings/tokens"
    st.markdown(
        f"""
        <a href="{target_url}" target="_blank" style="text-decoration: none;">
            <div style="
                background-color: #5c1d24;
                border: 1px solid #f5c2c7;
                border-left: 5px solid #ea868f;
                padding: 10px 12px;
                border-radius: 6px;
                margin-top: 6px;
                margin-bottom: 6px;
                cursor: pointer;
            ">
                <div style="color: #f8d7da; font-weight: bold; font-size: 12px; margin-bottom: 3px;">
                    {html.escape(message)}
                </div>
                <div style="color: #ffffff; font-size: 11px; text-decoration: underline; font-weight: 600;">
                    👉 깃허브 토큰 설정 페이지 바로가기
                </div>
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )


def save_data_to_file():
    backup_lines = []
    for line in st.session_state.lines:
        line_copy = line.copy()
        if isinstance(line_copy.get("join_date"), datetime.date):
            line_copy["join_date"] = line_copy["join_date"].isoformat()
        backup_lines.append(line_copy)

    backup_vas = []
    for vas in st.session_state.vas_list:
        vas_copy = vas.copy()
        if isinstance(vas_copy.get("start_date"), datetime.date):
            vas_copy["start_date"] = vas_copy["start_date"].isoformat()
        backup_vas.append(vas_copy)

    payload_data = {
        "lines": backup_lines,
        "vas_list": backup_vas
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(payload_data, f, ensure_ascii=False, indent=2)
        
    save_data_to_gist()


def recalculate_dates(item):
    today = datetime.date.today()
    if isinstance(item.get("join_date"), str):
        join_date = datetime.datetime.strptime(
            item["join_date"], "%Y-%m-%d"
        ).date()
    else:
        join_date = item["join_date"]

    mandatory_days = int(item.get("mandatory_days", 185))
    cancel_ok_date = join_date + datetime.timedelta(days=mandatory_days)
    dday = (cancel_ok_date - today).days

    plan_change_days = int(item.get("plan_change_days", 120))
    plan_change_ok_date = join_date + datetime.timedelta(days=plan_change_days)
    plan_dday = (plan_change_ok_date - today).days

    item["join_date"] = join_date
    item["join_date_str"] = join_date.strftime("%Y-%m-%d")
    item["cancel_ok_date_str"] = cancel_ok_date.strftime("%Y-%m-%d")
    item["dday_str"] = "🎉 가능" if dday <= 0 else f"D-{dday}"
    
    item["plan_change_days"] = plan_change_days
    item["plan_change_ok_date_str"] = plan_change_ok_date.strftime("%Y-%m-%d")
    item["plan_dday_str"] = "🎉 가능" if plan_dday <= 0 else f"D-{plan_dday}"

    return item


def recalculate_vas(item):
    today = datetime.date.today()
    if isinstance(item.get("start_date"), str):
        s_date = datetime.datetime.strptime(item["start_date"], "%Y-%m-%d").date()
    else:
        s_date = item["start_date"]

    mand_days = int(item.get("mandatory_days", 185))
    cancel_date = s_date + datetime.timedelta(days=mand_days)
    dday = (cancel_date - today).days

    item["start_date"] = s_date
    item["start_date_str"] = s_date.strftime("%Y-%m-%d")
    item["cancel_date_str"] = cancel_date.strftime("%Y-%m-%d")
    item["mandatory_days"] = mand_days
    item["dday"] = dday
    item["dday_str"] = f"D-day : {dday}"
    return item


def load_data_from_file():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = json.load(f)
                if isinstance(content, list):
                    return [recalculate_dates(item) for item in content], []
                elif isinstance(content, dict):
                    loaded_lines = [recalculate_dates(item) for item in content.get("lines", [])]
                    loaded_vas = [recalculate_vas(item) for item in content.get("vas_list", [])]
                    return loaded_lines, loaded_vas
        except Exception:
            return [], []
    return [], []


if not st.session_state.lines and not st.session_state.vas_list:
    st.session_state.lines, st.session_state.vas_list = load_data_from_file()

# 상단 대시보드 타이틀 및 테마 모드 선택
col_head, col_theme = st.columns([3, 1])
with col_head:
    st.title("📱 통신 회선 및 요금제 통합 관리 프로그램")
    st.caption("회선별 상세 정보 및 의무기간, 요금제 변경일, 해지 가능일, 부가서비스 일정을 관리하세요.")
with col_theme:
    st.selectbox(
        "🎨 테마 설정",
        ["라이트 모드", "다크 모드", "시스템 설정"],
        key="theme_mode"
    )

# 사이드바 입력 폼
with st.sidebar:
    st.header("➕ 새 회선 추가")
    with st.form(key="add_line_form_sidebar", clear_on_submit=True):
        phone_number = st.text_input("전화번호", placeholder="010-0000-0000", key="sb_phone")
        carrier = st.selectbox(
            "통신사",
            ["SKT", "KT", "LGU+", "SKT 알뜰폰", "KT 알뜰폰", "LGU+ 알뜰폰"],
            key="sb_carrier"
        )
        join_date = st.date_input("가입일", datetime.date.today(), key="sb_date")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            mandatory_days = st.number_input(
                "의무기간(일)", min_value=0, value=185, key="sb_mand"
            )
        with col_m2:
            plan_change_days = st.number_input(
                "요금제변경(일)", min_value=0, value=120, key="sb_pchange"
            )

        owner_name = st.text_input("명의", placeholder="홍길동", key="sb_owner")
        phone_model = st.text_input("폰모델", placeholder="Galaxy S24", key="sb_model")

        col_a, col_b = st.columns(2)
        with col_a:
            join_fee = st.text_input("가입비", value="0원", key="sb_fee")
        with col_b:
            buy_type = st.text_input("구입", placeholder="신규/번이/기변", key="sb_buy")

        carrier_id = st.text_input("통신사 계정 ID", placeholder="아이디 입력", key="sb_cid")
        payment_info = st.text_input(
            "납부정보", placeholder="카드/계좌 정보", key="sb_pay"
        )
        
        memo = st.text_area(
            "상세 참고사항 / 비고",
            placeholder="- 혜택/상품권 관련 메모\n- 결합할인 정보 및 고객센터 안내 내용 등 자유 작성",
            height=120,
            key="sb_memo"
        )

        submit_button = st.form_submit_button(
            label="목록에 추가", use_container_width=True
        )

    if submit_button:
        if not phone_number:
            st.error("전화번호를 입력해 주세요.")
        else:
            new_entry = {
                "phone_number": phone_number,
                "carrier": carrier,
                "join_date": join_date,
                "mandatory_days": mandatory_days,
                "plan_change_days": plan_change_days,
                "owner_name": owner_name,
                "phone_model": phone_model,
                "join_fee": join_fee,
                "buy_type": buy_type,
                "carrier_id": carrier_id,
                "payment_info": payment_info,
                "memo": memo,
            }
            new_entry = recalculate_dates(new_entry)
            st.session_state.lines.append(new_entry)
            save_data_to_file()
            st.success("회선이 추가되었습니다!")
            st.rerun()

    st.markdown("---")
    st.header("💾 수동 백업 및 복구")

    if st.session_state.lines or st.session_state.vas_list:
        backup_lines = []
        for line in st.session_state.lines:
            line_copy = line.copy()
            if isinstance(line_copy["join_date"], datetime.date):
                line_copy["join_date"] = line_copy["join_date"].isoformat()
            backup_lines.append(line_copy)

        backup_vas = []
        for vas in st.session_state.vas_list:
            vas_copy = vas.copy()
            if isinstance(vas_copy["start_date"], datetime.date):
                vas_copy["start_date"] = vas_copy["start_date"].isoformat()
            backup_vas.append(vas_copy)

        backup_data = {
            "lines": backup_lines,
            "vas_list": backup_vas
        }

        json_string = json.dumps(
            backup_data, ensure_ascii=False, indent=2
        ).encode("utf-8")

        st.download_button(
            label="📥 수동 백업 (파일 다운로드)",
            data=json_string,
            file_name=f"회선관리_백업_{datetime.date.today().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
        )

    uploaded_file = st.file_uploader(
        "📂 백업 파일 선택 (.json)", type=["json"]
    )
    if uploaded_file is not None:
        if st.button("🔄 파일에서 복구하기", use_container_width=True):
            try:
                content = json.load(uploaded_file)
                if isinstance(content, list):
                    st.session_state.lines = [recalculate_dates(item) for item in content]
                    st.session_state.vas_list = []
                else:
                    st.session_state.lines = [recalculate_dates(item) for item in content.get("lines", [])]
                    st.session_state.vas_list = [recalculate_vas(item) for item in content.get("vas_list", [])]

                st.session_state.editing_idx = None
                st.session_state.editing_vas_idx = None
                save_data_to_file()
                st.success("데이터 복구가 완료되었습니다!")
                st.rerun()
            except Exception:
                st.error("복구에 실패했습니다.")

    st.markdown("---")
    st.header("☁️ 깃허브(Gist) 자동 동기화")
    
    if st.button("☁️ 지금 저장", use_container_width=True):
        ok, msg = save_data_to_gist()
        if ok:
            st.success(msg)
        else:
            render_github_error_alert(msg)
            
    if st.button("🔄 최신 불러오기", use_container_width=True):
        data_tuple, msg = load_data_from_gist()
        if data_tuple is not None:
            st.session_state.lines, st.session_state.vas_list = data_tuple
            st.session_state.editing_idx = None
            st.session_state.editing_vas_idx = None
            save_data_to_file()
            st.success(msg)
            st.rerun()
        else:
            render_github_error_alert(msg)

# 메인 화면 컨트롤
col_title, col_btn_add, col_option = st.columns([2.5, 1.2, 1.3])
with col_title:
    st.subheader("📋 회선 세부 관리 목록")
with col_btn_add:
    add_toggle_label = "❌ 회선추가 닫기" if st.session_state.show_top_add_form else "➕ 새 회선 추가"
    if st.button(add_toggle_label, use_container_width=True):
        st.session_state.show_top_add_form = not st.session_state.show_top_add_form
        st.rerun()
with col_option:
    hide_memo = st.checkbox("👁️ 상세 메모 숨기기", value=False)

if st.session_state.show_top_add_form:
    with st.expander("➕ 새 회선 추가하기 입력창", expanded=True):
        with st.form(key="add_line_form_top", clear_on_submit=True):
            top_col1, top_col2, top_col3 = st.columns(3)
            with top_col1:
                t_phone_number = st.text_input("전화번호", placeholder="010-0000-0000", key="top_phone")
                t_carrier = st.selectbox(
                    "통신사",
                    ["SKT", "KT", "LGU+", "SKT 알뜰폰", "KT 알뜰폰", "LGU+ 알뜰폰"],
                    key="top_carrier"
                )
                t_join_date = st.date_input("가입일", datetime.date.today(), key="top_date")

            with top_col2:
                t_mandatory_days = st.number_input(
                    "의무기간(일)", min_value=0, value=185, key="top_mand"
                )
                t_plan_change_days = st.number_input(
                    "요금제 변경 가능(일)", min_value=0, value=120, key="top_pchange"
                )
                t_owner_name = st.text_input("명의", placeholder="홍길동", key="top_owner")
                t_phone_model = st.text_input("폰모델", placeholder="Galaxy S24", key="top_model")

            with top_col3:
                t_join_fee = st.text_input("가입비", value="0원", key="top_fee")
                t_buy_type = st.text_input("구입", placeholder="신규/번이/기변", key="top_buy")
                t_carrier_id = st.text_input("통신사 계정 ID", placeholder="아이디 입력", key="top_cid")
                t_payment_info = st.text_input("납부정보", placeholder="카드/계좌 정보", key="top_pay")

            t_memo = st.text_area("상세 참고사항 / 비고", placeholder="혜택/결합 정보 등", height=100, key="top_memo")
            top_submit = st.form_submit_button(label="➕ 회선 등록하기", use_container_width=True)

        if top_submit:
            if not t_phone_number:
                st.error("전화번호를 입력해 주세요.")
            else:
                new_entry = {
                    "phone_number": t_phone_number,
                    "carrier": t_carrier,
                    "join_date": t_join_date,
                    "mandatory_days": t_mandatory_days,
                    "plan_change_days": t_plan_change_days,
                    "owner_name": t_owner_name,
                    "phone_model": t_phone_model,
                    "join_fee": t_join_fee,
                    "buy_type": t_buy_type,
                    "carrier_id": t_carrier_id,
                    "payment_info": t_payment_info,
                    "memo": t_memo,
                }
                new_entry = recalculate_dates(new_entry)
                st.session_state.lines.append(new_entry)
                save_data_to_file()
                st.session_state.show_top_add_form = False
                st.success("회선이 추가되었습니다!")
                st.rerun()

st.divider()

# 회선 목록 출력
if not st.session_state.lines:
    st.info("👈 왼쪽 사이드바 또는 상단의 '➕ 새 회선 추가' 버튼을 눌러 회선 정보를 입력해 주세요.")
else:
    col_widths = [1.2, 0.9, 1.0, 1.0, 1.85, 1.0, 0.7, 0.9, 0.7, 0.7, 1.1, 1.3, 0.5, 0.5]
    headers = [
        "전화번호",
        "통신사",
        "가입일",
        "의무기간",
        "요금제 변경일(D-day)",
        "해지가능일",
        "명의",
        "폰모델",
        "가입비",
        "구입",
        "통신사",
        "납부정보",
        "수정",
        "삭제",
    ]

    header_cols = st.columns(col_widths)
    for col, header in zip(header_cols, headers):
        col.markdown(f"**{header}**")

    st.divider()

    for idx, item in enumerate(st.session_state.lines):
        row = st.columns(col_widths)

        row[0].write(f"**{item['phone_number']}**")
        row[1].write(item["carrier"])
        row[2].write(item["join_date_str"])

        if item["dday_str"] == "🎉 가능":
            row[3].markdown(f"🟢 **{item['dday_str']}**")
        else:
            row[3].markdown(f"🔴 **{item['dday_str']}**")

        plan_str = f"{item['plan_change_ok_date_str']} ({item['plan_dday_str']})"
        if item["plan_dday_str"] == "🎉 가능":
            row[4].markdown(f"🟢 **{plan_str}**")
        else:
            row[4].markdown(f"🔴 **{plan_str}**")

        row[5].write(item["cancel_ok_date_str"])
        row[6].write(item.get("owner_name", "-"))
        row[7].write(item.get("phone_model", "-"))
        row[8].write(item.get("join_fee", "-"))
        row[9].write(item.get("buy_type", "-"))
        row[10].write(item.get("carrier_id", "-"))
        row[11].write(item.get("payment_info", "-"))

        if row[12].button("✏️", key=f"btn_edit_{idx}"):
            st.session_state.editing_idx = (
                None if st.session_state.editing_idx == idx else idx
            )
            st.rerun()

        if row[13].button("🗑️", key=f"btn_del_{idx}"):
            st.session_state.lines.pop(idx)
            if st.session_state.editing_idx == idx:
                st.session_state.editing_idx = None
            save_data_to_file()
            st.rerun()

        # 메모 내용 출력 (상세 메모 숨기기가 아닐 때만 표시)
        memo_content = item.get("memo", "")
        if memo_content and not hide_memo:
            escaped_memo = html.escape(memo_content)
            st.markdown(
                f"""
                <div class="memo-box" style="padding: 6px 10px; border-radius: 6px; margin-top: 2px; margin-bottom: 2px;">
                    <div class="memo-title" style="font-weight: bold; font-size: clamp(11px, 0.85vw, 13px); margin-bottom: 2px;">📌 세부 참고사항 / 메모:</div>
                    <pre class="memo-text" style="margin: 0; font-family: inherit; font-size: clamp(11px, 0.85vw, 13px); line-height: 1.3; white-space: pre-wrap; word-wrap: break-word; background: transparent; border: none; padding: 0;">{escaped_memo}</pre>
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.session_state.editing_idx == idx:
            with st.form(key=f"inline_edit_form_{idx}"):
                st.markdown(f"**✏️ '{item['phone_number']}' 정보 수정**")
                col_e1, col_e2, col_e3 = st.columns(3)

                carrier_list = [
                    "SKT",
                    "KT",
                    "LGU+",
                    "SKT 알뜰폰",
                    "KT 알뜰폰",
                    "LGU+ 알뜰폰",
                ]

                with col_e1:
                    e_phone_number = st.text_input(
                        "전화번호",
                        value=item["phone_number"],
                        key=f"e_num_{idx}",
                    )
                    e_carrier = st.selectbox(
                        "통신사",
                        carrier_list,
                        index=(
                            carrier_list.index(item["carrier"])
                            if item["carrier"] in carrier_list
                            else 0
                        ),
                        key=f"e_car_{idx}",
                    )
                    e_join_date = st.date_input(
                        "가입일", value=item["join_date"], key=f"e_jdate_{idx}"
                    )

                with col_e2:
                    e_mandatory_days = st.number_input(
                        "의무기간(일)",
                        min_value=0,
                        value=int(item.get("mandatory_days", 185)),
                        key=f"e_mand_{idx}",
                    )
                    e_plan_change_days = st.number_input(
                        "요금제 변경 가능(일)",
                        min_value=0,
                        value=int(item.get("plan_change_days", 120)),
                        key=f"e_pchange_{idx}",
                    )
                    e_owner_name = st.text_input(
                        "명의",
                        value=item.get("owner_name", ""),
                        key=f"e_own_{idx}",
                    )
                    e_phone_model = st.text_input(
                        "폰모델",
                        value=item.get("phone_model", ""),
                        key=f"e_mod_{idx}",
                    )

                with col_e3:
                    e_join_fee = st.text_input(
                        "가입비",
                        value=item.get("join_fee", ""),
                        key=f"e_fee_{idx}",
                    )
                    e_buy_type = st.text_input(
                        "구입",
                        value=item.get("buy_type", ""),
                        key=f"e_buy_{idx}",
                    )
                    e_carrier_id = st.text_input(
                        "통신사 계정 ID",
                        value=item.get("carrier_id", ""),
                        key=f"e_cid_{idx}",
                    )
                    e_payment_info = st.text_input(
                        "납부정보",
                        value=item.get("payment_info", ""),
                        key=f"e_pay_{idx}",
                    )

                e_memo = st.text_area(
                    "상세 참고사항 / 비고",
                    value=item.get("memo", ""),
                    key=f"e_memo_{idx}",
                    height=120
                )

                col_btn1, col_btn2 = st.columns([1, 5])
                with col_btn1:
                    save_btn = st.form_submit_button(
                        "저장", use_container_width=True
                    )
                with col_btn2:
                    cancel_btn = st.form_submit_button("취소")

                if save_btn:
                    updated_item = {
                        "phone_number": e_phone_number,
                        "carrier": e_carrier,
                        "join_date": e_join_date,
                        "mandatory_days": e_mandatory_days,
                        "plan_change_days": e_plan_change_days,
                        "owner_name": e_owner_name,
                        "phone_model": e_phone_model,
                        "join_fee": e_join_fee,
                        "buy_type": e_buy_type,
                        "carrier_id": e_carrier_id,
                        "payment_info": e_payment_info,
                        "memo": e_memo,
                    }
                    st.session_state.lines[idx] = recalculate_dates(
                        updated_item
                    )
                    st.session_state.editing_idx = None
                    save_data_to_file()
                    st.success("수정이 완료되었습니다!")
                    st.rerun()

                if cancel_btn:
                    st.session_state.editing_idx = None
                    st.rerun()

            # --- 수정 모드(✏️)로 진입했을 때만 '의무 부가서비스 추가' 영역 노출 ---
            default_target_str = f"({item['carrier']},{item.get('owner_name', '회선')}회선) {item['phone_number']}"
            with st.expander(f"➕ [{item['phone_number']}] 의무 부가서비스 추가", expanded=True):
                
                # 본 회선에 이미 등록된 부가서비스가 있다면 목록을 보여주고 수정/삭제할 수 있는 영역 제공
                line_vas_indices = [v_idx for v_idx, v in enumerate(st.session_state.vas_list) if item['phone_number'] in v.get('target_line', '')]
                
                if line_vas_indices:
                    st.markdown("##### 📝 등록된 부가가입 서비스 목록 (수정 및 삭제 가능)")
                    for v_idx in line_vas_indices:
                        vas_item = st.session_state.vas_list[v_idx]
                        
                        col_text, col_edit_btn, col_del_btn = st.columns([10, 0.45, 0.45])
                        with col_text:
                            st.markdown(f"- **{vas_item.get('description')}** ({vas_item.get('start_date_str')} ~ {vas_item.get('mandatory_days')}일 / {vas_item.get('dday_str')})")
                        with col_edit_btn:
                            if st.button("✏️", key=f"line_edit_vas_{v_idx}", help="수정", use_container_width=True):
                                st.session_state.editing_vas_idx = None if st.session_state.editing_vas_idx == v_idx else v_idx
                                st.rerun()
                        with col_del_btn:
                            if st.button("🗑️", key=f"line_del_vas_{v_idx}", help="삭제", use_container_width=True):
                                st.session_state.vas_list.pop(v_idx)
                                if st.session_state.editing_vas_idx == v_idx:
                                    st.session_state.editing_vas_idx = None
                                save_data_to_file()
                                st.rerun()

                        # 개별 인라인 수정 폼
                        if st.session_state.editing_vas_idx == v_idx:
                            with st.form(key=f"inline_edit_vas_sub_form_{v_idx}"):
                                st.markdown(f"**✏️ 부가서비스 정보 수정**")
                                ve_col1, ve_col2, ve_col3, ve_col4 = st.columns([1.5, 2.0, 1.0, 1.0])
                                with ve_col1:
                                    ve_target = st.text_input("회선 식별명", value=vas_item.get('target_line', ''), key=f"sub_ve_target_{v_idx}")
                                with ve_col2:
                                    ve_desc = st.text_input("부가서비스 내용 / 메모", value=vas_item.get('description', ''), key=f"sub_ve_desc_{v_idx}")
                                with ve_col3:
                                    ve_start_date = st.date_input("시작일", value=vas_item['start_date'], key=f"sub_ve_sdate_{v_idx}")
                                with ve_col4:
                                    ve_mandatory_days = st.number_input("의무사용 일수", min_value=0, value=int(vas_item.get('mandatory_days', 183)), key=f"sub_ve_mdays_{v_idx}")

                                ve_btn1, ve_btn2 = st.columns([1, 5])
                                with ve_btn1:
                                    ve_save = st.form_submit_button("저장", use_container_width=True)
                                with ve_btn2:
                                    ve_cancel = st.form_submit_button("취소")

                                if ve_save:
                                    if not ve_desc:
                                        st.error("부가서비스 내용을 입력해 주세요.")
                                    else:
                                        updated_vas = {
                                            "target_line": ve_target,
                                            "description": ve_desc,
                                            "start_date": ve_start_date,
                                            "mandatory_days": ve_mandatory_days,
                                        }
                                        st.session_state.vas_list[v_idx] = recalculate_vas(updated_vas)
                                        st.session_state.editing_vas_idx = None
                                        save_data_to_file()
                                        st.success("부가서비스 수정이 완료되었습니다!")
                                        st.rerun()

                                if ve_cancel:
                                    st.session_state.editing_vas_idx = None
                                    st.rerun()
                    st.markdown("---")

                # 부가서비스 등록 폼
                with st.form(key=f"add_vas_form_{idx}", clear_on_submit=True):
                    v_col1, v_col2, v_col3, v_col4 = st.columns([1.5, 2.0, 1.0, 1.0])
                    with v_col1:
                        v_target = st.text_input("회선 식별명", value=default_target_str, key=f"v_target_{idx}")
                    with v_col2:
                        v_desc = st.text_input("부가서비스 내용 / 메모", placeholder="보증금 20만 환급 등", key=f"v_desc_{idx}")
                    with v_col3:
                        v_start_date = st.date_input("시작일", datetime.date.today(), key=f"v_sdate_{idx}")
                    with v_col4:
                        v_mandatory_days = st.number_input("의무사용 일수", min_value=0, value=183, key=f"v_mdays_{idx}")

                    v_submit = st.form_submit_button(label="➕ 이 회선에 부가서비스 등록", use_container_width=True)

                if v_submit:
                    if not v_desc:
                        st.error("부가서비스 내용을 입력해 주세요.")
                    else:
                        new_vas = {
                            "target_line": v_target,
                            "description": v_desc,
                            "start_date": v_start_date,
                            "mandatory_days": v_mandatory_days,
                        }
                        new_vas = recalculate_vas(new_vas)
                        st.session_state.vas_list.append(new_vas)
                        save_data_to_file()
                        st.success("의무 부가서비스가 추가되었습니다!")
                        st.rerun()

        st.divider()

# --- 📌 의무 부가서비스 일정 섹션 ---
st.markdown("---")
st.markdown("### 📌 의무 부가서비스 일정")

if not st.session_state.vas_list:
    st.info("등록된 의무 부가서비스 일정이 없습니다. 각 회선의 수정(✏️) 버튼을 눌러 부가서비스를 추가해 주세요.")
else:
    vas_col_widths = [1.5, 2.2, 2.2, 1.5, 0.45, 0.45]
    vas_headers = ["회선 / 번호", "부가서비스 내용", "의무사용 기간 및 D-day", "해지가능일", "수정", "삭제"]

    st.markdown('<div class="vas-section-container">', unsafe_allow_html=True)
    
    v_header_cols = st.columns(vas_col_widths)
    for col, header in zip(v_header_cols, vas_headers):
        col.markdown(f"**{header}**")

    st.divider()

    for v_idx, vas_item in enumerate(st.session_state.vas_list):
        v_row = st.columns(vas_col_widths)

        v_row[0].write(f"**{vas_item.get('target_line', '-')}**")
        v_row[1].write(vas_item.get('description', '-'))
        
        period_text = f"{vas_item['start_date_str']} 부터 {vas_item['mandatory_days']}일 의무사용 ({vas_item['dday_str']})"
        v_row[2].write(period_text)
        
        cancel_text = f"{vas_item['cancel_date_str']} 에 해지가능"
        v_row[3].write(cancel_text)

        if v_row[4].button("✏️", key=f"btn_edit_vas_{v_idx}", use_container_width=True):
            st.session_state.editing_vas_idx = (
                None if st.session_state.editing_vas_idx == v_idx else v_idx
            )
            st.rerun()

        if v_row[5].button("🗑️", key=f"btn_del_vas_{v_idx}", use_container_width=True):
            st.session_state.vas_list.pop(v_idx)
            if st.session_state.editing_vas_idx == v_idx:
                st.session_state.editing_vas_idx = None
            save_data_to_file()
            st.rerun()

        if st.session_state.editing_vas_idx == v_idx:
            with st.form(key=f"inline_edit_vas_form_{v_idx}"):
                st.markdown(f"**✏️ 부가서비스 정보 수정**")
                ve_col1, ve_col2, ve_col3, ve_col4 = st.columns([1.5, 2.0, 1.0, 1.0])
                with ve_col1:
                    ve_target = st.text_input("회선 식별명", value=vas_item.get('target_line', ''), key=f"ve_target_{v_idx}")
                with ve_col2:
                    ve_desc = st.text_input("부가서비스 내용 / 메모", value=vas_item.get('description', ''), key=f"ve_desc_{v_idx}")
                with ve_col3:
                    ve_start_date = st.date_input("시작일", value=vas_item['start_date'], key=f"ve_sdate_{v_idx}")
                with ve_col4:
                    ve_mandatory_days = st.number_input("의무사용 일수", min_value=0, value=int(vas_item.get('mandatory_days', 183)), key=f"ve_mdays_{v_idx}")

                ve_btn1, ve_btn2 = st.columns([1, 5])
                with ve_btn1:
                    ve_save = st.form_submit_button("저장", use_container_width=True)
                with ve_btn2:
                    ve_cancel = st.form_submit_button("취소")

                if ve_save:
                    if not ve_desc:
                        st.error("부가서비스 내용을 입력해 주세요.")
                    else:
                        updated_vas = {
                            "target_line": ve_target,
                            "description": ve_desc,
                            "start_date": ve_start_date,
                            "mandatory_days": ve_mandatory_days,
                        }
                        st.session_state.vas_list[v_idx] = recalculate_vas(updated_vas)
                        st.session_state.editing_vas_idx = None
                        save_data_to_file()
                        st.success("부가서비스 수정이 완료되었습니다!")
                        st.rerun()

                if ve_cancel:
                    st.session_state.editing_vas_idx = None
                    st.rerun()

        st.divider()
    
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("🚨 전체 목록 초기화"):
    st.session_state.lines = []
    st.session_state.vas_list = []
    st.session_state.editing_idx = None
    st.session_state.editing_vas_idx = None
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.warning("모든 회선 및 부가서비스 목록이 초기화되었습니다.")
    st.rerun()