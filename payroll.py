import os
import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(page_title="Employee Login Portal", page_icon="🔐")

# --- Language Translations Dictionary ---
translations = {
    "English": {
        "title": "🔐 Employee Login Portal",
        "subtitle": "Please enter your National ID and Password to proceed.",
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
        "password_input_label": "Password (كلمة المرور):",
        "login_btn": "Login",
        "logout_btn": "Logout",
        "empty_input": "Please enter both your National ID and Password.",
        "error_id": (
            "Incorrect National ID or Password. Please check and try again."
        ),
        "missing_pass_col": (
            "⚠️ Error: The uploaded Excel file must contain a password column"
            " (named 'Password' or 'كلمة المرور')."
        ),
        "error_read": "Error reading file: {error}",
        "dashboard_title": "Detailed Payroll & Salary Breakdown",
        "welcome_banner": "Welcome, {name}!",
        "id_display": "National ID:",
        "table_col_key": "Field / Column",
        "table_col_val": "Value",
    },
    "العربية": {
        "title": "🔐 بوابة تسجيل دخول الموظفين",
        "subtitle": "الرجاء إدخال الرقم القومي وكلمة المرور للمتابعة.",
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
        "password_input_label": "كلمة المرور (Password):",
        "login_btn": "تسجيل الدخول",
        "logout_btn": "تسجيل الخروج",
        "empty_input": "الرجاء إدخال الرقم القومي وكلمة المرور معاً.",
        "error_id": "الرقم القومي أو كلمة المرور غير صحيحة. يرجى التحقق.",
        "missing_pass_col": (
            "⚠️ خطأ: يجب أن يحتوي ملف الـ Excel على عمود كلمة المرور (مسمى"
            " 'Password' أو 'كلمة المرور')."
        ),
        "error_read": "خطأ في قراءة الملف: {error}",
        "dashboard_title": "تفصيل مفردات الراتب والبيانات المالية",
        "welcome_banner": "أهلاً بك يا {name}!",
        "id_display": "الرقم القومي:",
        "table_col_key": "الحقل / العمود",
        "table_col_val": "القيمة",
    },
}

# --- Language Switcher in Sidebar ---
st.sidebar.title("🌐 Language / اللغة")
selected_lang = st.sidebar.selectbox("Choose Language", ["العربية", "English"])
t = translations[selected_lang]

SHARED_FILE = "shared_payroll.xlsx"
ADMIN_PASSWORD = "Mirage_Payroll_Secured_2026!#$xK9"

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

if not file_exists and st.session_state.logged_in_user is not None:
  st.session_state.logged_in_user = None
  st.session_state.logged_in_id = None
  st.session_state.employee_row_data = None
  st.rerun()

# --- Main Page Layout ---
st.title(t["title"])

if st.session_state.logged_in_user:
  st.success(t["welcome_banner"].format(name=st.session_state.logged_in_user))

  st.markdown(f"### 📋 {t['dashboard_title']}")
  st.info(
      f"**{t['id_display']}**"
      f" `{str(st.session_state.logged_in_id).strip()}`"
  )

  if st.session_state.employee_row_data is not None:
    row_data = st.session_state.employee_row_data

    table_data = []
    for col_name, val in row_data.items():
      # Skip showing the password column in the employee dashboard for security
      if any(
          k in str(col_name).lower()
          for k in ["password", "pass", "كلمة المرور", "الرقم السري", "كلمه السر"]
      ):
        continue

      display_val = val
      if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan":
        display_val = 0
      table_data.append(
          {t["table_col_key"]: str(col_name), t["table_col_val"]: display_val}
      )

    df_display = pd.DataFrame(table_data)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

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

      # Identify the password column dynamically from the Excel sheet
      pass_col = None
      for col in df.columns:
        if (
            any(
                k in str(col).lower()
                for k in [
                    "password",
                    "pass",
                    "كلمة المرور",
                    "الرقم السري",
                    "كلمه السر",
                ]
            )
            and "قومي" not in str(col)
            and "id" not in str(col).lower()
        ):
          pass_col = col
          break

      if pass_col is None:
        st.error(t["missing_pass_col"])
      else:
        national_id_input = st.text_input(t["input_label"])
        password_input = st.text_input(t["password_input_label"], type="password")

        if st.button(t["login_btn"]):
          if not national_id_input or not password_input:
            st.warning(t["empty_input"])
          else:
            matched = df[
                (
                    df["الرقم القومي"].astype(str).str.strip()
                    == national_id_input.strip()
                )
                & (
                    df[pass_col].astype(str).str.strip()
                    == password_input.strip()
                )
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
