import os
import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(page_title="Employee Login Portal", page_icon="🔐")

# --- Language Translations Dictionary ---
translations = {
    "English": {
        "title": "🔐 Employee Login Portal",
        "subtitle": "Please enter your National ID to proceed.",
        "admin_header": "Admin Control Panel",
        "admin_pass_label": "Enter Admin Password:",
        "admin_pass_btn": "Unlock Admin Panel",
        "admin_access_denied": "Incorrect Admin Password.",
        "admin_panel_unlocked": "Admin Panel Unlocked Successfully!",
        "upload_label": "Upload Employees Excel File",
        "remove_btn": "Remove Excel Sheet (Logout Everyone)",
        "upload_success": (
            "Excel file uploaded successfully! All employees can now log in."
        ),
        "remove_success": "Excel file removed. All active sessions logged out.",
        "upload_warning": (
            "⚠️ Employee database not uploaded yet. Please ask the admin to"
            " upload the Excel file from the sidebar."
        ),
        "input_label": "National ID (الرقم القومي):",
        "login_btn": "Login",
        "logout_btn": "Logout",
        "empty_input": "Please enter your National ID.",
        "error_id": "Incorrect National ID. Please check and try again.",
        "error_read": "Error reading file: {error}",
        "dashboard_title": "Detailed Payroll & Salary Breakdown",
        "welcome_banner": "Welcome, {name}!",
        "id_display": "National ID:",
        "earnings_header": "💰 Earnings & Additions",
        "deductions_header": "📉 Deductions & Paycuts",
        "other_header": "📋 General & Other Details",
    },
    "العربية": {
        "title": "🔐 بوابة تسجيل دخول الموظفين",
        "subtitle": "الرجاء إدخال الرقم القومي الخاص بك للمتابعة.",
        "admin_header": "لوحة تحكم المسؤول (Admin)",
        "admin_pass_label": "أدخل كلمة مرور المسؤول:",
        "admin_pass_btn": "فتح لوحة المسؤول",
        "admin_access_denied": "كلمة مرور المسؤول غير صحيحة.",
        "admin_panel_unlocked": "تم فتح لوحة المسؤول بنجاح!",
        "upload_label": "رفع ملف الـ Excel للموظفين",
        "remove_btn": "حذف ملف الـ Excel (تسجيل خروج الجميع)",
        "upload_success": (
            "تم رفع ملف الـ Excel بنجاح! يمكن لجميع الموظفين تسجيل الدخول الآن."
        ),
        "remove_success": "تم حذف الملف وتسجيل خروج جميع الجلسات النشطة.",
        "upload_warning": (
            "⚠️ لم يتم رفع قاعدة بيانات الموظفين بعد. يرجى من المسؤول رفع ملف الـ"
            " Excel من القائمة الجانبية."
        ),
        "input_label": "الرقم القومي (National ID):",
        "login_btn": "تسجيل الدخول",
        "logout_btn": "تسجيل الخروج",
        "empty_input": "الرجاء إدخال الرقم القومي.",
        "error_id": "الرقم القومي غير صحيح. يرجى التحقق والمحاولة مرة أخرى.",
        "error_read": "خطأ في قراءة الملف: {error}",
        "dashboard_title": "تفصيل مفردات الراتب والبيانات المالية",
        "welcome_banner": "أهلاً بك يا {name}!",
        "id_display": "الرقم القومي:",
        "earnings_header": "💰 الإيرادات والمكافآت",
        "deductions_header": "📉 الخصومات والاستقطاعات",
        "other_header": "📋 البيانات العامة والأخرى",
    },
}

# --- Language Switcher in Sidebar ---
st.sidebar.title("🌐 Language / اللغة")
selected_lang = st.sidebar.selectbox("Choose Language", ["العربية", "English"])
t = translations[selected_lang]

SHARED_FILE = "shared_payroll.xlsx"
ADMIN_PASSWORD = (
    "admin123"  # You can change this secret password to whatever you want
)

# Initialize session states
if "logged_in_user" not in st.session_state:
  st.session_state.logged_in_user = None
if "logged_in_id" not in st.session_state:
  st.session_state.logged_in_id = None
if "employee_row_data" not in st.session_state:
  st.session_state.employee_row_data = None
if "admin_authenticated" not in st.session_state:
  st.session_state.admin_authenticated = False

# --- Admin Section (Sidebar with Password Protection) ---
st.sidebar.markdown("---")
st.sidebar.header(t["admin_header"])

if not st.session_state.admin_authenticated:
  admin_pass_input = st.sidebar.text_input(
      t["admin_pass_label"], type="password"
  )
  if st.sidebar.button(t["admin_pass_btn"]):
    if admin_pass_input == ADMIN_PASSWORD:
      st.session_state.admin_authenticated = True
      st.sidebar.success(t["admin_panel_unlocked"])
      st.rerun()
    else:
      st.sidebar.error(t["admin_access_denied"])
else:
  # Once unlocked, show the upload and delete controls
  uploaded_file = st.sidebar.file_uploader(t["upload_label"], type=["xlsx", "xls"])

  if uploaded_file is not None:
    try:
      with open(SHARED_FILE, "wb") as f:
        f.write(uploaded_file.getbuffer())
      st.sidebar.success(t["upload_success"])
    except Exception as e:
      st.sidebar.error(t["error_read"].format(error=e))

  if os.path.exists(SHARED_FILE):
    if st.sidebar.button(t["remove_btn"]):
      os.remove(SHARED_FILE)
      st.sidebar.success(t["remove_success"])
      st.rerun()

  if st.sidebar.button("Lock Admin Panel / قفل لوحة المسؤول"):
    st.session_state.admin_authenticated = False
    st.rerun()

# Check globally if the shared file exists on the server backend
file_exists = os.path.exists(SHARED_FILE)

# If the file was deleted globally by the admin, force logout any active user session
if not file_exists and st.session_state.logged_in_user is not None:
  st.session_state.logged_in_user = None
  st.session_state.logged_in_id = None
  st.session_state.employee_row_data = None
  st.rerun()

# --- Main Page Layout ---
st.title(t["title"])

# Check if an employee is currently logged in -> Show Employee Dashboard
if st.session_state.logged_in_user:
  st.success(t["welcome_banner"].format(name=st.session_state.logged_in_user))

  st.markdown(f"### 📋 {t['dashboard_title']}")
  st.info(
      f"**{t['id_display']}**"
      f" `{str(st.session_state.logged_in_id).strip()}`"
  )

  if st.session_state.employee_row_data is not None:
    row_data = st.session_state.employee_row_data

    earnings_cols = {}
    deductions_cols = {}
    other_cols = {}

    bonus_keywords = [
        "bonus",
        "incentive",
        "overtime",
        "allowance",
        "add",
        "مكافأة",
        "حافز",
        "إضافي",
        "بدل",
        "الراتب",
        "basic",
        "salary",
        "gross",
        "net",
        "صافي",
        "الاساسي",
    ]
    deduction_keywords = [
        "deduction",
        "cut",
        "penalty",
        "absence",
        "tax",
        "insurance",
        "خصم",
        "جزاء",
        "غياب",
        "ضريبة",
        "تأمين",
        "استقطاع",
    ]

    for col_name, val in row_data.items():
      if col_name in ["الاسم", "الرقم القومي", "Name", "National ID"]:
        continue

      display_val = val
      if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan":
        display_val = 0

      col_lower = str(col_name).lower()

      if any(kw in col_lower for kw in deduction_keywords):
        deductions_cols[col_name] = display_val
      elif any(kw in col_lower for kw in bonus_keywords):
        earnings_cols[col_name] = display_val
      else:
        other_cols[col_name] = display_val

    # Render Earnings Section
    if earnings_cols:
      st.markdown(f"#### {t['earnings_header']}")
      cols = st.columns(2)
      idx = 0
      for c_name, c_val in earnings_cols.items():
        with cols[idx % 2]:
          st.metric(label=str(c_name), value=str(c_val))
        idx += 1

    # Render Deductions Section
    if deductions_cols:
      st.markdown(f"#### {t['deductions_header']}")
      cols = st.columns(2)
      idx = 0
      for c_name, c_val in deductions_cols.items():
        with cols[idx % 2]:
          st.metric(label=str(c_name), value=str(c_val))
        idx += 1

    # Render Other Details Section
    if other_cols:
      st.markdown(f"#### {t['other_header']}")
      cols = st.columns(2)
      idx = 0
      for c_name, c_val in other_cols.items():
        with cols[idx % 2]:
          st.metric(label=str(c_name), value=str(c_val))
        idx += 1

  st.markdown("---")
  if st.button(t["logout_btn"]):
    st.session_state.logged_in_user = None
    st.session_state.logged_in_id = None
    st.session_state.employee_row_data = None
    st.rerun()

else:
  st.write(t["subtitle"])

  if not file_exists:
    st.warning(t["upload_warning"])
  else:
    try:
      df = pd.read_excel(SHARED_FILE)
      df.columns = df.columns.str.strip()

      national_id_input = st.text_input(t["input_label"], type="password")

      if st.button(t["login_btn"]):
        if not national_id_input:
          st.warning(t["empty_input"])
        else:
          matched = df[
              df["الرقم القومي"].astype(str).str.strip()
              == national_id_input.strip()
          ]

          if not matched.empty:
            employee_name = matched.iloc[0]["الاسم"]
            st.session_state.logged_in_user = employee_name
            st.session_state.logged_in_id = national_id_input.strip()
            st.session_state.employee_row_data = matched.iloc[0].to_dict()
            st.rerun()
          else:
            st.error(t["error_id"])
    except Exception as e:
      st.error(t["error_read"].format(error=e))
